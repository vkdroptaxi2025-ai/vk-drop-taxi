#!/usr/bin/env python3
"""
Comprehensive Driver Onboarding System Testing
Tests the complete driver onboarding flow as requested
"""

import requests
import json
import base64
from datetime import datetime

# API Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

def create_sample_base64_image():
    """Create a sample base64 image for testing"""
    # Simple 1x1 pixel PNG in base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_comprehensive_driver_onboarding():
    """Test 1: POST /api/driver/onboard with full data structure"""
    print("🔍 TEST 1: Comprehensive Driver Onboarding API")
    
    # Create comprehensive onboarding data
    unique_phone = f"987654{datetime.now().microsecond % 10000:04d}"
    onboarding_data = {
        "basic_details": {
            "full_name": "Rajesh Kumar Singh",
            "phone": unique_phone,
            "address": "123 MG Road, Bangalore, Karnataka 560001",
            "aadhaar_number": "123456789012",
            "pan_number": "ABCDE1234F",
            "driving_license_number": "KA0320110012345",
            "driving_experience_years": 8
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
            "vehicle_number": "KA01AB1234",
            "vehicle_model": "Maruti Suzuki Dzire",
            "vehicle_year": 2020
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
            "amount": 5000,
            "screenshot": create_sample_base64_image()
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/driver/onboard", json=onboarding_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("driver_id") and data.get("approval_status") == "pending":
                print("✅ PASS: Driver onboarding successful with pending status")
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

def test_driver_status_check(driver_id):
    """Test 2: GET /api/driver/{driver_id}/status"""
    print(f"\n🔍 TEST 2: Verify Driver Status (Pending)")
    
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id}/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("approval_status") == "pending":
                print("✅ PASS: Driver status is pending as expected")
                return True
            else:
                print(f"❌ FAIL: Expected pending status, got {data.get('approval_status')}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def test_admin_view_drivers(test_phone):
    """Test 3: GET /api/admin/drivers"""
    print(f"\n🔍 TEST 3: Admin View Drivers")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/drivers")
        print(f"Status Code: {response.status_code}")
        print(f"Response length: {len(response.text)} characters")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data.get("success") and isinstance(data.get("drivers"), list):
                drivers_list = data["drivers"]
                print(f"✅ PASS: Admin can view drivers list ({len(drivers_list)} drivers)")
                # Check if our newly registered driver is in the list
                for driver in drivers_list:
                    if driver.get("phone") == test_phone:
                        print("✅ PASS: Newly registered driver found in admin list")
                        return True
                print("⚠️  WARNING: Newly registered driver not found in list")
                return True
            else:
                print("❌ FAIL: Invalid drivers list response")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def test_admin_approve_driver(driver_id):
    """Test 4: PUT /api/admin/driver/approve"""
    print(f"\n🔍 TEST 4: Admin Approve Driver")
    
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

def test_verify_approved_status(driver_id):
    """Test 5: GET /api/driver/{driver_id}/status (verify approved)"""
    print(f"\n🔍 TEST 5: Verify Approved Status")
    
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id}/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("approval_status") == "approved":
                print("✅ PASS: Driver status is approved as expected")
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

def test_admin_reject_driver():
    """Test 6: Admin Reject Driver with reason"""
    print(f"\n🔍 TEST 6: Admin Reject Driver")
    
    # First create another driver for rejection
    print("Creating another driver for rejection test...")
    
    onboarding_data = {
        "basic_details": {
            "full_name": "Suresh Kumar",
            "phone": f"987654{datetime.now().microsecond % 10000:04d}",  # Generate unique phone
            "address": "456 Brigade Road, Bangalore, Karnataka 560025",
            "aadhaar_number": "987654321098",
            "pan_number": "FGHIJ5678K",
            "driving_license_number": "KA0320110098765",
            "driving_experience_years": 5
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
            "vehicle_type": "suv",
            "vehicle_number": "KA01CD5678",
            "vehicle_model": "Mahindra Scorpio",
            "vehicle_year": 2019
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
        }
    }
    
    try:
        # Create driver
        response = requests.post(f"{BASE_URL}/driver/onboard", json=onboarding_data)
        if response.status_code != 200:
            print(f"❌ FAIL: Could not create driver for rejection test - HTTP {response.status_code}")
            return False
            
        driver_data = response.json()
        reject_driver_id = driver_data.get("driver_id")
        
        if not reject_driver_id:
            print("❌ FAIL: No driver_id returned for rejection test")
            return False
        
        # Now reject the driver
        rejection_data = {
            "driver_id": reject_driver_id,
            "approval_status": "rejected",
            "rejection_reason": "Incomplete documents - License photo unclear"
        }
        
        response = requests.put(f"{BASE_URL}/admin/driver/approve", json=rejection_data)
        print(f"Rejection Status Code: {response.status_code}")
        print(f"Rejection Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ PASS: Driver rejected successfully with reason")
                
                # Verify rejection status
                status_response = requests.get(f"{BASE_URL}/driver/{reject_driver_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("approval_status") == "rejected":
                        print("✅ PASS: Driver rejection status verified")
                        return True
                    else:
                        print(f"❌ FAIL: Expected rejected status, got {status_data.get('approval_status')}")
                        return False
                else:
                    print("⚠️  WARNING: Could not verify rejection status")
                    return True
            else:
                print("❌ FAIL: Rejection failed")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def main():
    """Run all comprehensive driver onboarding tests"""
    print("🚀 COMPREHENSIVE DRIVER ONBOARDING SYSTEM TESTING")
    print("=" * 60)
    print(f"API Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    driver_id = None
    test_phone = None
    
    # Test 1: Comprehensive Driver Onboarding
    driver_id, test_phone = test_comprehensive_driver_onboarding()
    results.append(("Comprehensive Driver Onboarding", driver_id is not None))
    
    if driver_id:
        # Test 2: Verify Driver Status (Pending)
        results.append(("Verify Driver Status (Pending)", test_driver_status_check(driver_id)))
        
        # Test 3: Admin View Drivers
        results.append(("Admin View Drivers", test_admin_view_drivers(test_phone)))
        
        # Test 4: Admin Approve Driver
        approval_success = test_admin_approve_driver(driver_id)
        results.append(("Admin Approve Driver", approval_success))
        
        if approval_success:
            # Test 5: Verify Approved Status
            results.append(("Verify Approved Status", test_verify_approved_status(driver_id)))
    
    # Test 6: Admin Reject Driver (independent test)
    results.append(("Admin Reject Driver", test_admin_reject_driver()))
    
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
        print("🎉 ALL TESTS PASSED - Comprehensive Driver Onboarding System is working perfectly!")
    else:
        print("⚠️  SOME TESTS FAILED - Please check the failed tests above")
    
    return passed == total

if __name__ == "__main__":
    main()