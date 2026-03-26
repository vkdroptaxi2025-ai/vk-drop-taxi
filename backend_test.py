#!/usr/bin/env python3
"""
VK Drop Taxi Driver Approval Flow Testing
Testing the complete driver approval workflow end-to-end
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def log_test(test_name, status, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_emoji = "✅" if status == "PASS" else "❌"
    print(f"[{timestamp}] {status_emoji} {test_name}")
    if details:
        print(f"    {details}")
    print()

def create_test_driver_data(phone_suffix):
    """Create comprehensive test driver data"""
    phone = f"987654{phone_suffix:04d}"
    return {
        "basic_details": {
            "phone": phone,
            "full_name": f"Test Driver {phone_suffix}",
            "address": "123 Test Street, Test City, Test State 123456",
            "aadhaar_number": f"123456{phone_suffix:06d}",
            "pan_number": f"ABCDE{phone_suffix:04d}F",
            "driving_license_number": f"DL{phone_suffix:08d}",
            "driving_experience_years": 5
        },
        "driver_photos": {
            "driver_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "driver_with_vehicle_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        },
        "driver_documents": {
            "aadhaar_front": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "aadhaar_back": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "license_front": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "license_back": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        },
        "vehicle_details": {
            "vehicle_type": "sedan",
            "vehicle_number": f"KA01AB{phone_suffix:04d}",
            "vehicle_model": "Honda City",
            "vehicle_year": 2020
        },
        "vehicle_documents": {
            "rc_front": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "rc_back": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "insurance": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "permit": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "pollution_certificate": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        },
        "vehicle_photos": {
            "front_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "back_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "left_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "right_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        },
        "payment": {
            "amount": 500,
            "screenshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        }
    }

def test_driver_approval_flow():
    """Test the complete driver approval flow end-to-end"""
    print("🎯 VK DROP TAXI DRIVER APPROVAL FLOW TESTING")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Create a new driver
    print("TEST 1: Create a new driver with PENDING status")
    try:
        driver_data = create_test_driver_data(9001)
        response = requests.post(f"{BASE_URL}/driver/onboard", json=driver_data, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('driver_id'):
                driver_id_1 = result['driver_id']
                approval_status = result.get('approval_status', 'unknown')
                log_test("Create Driver", "PASS", f"Driver created with ID: {driver_id_1}, Status: {approval_status}")
                test_results.append(("Create Driver", "PASS", driver_id_1, approval_status))
            else:
                log_test("Create Driver", "FAIL", f"Unexpected response: {result}")
                test_results.append(("Create Driver", "FAIL", None, None))
                return test_results
        else:
            log_test("Create Driver", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Create Driver", "FAIL", None, None))
            return test_results
    except Exception as e:
        log_test("Create Driver", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Create Driver", "FAIL", None, None))
        return test_results
    
    # Test 2: Verify driver is created with PENDING status
    print("TEST 2: Verify driver status is PENDING")
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id_1}/status", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('approval_status', 'unknown')
            if status == 'pending':
                log_test("Verify PENDING Status", "PASS", f"Driver status confirmed as: {status}")
                test_results.append(("Verify PENDING Status", "PASS", driver_id_1, status))
            else:
                log_test("Verify PENDING Status", "FAIL", f"Expected 'pending', got: {status}")
                test_results.append(("Verify PENDING Status", "FAIL", driver_id_1, status))
        else:
            log_test("Verify PENDING Status", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Verify PENDING Status", "FAIL", driver_id_1, None))
    except Exception as e:
        log_test("Verify PENDING Status", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Verify PENDING Status", "FAIL", driver_id_1, None))
    
    # Test 3: Approve the driver using main endpoint
    print("TEST 3: Approve driver using PUT /api/admin/driver/approve")
    try:
        approval_data = {
            "driver_id": driver_id_1,
            "approval_status": "approved"
        }
        response = requests.put(f"{BASE_URL}/admin/driver/approve", json=approval_data, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                log_test("Approve Driver (Main Endpoint)", "PASS", f"Driver approved successfully: {result.get('message')}")
                test_results.append(("Approve Driver (Main Endpoint)", "PASS", driver_id_1, "approved"))
            else:
                log_test("Approve Driver (Main Endpoint)", "FAIL", f"Approval failed: {result}")
                test_results.append(("Approve Driver (Main Endpoint)", "FAIL", driver_id_1, None))
        else:
            log_test("Approve Driver (Main Endpoint)", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Approve Driver (Main Endpoint)", "FAIL", driver_id_1, None))
    except Exception as e:
        log_test("Approve Driver (Main Endpoint)", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Approve Driver (Main Endpoint)", "FAIL", driver_id_1, None))
    
    # Test 4: Verify driver status changed to 'approved'
    print("TEST 4: Verify driver status changed to APPROVED")
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id_1}/status", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('approval_status', 'unknown')
            if status == 'approved':
                log_test("Verify APPROVED Status", "PASS", f"Driver status confirmed as: {status}")
                test_results.append(("Verify APPROVED Status", "PASS", driver_id_1, status))
            else:
                log_test("Verify APPROVED Status", "FAIL", f"Expected 'approved', got: {status}")
                test_results.append(("Verify APPROVED Status", "FAIL", driver_id_1, status))
        else:
            log_test("Verify APPROVED Status", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Verify APPROVED Status", "FAIL", driver_id_1, None))
    except Exception as e:
        log_test("Verify APPROVED Status", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Verify APPROVED Status", "FAIL", driver_id_1, None))
    
    # Test 5: Create another driver for alias endpoint testing
    print("TEST 5: Create second driver for alias endpoint testing")
    try:
        driver_data_2 = create_test_driver_data(9002)
        response = requests.post(f"{BASE_URL}/driver/onboard", json=driver_data_2, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('driver_id'):
                driver_id_2 = result['driver_id']
                approval_status = result.get('approval_status', 'unknown')
                log_test("Create Second Driver", "PASS", f"Driver created with ID: {driver_id_2}, Status: {approval_status}")
                test_results.append(("Create Second Driver", "PASS", driver_id_2, approval_status))
            else:
                log_test("Create Second Driver", "FAIL", f"Unexpected response: {result}")
                test_results.append(("Create Second Driver", "FAIL", None, None))
                return test_results
        else:
            log_test("Create Second Driver", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Create Second Driver", "FAIL", None, None))
            return test_results
    except Exception as e:
        log_test("Create Second Driver", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Create Second Driver", "FAIL", None, None))
        return test_results
    
    # Test 6: Test the alias endpoint
    print("TEST 6: Test alias endpoint PUT /api/admin/approve-driver")
    try:
        approval_data = {
            "driver_id": driver_id_2,
            "approval_status": "approved"
        }
        response = requests.put(f"{BASE_URL}/admin/approve-driver", json=approval_data, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                log_test("Approve Driver (Alias Endpoint)", "PASS", f"Driver approved via alias: {result.get('message')}")
                test_results.append(("Approve Driver (Alias Endpoint)", "PASS", driver_id_2, "approved"))
            else:
                log_test("Approve Driver (Alias Endpoint)", "FAIL", f"Approval failed: {result}")
                test_results.append(("Approve Driver (Alias Endpoint)", "FAIL", driver_id_2, None))
        else:
            log_test("Approve Driver (Alias Endpoint)", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Approve Driver (Alias Endpoint)", "FAIL", driver_id_2, None))
    except Exception as e:
        log_test("Approve Driver (Alias Endpoint)", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Approve Driver (Alias Endpoint)", "FAIL", driver_id_2, None))
    
    # Test 7: Verify alias endpoint worked
    print("TEST 7: Verify alias endpoint approval worked")
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id_2}/status", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('approval_status', 'unknown')
            if status == 'approved':
                log_test("Verify Alias Approval", "PASS", f"Driver status confirmed as: {status}")
                test_results.append(("Verify Alias Approval", "PASS", driver_id_2, status))
            else:
                log_test("Verify Alias Approval", "FAIL", f"Expected 'approved', got: {status}")
                test_results.append(("Verify Alias Approval", "FAIL", driver_id_2, status))
        else:
            log_test("Verify Alias Approval", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Verify Alias Approval", "FAIL", driver_id_2, None))
    except Exception as e:
        log_test("Verify Alias Approval", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Verify Alias Approval", "FAIL", driver_id_2, None))
    
    # Test 8: Create third driver for rejection testing
    print("TEST 8: Create third driver for rejection testing")
    try:
        driver_data_3 = create_test_driver_data(9003)
        response = requests.post(f"{BASE_URL}/driver/onboard", json=driver_data_3, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('driver_id'):
                driver_id_3 = result['driver_id']
                approval_status = result.get('approval_status', 'unknown')
                log_test("Create Third Driver", "PASS", f"Driver created with ID: {driver_id_3}, Status: {approval_status}")
                test_results.append(("Create Third Driver", "PASS", driver_id_3, approval_status))
            else:
                log_test("Create Third Driver", "FAIL", f"Unexpected response: {result}")
                test_results.append(("Create Third Driver", "FAIL", None, None))
                return test_results
        else:
            log_test("Create Third Driver", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Create Third Driver", "FAIL", None, None))
            return test_results
    except Exception as e:
        log_test("Create Third Driver", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Create Third Driver", "FAIL", None, None))
        return test_results
    
    # Test 9: Reject the third driver
    print("TEST 9: Reject driver with rejection reason")
    try:
        rejection_data = {
            "driver_id": driver_id_3,
            "approval_status": "rejected",
            "rejection_reason": "Test rejection - Documents not clear for testing purposes"
        }
        response = requests.put(f"{BASE_URL}/admin/driver/approve", json=rejection_data, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                log_test("Reject Driver", "PASS", f"Driver rejected successfully: {result.get('message')}")
                test_results.append(("Reject Driver", "PASS", driver_id_3, "rejected"))
            else:
                log_test("Reject Driver", "FAIL", f"Rejection failed: {result}")
                test_results.append(("Reject Driver", "FAIL", driver_id_3, None))
        else:
            log_test("Reject Driver", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Reject Driver", "FAIL", driver_id_3, None))
    except Exception as e:
        log_test("Reject Driver", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Reject Driver", "FAIL", driver_id_3, None))
    
    # Test 10: Verify driver status changed to 'rejected'
    print("TEST 10: Verify driver status changed to REJECTED")
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id_3}/status", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('approval_status', 'unknown')
            if status == 'rejected':
                log_test("Verify REJECTED Status", "PASS", f"Driver status confirmed as: {status}")
                test_results.append(("Verify REJECTED Status", "PASS", driver_id_3, status))
            else:
                log_test("Verify REJECTED Status", "FAIL", f"Expected 'rejected', got: {status}")
                test_results.append(("Verify REJECTED Status", "FAIL", driver_id_3, status))
        else:
            log_test("Verify REJECTED Status", "FAIL", f"HTTP {response.status_code}: {response.text}")
            test_results.append(("Verify REJECTED Status", "FAIL", driver_id_3, None))
    except Exception as e:
        log_test("Verify REJECTED Status", "FAIL", f"Exception: {str(e)}")
        test_results.append(("Verify REJECTED Status", "FAIL", driver_id_3, None))
    
    return test_results

def print_summary(test_results):
    """Print comprehensive test summary"""
    print("\n" + "=" * 60)
    print("🎯 VK DROP TAXI DRIVER APPROVAL FLOW - TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = [t for t in test_results if t[1] == "PASS"]
    failed_tests = [t for t in test_results if t[1] == "FAIL"]
    
    print(f"✅ PASSED: {len(passed_tests)}/{len(test_results)} tests")
    print(f"❌ FAILED: {len(failed_tests)}/{len(test_results)} tests")
    print(f"📊 SUCCESS RATE: {(len(passed_tests)/len(test_results)*100):.1f}%")
    
    if passed_tests:
        print("\n✅ SUCCESSFUL TESTS:")
        for test_name, status, driver_id, approval_status in passed_tests:
            if driver_id:
                print(f"   • {test_name}: {driver_id} ({approval_status})")
            else:
                print(f"   • {test_name}")
    
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test_name, status, driver_id, approval_status in failed_tests:
            if driver_id:
                print(f"   • {test_name}: {driver_id}")
            else:
                print(f"   • {test_name}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_results = test_driver_approval_flow()
    print_summary(test_results)