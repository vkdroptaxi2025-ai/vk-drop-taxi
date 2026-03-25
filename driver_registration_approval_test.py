#!/usr/bin/env python3
"""
VK Drop Taxi - Driver Registration and Approval Flow Testing
Testing the complete driver registration and approval workflow as requested
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

class DriverRegistrationApprovalTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.driver_id = None
        self.driver_id_2 = None  # For rejection test
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def test_1_new_driver_registration(self):
        """Test 1: NEW DRIVER REGISTRATION"""
        print("\n=== TEST 1: NEW DRIVER REGISTRATION ===")
        
        driver_data = {
            "phone": "9876543299",
            "full_name": "Test New Driver",
            "address": "123 Test St, Chennai",
            "driving_license_number": "TN01 2020 0099999",
            "driving_license_image": "data:image/png;base64,test",
            "vehicle_type": "suv",
            "vehicle_number": "TN99ZZ9999",
            "rc_book_image": "data:image/png;base64,test",
            "insurance_details": "Policy 999, Valid 2025"
        }
        
        response = self.make_request("POST", "/driver/register", driver_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("driver_id") and data.get("approval_status") == "pending":
                self.driver_id = data.get("driver_id")
                self.log_result(
                    "Driver Registration",
                    True,
                    f"Driver registered successfully with ID: {self.driver_id}",
                    f"Status: {data.get('approval_status')}, Message: {data.get('message')}"
                )
                return True
            else:
                self.log_result(
                    "Driver Registration",
                    False,
                    "Registration response missing required fields",
                    f"Response: {data}"
                )
        else:
            error_msg = response.json() if response else "No response"
            self.log_result(
                "Driver Registration",
                False,
                f"Registration failed with status {response.status_code if response else 'None'}",
                f"Error: {error_msg}"
            )
        return False
    
    def test_2_check_driver_status(self):
        """Test 2: CHECK DRIVER STATUS"""
        print("\n=== TEST 2: CHECK DRIVER STATUS ===")
        
        if not self.driver_id:
            self.log_result("Check Driver Status", False, "No driver_id available from registration", None)
            return False
        
        response = self.make_request("GET", f"/driver/{self.driver_id}/status")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("approval_status") == "pending":
                self.log_result(
                    "Check Driver Status",
                    True,
                    "Driver status retrieved successfully",
                    f"Status: {data.get('approval_status')}, Online: {data.get('is_online')}, Duty: {data.get('duty_on')}"
                )
                return True
            else:
                self.log_result(
                    "Check Driver Status",
                    False,
                    "Status response missing required fields or wrong status",
                    f"Response: {data}"
                )
        else:
            error_msg = response.json() if response else "No response"
            self.log_result(
                "Check Driver Status",
                False,
                f"Status check failed with status {response.status_code if response else 'None'}",
                f"Error: {error_msg}"
            )
        return False
    
    def test_3_admin_views_drivers(self):
        """Test 3: ADMIN VIEWS DRIVERS"""
        print("\n=== TEST 3: ADMIN VIEWS DRIVERS ===")
        
        response = self.make_request("GET", "/admin/drivers")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") and "drivers" in data:
                drivers = data.get("drivers", [])
                # Check if our new driver is in the list
                found_driver = None
                for driver in drivers:
                    if driver.get("driver_id") == self.driver_id:
                        found_driver = driver
                        break
                
                if found_driver:
                    self.log_result(
                        "Admin Views Drivers",
                        True,
                        f"New driver found in admin list (Total drivers: {len(drivers)})",
                        f"Driver: {found_driver.get('full_name')} - {found_driver.get('phone')} - Status: {found_driver.get('approval_status')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Views Drivers",
                        False,
                        f"New driver not found in admin list (Total drivers: {len(drivers)})",
                        f"Looking for driver_id: {self.driver_id}"
                    )
            else:
                self.log_result(
                    "Admin Views Drivers",
                    False,
                    "Admin drivers response missing required fields",
                    f"Response: {data}"
                )
        else:
            error_msg = response.json() if response else "No response"
            self.log_result(
                "Admin Views Drivers",
                False,
                f"Admin drivers request failed with status {response.status_code if response else 'None'}",
                f"Error: {error_msg}"
            )
        return False
    
    def test_4_admin_approves_driver(self):
        """Test 4: ADMIN APPROVES DRIVER"""
        print("\n=== TEST 4: ADMIN APPROVES DRIVER ===")
        
        if not self.driver_id:
            self.log_result("Admin Approves Driver", False, "No driver_id available", None)
            return False
        
        approval_data = {
            "driver_id": self.driver_id,
            "approval_status": "approved"
        }
        
        response = self.make_request("PUT", "/admin/driver/approve", approval_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result(
                    "Admin Approves Driver",
                    True,
                    "Driver approved successfully",
                    f"Message: {data.get('message')}, Driver ID: {data.get('driver_id')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Approves Driver",
                    False,
                    "Approval response indicates failure",
                    f"Response: {data}"
                )
        else:
            error_msg = response.json() if response else "No response"
            self.log_result(
                "Admin Approves Driver",
                False,
                f"Driver approval failed with status {response.status_code if response else 'None'}",
                f"Error: {error_msg}"
            )
        return False
    
    def test_5_verify_approval(self):
        """Test 5: VERIFY APPROVAL"""
        print("\n=== TEST 5: VERIFY APPROVAL ===")
        
        if not self.driver_id:
            self.log_result("Verify Approval", False, "No driver_id available", None)
            return False
        
        response = self.make_request("GET", f"/driver/{self.driver_id}/status")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("approval_status") == "approved":
                self.log_result(
                    "Verify Approval",
                    True,
                    "Driver approval status verified successfully",
                    f"Status: {data.get('approval_status')}, Online: {data.get('is_online')}, Duty: {data.get('duty_on')}"
                )
                return True
            else:
                self.log_result(
                    "Verify Approval",
                    False,
                    f"Driver status is not 'approved': {data.get('approval_status')}",
                    f"Response: {data}"
                )
        else:
            error_msg = response.json() if response else "No response"
            self.log_result(
                "Verify Approval",
                False,
                f"Approval verification failed with status {response.status_code if response else 'None'}",
                f"Error: {error_msg}"
            )
        return False
    
    def test_6_admin_rejects_driver(self):
        """Test 6: ADMIN REJECTS DRIVER (separate test)"""
        print("\n=== TEST 6: ADMIN REJECTS DRIVER ===")
        
        # First register another driver
        driver_data_2 = {
            "phone": "9876543298",
            "full_name": "Test Reject Driver",
            "address": "456 Test Ave, Chennai",
            "driving_license_number": "TN01 2020 0099998",
            "driving_license_image": "data:image/png;base64,test2",
            "vehicle_type": "sedan",
            "vehicle_number": "TN99ZZ9998",
            "rc_book_image": "data:image/png;base64,test2",
            "insurance_details": "Policy 998, Valid 2025"
        }
        
        response = self.make_request("POST", "/driver/register", driver_data_2)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("driver_id"):
                self.driver_id_2 = data.get("driver_id")
                print(f"   Second driver registered with ID: {self.driver_id_2}")
                
                # Now reject this driver
                rejection_data = {
                    "driver_id": self.driver_id_2,
                    "approval_status": "rejected",
                    "rejection_reason": "Incomplete documentation"
                }
                
                response = self.make_request("PUT", "/admin/driver/approve", rejection_data)
                
                if response and response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        # Verify rejection status
                        status_response = self.make_request("GET", f"/driver/{self.driver_id_2}/status")
                        if status_response and status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data.get("approval_status") == "rejected":
                                self.log_result(
                                    "Admin Rejects Driver",
                                    True,
                                    "Driver rejected successfully and status verified",
                                    f"Reason: {status_data.get('rejection_reason')}, Status: {status_data.get('approval_status')}"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Admin Rejects Driver",
                                    False,
                                    f"Driver status not updated to 'rejected': {status_data.get('approval_status')}",
                                    f"Status response: {status_data}"
                                )
                        else:
                            self.log_result(
                                "Admin Rejects Driver",
                                False,
                                "Failed to verify rejection status",
                                "Status check failed after rejection"
                            )
                    else:
                        self.log_result(
                            "Admin Rejects Driver",
                            False,
                            "Rejection response indicates failure",
                            f"Response: {data}"
                        )
                else:
                    error_msg = response.json() if response else "No response"
                    self.log_result(
                        "Admin Rejects Driver",
                        False,
                        f"Driver rejection failed with status {response.status_code if response else 'None'}",
                        f"Error: {error_msg}"
                    )
            else:
                self.log_result(
                    "Admin Rejects Driver",
                    False,
                    "Failed to register second driver for rejection test",
                    f"Registration response: {data}"
                )
        else:
            error_msg = response.json() if response else "No response"
            self.log_result(
                "Admin Rejects Driver",
                False,
                f"Second driver registration failed with status {response.status_code if response else 'None'}",
                f"Error: {error_msg}"
            )
        return False
    
    def run_all_tests(self):
        """Run all driver registration and approval tests"""
        print("🚀 STARTING DRIVER REGISTRATION AND APPROVAL FLOW TESTING")
        print(f"API BASE: {self.base_url}")
        print("=" * 80)
        
        # Run tests in sequence
        test_1_success = self.test_1_new_driver_registration()
        test_2_success = self.test_2_check_driver_status()
        test_3_success = self.test_3_admin_views_drivers()
        test_4_success = self.test_4_admin_approves_driver()
        test_5_success = self.test_5_verify_approval()
        test_6_success = self.test_6_admin_rejects_driver()
        
        # Summary
        print("\n" + "=" * 80)
        print("🏁 DRIVER REGISTRATION AND APPROVAL FLOW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']} - {result['message']}")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"- {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"  Details: {result['details']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = DriverRegistrationApprovalTester()
    passed, failed = tester.run_all_tests()
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Driver Registration and Approval flow is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")