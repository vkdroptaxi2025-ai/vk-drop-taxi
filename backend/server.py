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

# ==================== HEALTH CHECK ====================
@api_router.get("/health")
async def health_check():
    """Health check endpoint to verify server is running"""
    try:
        # Check MongoDB connection
        await db.command('ping')
        return {
            "status": "healthy",
            "message": "VK Drop Taxi API is running",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e),
            "database": "disconnected"
        }

# ==================== BRANDED ID GENERATOR ====================
async def get_next_counter(counter_name: str, start_value: int = 1001) -> int:
    """Get next counter value for branded IDs"""
    counter = await db.counters.find_one_and_update(
        {"_id": counter_name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True
    )
    if counter['value'] < start_value:
        await db.counters.update_one(
            {"_id": counter_name},
            {"$set": {"value": start_value}}
        )
        return start_value
    return counter['value']

async def generate_driver_id() -> str:
    """Generate branded driver ID like VKDRV1001"""
    counter = await get_next_counter("driver_counter", 1001)
    return f"VKDRV{counter}"

async def generate_customer_id() -> str:
    """Generate branded customer ID like VKCST1001"""
    counter = await get_next_counter("customer_counter", 1001)
    return f"VKCST{counter}"

async def generate_booking_id() -> str:
    """Generate branded booking ID like VKBK1001"""
    counter = await get_next_counter("booking_counter", 1001)
    return f"VKBK{counter}"

# ==================== ENUMS ====================
class UserRole(str, Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    ADMIN = "admin"

class VehicleType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    CRYSTA = "crysta"

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

class DriverAgreement(BaseModel):
    accepted: bool
    agreement_file: Optional[str] = None
    accepted_at: Optional[str] = None

class ComprehensiveDriverRegister(BaseModel):
    phone: str
    personal_details: PersonalDetails
    vehicle_details: VehicleDetails
    documents: Documents
    document_expiry: DocumentExpiry
    driver_vehicle_photo: DriverVehiclePhoto
    agreement: Optional[DriverAgreement] = None

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

# Simplified driver registration
class SimpleDriverDocuments(BaseModel):
    license_front: str
    license_back: str
    rc_front: str
    rc_back: str
    insurance: str
    driver_photo: str

class SimpleDriverPayment(BaseModel):
    amount: int
    screenshot: str

class SimpleDriverAgreement(BaseModel):
    accepted: bool
    signed_document: str
    accepted_at: str

class SimpleDriverRegister(BaseModel):
    phone: str
    full_name: str
    driving_experience: int
    vehicle_type: VehicleType
    vehicle_number: str
    vehicle_model: str
    documents: SimpleDriverDocuments
    payment: SimpleDriverPayment
    agreement: SimpleDriverAgreement

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

# ==================== COMPREHENSIVE DRIVER ONBOARDING ====================
class DriverBasicDetails(BaseModel):
    full_name: str
    phone: str
    address: str
    aadhaar_number: str
    pan_number: Optional[str] = None
    driving_license_number: str
    driving_experience_years: int

class DriverPhotos(BaseModel):
    driver_photo: str  # Base64 image
    driver_with_vehicle_photo: str  # Base64 image - number plate visible

class DriverDocuments(BaseModel):
    aadhaar_front: str  # Base64 image
    aadhaar_back: str  # Base64 image
    license_front: str  # Base64 image
    license_back: str  # Base64 image

class VehicleDetails(BaseModel):
    vehicle_type: str  # sedan, suv, crysta
    vehicle_number: str
    vehicle_model: str
    vehicle_year: int

class VehicleDocuments(BaseModel):
    rc_front: str  # Base64 image
    rc_back: str  # Base64 image
    insurance: str  # Base64 image
    permit: str  # Base64 image
    pollution_certificate: str  # Base64 image

class VehiclePhotos(BaseModel):
    front_photo: str  # Base64 image
    back_photo: str  # Base64 image
    left_photo: str  # Base64 image
    right_photo: str  # Base64 image

class PaymentDetails(BaseModel):
    amount: Optional[int] = 0
    screenshot: Optional[str] = None  # Base64 image

class ComprehensiveDriverOnboarding(BaseModel):
    """Complete driver onboarding with all required fields"""
    basic_details: DriverBasicDetails
    driver_photos: DriverPhotos
    driver_documents: DriverDocuments
    vehicle_details: VehicleDetails
    vehicle_documents: VehicleDocuments
    vehicle_photos: VehiclePhotos
    payment: Optional[PaymentDetails] = None

# Simple driver registration for backward compatibility
class CleanDriverRegister(BaseModel):
    """Simple driver registration with basic required fields"""
    phone: str
    full_name: str
    address: str
    driving_license_number: str
    driving_license_image: str
    vehicle_type: str
    vehicle_number: str
    rc_book_image: str
    insurance_details: str
    insurance_image: Optional[str] = None

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

# ==================== AUTH ENDPOINTS ====================
@api_router.post("/auth/send-otp")
async def send_otp(request: OTPRequest):
    result = send_mock_otp(request.phone)
    return {"success": True, "message": result['message'], "otp_mock": "123456"}

@api_router.post("/auth/verify-otp")
async def verify_otp(request: OTPVerify):
    if not verify_mock_otp(request.phone, request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # ADMIN SECURITY: Only authorized phone number can login as admin
    AUTHORIZED_ADMIN_PHONE = os.environ.get('AUTHORIZED_ADMIN_PHONE', '9345538164')
    if request.role == UserRole.ADMIN:
        if request.phone != AUTHORIZED_ADMIN_PHONE:
            raise HTTPException(status_code=403, detail="Access Denied")
        # Admin login successful
        return {"success": True, "user": {"phone": request.phone, "role": "admin"}, "new_user": False}
    
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
            expiry_alerts = await check_all_driver_expiries(driver['driver_id'])
            driver['expiry_alerts'] = expiry_alerts
            return {"success": True, "user": driver, "new_user": False}
        return {"success": True, "new_user": True, "phone": request.phone}
    
    return {"success": False, "message": "Invalid role"}

# ==================== DRIVER STATUS BY PHONE ====================
@api_router.get("/driver/phone/{phone}/status")
async def get_driver_status_by_phone(phone: str):
    """
    Check driver status by phone number.
    Returns: NOT_FOUND, PENDING, APPROVED, or REJECTED
    """
    driver = await db.drivers.find_one({"phone": phone})
    if not driver:
        return {
            "success": True,
            "found": False,
            "status": "NOT_FOUND",
            "message": "Driver not registered"
        }
    
    return {
        "success": True,
        "found": True,
        "driver_id": driver.get("driver_id"),
        "status": driver.get("approval_status", "pending").upper(),
        "full_name": driver.get("full_name"),
        "phone": driver.get("phone"),
        "vehicle_number": driver.get("vehicle_number"),
        "rejection_reason": driver.get("rejection_reason")
    }

# ==================== CUSTOMER ENDPOINTS ====================
@api_router.post("/customer/register")
async def register_customer(customer: CustomerRegister):
    existing = await db.users.find_one({"phone": customer.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists")
    
    # Generate branded customer ID (VKCST1001, VKCST1002, etc.)
    customer_id = await generate_customer_id()
    
    user_data = {
        "user_id": customer_id,
        "phone": customer.phone,
        "name": customer.name,
        "location": customer.location.dict() if customer.location else None,
        "role": UserRole.CUSTOMER.value,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user_data)
    
    wallet_data = {
        "user_id": customer_id,
        "balance": 0.0,
        "transactions": []
    }
    await db.wallets.insert_one(wallet_data)
    
    user_data['_id'] = str(user_data.get('_id'))
    return {"success": True, "user": user_data}

@api_router.get("/customer/{customer_id}/profile")
async def get_customer_profile(customer_id: str):
    user = await db.users.find_one({"user_id": customer_id})
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    user['_id'] = str(user['_id'])
    return {"success": True, "user": user}

@api_router.get("/customer/{customer_id}/bookings")
async def get_customer_bookings(customer_id: str):
    bookings = await db.bookings.find({"customer_id": customer_id}).sort("created_at", -1).to_list(100)
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    return {"success": True, "bookings": bookings}

# ==================== PHASE 1: DRIVER KYC REGISTRATION ====================
@api_router.post("/driver/register-kyc")
async def register_driver_kyc(driver_data: ComprehensiveDriverRegister):
    """
    Essential Phase 1: Complete KYC registration with all required fields
    Single image upload per document
    """
    # Check existing
    existing = await db.drivers.find_one({"phone": driver_data.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Driver already registered with this phone")
    
    # Validation
    if len(driver_data.personal_details.aadhaar_number) != 12 or not driver_data.personal_details.aadhaar_number.isdigit():
        raise HTTPException(status_code=400, detail="Aadhaar must be 12 digits")
    
    if len(driver_data.personal_details.pan_number) != 10:
        raise HTTPException(status_code=400, detail="PAN must be 10 characters")
    
    # Check expiry dates
    try:
        insurance_exp = date.fromisoformat(driver_data.document_expiry.insurance_expiry)
        license_exp = date.fromisoformat(driver_data.document_expiry.license_expiry)
        
        if insurance_exp < date.today():
            raise HTTPException(status_code=400, detail="Insurance has expired")
        if license_exp < date.today():
            raise HTTPException(status_code=400, detail="Driving license has expired")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    driver_id = str(uuid.uuid4())
    
    driver_document = {
        "driver_id": driver_id,
        "phone": driver_data.phone,
        "role": UserRole.DRIVER.value,
        
        "personal_details": {
            "full_name": driver_data.personal_details.full_name,
            "mobile_number": driver_data.personal_details.mobile_number,
            "full_address": driver_data.personal_details.full_address,
            "aadhaar_number": driver_data.personal_details.aadhaar_number,
            "pan_number": driver_data.personal_details.pan_number.upper(),
            "driving_license_number": driver_data.personal_details.driving_license_number,
            "driving_experience_years": driver_data.personal_details.driving_experience_years,
            "driver_photo": driver_data.personal_details.driver_photo
        },
        
        "vehicle_details": {
            "vehicle_type": driver_data.vehicle_details.vehicle_type.value,
            "vehicle_number": driver_data.vehicle_details.vehicle_number.upper(),
            "vehicle_model": driver_data.vehicle_details.vehicle_model,
            "vehicle_year": driver_data.vehicle_details.vehicle_year
        },
        
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
        
        "document_expiry": {
            "insurance_expiry": driver_data.document_expiry.insurance_expiry,
            "fc_expiry": driver_data.document_expiry.fc_expiry,
            "permit_expiry": driver_data.document_expiry.permit_expiry,
            "pollution_expiry": driver_data.document_expiry.pollution_expiry,
            "license_expiry": driver_data.document_expiry.license_expiry
        },
        
        "driver_vehicle_photo": driver_data.driver_vehicle_photo.photo,
        
        "agreement": {
            "accepted": driver_data.agreement.accepted if driver_data.agreement else False,
            "agreement_file": driver_data.agreement.agreement_file if driver_data.agreement else None,
            "accepted_at": driver_data.agreement.accepted_at if driver_data.agreement else None
        },
        
        "approval_status": DriverApprovalStatus.PENDING.value,
        "approval_remarks": None,
        
        "driver_status": DriverStatus.OFFLINE.value,
        "is_online": False,
        "duty_on": False,
        
        "earnings": 0.0,
        "total_trips": 0,
        "completed_trips": 0,
        
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.drivers.insert_one(driver_document)
    
    wallet_data = {
        "user_id": driver_id,
        "balance": 0.0,
        "transactions": [],
        "minimum_balance_required": 1000.0
    }
    await db.wallets.insert_one(wallet_data)
    
    return {
        "success": True,
        "driver_id": driver_id,
        "message": "Registration submitted successfully. Awaiting admin approval.",
        "approval_status": DriverApprovalStatus.PENDING.value
    }

@api_router.post("/driver/register-simple")
async def register_driver_simple(driver_data: SimpleDriverRegister):
    """
    Simplified driver registration - 3 steps only
    No bank details, no PAN/Aadhaar, minimal fields
    """
    # Check existing
    existing = await db.drivers.find_one({"phone": driver_data.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Driver already registered with this phone")
    
    # Basic validation
    if len(driver_data.full_name.strip()) < 3:
        raise HTTPException(status_code=400, detail="Full name must be at least 3 characters")
    
    if driver_data.driving_experience < 1:
        raise HTTPException(status_code=400, detail="Minimum 1 year driving experience required")
    
    if len(driver_data.vehicle_number) < 6:
        raise HTTPException(status_code=400, detail="Invalid vehicle number")
    
    if not driver_data.agreement.accepted:
        raise HTTPException(status_code=400, detail="Agreement must be accepted")
    
    driver_id = str(uuid.uuid4())
    
    driver_document = {
        "driver_id": driver_id,
        "phone": driver_data.phone,
        "role": UserRole.DRIVER.value,
        "name": driver_data.full_name,
        
        "personal_details": {
            "full_name": driver_data.full_name,
            "mobile_number": driver_data.phone,
            "driving_experience_years": driver_data.driving_experience,
        },
        
        "vehicle_details": {
            "vehicle_type": driver_data.vehicle_type.value,
            "vehicle_number": driver_data.vehicle_number.upper(),
            "vehicle_model": driver_data.vehicle_model,
        },
        
        "documents": {
            "license_front": driver_data.documents.license_front,
            "license_back": driver_data.documents.license_back,
            "rc_front": driver_data.documents.rc_front,
            "rc_back": driver_data.documents.rc_back,
            "insurance": driver_data.documents.insurance,
            "driver_photo": driver_data.documents.driver_photo,
        },
        
        "payment": {
            "registration_fee": driver_data.payment.amount,
            "payment_screenshot": driver_data.payment.screenshot,
            "paid_at": datetime.utcnow().isoformat(),
        },
        
        "agreement": {
            "accepted": driver_data.agreement.accepted,
            "signed_document": driver_data.agreement.signed_document,
            "accepted_at": driver_data.agreement.accepted_at,
        },
        
        "approval_status": DriverApprovalStatus.PENDING.value,
        "approval_remarks": None,
        
        "driver_status": DriverStatus.OFFLINE.value,
        "is_online": False,
        "duty_on": False,
        
        "earnings": 0.0,
        "total_trips": 0,
        "completed_trips": 0,
        "continuous_trips_count": 0,
        
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.drivers.insert_one(driver_document)
    
    # Create wallet
    wallet_data = {
        "user_id": driver_id,
        "balance": 0.0,
        "transactions": [],
        "minimum_balance_required": 1000.0
    }
    await db.wallets.insert_one(wallet_data)
    
    return {
        "success": True,
        "driver_id": driver_id,
        "message": "Registration submitted. Awaiting admin approval.",
        "approval_status": DriverApprovalStatus.PENDING.value
    }

@api_router.get("/driver/{driver_id}/profile-complete")
async def get_driver_profile_complete(driver_id: str):
    """Get complete driver profile with all KYC details"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver['_id'] = str(driver['_id'])
    
    # Check expiries
    expiry_alerts = await check_all_driver_expiries(driver_id)
    driver['expiry_alerts'] = expiry_alerts
    
    return {"success": True, "driver": driver}

@api_router.get("/driver/{driver_id}/expiry-alerts")
async def get_driver_expiry_alerts(driver_id: str):
    """Get document expiry alerts for driver"""
    alerts = await check_all_driver_expiries(driver_id)
    if not alerts:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {"success": True, "expiry_alerts": alerts}

# ==================== COMPREHENSIVE DRIVER ONBOARDING ====================
@api_router.post("/driver/onboard")
async def onboard_driver_comprehensive(data: ComprehensiveDriverOnboarding):
    """
    Complete driver onboarding with all details and documents.
    Creates a new driver with PENDING status and branded ID (VKDRV1001, etc.)
    """
    print(f"[Onboard] Starting driver registration for phone: {data.basic_details.phone}")
    
    # Check if driver already exists
    existing = await db.drivers.find_one({"phone": data.basic_details.phone})
    if existing:
        print(f"[Onboard] Driver already exists with ID: {existing.get('driver_id')}")
        # Return existing driver info instead of error
        return {
            "success": True,
            "driver_id": existing.get('driver_id'),
            "message": "Driver already registered. Redirecting to status page.",
            "approval_status": existing.get('approval_status', 'pending'),
            "existing": True
        }
    
    print(f"[Onboard] Generating new driver ID...")
    # Generate branded driver ID (VKDRV1001, VKDRV1002, etc.)
    driver_id = await generate_driver_id()
    print(f"[Onboard] Generated driver ID: {driver_id}")
    
    # Normalize vehicle type
    vehicle_type = data.vehicle_details.vehicle_type.lower()
    if vehicle_type not in ['sedan', 'suv', 'crysta']:
        vehicle_type = 'sedan'
    
    driver_document = {
        "driver_id": driver_id,
        
        # Basic Details
        "phone": data.basic_details.phone,
        "full_name": data.basic_details.full_name,
        "address": data.basic_details.address,
        "aadhaar_number": data.basic_details.aadhaar_number,
        "pan_number": data.basic_details.pan_number,
        "driving_license_number": data.basic_details.driving_license_number,
        "driving_experience_years": data.basic_details.driving_experience_years,
        
        # Driver Photos
        "driver_photo": data.driver_photos.driver_photo,
        "driver_with_vehicle_photo": data.driver_photos.driver_with_vehicle_photo,
        
        # Driver Documents
        "aadhaar_front": data.driver_documents.aadhaar_front,
        "aadhaar_back": data.driver_documents.aadhaar_back,
        "license_front": data.driver_documents.license_front,
        "license_back": data.driver_documents.license_back,
        
        # Vehicle Details
        "vehicle_type": vehicle_type,
        "vehicle_number": data.vehicle_details.vehicle_number.upper(),
        "vehicle_model": data.vehicle_details.vehicle_model,
        "vehicle_year": data.vehicle_details.vehicle_year,
        
        # Vehicle Documents
        "rc_front": data.vehicle_documents.rc_front,
        "rc_back": data.vehicle_documents.rc_back,
        "insurance": data.vehicle_documents.insurance,
        "permit": data.vehicle_documents.permit,
        "pollution_certificate": data.vehicle_documents.pollution_certificate,
        
        # Vehicle Photos
        "vehicle_front_photo": data.vehicle_photos.front_photo,
        "vehicle_back_photo": data.vehicle_photos.back_photo,
        "vehicle_left_photo": data.vehicle_photos.left_photo,
        "vehicle_right_photo": data.vehicle_photos.right_photo,
        
        # Payment (optional)
        "payment_amount": data.payment.amount if data.payment else 0,
        "payment_screenshot": data.payment.screenshot if data.payment else None,
        
        # Status fields
        "approval_status": "pending",
        "rejection_reason": None,
        "driver_status": "offline",
        "is_online": False,
        "duty_on": False,
        
        # Stats
        "earnings": 0.0,
        "total_trips": 0,
        "completed_trips": 0,
        "rating": 5.0,
        
        # Location
        "current_location": None,
        
        # Timestamps
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    print(f"[Onboard] Inserting driver document into database...")
    await db.drivers.insert_one(driver_document)
    print(f"[Onboard] Driver inserted successfully")
    
    # Create wallet for driver
    print(f"[Onboard] Creating wallet for driver...")
    wallet_data = {
        "user_id": driver_id,
        "balance": 0.0,
        "transactions": [],
        "minimum_balance_required": 1000.0
    }
    await db.wallets.insert_one(wallet_data)
    print(f"[Onboard] Wallet created successfully")
    
    print(f"[Onboard] SUCCESS - Driver {driver_id} registered with phone {data.basic_details.phone}")
    return {
        "success": True,
        "driver_id": driver_id,
        "message": "Driver onboarding completed. Awaiting admin approval.",
        "approval_status": "pending"
    }

# Keep the simple registration for backward compatibility
@api_router.post("/driver/register")
async def register_driver_clean(driver_data: CleanDriverRegister):
    """
    Clean driver registration endpoint.
    Creates a new driver with PENDING status.
    """
    # Check if driver already exists
    existing = await db.drivers.find_one({"phone": driver_data.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Driver with this phone already exists")
    
    driver_id = str(uuid.uuid4())
    
    # Normalize vehicle type
    vehicle_type = driver_data.vehicle_type.lower()
    if vehicle_type not in ['sedan', 'suv', 'crysta']:
        vehicle_type = 'sedan'
    
    driver_document = {
        "driver_id": driver_id,
        "phone": driver_data.phone,
        "full_name": driver_data.full_name,
        "address": driver_data.address,
        "driving_license_number": driver_data.driving_license_number,
        "driving_license_image": driver_data.driving_license_image,
        "vehicle_type": vehicle_type,
        "vehicle_number": driver_data.vehicle_number.upper(),
        "rc_book_image": driver_data.rc_book_image,
        "insurance_details": driver_data.insurance_details,
        "insurance_image": driver_data.insurance_image,
        
        # Status fields
        "approval_status": "pending",
        "rejection_reason": None,
        "driver_status": "offline",
        "is_online": False,
        "duty_on": False,
        
        # Stats
        "earnings": 0.0,
        "total_trips": 0,
        "completed_trips": 0,
        "rating": 5.0,
        
        # Location
        "current_location": None,
        
        # Timestamps
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.drivers.insert_one(driver_document)
    
    # Create wallet for driver
    wallet_data = {
        "user_id": driver_id,
        "balance": 0.0,
        "transactions": [],
        "minimum_balance_required": 1000.0
    }
    await db.wallets.insert_one(wallet_data)
    
    return {
        "success": True,
        "driver_id": driver_id,
        "message": "Registration submitted successfully. Awaiting admin approval.",
        "approval_status": "pending"
    }

@api_router.get("/driver/{driver_id}/status")
async def get_driver_status(driver_id: str):
    """Get driver approval and online status"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {
        "success": True,
        "driver_id": driver_id,
        "approval_status": driver.get("approval_status", "pending"),
        "rejection_reason": driver.get("rejection_reason"),
        "is_online": driver.get("is_online", False),
        "duty_on": driver.get("duty_on", False)
    }

# ==================== ADMIN KYC VERIFICATION ENDPOINTS ====================
@api_router.get("/admin/drivers/pending-verification")
async def get_pending_drivers():
    """Get all drivers awaiting verification"""
    drivers = await db.drivers.find({
        "approval_status": DriverApprovalStatus.PENDING.value
    }).sort("created_at", -1).to_list(100)
    
    for driver in drivers:
        driver['_id'] = str(driver['_id'])
        # Add expiry alerts
        alerts = await check_all_driver_expiries(driver['driver_id'])
        driver['expiry_alerts'] = alerts
    
    return {"success": True, "pending_drivers": drivers}

@api_router.get("/admin/driver/{driver_id}/verification-view")
async def get_driver_for_verification(driver_id: str):
    """Get complete driver details for admin verification"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver['_id'] = str(driver['_id'])
    
    # Add expiry alerts
    alerts = await check_all_driver_expiries(driver_id)
    driver['expiry_alerts'] = alerts
    
    return {"success": True, "driver": driver}

@api_router.put("/admin/driver/approve")
async def approve_driver(approval: DriverApproval):
    """Approve or reject driver application"""
    driver = await db.drivers.find_one({"driver_id": approval.driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    await db.drivers.update_one(
        {"driver_id": approval.driver_id},
        {
            "$set": {
                "approval_status": approval.approval_status.value,
                "approval_remarks": approval.rejection_reason,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Driver {approval.approval_status.value}",
        "driver_id": approval.driver_id
    }

# Alias endpoint for backward compatibility (old path used by production)
@api_router.put("/admin/approve-driver")
async def approve_driver_alias(approval: DriverApproval):
    """Alias for approve_driver - backward compatibility"""
    return await approve_driver(approval)

@api_router.put("/admin/driver/reset/{driver_id}")
async def reset_driver_status(driver_id: str):
    """Reset driver status from APPROVED back to PENDING"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    await db.drivers.update_one(
        {"driver_id": driver_id},
        {
            "$set": {
                "approval_status": "pending",
                "rejection_reason": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "success": True,
        "message": "Driver status reset to PENDING",
        "driver_id": driver_id
    }

@api_router.delete("/admin/driver/{driver_id}")
async def delete_driver(driver_id: str):
    """Delete driver completely from the system"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Delete driver
    await db.drivers.delete_one({"driver_id": driver_id})
    
    # Delete driver's wallet
    await db.wallets.delete_one({"user_id": driver_id})
    
    # Delete driver's bookings (optional - keep for records)
    # await db.bookings.delete_many({"driver_id": driver_id})
    
    return {
        "success": True,
        "message": "Driver deleted successfully",
        "driver_id": driver_id
    }

# ==================== LEGACY DRIVER ENDPOINTS (keeping for compatibility) ====================
@api_router.post("/driver/register")
async def register_driver_legacy(driver: DriverRegister):
    """Legacy driver registration - kept for backward compatibility"""
    existing = await db.drivers.find_one({"phone": driver.phone})
    if existing:
        raise HTTPException(status_code=400, detail="Driver already exists")
    
    driver_data = {
        "driver_id": str(uuid.uuid4()),
        "phone": driver.phone,
        "name": driver.name,
        "vehicle_type": driver.vehicle_type.value,
        "vehicle_number": driver.vehicle_number,
        "license_image": driver.license_image,
        "rc_image": driver.rc_image,
        "approval_status": DriverApprovalStatus.PENDING.value,
        "is_online": False,
        "earnings": 0.0,
        "current_location": None,
        "role": UserRole.DRIVER.value,
        "created_at": datetime.utcnow()
    }
    
    await db.drivers.insert_one(driver_data)
    
    wallet_data = {
        "user_id": driver_data['driver_id'],
        "balance": 0.0,
        "transactions": []
    }
    await db.wallets.insert_one(wallet_data)
    
    driver_data['_id'] = str(driver_data.get('_id'))
    return {"success": True, "driver": driver_data, "message": "Driver registered. Waiting for admin approval."}

@api_router.get("/driver/{driver_id}/profile")
async def get_driver_profile(driver_id: str):
    """Get driver profile"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver['_id'] = str(driver['_id'])
    return {"success": True, "driver": driver}

@api_router.put("/driver/{driver_id}/status")
async def update_driver_status(driver_id: str, status_update: DriverStatusUpdate):
    """Update driver online/offline status"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if driver['approval_status'] != DriverApprovalStatus.APPROVED.value:
        raise HTTPException(status_code=403, detail="Driver not approved yet")
    
    await db.drivers.update_one(
        {"driver_id": driver_id},
        {"$set": {"is_online": status_update.is_online}}
    )
    
    return {"success": True, "is_online": status_update.is_online}

@api_router.get("/driver/{driver_id}/rides")
async def get_driver_rides(driver_id: str):
    """Get driver ride history"""
    bookings = await db.bookings.find({"driver_id": driver_id}).sort("created_at", -1).to_list(100)
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    return {"success": True, "rides": bookings}

@api_router.get("/driver/{driver_id}/pending-rides")
async def get_pending_rides(driver_id: str):
    """Get pending ride requests for driver"""
    bookings = await db.bookings.find({
        "driver_id": driver_id,
        "status": BookingStatus.REQUESTED.value
    }).to_list(100)
    
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    
    return {"success": True, "pending_rides": bookings}

@api_router.get("/driver/{driver_id}/earnings")
async def get_driver_earnings(driver_id: str):
    """Get driver earnings summary"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Use MongoDB aggregation for efficient earnings calculation
    earnings_pipeline = [
        {"$match": {"driver_id": driver_id, "status": BookingStatus.COMPLETED.value}},
        {"$group": {
            "_id": None,
            "total_rides": {"$sum": 1},
            "total_earnings": {"$sum": "$driver_earning"}
        }}
    ]
    earnings_result = await db.bookings.aggregate(earnings_pipeline).to_list(1)
    total_rides = earnings_result[0]['total_rides'] if earnings_result else 0
    total_earnings = earnings_result[0]['total_earnings'] if earnings_result else 0
    
    return {
        "success": True,
        "total_rides": total_rides,
        "total_earnings": total_earnings,
        "wallet_balance": driver.get('earnings', 0)
    }

# ==================== BOOKING ENDPOINTS ====================
@api_router.post("/booking/create")
async def create_booking(booking: BookingCreate):
    """Create new booking and auto-assign driver"""
    distance = calculate_mock_distance(booking.pickup, booking.drop)
    fare = await calculate_fare(distance, booking.vehicle_type)
    
    # Find available driver
    driver = await db.drivers.find_one({
        "vehicle_details.vehicle_type": booking.vehicle_type.value,
        "is_online": True,
        "approval_status": DriverApprovalStatus.APPROVED.value
    })
    
    if not driver:
        raise HTTPException(status_code=404, detail="No drivers available")
    
    commission = fare * 0.10
    driver_earning = fare - commission
    
    # Generate branded booking ID (VKBK1001, VKBK1002, etc.)
    booking_id = await generate_booking_id()
    
    booking_data = {
        "booking_id": booking_id,
        "customer_id": booking.customer_id,
        "driver_id": driver['driver_id'],
        "pickup": booking.pickup.dict(),
        "drop": booking.drop.dict(),
        "vehicle_type": booking.vehicle_type.value,
        "distance": distance,
        "fare": round(fare, 2),
        "commission": round(commission, 2),
        "driver_earning": round(driver_earning, 2),
        "status": BookingStatus.REQUESTED.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.bookings.insert_one(booking_data)
    
    booking_data['_id'] = str(booking_data.get('_id'))
    booking_data['driver_name'] = driver.get('personal_details', {}).get('full_name', driver.get('name', 'Driver'))
    booking_data['driver_phone'] = driver.get('phone', '')
    booking_data['vehicle_number'] = driver.get('vehicle_details', {}).get('vehicle_number', driver.get('vehicle_number', ''))
    
    return {"success": True, "booking": booking_data}

@api_router.put("/booking/update")
async def update_booking(update: BookingUpdate):
    """Update booking status"""
    booking = await db.bookings.find_one({"booking_id": update.booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    update_data = {
        "status": update.status.value,
        "updated_at": datetime.utcnow()
    }
    
    if update.status == BookingStatus.COMPLETED:
        driver_earning = booking.get('driver_earning', 0)
        await db.drivers.update_one(
            {"driver_id": booking['driver_id']},
            {"$inc": {"earnings": driver_earning, "completed_trips": 1}}
        )
    
    await db.bookings.update_one(
        {"booking_id": update.booking_id},
        {"$set": update_data}
    )
    
    return {"success": True, "message": "Booking updated"}

@api_router.get("/booking/{booking_id}")
async def get_booking(booking_id: str):
    """Get booking details"""
    booking = await db.bookings.find_one({"booking_id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking['_id'] = str(booking['_id'])
    
    customer = await db.users.find_one({"user_id": booking['customer_id']})
    driver = await db.drivers.find_one({"driver_id": booking['driver_id']})
    
    if customer:
        booking['customer_name'] = customer['name']
        booking['customer_phone'] = customer['phone']
    
    if driver:
        booking['driver_name'] = driver.get('personal_details', {}).get('full_name', driver.get('name', 'Driver'))
        booking['driver_phone'] = driver.get('phone', '')
        booking['vehicle_number'] = driver.get('vehicle_details', {}).get('vehicle_number', driver.get('vehicle_number', ''))
    
    return {"success": True, "booking": booking}

# ==================== WALLET ENDPOINTS ====================
@api_router.get("/wallet/{user_id}")
async def get_wallet(user_id: str):
    """Get wallet details"""
    wallet = await db.wallets.find_one({"user_id": user_id})
    if not wallet:
        wallet = {
            "user_id": user_id,
            "balance": 0.0,
            "transactions": []
        }
        await db.wallets.insert_one(wallet)
    
    wallet['_id'] = str(wallet.get('_id'))
    return {"success": True, "wallet": wallet}

@api_router.post("/wallet/add-money")
async def add_money(request: WalletAddMoney):
    """Add money to wallet (Mock payment)"""
    wallet = await db.wallets.find_one({"user_id": request.user_id})
    
    if not wallet:
        wallet = {
            "user_id": request.user_id,
            "balance": 0.0,
            "transactions": []
        }
        await db.wallets.insert_one(wallet)
    
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "amount": request.amount,
        "type": "credit",
        "description": "Money added to wallet",
        "timestamp": datetime.utcnow()
    }
    
    await db.wallets.update_one(
        {"user_id": request.user_id},
        {
            "$inc": {"balance": request.amount},
            "$push": {"transactions": transaction}
        }
    )
    
    return {"success": True, "message": "Money added successfully", "new_balance": wallet['balance'] + request.amount}

@api_router.post("/wallet/withdraw")
async def withdraw_money(request: WithdrawRequest):
    """Driver withdraw request"""
    driver = await db.drivers.find_one({"driver_id": request.driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if driver['earnings'] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    await db.drivers.update_one(
        {"driver_id": request.driver_id},
        {"$inc": {"earnings": -request.amount}}
    )
    
    withdrawal = {
        "withdrawal_id": str(uuid.uuid4()),
        "driver_id": request.driver_id,
        "amount": request.amount,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    await db.withdrawals.insert_one(withdrawal)
    
    return {"success": True, "message": "Withdrawal request submitted"}

# ==================== ADMIN ENDPOINTS ====================
@api_router.get("/admin/drivers")
async def get_all_drivers():
    """Get all drivers"""
    drivers = await db.drivers.find().sort("created_at", -1).to_list(1000)
    for driver in drivers:
        driver['_id'] = str(driver['_id'])
    return {"success": True, "drivers": drivers}

@api_router.get("/admin/customers")
async def get_all_customers():
    """Get all customers"""
    customers = await db.users.find({"role": UserRole.CUSTOMER.value}).to_list(1000)
    for customer in customers:
        customer['_id'] = str(customer['_id'])
    return {"success": True, "customers": customers}

@api_router.get("/admin/bookings")
async def get_all_bookings():
    """Get all bookings"""
    bookings = await db.bookings.find().sort("created_at", -1).to_list(1000)
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    return {"success": True, "bookings": bookings}

@api_router.get("/admin/tariffs")
async def get_tariffs():
    """Get tariff settings"""
    tariffs = await db.tariffs.find().to_list(100)
    
    if not tariffs:
        default_tariffs = [
            {
                "vehicle_type": VehicleType.SEDAN.value,
                "rate_per_km": 14.0,
                "minimum_fare": 300.0
            },
            {
                "vehicle_type": VehicleType.SUV.value,
                "rate_per_km": 18.0,
                "minimum_fare": 300.0
            }
        ]
        await db.tariffs.insert_many(default_tariffs)
        tariffs = default_tariffs
    
    for tariff in tariffs:
        if '_id' in tariff:
            tariff['_id'] = str(tariff['_id'])
    
    return {"success": True, "tariffs": tariffs}

@api_router.put("/admin/update-tariff")
async def update_tariff(tariff_update: TariffUpdate):
    """Update tariff"""
    await db.tariffs.update_one(
        {"vehicle_type": tariff_update.vehicle_type.value},
        {"$set": {
            "rate_per_km": tariff_update.rate_per_km,
            "minimum_fare": tariff_update.minimum_fare
        }},
        upsert=True
    )
    
    return {"success": True, "message": "Tariff updated"}

@api_router.get("/admin/stats")
async def get_admin_stats():
    """Get admin dashboard stats"""
    total_customers = await db.users.count_documents({"role": UserRole.CUSTOMER.value})
    total_drivers = await db.drivers.count_documents({})
    pending_drivers = await db.drivers.count_documents({"approval_status": DriverApprovalStatus.PENDING.value})
    approved_drivers = await db.drivers.count_documents({"approval_status": DriverApprovalStatus.APPROVED.value})
    total_bookings = await db.bookings.count_documents({})
    completed_bookings = await db.bookings.count_documents({"status": BookingStatus.COMPLETED.value})
    
    # Use MongoDB aggregation for efficient revenue calculation
    revenue_pipeline = [
        {"$match": {"status": BookingStatus.COMPLETED.value}},
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$fare"},
            "total_commission": {"$sum": "$commission"}
        }}
    ]
    revenue_result = await db.bookings.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
    total_commission = revenue_result[0]['total_commission'] if revenue_result else 0
    
    return {
        "success": True,
        "stats": {
            "total_customers": total_customers,
            "total_drivers": total_drivers,
            "pending_drivers": pending_drivers,
            "approved_drivers": approved_drivers,
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "total_revenue": round(total_revenue, 2),
            "total_commission": round(total_commission, 2)
        }
    }

# ==================== PHASE 2 & 3: DISPATCH SYSTEM ====================
# Import dispatch logic
from dispatch_logic import (
    calculate_distance,
    calculate_matching_score,
    check_driver_eligibility,
    is_trip_towards_home,
    calculate_queue_priority,
    check_and_update_trip_continuity,
    can_driver_reach_in_time,
)

# Phase 2 & 3 Models
class DutyStatusUpdate(BaseModel):
    duty_on: bool
    go_home_mode: bool = False
    home_latitude: Optional[float] = None
    home_longitude: Optional[float] = None
    home_address: Optional[str] = None

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    address: str

class SmartBookingCreate(BaseModel):
    customer_id: str
    pickup: Location
    drop: Location
    vehicle_type: VehicleType
    assignment_mode: str = "auto"  # auto or manual
    manual_driver_id: Optional[str] = None

class BookingAcceptReject(BaseModel):
    booking_id: str
    driver_id: str
    action: str  # "accept" or "reject"

# ==================== DRIVER DUTY & STATUS ====================
@api_router.put("/driver/{driver_id}/duty-status")
async def update_duty_status(driver_id: str, duty_update: DutyStatusUpdate):
    """
    Update driver duty status
    - Duty ON/OFF
    - Go Home mode with home location
    """
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if driver['approval_status'] != DriverApprovalStatus.APPROVED.value:
        raise HTTPException(status_code=403, detail="Driver not approved yet")
    
    update_data = {
        "duty_on": duty_update.duty_on,
        "go_home_mode": duty_update.go_home_mode,
        "updated_at": datetime.utcnow()
    }
    
    # Update home location if go home mode is enabled
    if duty_update.go_home_mode and duty_update.home_latitude and duty_update.home_longitude:
        update_data["home_location"] = {
            "latitude": duty_update.home_latitude,
            "longitude": duty_update.home_longitude,
            "address": duty_update.home_address or "Home"
        }
    
    # Set driver status
    if duty_update.duty_on:
        if duty_update.go_home_mode:
            update_data["driver_status"] = DriverStatus.GOING_HOME.value
        else:
            update_data["driver_status"] = DriverStatus.AVAILABLE.value
        update_data["is_online"] = True
    else:
        update_data["driver_status"] = DriverStatus.OFFLINE.value
        update_data["is_online"] = False
        update_data["go_home_mode"] = False
    
    await db.drivers.update_one(
        {"driver_id": driver_id},
        {"$set": update_data}
    )
    
    return {"success": True, "message": "Duty status updated", "duty_on": duty_update.duty_on}

@api_router.put("/driver/{driver_id}/location")
async def update_driver_location(driver_id: str, location: LocationUpdate):
    """Update driver's current location"""
    await db.drivers.update_one(
        {"driver_id": driver_id},
        {"$set": {
            "current_location": {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            },
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"success": True, "message": "Location updated"}

# ==================== SMART DISPATCH BOOKING ====================
@api_router.post("/booking/create-smart")
async def create_smart_booking(booking: SmartBookingCreate):
    """
    Create booking with smart dispatch algorithm
    - Auto mode: Find best matching driver
    - Manual mode: Assign specific driver
    - Implements 2-trip continuity and queue system
    """
    # Calculate distance and fare
    distance = calculate_distance(
        booking.pickup.latitude, booking.pickup.longitude,
        booking.drop.latitude, booking.drop.longitude
    )
    fare = await calculate_fare(distance, booking.vehicle_type)
    commission = fare * 0.10
    driver_earning = fare - commission
    
    selected_driver = None
    
    if booking.assignment_mode == "manual" and booking.manual_driver_id:
        # Manual assignment
        selected_driver = await db.drivers.find_one({"driver_id": booking.manual_driver_id})
        if not selected_driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Check wallet balance for manual assignment too
        wallet = await db.wallets.find_one({"user_id": booking.manual_driver_id})
        wallet_balance = wallet.get('balance', 0) if wallet else 0
        if wallet_balance < 1000:
            raise HTTPException(status_code=400, detail=f"Driver wallet balance ({wallet_balance}) is below minimum ₹1000")
    else:
        # Auto assignment with smart matching
        # Get all approved, online, duty-on drivers
        all_drivers = await db.drivers.find({
            "approval_status": DriverApprovalStatus.APPROVED.value,
            "duty_on": True,
            "is_online": True,
            "driver_status": {"$in": [DriverStatus.AVAILABLE.value, DriverStatus.WAITING.value, DriverStatus.GOING_HOME.value]}
        }).to_list(1000)
        
        eligible_drivers = []
        
        for driver in all_drivers:
            # Check wallet balance
            wallet = await db.wallets.find_one({"user_id": driver['driver_id']})
            wallet_balance = wallet.get('balance', 0) if wallet else 0
            
            # Check eligibility
            eligibility = await check_driver_eligibility(driver, wallet_balance)
            
            if not eligibility['eligible']:
                continue
            
            # Check distance (30-40 KM radius)
            driver_loc = driver.get('current_location') or driver.get('last_trip_end_location')
            if not driver_loc:
                continue
            
            dist_to_pickup = calculate_distance(
                driver_loc['latitude'], driver_loc['longitude'],
                booking.pickup.latitude, booking.pickup.longitude
            )
            
            if dist_to_pickup > 40:  # Beyond 40 KM radius
                continue
            
            # Check time availability (1-hour buffer)
            if not can_driver_reach_in_time(driver, booking.pickup.dict(), buffer_hours=1.0):
                continue
            
            # If driver is in go-home mode, check if trip is towards home
            if driver.get('go_home_mode'):
                home_loc = driver.get('home_location')
                if home_loc:
                    if not is_trip_towards_home(booking.pickup.dict(), booking.drop.dict(), home_loc, threshold_km=10):
                        continue  # Skip this driver if trip not towards home
            
            # Calculate matching score
            booking_dict = {
                "pickup": booking.pickup.dict(),
                "drop": booking.drop.dict()
            }
            score = calculate_matching_score(driver, booking_dict)
            
            eligible_drivers.append({
                "driver": driver,
                "score": score,
                "distance": dist_to_pickup
            })
        
        if not eligible_drivers:
            raise HTTPException(status_code=404, detail="No eligible drivers available")
        
        # Sort by matching score (highest first)
        eligible_drivers.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top driver
        selected_driver = eligible_drivers[0]['driver']
    
    # Generate branded booking ID (VKBK1001, VKBK1002, etc.)
    booking_id = await generate_booking_id()
    
    # Create booking
    booking_data = {
        "booking_id": booking_id,
        "customer_id": booking.customer_id,
        "driver_id": selected_driver['driver_id'],
        "pickup": booking.pickup.dict(),
        "drop": booking.drop.dict(),
        "vehicle_type": booking.vehicle_type.value,
        "distance": round(distance, 2),
        "fare": round(fare, 2),
        "commission": round(commission, 2),
        "driver_earning": round(driver_earning, 2),
        "status": BookingStatus.REQUESTED.value,
        "assignment_mode": booking.assignment_mode,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "assigned_at": datetime.utcnow()
    }
    
    await db.bookings.insert_one(booking_data)
    
    # Update driver status
    await db.drivers.update_one(
        {"driver_id": selected_driver['driver_id']},
        {"$set": {"driver_status": DriverStatus.WAITING.value}}
    )
    
    booking_data['_id'] = str(booking_data.get('_id'))
    booking_data['driver_name'] = selected_driver.get('personal_details', {}).get('full_name', selected_driver.get('name', 'Driver'))
    booking_data['driver_phone'] = selected_driver.get('phone', '')
    booking_data['vehicle_number'] = selected_driver.get('vehicle_details', {}).get('vehicle_number', '')
    
    return {"success": True, "booking": booking_data}

# ==================== BOOKING ACCEPT/REJECT ====================
@api_router.post("/booking/accept-reject")
async def accept_reject_booking(action: BookingAcceptReject):
    """
    Driver accepts or rejects booking
    - Accept: Move to accepted status, update 2-trip count
    - Reject: Reassign to next driver
    """
    booking = await db.bookings.find_one({"booking_id": action.booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking['driver_id'] != action.driver_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if action.action == "accept":
        # Accept booking
        await db.bookings.update_one(
            {"booking_id": action.booking_id},
            {"$set": {
                "status": BookingStatus.ACCEPTED.value,
                "accepted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Update driver status
        await db.drivers.update_one(
            {"driver_id": action.driver_id},
            {"$set": {"driver_status": DriverStatus.ON_TRIP.value}}
        )
        
        # Update 2-trip continuity
        await check_and_update_trip_continuity(db, action.driver_id, "accepted")
        
        return {"success": True, "message": "Booking accepted"}
    
    elif action.action == "reject":
        # Reject booking - reassign to next driver
        # Mark current booking as cancelled
        await db.bookings.update_one(
            {"booking_id": action.booking_id},
            {"$set": {
                "status": BookingStatus.CANCELLED.value,
                "rejection_reason": "Driver rejected",
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Reset driver status
        await db.drivers.update_one(
            {"driver_id": action.driver_id},
            {"$set": {"driver_status": DriverStatus.AVAILABLE.value}}
        )
        
        # TODO: Implement reassignment to next driver
        # For MVP, just mark as cancelled and require new booking
        
        return {"success": True, "message": "Booking rejected"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

# ==================== TRIP START/COMPLETE ====================
@api_router.put("/booking/{booking_id}/start-trip")
async def start_trip(booking_id: str):
    """Start trip - move to ongoing status"""
    booking = await db.bookings.find_one({"booking_id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking['status'] != BookingStatus.ACCEPTED.value:
        raise HTTPException(status_code=400, detail="Booking must be accepted first")
    
    await db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {
            "status": BookingStatus.ONGOING.value,
            "started_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Update driver status
    await db.drivers.update_one(
        {"driver_id": booking['driver_id']},
        {"$set": {"driver_status": DriverStatus.ON_TRIP.value}}
    )
    
    return {"success": True, "message": "Trip started"}

@api_router.put("/booking/{booking_id}/complete-trip")
async def complete_trip(booking_id: str):
    """
    Complete trip
    - Update driver earnings
    - Update trip end location and time
    - Check 2-trip continuity rule
    - Move driver to queue if needed
    """
    booking = await db.bookings.find_one({"booking_id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking['status'] != BookingStatus.ONGOING.value:
        raise HTTPException(status_code=400, detail="Trip must be ongoing")
    
    # Complete booking
    await db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {
            "status": BookingStatus.COMPLETED.value,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Update driver earnings and trip count
    driver_earning = booking.get('driver_earning', 0)
    await db.drivers.update_one(
        {"driver_id": booking['driver_id']},
        {
            "$inc": {
                "earnings": driver_earning,
                "completed_trips": 1,
                "total_trips": 1
            },
            "$set": {
                "last_trip_end_location": booking['drop'],
                "last_trip_end_time": datetime.utcnow().isoformat(),
                "driver_status": DriverStatus.AVAILABLE.value
            }
        }
    )
    
    # Check 2-trip continuity
    await check_and_update_trip_continuity(db, booking['driver_id'], "completed")
    
    return {"success": True, "message": "Trip completed", "earning": driver_earning}

# ==================== QUEUE STATUS ====================
@api_router.get("/driver/{driver_id}/queue-status")
async def get_queue_status(driver_id: str):
    """Get driver's queue status and position"""
    driver = await db.drivers.find_one({"driver_id": driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Get all drivers in queue
    queue_drivers = await db.drivers.find({
        "in_queue": True,
        "duty_on": True
    }).to_list(1000)
    
    # Calculate priorities
    driver_priorities = []
    for qd in queue_drivers:
        priority = calculate_queue_priority(qd)
        driver_priorities.append({
            "driver_id": qd['driver_id'],
            "priority": priority,
            "name": qd.get('personal_details', {}).get('full_name', qd.get('name', 'Driver'))
        })
    
    # Sort by priority (highest first)
    driver_priorities.sort(key=lambda x: x['priority'], reverse=True)
    
    # Find driver's position
    position = None
    for idx, dp in enumerate(driver_priorities):
        if dp['driver_id'] == driver_id:
            position = idx + 1
            break
    
    return {
        "success": True,
        "in_queue": driver.get('in_queue', False),
        "queue_position": position,
        "total_in_queue": len(driver_priorities),
        "continuous_trips_count": driver.get('continuous_trips_count', 0)
    }

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

