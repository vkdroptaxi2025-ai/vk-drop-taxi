from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime, date, timedelta
import random

# Import models
from models import *

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

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

def check_document_expiry(expiry_date: date, warning_days: int = 30) -> dict:
    """Check if document is expired or expiring soon"""
    today = date.today()
    days_until_expiry = (expiry_date - today).days
    
    if days_until_expiry < 0:
        return {"status": "expired", "days": abs(days_until_expiry), "alert": True}
    elif days_until_expiry <= warning_days:
        return {"status": "expiring_soon", "days": days_until_expiry, "alert": True}
    else:
        return {"status": "valid", "days": days_until_expiry, "alert": False}

# ==================== AUTH ENDPOINTS ====================
@api_router.post("/auth/send-otp")
async def send_otp(request: OTPRequest):
    """Send OTP to phone number (Mock - always 123456)"""
    result = send_mock_otp(request.phone)
    return {"success": True, "message": result['message'], "otp_mock": "123456"}

@api_router.post("/auth/verify-otp")
async def verify_otp(request: OTPVerify):
    """Verify OTP and return user info"""
    if not verify_mock_otp(request.phone, request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if request.role == UserRole.CUSTOMER:
        user = await db.users.find_one({"phone": request.phone})
        if user:
            user['_id'] = str(user['_id'])
            return {"success": True, "user": user, "new_user": False}
        return {"success": True, "new_user": True, "phone": request.phone}
    
    elif request.role == UserRole.DRIVER:
        driver = await db.drivers.find_one({"phone": request.phone})
        if driver:
            driver['_id'] = str(driver['_id'])
            return {"success": True, "user": driver, "new_user": False}
        return {"success": True, "new_user": True, "phone": request.phone}
    
    return {"success": False, "message": "Invalid role"}

# ==================== CUSTOMER ENDPOINTS ====================
@api_router.post("/customer/register")
async def register_customer(customer: CustomerRegister):
    """Register new customer"""
    existing = await db.users.find_one({"phone": customer.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists")
    
    user_data = {
        "user_id": str(uuid.uuid4()),
        "phone": customer.phone,
        "name": customer.name,
        "location": customer.location.dict() if customer.location else None,
        "role": UserRole.CUSTOMER.value,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user_data)
    
    # Create wallet
    wallet_data = {
        "user_id": user_data['user_id'],
        "balance": 0.0,
        "transactions": []
    }
    await db.wallets.insert_one(wallet_data)
    
    user_data['_id'] = str(user_data.get('_id'))
    return {"success": True, "user": user_data}

@api_router.get("/customer/{customer_id}/profile")
async def get_customer_profile(customer_id: str):
    """Get customer profile"""
    user = await db.users.find_one({"user_id": customer_id})
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    user['_id'] = str(user['_id'])
    return {"success": True, "user": user}

@api_router.get("/customer/{customer_id}/bookings")
async def get_customer_bookings(customer_id: str):
    """Get customer booking history"""
    bookings = await db.bookings.find({"customer_id": customer_id}).sort("created_at", -1).to_list(100)
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    return {"success": True, "bookings": bookings}

# ==================== PHASE 1: COMPREHENSIVE DRIVER REGISTRATION ====================
@api_router.post("/driver/register/comprehensive")
async def register_driver_comprehensive(driver_data: ComprehensiveDriverRegister):
    """
    Comprehensive driver registration with complete KYC
    Phase 1: Full implementation with all documents
    """
    # Check if driver already exists
    existing = await db.drivers.find_one({"phone": driver_data.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Driver already exists with this phone number")
    
    # Validate Aadhaar number (12 digits)
    if len(driver_data.personal_details.aadhaar_number) != 12:
        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
    
    # Validate PAN number (10 characters)
    if len(driver_data.personal_details.pan_number) != 10:
        raise HTTPException(status_code=400, detail="Invalid PAN number")
    
    # Validate IFSC code (11 characters)
    if len(driver_data.bank_details.ifsc_code) != 11:
        raise HTTPException(status_code=400, detail="Invalid IFSC code")
    
    # Check document expiry dates
    today = date.today()
    if driver_data.document_expiry.insurance_expiry < today:
        raise HTTPException(status_code=400, detail="Insurance has expired")
    if driver_data.document_expiry.license_expiry < today:
        raise HTTPException(status_code=400, detail="Driving license has expired")
    
    # Generate driver ID
    driver_id = str(uuid.uuid4())
    
    # Prepare comprehensive driver document
    driver_document = {
        "driver_id": driver_id,
        "phone": driver_data.phone,
        "role": UserRole.DRIVER.value,
        
        # Personal Details
        "personal_details": {
            "full_name": driver_data.personal_details.full_name,
            "mobile_number": driver_data.personal_details.mobile_number,
            "full_address": driver_data.personal_details.full_address,
            "aadhaar_number": driver_data.personal_details.aadhaar_number,
            "pan_number": driver_data.personal_details.pan_number,
            "driving_license_number": driver_data.personal_details.driving_license_number,
            "driving_experience_years": driver_data.personal_details.driving_experience_years,
            "driver_photo": driver_data.personal_details.driver_photo
        },
        
        # Bank Details
        "bank_details": {
            "account_holder_name": driver_data.bank_details.account_holder_name,
            "bank_name": driver_data.bank_details.bank_name,
            "account_number": driver_data.bank_details.account_number,
            "ifsc_code": driver_data.bank_details.ifsc_code,
            "branch_name": driver_data.bank_details.branch_name
        },
        
        # Vehicle Details
        "vehicle_details": {
            "vehicle_type": driver_data.vehicle_details.vehicle_type.value,
            "vehicle_number": driver_data.vehicle_details.vehicle_number,
            "vehicle_model": driver_data.vehicle_details.vehicle_model,
            "vehicle_year": driver_data.vehicle_details.vehicle_year
        },
        
        # Documents (Base64)
        "documents": {
            "aadhaar_card": driver_data.documents.aadhaar_card.dict(),
            "pan_card": driver_data.documents.pan_card.dict(),
            "driving_license": driver_data.documents.driving_license.dict(),
            "rc_book": driver_data.documents.rc_book.dict(),
            "insurance": driver_data.documents.insurance.dict(),
            "fitness_certificate": driver_data.documents.fitness_certificate.dict(),
            "permit": driver_data.documents.permit.dict(),
            "pollution_certificate": driver_data.documents.pollution_certificate.dict()
        },
        
        # Document Expiry Dates
        "document_expiry": {
            "insurance_expiry": driver_data.document_expiry.insurance_expiry.isoformat(),
            "fc_expiry": driver_data.document_expiry.fc_expiry.isoformat(),
            "permit_expiry": driver_data.document_expiry.permit_expiry.isoformat(),
            "pollution_expiry": driver_data.document_expiry.pollution_expiry.isoformat(),
            "license_expiry": driver_data.document_expiry.license_expiry.isoformat()
        },
        
        # Driver + Vehicle Photo Verification
        "driver_vehicle_photo": driver_data.driver_vehicle_photo.photo,
        
        # Document Verification Status
        "document_verification": {
            "aadhaar_card": DocumentStatus.PENDING.value,
            "pan_card": DocumentStatus.PENDING.value,
            "driving_license": DocumentStatus.PENDING.value,
            "rc_book": DocumentStatus.PENDING.value,
            "insurance": DocumentStatus.PENDING.value,
            "fitness_certificate": DocumentStatus.PENDING.value,
            "permit": DocumentStatus.PENDING.value,
            "pollution_certificate": DocumentStatus.PENDING.value,
            "driver_vehicle_photo": DocumentStatus.PENDING.value
        },
        
        # Approval Status
        "approval_status": DriverApprovalStatus.PENDING.value,
        "approval_remarks": None,
        
        # Driver Status (for Phase 2)
        "driver_status": DriverStatus.OFFLINE.value,
        "is_online": False,
        "duty_on": False,
        "go_home_mode": False,
        "home_location": None,
        
        # Earnings & Stats (for Phase 2)
        "earnings": 0.0,
        "total_trips": 0,
        "completed_trips": 0,
        "continuous_trips_count": 0,  # For 2-trip rule
        "in_queue": False,
        "queue_position": None,
        "current_location": None,
        "last_trip_end_location": None,
        "last_trip_end_time": None,
        
        # Timestamps
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert driver
    await db.drivers.insert_one(driver_document)
    
    # Create wallet for driver
    wallet_data = {
        "user_id": driver_id,
        "balance": 0.0,
        "transactions": [],
        "minimum_balance_required": 1000.0  # Phase 2 requirement
    }
    await db.wallets.insert_one(wallet_data)
    
    driver_document['_id'] = str(driver_document.get('_id'))
    
    return {
        "success": True,
        "driver_id": driver_id,
        "message": "Driver registration submitted successfully. Your application is under review.",
        "approval_status": DriverApprovalStatus.PENDING.value
    }

# Continue in next file...
