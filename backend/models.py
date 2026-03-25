from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum

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
    front_image: str  # base64
    back_image: Optional[str] = None  # base64, optional for single-sided documents

# ==================== DRIVER KYC MODELS ====================
class PersonalDetails(BaseModel):
    full_name: str
    mobile_number: str
    full_address: str
    aadhaar_number: str
    pan_number: str
    driving_license_number: str
    driving_experience_years: int
    driver_photo: str  # base64

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
    insurance_expiry: date
    fc_expiry: date
    permit_expiry: date
    pollution_expiry: date
    license_expiry: date

class DriverVehiclePhoto(BaseModel):
    photo: str  # base64 - driver standing near vehicle with visible number plate

# ==================== COMPREHENSIVE DRIVER REGISTRATION ====================
class ComprehensiveDriverRegister(BaseModel):
    phone: str
    personal_details: PersonalDetails
    bank_details: BankDetails
    vehicle_details: VehicleDetails
    documents: Documents
    document_expiry: DocumentExpiry
    driver_vehicle_photo: DriverVehiclePhoto

# ==================== AUTH MODELS ====================
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

# Legacy driver register (keeping for backward compatibility)
class DriverRegister(BaseModel):
    phone: str
    name: str
    vehicle_type: VehicleType
    vehicle_number: str
    license_image: str  # base64
    rc_image: str  # base64

# ==================== STATUS UPDATE MODELS ====================
class DriverStatusUpdate(BaseModel):
    is_online: bool

class DriverDutyUpdate(BaseModel):
    duty_status: bool  # ON/OFF
    go_home_mode: bool = False
    home_location: Optional[Location] = None

# ==================== BOOKING MODELS ====================
class BookingCreate(BaseModel):
    customer_id: str
    pickup: Location
    drop: Location
    vehicle_type: VehicleType

class BookingUpdate(BaseModel):
    booking_id: str
    status: BookingStatus
    driver_id: Optional[str] = None

# ==================== WALLET MODELS ====================
class WalletAddMoney(BaseModel):
    user_id: str
    amount: float

class WithdrawRequest(BaseModel):
    driver_id: str
    amount: float

# ==================== ADMIN MODELS ====================
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
