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
from typing import List

# Import models
from models import *

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="VK Drop Taxi - Phase 1 Complete KYC System")
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

def check_document_expiry(expiry_date_str: str, warning_days: int = 30) -> dict:
    """Check if document is expired or expiring soon"""
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

async def check_all_driver_expiries(driver_id: str) -> dict:
    """Check all document expiries for a driver"""
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
            
            # Check document expiries
            expiry_alerts = await check_all_driver_expiries(driver['driver_id'])
            driver['expiry_alerts'] = expiry_alerts
            
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

# Continue in next response due to length...
