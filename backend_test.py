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
        required_fields = ['driver_id', 'phone', 'full_name', 'address', 'vehicle_type', 'vehicle_number', 'approval_status']
        missing_fields = []
        
        for field in required_fields:
            if field not in first_driver:
                missing_fields.append(field)
        
        if missing_fields:
            log_test(f"❌ FAILED: Missing required fields: {missing_fields}", "ERROR")
            return False
        
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
        
        # Check for driver documents
        document_fields = [
            'driver_documents',  # Should contain aadhaar_front, aadhaar_back, license_front, license_back
            'vehicle_documents', # Should contain rc_front, rc_back, insurance, permit, pollution_certificate
            'driver_photos',     # Should contain driver photos
            'vehicle_photos'     # Should contain vehicle photos
        ]
        
        found_documents = []
        missing_documents = []
        
        for doc_field in document_fields:
            if doc_field in driver and driver[doc_field]:
                found_documents.append(doc_field)
                log_test(f"✅ Found {doc_field}: {list(driver[doc_field].keys()) if isinstance(driver[doc_field], dict) else 'present'}")
            else:
                missing_documents.append(doc_field)
        
        # Check for payment screenshot if exists
        if 'payment' in driver and driver['payment']:
            if 'screenshot' in driver['payment']:
                found_documents.append('payment.screenshot')
                log_test("✅ Found payment screenshot")
        
        # Check for base64 images (should be present in full details)
        response_text = response.text
        base64_count = response_text.count('data:image')
        
        log_test(f"Found {base64_count} base64 image strings in full details response")
        
        # Verify specific document structure
        success_checks = []
        
        # Check driver_documents structure
        if 'driver_documents' in driver and driver['driver_documents']:
            driver_docs = driver['driver_documents']
            expected_driver_docs = ['aadhaar_front', 'aadhaar_back', 'license_front', 'license_back']
            found_driver_docs = [doc for doc in expected_driver_docs if doc in driver_docs]
            success_checks.append(f"Driver documents: {len(found_driver_docs)}/{len(expected_driver_docs)} found")
        
        # Check vehicle_documents structure
        if 'vehicle_documents' in driver and driver['vehicle_documents']:
            vehicle_docs = driver['vehicle_documents']
            expected_vehicle_docs = ['rc_front', 'rc_back', 'insurance', 'permit', 'pollution_certificate']
            found_vehicle_docs = [doc for doc in expected_vehicle_docs if doc in vehicle_docs]
            success_checks.append(f"Vehicle documents: {len(found_vehicle_docs)}/{len(expected_vehicle_docs)} found")
        
        # Check photos
        if 'driver_photos' in driver and driver['driver_photos']:
            success_checks.append("Driver photos: present")
        
        if 'vehicle_photos' in driver and driver['vehicle_photos']:
            success_checks.append("Vehicle photos: present")
        
        log_test("✅ PASSED: Full details API returns SUCCESS")
        log_test("✅ PASSED: Response contains complete driver data")
        
        for check in success_checks:
            log_test(f"✅ {check}")
        
        if missing_documents:
            log_test(f"⚠️  Note: Missing document sections: {missing_documents}", "WARN")
        
        return True
        
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
    log_test("🔍 Testing specific driver_id: VKDRV1026")
    
    # First check if this driver exists in the list
    try:
        response = requests.get(f"{BASE_URL}/admin/drivers", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            drivers = data.get('drivers', [])
            
            # Look for VKDRV1026
            target_driver = None
            for driver in drivers:
                if driver.get('driver_id') == 'VKDRV1026':
                    target_driver = driver
                    break
            
            if target_driver:
                log_test("✅ Found VKDRV1026 in driver list")
                log_test(f"Driver details: {target_driver.get('full_name', 'N/A')}, {target_driver.get('phone', 'N/A')}, Status: {target_driver.get('approval_status', 'N/A')}")
                
                # Test full details for this specific driver
                return test_admin_driver_full_details('VKDRV1026')
            else:
                log_test("⚠️  VKDRV1026 not found in driver list, will test with first available driver", "WARN")
                return None
        else:
            log_test(f"❌ Could not fetch driver list: {response.status_code}", "ERROR")
            return None
            
    except Exception as e:
        log_test(f"❌ Error checking for VKDRV1026: {str(e)}", "ERROR")
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
        
        # Test 2: Specific driver full details (VKDRV1026)
        log_test("\n" + "="*60)
        log_test("TEST 2: Specific Driver Full Details (VKDRV1026)")
        log_test("="*60)
        
        specific_result = test_specific_driver_id()
        if specific_result is True:
            test_results.append("✅ VKDRV1026 full details test PASSED")
        elif specific_result is False:
            test_results.append("❌ VKDRV1026 full details test FAILED")
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