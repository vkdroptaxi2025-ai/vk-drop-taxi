#!/usr/bin/env python3
"""
VK Drop Taxi - Admin Panel Driver Details API Testing
Testing the Admin Panel driver details API to verify it correctly returns full driver data including documents.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
TIMEOUT = 30

def log_test(message, status="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_admin_drivers_list():
    """
    Test GET /api/admin/drivers - List view (lightweight)
    Should return driver list with basic fields without base64 image strings
    """
    log_test("🔍 Testing GET /api/admin/drivers (List view - lightweight)")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/drivers", timeout=TIMEOUT)
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Size: {len(response.content)} bytes ({len(response.content)/1024:.2f} KB)")
        
        if response.status_code != 200:
            log_test(f"❌ FAILED: Expected 200, got {response.status_code}", "ERROR")
            log_test(f"Response: {response.text}", "ERROR")
            return False
        
        data = response.json()
        
        # Check response structure
        if not data.get('success'):
            log_test("❌ FAILED: Response success is not True", "ERROR")
            return False
        
        if 'drivers' not in data:
            log_test("❌ FAILED: No 'drivers' field in response", "ERROR")
            return False
        
        drivers = data['drivers']
        log_test(f"Found {len(drivers)} drivers in the system")
        
        if len(drivers) == 0:
            log_test("⚠️  WARNING: No drivers found in system", "WARN")
            return True
        
        # Check first driver structure
        first_driver = drivers[0]
        log_test(f"Sample driver fields: {list(first_driver.keys())}")
        
        # Verify required fields are present
        required_fields = ['driver_id', 'full_name', 'phone', 'address', 'vehicle_number', 'vehicle_type', 'vehicle_model', 'vehicle_year', 'approval_status']
        missing_fields = []
        
        for field in required_fields:
            if field not in first_driver:
                missing_fields.append(field)
        
        if missing_fields:
            log_test(f"❌ FAILED: Missing required fields: {missing_fields}", "ERROR")
            return False
        
        log_test("✅ PASSED: All required fields present in list view:")
        log_test(f"  - driver_id: {first_driver.get('driver_id', 'N/A')}")
        log_test(f"  - full_name: {first_driver.get('full_name', 'N/A')}")
        log_test(f"  - phone: {first_driver.get('phone', 'N/A')}")
        log_test(f"  - address: {first_driver.get('address', 'N/A')}")
        log_test(f"  - vehicle_number: {first_driver.get('vehicle_number', 'N/A')}")
        log_test(f"  - vehicle_type: {first_driver.get('vehicle_type', 'N/A')}")
        log_test(f"  - vehicle_model: {first_driver.get('vehicle_model', 'N/A')}")
        log_test(f"  - vehicle_year: {first_driver.get('vehicle_year', 'N/A')}")
        log_test(f"  - approval_status: {first_driver.get('approval_status', 'N/A')}")
        
        # Check for base64 image strings (should NOT be present)
        response_text = response.text
        base64_count = response_text.count('data:image')
        
        if base64_count > 0:
            log_test(f"❌ FAILED: Found {base64_count} base64 image strings in response", "ERROR")
            return False
        
        log_test("✅ PASSED: List API returns lightweight data without base64 images")
        log_test(f"✅ PASSED: Contains required fields: driver_id, phone, full_name, address, vehicle_type, vehicle_number, approval_status")
        
        # Return a driver_id for full details testing
        return first_driver['driver_id'] if drivers else None
        
    except requests.exceptions.RequestException as e:
        log_test(f"❌ FAILED: Request error - {str(e)}", "ERROR")
        return False
    except json.JSONDecodeError as e:
        log_test(f"❌ FAILED: JSON decode error - {str(e)}", "ERROR")
        return False
    except Exception as e:
        log_test(f"❌ FAILED: Unexpected error - {str(e)}", "ERROR")
        return False

def test_admin_driver_full_details(driver_id):
    """
    Test GET /api/admin/driver/{driver_id}/full - Full details view
    Should return complete data with all documents including base64 images
    """
    log_test(f"🔍 Testing GET /api/admin/driver/{driver_id}/full (Full details view)")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/driver/{driver_id}/full", timeout=TIMEOUT)
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Size: {len(response.content)} bytes ({len(response.content)/1024:.2f} KB)")
        
        if response.status_code != 200:
            log_test(f"❌ FAILED: Expected 200, got {response.status_code}", "ERROR")
            log_test(f"Response: {response.text}", "ERROR")
            return False
        
        data = response.json()
        
        # Check response structure
        if not data.get('success'):
            log_test("❌ FAILED: Response success is not True", "ERROR")
            return False
        
        if 'driver' not in data:
            log_test("❌ FAILED: No 'driver' field in response", "ERROR")
            return False
        
        driver = data['driver']
        log_test(f"Driver fields: {list(driver.keys())}")
        
        # Verify all required fields from the review request are present
        required_basic_fields = [
            'driver_id', 'full_name', 'phone', 'address', 'aadhaar_number', 'pan_number', 
            'driving_license_number', 'driving_experience_years'
        ]
        
        required_vehicle_fields = [
            'vehicle_type', 'vehicle_number', 'vehicle_model', 'vehicle_year'
        ]
        
        required_approval_fields = [
            'approval_status', 'is_online', 'rating'
        ]
        
        required_document_images = [
            'driver_photo', 'aadhaar_front', 'aadhaar_back', 'license_front', 'license_back',
            'rc_front', 'rc_back', 'insurance', 'permit', 'pollution_certificate',
            'vehicle_front_photo', 'vehicle_back_photo'
        ]
        
        # Check basic fields
        missing_basic = []
        for field in required_basic_fields:
            if field not in driver or driver[field] is None:
                missing_basic.append(field)
        
        # Check vehicle fields
        missing_vehicle = []
        for field in required_vehicle_fields:
            if field not in driver or driver[field] is None:
                missing_vehicle.append(field)
        
        # Check approval fields
        missing_approval = []
        for field in required_approval_fields:
            if field not in driver or driver[field] is None:
                missing_approval.append(field)
        
        # Check document images
        missing_documents = []
        for field in required_document_images:
            if field not in driver or not driver[field]:
                missing_documents.append(field)
        
        # Log results
        if not missing_basic:
            log_test("✅ All basic driver fields present:")
            for field in required_basic_fields:
                log_test(f"  - {field}: {str(driver[field])[:50]}{'...' if len(str(driver[field])) > 50 else ''}")
        else:
            log_test(f"❌ Missing basic fields: {missing_basic}", "ERROR")
        
        if not missing_vehicle:
            log_test("✅ All vehicle fields present:")
            for field in required_vehicle_fields:
                log_test(f"  - {field}: {driver[field]}")
        else:
            log_test(f"❌ Missing vehicle fields: {missing_vehicle}", "ERROR")
        
        if not missing_approval:
            log_test("✅ All approval fields present:")
            for field in required_approval_fields:
                log_test(f"  - {field}: {driver[field]}")
        else:
            log_test(f"❌ Missing approval fields: {missing_approval}", "ERROR")
        
        if not missing_documents:
            log_test("✅ All document images present:")
            for field in required_document_images:
                image_data = driver[field]
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    log_test(f"  - {field}: Base64 image ({len(image_data)} chars)")
                else:
                    log_test(f"  - {field}: {str(image_data)[:50]}{'...' if len(str(image_data)) > 50 else ''}")
        else:
            log_test(f"❌ Missing document images: {missing_documents}", "ERROR")
        
        # Check for base64 images (should be present in full details)
        response_text = response.text
        base64_count = response_text.count('data:image')
        
        log_test(f"Found {base64_count} base64 image strings in full details response")
        
        # Determine overall success
        all_fields_present = (
            not missing_basic and 
            not missing_vehicle and 
            not missing_approval and 
            not missing_documents
        )
        
        if all_fields_present:
            log_test("✅ PASSED: Full details API returns SUCCESS")
            log_test("✅ PASSED: All required fields present")
            log_test("✅ PASSED: All document images present")
            return True
        else:
            log_test("❌ FAILED: Some required fields or documents are missing", "ERROR")
            return False
        
    except requests.exceptions.RequestException as e:
        log_test(f"❌ FAILED: Request error - {str(e)}", "ERROR")
        return False
    except json.JSONDecodeError as e:
        log_test(f"❌ FAILED: JSON decode error - {str(e)}", "ERROR")
        return False
    except Exception as e:
        log_test(f"❌ FAILED: Unexpected error - {str(e)}", "ERROR")
        return False

def test_specific_driver_id():
    """Test with the specific driver_id mentioned in the review request"""
    log_test("🔍 Testing specific driver_id: VKDRV1025")
    
    # First check if this driver exists in the list
    try:
        response = requests.get(f"{BASE_URL}/admin/drivers", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            drivers = data.get('drivers', [])
            
            # Look for VKDRV1025
            target_driver = None
            for driver in drivers:
                if driver.get('driver_id') == 'VKDRV1025':
                    target_driver = driver
                    break
            
            if target_driver:
                log_test("✅ Found VKDRV1025 in driver list")
                log_test(f"Driver details: {target_driver.get('full_name', 'N/A')}, {target_driver.get('phone', 'N/A')}, Status: {target_driver.get('approval_status', 'N/A')}")
                
                # Test full details for this specific driver
                return test_admin_driver_full_details('VKDRV1025')
            else:
                log_test("⚠️  VKDRV1025 not found in driver list, will test with first available driver", "WARN")
                return None
        else:
            log_test(f"❌ Could not fetch driver list: {response.status_code}", "ERROR")
            return None
            
    except Exception as e:
        log_test(f"❌ Error checking for VKDRV1025: {str(e)}", "ERROR")
        return None

def main():
    """Main test execution"""
    log_test("🚀 Starting VK Drop Taxi Admin Panel Driver Details API Testing")
    log_test(f"Base URL: {BASE_URL}")
    
    test_results = []
    
    # Test 1: Admin drivers list (lightweight)
    log_test("\n" + "="*60)
    log_test("TEST 1: Admin Drivers List (Lightweight)")
    log_test("="*60)
    
    list_result = test_admin_drivers_list()
    if list_result is False:
        test_results.append("❌ Admin drivers list test FAILED")
    elif list_result is None:
        test_results.append("⚠️  Admin drivers list test - No drivers found")
    else:
        test_results.append("✅ Admin drivers list test PASSED")
        
        # Test 2: Specific driver full details (VKDRV1025)
        log_test("\n" + "="*60)
        log_test("TEST 2: Specific Driver Full Details (VKDRV1025)")
        log_test("="*60)
        
        specific_result = test_specific_driver_id()
        if specific_result is True:
            test_results.append("✅ VKDRV1025 full details test PASSED")
        elif specific_result is False:
            test_results.append("❌ VKDRV1025 full details test FAILED")
        else:
            # VKDRV1026 not found, test with first available driver
            if isinstance(list_result, str):  # We got a driver_id from list test
                log_test("\n" + "="*60)
                log_test(f"TEST 2b: First Available Driver Full Details ({list_result})")
                log_test("="*60)
                
                full_result = test_admin_driver_full_details(list_result)
                if full_result:
                    test_results.append(f"✅ Driver {list_result} full details test PASSED")
                else:
                    test_results.append(f"❌ Driver {list_result} full details test FAILED")
            else:
                test_results.append("⚠️  No driver available for full details testing")
    
    # Summary
    log_test("\n" + "="*60)
    log_test("TEST SUMMARY")
    log_test("="*60)
    
    for result in test_results:
        log_test(result)
    
    # Determine overall success
    failed_tests = [r for r in test_results if "❌" in r]
    passed_tests = [r for r in test_results if "✅" in r]
    
    log_test(f"\nOverall Results: {len(passed_tests)} PASSED, {len(failed_tests)} FAILED")
    
    if failed_tests:
        log_test("🔴 OVERALL STATUS: FAILED", "ERROR")
        sys.exit(1)
    else:
        log_test("🟢 OVERALL STATUS: PASSED", "SUCCESS")
        sys.exit(0)

if __name__ == "__main__":
    main()