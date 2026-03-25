#!/usr/bin/env python3
"""
APPROVE/REJECT API Testing
Tests the specific APPROVE/REJECT API functionality as requested
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

def create_test_driver(driver_name, phone_suffix):
    """Create a new test driver using POST /api/driver/onboard"""
    print(f"🔍 Creating test driver: {driver_name}")
    
    # Create comprehensive onboarding data
    unique_phone = f"98765{phone_suffix:05d}"
    onboarding_data = {
        "basic_details": {
            "full_name": driver_name,
            "phone": unique_phone,
            "address": "123 Test Road, Bangalore, Karnataka 560001",
            "aadhaar_number": "123456789012",
            "pan_number": "ABCDE1234F",
            "driving_license_number": f"KA032011{phone_suffix:07d}",
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
            "vehicle_type": "sedan",
            "vehicle_number": f"KA01AB{phone_suffix:04d}",
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
    
    print(f"📤 REQUEST: POST {BASE_URL}/driver/onboard")
    print(f"📤 PAYLOAD: {json.dumps(onboarding_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/driver/onboard", json=onboarding_data)
        print(f"📥 RESPONSE STATUS: {response.status_code}")
        print(f"📥 RESPONSE BODY: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("driver_id"):
                print(f"✅ SUCCESS: Driver created with ID: {data['driver_id']}")
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

def test_approve_driver(driver_id):
    """Test APPROVE: PUT /api/admin/driver/approve with approval_status: 'approved'"""
    print(f"\n🔍 TESTING APPROVE API for driver_id: {driver_id}")
    
    approval_data = {
        "driver_id": driver_id,
        "approval_status": "approved"
    }
    
    print(f"📤 REQUEST: PUT {BASE_URL}/admin/driver/approve")
    print(f"📤 PAYLOAD: {json.dumps(approval_data, indent=2)}")
    
    try:
        response = requests.put(f"{BASE_URL}/admin/driver/approve", json=approval_data)
        print(f"📥 RESPONSE STATUS: {response.status_code}")
        print(f"📥 RESPONSE BODY: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ SUCCESS: Driver approved successfully")
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

def test_reject_driver(driver_id):
    """Test REJECT: PUT /api/admin/driver/approve with approval_status: 'rejected' and rejection_reason"""
    print(f"\n🔍 TESTING REJECT API for driver_id: {driver_id}")
    
    rejection_data = {
        "driver_id": driver_id,
        "approval_status": "rejected",
        "rejection_reason": "Test rejection - Documents not clear"
    }
    
    print(f"📤 REQUEST: PUT {BASE_URL}/admin/driver/approve")
    print(f"📤 PAYLOAD: {json.dumps(rejection_data, indent=2)}")
    
    try:
        response = requests.put(f"{BASE_URL}/admin/driver/approve", json=rejection_data)
        print(f"📥 RESPONSE STATUS: {response.status_code}")
        print(f"📥 RESPONSE BODY: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ SUCCESS: Driver rejected successfully")
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

def verify_driver_status(driver_id, expected_status):
    """Verify the driver status changed to expected status"""
    print(f"\n🔍 VERIFYING DRIVER STATUS for driver_id: {driver_id}")
    print(f"Expected status: {expected_status}")
    
    print(f"📤 REQUEST: GET {BASE_URL}/driver/{driver_id}/status")
    
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id}/status")
        print(f"📥 RESPONSE STATUS: {response.status_code}")
        print(f"📥 RESPONSE BODY: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            actual_status = data.get("approval_status")
            if actual_status == expected_status:
                print(f"✅ SUCCESS: Driver status is {actual_status} as expected")
                return True
            else:
                print(f"❌ FAIL: Expected {expected_status}, got {actual_status}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
        return False

def main():
    """Run the specific APPROVE/REJECT API tests as requested"""
    print("🚀 APPROVE/REJECT API TESTING")
    print("=" * 80)
    print(f"API Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = []
    
    # Step 1: Create first test driver for APPROVE test
    print("\n" + "="*50)
    print("STEP 1: Create first test driver for APPROVE test")
    print("="*50)
    
    driver1_id, driver1_phone = create_test_driver("Test Driver Approve", 12345)
    results.append(("Create Driver 1 for Approve", driver1_id is not None))
    
    if driver1_id:
        # Step 2: Test APPROVE API
        print("\n" + "="*50)
        print("STEP 2: Test APPROVE API")
        print("="*50)
        
        approve_success = test_approve_driver(driver1_id)
        results.append(("APPROVE API Test", approve_success))
        
        if approve_success:
            # Step 3: Verify driver status changed to approved
            print("\n" + "="*50)
            print("STEP 3: Verify driver status changed to approved")
            print("="*50)
            
            verify_approved = verify_driver_status(driver1_id, "approved")
            results.append(("Verify Approved Status", verify_approved))
    
    # Step 4: Create second test driver for REJECT test
    print("\n" + "="*50)
    print("STEP 4: Create second test driver for REJECT test")
    print("="*50)
    
    driver2_id, driver2_phone = create_test_driver("Test Driver Reject", 67890)
    results.append(("Create Driver 2 for Reject", driver2_id is not None))
    
    if driver2_id:
        # Step 5: Test REJECT API
        print("\n" + "="*50)
        print("STEP 5: Test REJECT API")
        print("="*50)
        
        reject_success = test_reject_driver(driver2_id)
        results.append(("REJECT API Test", reject_success))
        
        if reject_success:
            # Step 6: Verify driver status changed to rejected
            print("\n" + "="*50)
            print("STEP 6: Verify driver status changed to rejected")
            print("="*50)
            
            verify_rejected = verify_driver_status(driver2_id, "rejected")
            results.append(("Verify Rejected Status", verify_rejected))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print("=" * 80)
    print(f"📈 OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - APPROVE/REJECT API is working perfectly!")
    else:
        print("⚠️  SOME TESTS FAILED - Please check the failed tests above")
    
    return passed == total

if __name__ == "__main__":
    main()