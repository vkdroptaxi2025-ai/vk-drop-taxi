#!/usr/bin/env python3
"""
Debug wallet restriction issue
"""

import requests
import json
from datetime import datetime, date, timedelta

BACKEND_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
MOCK_OTP = "123456"

def make_request(method, endpoint, data=None):
    """Make HTTP request with error handling"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        return None

def debug_wallet_restriction():
    """Debug the wallet restriction issue"""
    print("🔍 DEBUGGING WALLET RESTRICTION ISSUE")
    print("=" * 50)
    
    # Create a new driver
    driver_phone = "8888899999"
    
    # Step 1: Send OTP
    otp_response = make_request("POST", "/auth/send-otp", {
        "phone": driver_phone,
        "role": "driver"
    })
    print(f"Send OTP: {otp_response.status_code}")
    
    # Step 2: Verify OTP
    verify_response = make_request("POST", "/auth/verify-otp", {
        "phone": driver_phone,
        "otp": MOCK_OTP,
        "role": "driver"
    })
    print(f"Verify OTP: {verify_response.status_code}")
    
    # Step 3: Register KYC
    future_date = (date.today() + timedelta(days=365)).isoformat()
    
    kyc_data = {
        "phone": driver_phone,
        "personal_details": {
            "full_name": "Debug Driver",
            "mobile_number": driver_phone,
            "full_address": "Test Address, Test City",
            "aadhaar_number": "123456789012",
            "pan_number": "ABCDE1234F",
            "driving_license_number": "DL123456789",
            "driving_experience_years": 5,
            "driver_photo": "base64_photo_data"
        },
        "bank_details": {
            "account_holder_name": "Debug Driver",
            "bank_name": "Test Bank",
            "account_number": "1234567890123456",
            "ifsc_code": "TEST0123456",
            "branch_name": "Test Branch"
        },
        "vehicle_details": {
            "vehicle_type": "sedan",
            "vehicle_number": "TN01AB1234",
            "vehicle_model": "Test Model",
            "vehicle_year": 2020
        },
        "documents": {
            "aadhaar_card": {"front_image": "base64_aadhaar_front", "back_image": "base64_aadhaar_back"},
            "pan_card": {"front_image": "base64_pan_front"},
            "driving_license": {"front_image": "base64_dl_front", "back_image": "base64_dl_back"},
            "rc_book": {"front_image": "base64_rc_front", "back_image": "base64_rc_back"},
            "insurance": {"front_image": "base64_insurance"},
            "fitness_certificate": {"front_image": "base64_fc"},
            "permit": {"front_image": "base64_permit"},
            "pollution_certificate": {"front_image": "base64_pollution"}
        },
        "document_expiry": {
            "insurance_expiry": future_date,
            "fc_expiry": future_date,
            "permit_expiry": future_date,
            "pollution_expiry": future_date,
            "license_expiry": future_date
        },
        "driver_vehicle_photo": {
            "photo": "base64_vehicle_photo"
        }
    }
    
    kyc_response = make_request("POST", "/driver/register-kyc", kyc_data)
    print(f"Register KYC: {kyc_response.status_code}")
    
    if kyc_response.status_code != 200:
        print("Failed to register driver")
        return
    
    driver_data = kyc_response.json()
    driver_id = driver_data.get('driver_id')
    print(f"Driver ID: {driver_id}")
    
    # Step 4: Approve driver
    approve_response = make_request("PUT", "/admin/driver/approve", {
        "driver_id": driver_id,
        "approval_status": "approved"
    })
    print(f"Approve Driver: {approve_response.status_code}")
    
    # Step 5: Check wallet balance (should be ₹0)
    wallet_response = make_request("GET", f"/wallet/{driver_id}")
    if wallet_response.status_code == 200:
        wallet_data = wallet_response.json()
        balance = wallet_data.get('wallet', {}).get('balance', 0)
        print(f"Initial Wallet Balance: ₹{balance}")
    
    # Step 6: Set duty ON
    duty_response = make_request("PUT", f"/driver/{driver_id}/duty-status", {
        "duty_on": True,
        "go_home_mode": False
    })
    print(f"Set Duty ON: {duty_response.status_code}")
    
    # Step 7: Update location
    location_response = make_request("PUT", f"/driver/{driver_id}/location", {
        "latitude": 12.97,
        "longitude": 80.24,
        "address": "Test Location"
    })
    print(f"Update Location: {location_response.status_code}")
    
    # Step 8: Create customer
    customer_phone = "7777788888"
    
    # Customer OTP
    cust_otp_response = make_request("POST", "/auth/send-otp", {
        "phone": customer_phone,
        "role": "customer"
    })
    print(f"Customer Send OTP: {cust_otp_response.status_code}")
    
    # Customer verify OTP
    cust_verify_response = make_request("POST", "/auth/verify-otp", {
        "phone": customer_phone,
        "otp": MOCK_OTP,
        "role": "customer"
    })
    print(f"Customer Verify OTP: {cust_verify_response.status_code}")
    
    # Customer register
    cust_register_response = make_request("POST", "/customer/register", {
        "phone": customer_phone,
        "name": "Debug Customer"
    })
    print(f"Customer Register: {cust_register_response.status_code}")
    
    if cust_register_response.status_code != 200:
        print("Failed to register customer")
        return
    
    customer_data = cust_register_response.json()
    customer_id = customer_data.get('user', {}).get('user_id')
    print(f"Customer ID: {customer_id}")
    
    # Step 9: Try smart booking with ₹0 wallet - SHOULD FAIL
    booking_data = {
        "customer_id": customer_id,
        "pickup": {
            "latitude": 12.97,
            "longitude": 80.24,
            "address": "Pickup Location"
        },
        "drop": {
            "latitude": 13.08,
            "longitude": 80.27,
            "address": "Drop Location"
        },
        "vehicle_type": "sedan",
        "assignment_mode": "auto"
    }
    
    print("\n🚨 CRITICAL TEST: Smart booking with ₹0 wallet")
    booking_response = make_request("POST", "/booking/create-smart", booking_data)
    print(f"Smart Booking Response Code: {booking_response.status_code}")
    
    if booking_response:
        response_data = booking_response.json()
        print(f"Response Data: {json.dumps(response_data, indent=2)}")
        
        if booking_response.status_code == 200:
            print("❌ CRITICAL BUG: Booking succeeded when it should have failed!")
            print("The wallet restriction (₹1000 minimum) is NOT working!")
        else:
            print("✅ Wallet restriction working correctly")
    else:
        print("❌ No response from server")

if __name__ == "__main__":
    debug_wallet_restriction()