from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime, date, timedelta
import random
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="VK Drop Taxi - Complete System")
api_router = APIRouter(prefix="/api")

# ==================== ENUMS ====================
class UserRole(str, Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    ADMIN = "admin"

class VehicleType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"

class BookingStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DriverApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DriverStatus(str, Enum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    WAITING = "waiting"
    GOING_HOME = "going_home"
    OFFLINE = "offline"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

# ==================== BASE MODELS ====================
class Location(BaseModel):
    latitude: float
    longitude: float
    address: str

class DocumentUpload(BaseModel):
    front_image: str
    back_image: Optional[str] = None

class PersonalDetails(BaseModel):
    full_name: str
    mobile_number: str
    full_address: str
    aadhaar_number: str
    pan_number: str
    driving_license_number: str
    driving_experience_years: int
    driver_photo: str

class BankDetails(BaseModel):
    account_holder_name: str
    bank_name: str
    account_number: str
    ifsc_code: str
    branch_name: str

class VehicleDetails(BaseModel):
    vehicle_type: VehicleType
    vehicle_number: str
    vehicle_model: str
    vehicle_year: int

class Documents(BaseModel):
    aadhaar_card: DocumentUpload
    pan_card: DocumentUpload
    driving_license: DocumentUpload
    rc_book: DocumentUpload
    insurance: DocumentUpload
    fitness_certificate: DocumentUpload
    permit: DocumentUpload
    pollution_certificate: DocumentUpload

class DocumentExpiry(BaseModel):
    insurance_expiry: str
    fc_expiry: str
    permit_expiry: str
    pollution_expiry: str
    license_expiry: str

class DriverVehiclePhoto(BaseModel):
    photo: str

class ComprehensiveDriverRegister(BaseModel):
    phone: str
    personal_details: PersonalDetails
    bank_details: BankDetails
    vehicle_details: VehicleDetails
    documents: Documents
    document_expiry: DocumentExpiry
    driver_vehicle_photo: DriverVehiclePhoto

# Auth models
class OTPRequest(BaseModel):
    phone: str
    role: UserRole

class OTPVerify(BaseModel):
    phone: str
    otp: str
    role: UserRole

class CustomerRegister(BaseModel):
    phone: str
    name: str
    location: Optional[Location] = None

# Legacy driver register
class DriverRegister(BaseModel):
    phone: str
    name: str
    vehicle_type: VehicleType
    vehicle_number: str
    license_image: str
    rc_image: str

class DriverStatusUpdate(BaseModel):
    is_online: bool

class BookingCreate(BaseModel):
    customer_id: str
    pickup: Location
    drop: Location
    vehicle_type: VehicleType

class BookingUpdate(BaseModel):
    booking_id: str
    status: BookingStatus
    driver_id: Optional[str] = None

class WalletAddMoney(BaseModel):
    user_id: str
    amount: float

class WithdrawRequest(BaseModel):
    driver_id: str
    amount: float

class TariffUpdate(BaseModel):
    vehicle_type: VehicleType
    rate_per_km: float
    minimum_fare: float

class DriverApproval(BaseModel):
    driver_id: str
    approval_status: DriverApprovalStatus
    rejection_reason: Optional[str] = None

class DocumentVerification(BaseModel):
    driver_id: str
    document_type: str
    status: DocumentStatus
    remarks: Optional[str] = None

# ==================== HELPER FUNCTIONS ====================
def send_mock_otp(phone: str):
    return {"otp": "123456", "message": "OTP sent successfully (Mock)"}

def verify_mock_otp(phone: str, otp: str):
    return otp == "123456"

def calculate_mock_distance(pickup: Location, drop: Location):
    lat_diff = abs(pickup.latitude - drop.latitude)
    lon_diff = abs(pickup.longitude - drop.longitude)
    distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
    return round(distance, 2)

async def calculate_fare(distance: float, vehicle_type: VehicleType):
    tariff = await db.tariffs.find_one({"vehicle_type": vehicle_type.value})
    if not tariff:
        rate = 14 if vehicle_type == VehicleType.SEDAN else 18
        minimum = 300
    else:
        rate = tariff['rate_per_km']
        minimum = tariff['minimum_fare']
    fare = distance * rate
    return max(fare, minimum)

def check_document_expiry(expiry_date_str: str, warning_days: int = 30) -> dict:
    try:
        expiry_date = date.fromisoformat(expiry_date_str)
        today = date.today()
        days_until_expiry = (expiry_date - today).days
        
        if days_until_expiry < 0:
            return {
                "status": "expired",
                "days_overdue": abs(days_until_expiry),
                "alert_level": "critical",
                "message": f"Expired {abs(days_until_expiry)} days ago"
            }
        elif days_until_expiry <= warning_days:
            return {
                "status": "expiring_soon",
                "days_remaining": days_until_expiry,
                "alert_level": "warning",
                "message": f"Expires in {days_until_expiry} days"
            }
        else:
            return {
                "status": "valid",
                "days_remaining": days_until_expiry,
                "alert_level": "none",
                "message": f"Valid for {days_until_expiry} days"
            }
    except:
        return {
            "status": "invalid",
            "alert_level": "critical",
            "message": "Invalid date format"
        }

async def check_all_driver_expiries(driver_id: str) -> dict:
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        return None
    
    expiry_data = driver.get('document_expiry', {})
    alerts = {}
    critical_alerts = []
    
    for doc_type, expiry_date_str in expiry_data.items():
        check_result = check_document_expiry(expiry_date_str)
        alerts[doc_type] = check_result
        
        if check_result['alert_level'] in ['critical', 'warning']:
            critical_alerts.append({
                "document": doc_type,
                "status": check_result['status'],
                "message": check_result['message'],
                "alert_level": check_result['alert_level']
            })
    
    return {
        "all_expiries": alerts,
        "critical_alerts": critical_alerts,
        "has_expired_documents": any(a['alert_level'] == 'critical' for a in alerts.values()),
        "has_expiring_documents": any(a['alert_level'] == 'warning' for a in alerts.values())
    }

# Due to length, I'll split this into multiple parts. Continuing in next file...
