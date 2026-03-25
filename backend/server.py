from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
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

# ==================== MODELS ====================
class Location(BaseModel):
    latitude: float
    longitude: float
    address: str

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

class DriverRegister(BaseModel):
    phone: str
    name: str
    vehicle_type: VehicleType
    vehicle_number: str
    license_image: str  # base64
    rc_image: str  # base64

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

# ==================== MOCK SERVICES ====================
# Mock OTP - Always returns 123456
def send_mock_otp(phone: str):
    return {"otp": "123456", "message": "OTP sent successfully (Mock)"}

def verify_mock_otp(phone: str, otp: str):
    return otp == "123456"

# Mock Distance Calculation (in km)
def calculate_mock_distance(pickup: Location, drop: Location):
    # Simple mock distance based on coordinate difference
    lat_diff = abs(pickup.latitude - drop.latitude)
    lon_diff = abs(pickup.longitude - drop.longitude)
    distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough conversion to km
    return round(distance, 2)

# Calculate fare based on tariff
async def calculate_fare(distance: float, vehicle_type: VehicleType):
    tariff = await db.tariffs.find_one({"vehicle_type": vehicle_type.value})
    if not tariff:
        # Default tariffs
        if vehicle_type == VehicleType.SEDAN:
            rate = 14
            minimum = 300
        else:
            rate = 18
            minimum = 300
    else:
        rate = tariff['rate_per_km']
        minimum = tariff['minimum_fare']
    
    fare = distance * rate
    return max(fare, minimum)

# Auto-assign nearest available driver
async def find_nearest_driver(pickup: Location, vehicle_type: VehicleType):
    drivers = await db.drivers.find({
        "vehicle_type": vehicle_type.value,
        "is_online": True,
        "approval_status": DriverApprovalStatus.APPROVED.value
    }).to_list(100)
    
    if not drivers:
        return None
    
    # Mock: Return random driver from available ones
    return random.choice(drivers)

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
    
    # Check if user exists
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

# ==================== DRIVER ENDPOINTS ====================
@api_router.post("/driver/register")
async def register_driver(driver: DriverRegister):
    """Register new driver"""
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
    
    # Create wallet for driver
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
    # Get rides assigned to this driver with status 'requested'
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
    
    # Get completed rides
    completed_rides = await db.bookings.find({
        "driver_id": driver_id,
        "status": BookingStatus.COMPLETED.value
    }).to_list(1000)
    
    total_rides = len(completed_rides)
    total_earnings = sum(ride.get('driver_earning', 0) for ride in completed_rides)
    
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
    # Calculate distance
    distance = calculate_mock_distance(booking.pickup, booking.drop)
    
    # Calculate fare
    fare = await calculate_fare(distance, booking.vehicle_type)
    
    # Find nearest driver
    driver = await find_nearest_driver(booking.pickup, booking.vehicle_type)
    
    if not driver:
        raise HTTPException(status_code=404, detail="No drivers available")
    
    # Calculate commission (10%)
    commission = fare * 0.10
    driver_earning = fare - commission
    
    booking_data = {
        "booking_id": str(uuid.uuid4()),
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
    booking_data['driver_name'] = driver['name']
    booking_data['driver_phone'] = driver['phone']
    booking_data['vehicle_number'] = driver['vehicle_number']
    
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
    
    # If completed, update driver earnings
    if update.status == BookingStatus.COMPLETED:
        driver_earning = booking.get('driver_earning', 0)
        await db.drivers.update_one(
            {"driver_id": booking['driver_id']},
            {"$inc": {"earnings": driver_earning}}
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
    
    # Get customer and driver details
    customer = await db.users.find_one({"user_id": booking['customer_id']})
    driver = await db.drivers.find_one({"driver_id": booking['driver_id']})
    
    if customer:
        booking['customer_name'] = customer['name']
        booking['customer_phone'] = customer['phone']
    
    if driver:
        booking['driver_name'] = driver['name']
        booking['driver_phone'] = driver['phone']
        booking['vehicle_number'] = driver['vehicle_number']
    
    return {"success": True, "booking": booking}

# ==================== WALLET ENDPOINTS ====================
@api_router.get("/wallet/{user_id}")
async def get_wallet(user_id: str):
    """Get wallet details"""
    wallet = await db.wallets.find_one({"user_id": user_id})
    if not wallet:
        # Create wallet if not exists
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
    
    # Deduct from earnings
    await db.drivers.update_one(
        {"driver_id": request.driver_id},
        {"$inc": {"earnings": -request.amount}}
    )
    
    # Create withdrawal record
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

@api_router.put("/admin/approve-driver")
async def approve_driver(approval: DriverApproval):
    """Approve or reject driver"""
    driver = await db.drivers.find_one({"driver_id": approval.driver_id})
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    await db.drivers.update_one(
        {"driver_id": approval.driver_id},
        {"$set": {"approval_status": approval.approval_status.value}}
    )
    
    return {"success": True, "message": f"Driver {approval.approval_status.value}"}

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
    
    # Initialize default tariffs if not exists
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
    total_bookings = await db.bookings.count_documents({})
    completed_bookings = await db.bookings.count_documents({"status": BookingStatus.COMPLETED.value})
    
    # Calculate total revenue
    all_bookings = await db.bookings.find({"status": BookingStatus.COMPLETED.value}).to_list(10000)
    total_revenue = sum(booking.get('fare', 0) for booking in all_bookings)
    total_commission = sum(booking.get('commission', 0) for booking in all_bookings)
    
    return {
        "success": True,
        "stats": {
            "total_customers": total_customers,
            "total_drivers": total_drivers,
            "pending_drivers": pending_drivers,
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "total_revenue": round(total_revenue, 2),
            "total_commission": round(total_commission, 2)
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
