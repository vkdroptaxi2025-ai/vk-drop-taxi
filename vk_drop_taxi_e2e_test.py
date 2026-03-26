#!/usr/bin/env python3
"""
VK Drop Taxi End-to-End Testing
Tests the specific endpoints requested by the user
"""

import requests
import json
import base64
from datetime import datetime

# API Configuration - Using the correct backend URL from environment
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

def create_sample_base64_image():
    """Create a sample base64 image for testing"""
    # Simple 1x1 pixel PNG in base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_driver_registration_with_payment():
    """Test 1: POST /api/driver/onboard with payment details"""
    print("🔍 TEST 1: Driver Registration with Payment")
    
    # Create realistic driver data with payment
    unique_phone = f"987654{datetime.now().microsecond % 10000:04d}"
    driver_data = {
        "basic_details": {
            "full_name": "Arjun Reddy",
            "phone": unique_phone,
            "address": "15/2, Koramangala 4th Block, Bangalore, Karnataka 560034",
            "aadhaar_number": "456789123456",
            "pan_number": "CDEFG2345H",
            "driving_license_number": "KA0320110054321",
            "driving_experience_years": 6
        },
        "driver_photos": {
            "driver_photo": create_sample_base64_image(),
            "driver_with_vehicle_photo": create_sample_base64_image()
        },
        "driver_documents": {
            "aadhaar_front": create_sample_base64_image(),
            "aadhaar_back": create_sample_base64_image(),
            "license_front": create_sample_base64_image(),
            "license_back": create_sample_base64_image()
        },
        "vehicle_details": {
            "vehicle_type": "sedan",
            "vehicle_number": "KA05MN7890",
            "vehicle_model": "Honda City",
            "vehicle_year": 2021
        },
        "vehicle_documents": {
            "rc_front": create_sample_base64_image(),
            "rc_back": create_sample_base64_image(),
            "insurance": create_sample_base64_image(),
            "permit": create_sample_base64_image(),
            "pollution_certificate": create_sample_base64_image()
        },
        "vehicle_photos": {
            "front_photo": create_sample_base64_image(),
            "back_photo": create_sample_base64_image(),
            "left_photo": create_sample_base64_image(),
            "right_photo": create_sample_base64_image()
        },
        "payment": {
            "amount": 500,
            "screenshot": create_sample_base64_image()
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/driver/onboard", json=driver_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("driver_id") and data.get("approval_status") == "pending":
                print("✅ PASS: Driver registration with payment successful")
                return data["driver_id"], unique_phone
            else:
                print("❌ FAIL: Invalid response structure")
                return None, None
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return None, None

def test_admin_approve_driver(driver_id):
    """Test 2: PUT /api/admin/driver/approve"""
    print(f"\n🔍 TEST 2: Admin Approve Driver")
    
    approval_data = {
        "driver_id": driver_id,
        "approval_status": "approved"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/admin/driver/approve", json=approval_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ PASS: Driver approved successfully")
                return True
            else:
                print("❌ FAIL: Approval failed")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def test_wallet_add_balance(user_id):
    """Test 3: POST /api/wallet/add-money"""
    print(f"\n🔍 TEST 3: Wallet Add Balance")
    
    wallet_data = {
        "user_id": user_id,
        "amount": 2000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/wallet/add-money", json=wallet_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("new_balance"):
                print(f"✅ PASS: Money added successfully. New balance: ₹{data.get('new_balance')}")
                return True
            else:
                print("❌ FAIL: Money addition failed")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def test_get_wallet_balance(user_id):
    """Test 4: GET /api/wallet/{user_id}"""
    print(f"\n🔍 TEST 4: Get Wallet Balance")
    
    try:
        response = requests.get(f"{BASE_URL}/wallet/{user_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "wallet" in data:
                wallet = data["wallet"]
                balance = wallet.get("balance", 0)
                print(f"✅ PASS: Wallet balance retrieved successfully. Balance: ₹{balance}")
                return True
            else:
                print("❌ FAIL: Invalid wallet response")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def test_driver_status_check(driver_id):
    """Test 5: GET /api/driver/{driver_id}/status"""
    print(f"\n🔍 TEST 5: Driver Status Check")
    
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id}/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("approval_status") == "approved":
                print("✅ PASS: Driver status shows 'approved'")
                return True
            else:
                print(f"❌ FAIL: Expected approved status, got {data.get('approval_status')}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def main():
    """Run all VK Drop Taxi end-to-end tests"""
    print("🚀 VK DROP TAXI END-TO-END TESTING")
    print("=" * 60)
    print(f"API Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    driver_id = None
    test_phone = None
    
    # Test 1: Driver Registration with Payment
    driver_id, test_phone = test_driver_registration_with_payment()
    results.append(("Driver Registration with Payment", driver_id is not None))
    
    if driver_id:
        # Test 2: Admin Approve Driver
        approval_success = test_admin_approve_driver(driver_id)
        results.append(("Admin Approve Driver", approval_success))
        
        # Test 3: Wallet Add Balance
        wallet_add_success = test_wallet_add_balance(driver_id)
        results.append(("Wallet Add Balance", wallet_add_success))
        
        # Test 4: Get Wallet Balance
        wallet_get_success = test_get_wallet_balance(driver_id)
        results.append(("Get Wallet Balance", wallet_get_success))
        
        # Test 5: Driver Status Check (should show approved)
        status_check_success = test_driver_status_check(driver_id)
        results.append(("Driver Status Check", status_check_success))
    else:
        # If driver registration failed, mark other tests as failed
        results.extend([
            ("Admin Approve Driver", False),
            ("Wallet Add Balance", False),
            ("Get Wallet Balance", False),
            ("Driver Status Check", False)
        ])
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print("=" * 60)
    print(f"📈 OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - VK Drop Taxi system is working perfectly!")
    else:
        print("⚠️  SOME TESTS FAILED - Please check the failed tests above")
    
    return passed == total

if __name__ == "__main__":
    main()