#!/usr/bin/env python3
"""
Isolated wallet restriction test - ensure only one driver exists
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

def test_isolated_wallet_restriction():
    """Test wallet restriction in isolation"""
    print("🔍 ISOLATED WALLET RESTRICTION TEST")
    print("=" * 50)
    
    # Step 1: Check all existing drivers and turn them offline
    print("Step 1: Checking existing drivers...")
    drivers_response = make_request("GET", "/admin/drivers")
    if drivers_response and drivers_response.status_code == 200:
        drivers_data = drivers_response.json()
        existing_drivers = drivers_data.get('drivers', [])
        print(f"Found {len(existing_drivers)} existing drivers")
        
        # Turn all existing drivers offline
        for driver in existing_drivers:
            driver_id = driver.get('driver_id')
            if driver_id:
                offline_response = make_request("PUT", f"/driver/{driver_id}/duty-status", {
                    "duty_on": False,
                    "go_home_mode": False
                })
                print(f"  Turned driver {driver_id} offline: {offline_response.status_code if offline_response else 'Failed'}")
    
    # Step 2: Create a new driver with ₹0 wallet
    print("\nStep 2: Creating new driver with ₹0 wallet...")
    driver_phone = "9999900000"
    
    # Send OTP
    otp_response = make_request("POST", "/auth/send-otp", {
        "phone": driver_phone,
        "role": "driver"
    })
    
    # Verify OTP
    verify_response = make_request("POST", "/auth/verify-otp", {
        "phone": driver_phone,
        "otp": MOCK_OTP,
        "role": "driver"
    })
    
    # Register KYC
    future_date = (date.today() + timedelta(days=365)).isoformat()
    
    kyc_data = {
        "phone": driver_phone,
        "personal_details": {
            "full_name": "Isolated Test Driver",
            "mobile_number": driver_phone,
            "full_address": "Test Address, Test City",
            "aadhaar_number": "123456789012",
            "pan_number": "ABCDE1234F",
            "driving_license_number": "DL123456789",
            "driving_experience_years": 5,
            "driver_photo": "base64_photo_data"
        },
        "bank_details": {
            "account_holder_name": "Isolated Test Driver",
            "bank_name": "Test Bank",
            "account_number": "1234567890123456",
            "ifsc_code": "TEST0123456",
            "branch_name": "Test Branch"
        },
        "vehicle_details": {
            "vehicle_type": "sedan",
            "vehicle_number": "TN01AB9999",
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
    
    if not kyc_response or kyc_response.status_code != 200:
        print("❌ Failed to register driver")
        return
    
    driver_data = kyc_response.json()
    driver_id = driver_data.get('driver_id')
    print(f"✅ Driver created: {driver_id}")
    
    # Approve driver
    approve_response = make_request("PUT", "/admin/driver/approve", {
        "driver_id": driver_id,
        "approval_status": "approved"
    })
    print(f"✅ Driver approved: {approve_response.status_code}")
    
    # Check wallet balance (should be ₹0)
    wallet_response = make_request("GET", f"/wallet/{driver_id}")
    if wallet_response and wallet_response.status_code == 200:
        wallet_data = wallet_response.json()
        balance = wallet_data.get('wallet', {}).get('balance', 0)
        print(f"✅ Wallet Balance: ₹{balance}")
    
    # Set duty ON
    duty_response = make_request("PUT", f"/driver/{driver_id}/duty-status", {
        "duty_on": True,
        "go_home_mode": False
    })
    print(f"✅ Duty ON: {duty_response.status_code}")
    
    # Update location
    location_response = make_request("PUT", f"/driver/{driver_id}/location", {
        "latitude": 12.97,
        "longitude": 80.24,
        "address": "Test Location"
    })
    print(f"✅ Location updated: {location_response.status_code}")
    
    # Step 3: Create customer
    print("\nStep 3: Creating customer...")
    customer_phone = "8888800000"
    
    # Customer OTP flow
    make_request("POST", "/auth/send-otp", {"phone": customer_phone, "role": "customer"})
    make_request("POST", "/auth/verify-otp", {"phone": customer_phone, "otp": MOCK_OTP, "role": "customer"})
    
    cust_register_response = make_request("POST", "/customer/register", {
        "phone": customer_phone,
        "name": "Isolated Test Customer"
    })
    
    if not cust_register_response or cust_register_response.status_code != 200:
        print("❌ Failed to register customer")
        return
    
    customer_data = cust_register_response.json()
    customer_id = customer_data.get('user', {}).get('user_id')
    print(f"✅ Customer created: {customer_id}")
    
    # Step 4: Test smart booking with ₹0 wallet - SHOULD FAIL
    print("\nStep 4: Testing smart booking with ₹0 wallet...")
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
    
    booking_response = make_request("POST", "/booking/create-smart", booking_data)
    print(f"Smart Booking Response Code: {booking_response.status_code}")
    
    if booking_response:
        response_data = booking_response.json()
        
        if booking_response.status_code == 200:
            selected_driver_id = response_data.get('booking', {}).get('driver_id')
            print(f"❌ CRITICAL BUG: Booking succeeded!")
            print(f"   Expected: 404 'No eligible drivers available'")
            print(f"   Actual: 200 with driver_id: {selected_driver_id}")
            print(f"   Our driver_id: {driver_id}")
            
            if selected_driver_id == driver_id:
                print("   🚨 WALLET RESTRICTION NOT WORKING - Same driver with ₹0 wallet was selected!")
            else:
                print("   🚨 DIFFERENT DRIVER SELECTED - Check if other drivers are still online")
                
        elif booking_response.status_code == 404:
            error_detail = response_data.get('detail', '')
            if "No eligible drivers available" in error_detail:
                print("✅ WALLET RESTRICTION WORKING: Correctly rejected booking")
            else:
                print(f"❓ Unexpected 404 error: {error_detail}")
        else:
            print(f"❓ Unexpected response: {response_data}")
    else:
        print("❌ No response from server")
    
    # Step 5: Add ₹1100 and test again - SHOULD SUCCEED
    print("\nStep 5: Adding ₹1100 to wallet and testing again...")
    add_money_response = make_request("POST", "/wallet/add-money", {
        "user_id": driver_id,
        "amount": 1100
    })
    print(f"Add Money: {add_money_response.status_code}")
    
    # Test booking again
    booking_response_2 = make_request("POST", "/booking/create-smart", booking_data)
    print(f"Smart Booking with ₹1100 Response Code: {booking_response_2.status_code}")
    
    if booking_response_2 and booking_response_2.status_code == 200:
        response_data_2 = booking_response_2.json()
        selected_driver_id_2 = response_data_2.get('booking', {}).get('driver_id')
        print(f"✅ Booking succeeded with ₹1100 wallet")
        print(f"   Selected driver: {selected_driver_id_2}")
        
        if selected_driver_id_2 == driver_id:
            print("✅ Correct driver selected after wallet top-up")
        else:
            print("❓ Different driver selected even after wallet top-up")
    else:
        print("❌ Booking failed even with ₹1100 wallet")

if __name__ == "__main__":
    test_isolated_wallet_restriction()