#!/usr/bin/env python3
"""
VK Drop Taxi - Critical Driver System APIs Testing
Tests the specific critical driver system APIs as requested:
1. Driver Registration (Complete Onboarding) - POST /api/driver/onboard
2. Delete Driver (All Statuses) - DELETE /api/admin/driver/{driver_id}
3. Driver Status Check by Phone - GET /api/driver/phone/{phone}/status
4. Wallet Add Balance - POST /api/wallet/add-money
5. Driver Profile Complete - GET /api/driver/{driver_id}/profile-complete
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "https://ride-dispatch-app.preview.emergentagent.com/api"

class CriticalDriverTester:
    def __init__(self):
        self.api_base = API_BASE
        self.test_results = []
        self.created_drivers = []
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response_data"] = response_data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"    Details: {details}")
        if response_data and isinstance(response_data, dict):
            if 'driver_id' in response_data:
                print(f"    Driver ID: {response_data['driver_id']}")
            if 'approval_status' in response_data:
                print(f"    Status: {response_data['approval_status']}")
        print()
    
    def test_1_driver_registration_complete_onboarding(self):
        """Test 1: POST /api/driver/onboard with comprehensive data"""
        print("🔍 TEST 1: DRIVER REGISTRATION (COMPLETE ONBOARDING)")
        
        # Comprehensive driver onboarding data
        driver_data = {
            "basic_details": {
                "full_name": "Rajesh Kumar Singh",
                "phone": "9876543201",
                "address": "123 MG Road, Bangalore, Karnataka 560001",
                "aadhaar_number": "123456789012",
                "pan_number": "ABCDE1234F",
                "driving_license_number": "KA0320110012345",
                "driving_experience_years": 7
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
                "vehicle_number": "KA01AB1234",
                "vehicle_model": "Maruti Suzuki Dzire",
                "vehicle_year": 2020
            },
            "vehicle_documents": {
                "rc_front": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "rc_back": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "insurance": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "permit": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "pollution_certificate": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
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
        
        try:
            response = requests.post(
                f"{self.api_base}/driver/onboard",
                json=driver_data,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    driver_id = data.get("driver_id")
                    approval_status = data.get("approval_status")
                    
                    # Verify branded driver_id format (VKDRV format)
                    if driver_id and driver_id.startswith("VKDRV") and len(driver_id) >= 8:
                        # Verify approval_status is 'pending'
                        if approval_status == 'pending':
                            self.created_drivers.append(driver_id)
                            self.log_result(
                                "Driver Registration (Complete Onboarding)",
                                True,
                                f"Driver registered successfully with branded ID {driver_id} and approval_status='pending'",
                                {"driver_id": driver_id, "approval_status": approval_status}
                            )
                            return driver_id
                        else:
                            self.log_result(
                                "Driver Registration (Complete Onboarding)",
                                False,
                                f"Expected approval_status='pending', got '{approval_status}'"
                            )
                    else:
                        self.log_result(
                            "Driver Registration (Complete Onboarding)",
                            False,
                            f"Driver ID format incorrect: {driver_id} (expected VKDRV format)"
                        )
                else:
                    self.log_result(
                        "Driver Registration (Complete Onboarding)",
                        False,
                        f"Registration failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Driver Registration (Complete Onboarding)",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_result(
                "Driver Registration (Complete Onboarding)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_2_delete_driver_all_statuses(self):
        """Test 2: DELETE /api/admin/driver/{driver_id} for all statuses"""
        print("🔍 TEST 2: DELETE DRIVER (ALL STATUSES)")
        
        # Test 2a: Delete PENDING driver
        print("  Test 2a: Delete PENDING driver")
        pending_driver_id = self.create_test_driver("9876543202", "Test Driver Pending")
        if pending_driver_id:
            success = self.delete_driver(pending_driver_id, "PENDING")
            if not success:
                return False
        else:
            self.log_result("Delete PENDING Driver", False, "Failed to create test driver")
            return False
        
        # Test 2b: Delete APPROVED driver
        print("  Test 2b: Delete APPROVED driver")
        approved_driver_id = self.create_test_driver("9876543203", "Test Driver Approved")
        if approved_driver_id:
            # First approve the driver
            if self.approve_driver(approved_driver_id):
                success = self.delete_driver(approved_driver_id, "APPROVED")
                if not success:
                    return False
            else:
                self.log_result("Delete APPROVED Driver", False, "Failed to approve test driver")
                return False
        else:
            self.log_result("Delete APPROVED Driver", False, "Failed to create test driver")
            return False
        
        # Test 2c: Delete REJECTED driver
        print("  Test 2c: Delete REJECTED driver")
        rejected_driver_id = self.create_test_driver("9876543204", "Test Driver Rejected")
        if rejected_driver_id:
            # First reject the driver
            if self.reject_driver(rejected_driver_id):
                success = self.delete_driver(rejected_driver_id, "REJECTED")
                if not success:
                    return False
            else:
                self.log_result("Delete REJECTED Driver", False, "Failed to reject test driver")
                return False
        else:
            self.log_result("Delete REJECTED Driver", False, "Failed to create test driver")
            return False
        
        self.log_result(
            "Delete Driver (All Statuses)",
            True,
            "Successfully deleted drivers in all statuses (PENDING, APPROVED, REJECTED)"
        )
        return True
    
    def create_test_driver(self, phone, name):
        """Helper: Create a test driver for deletion tests"""
        driver_data = {
            "basic_details": {
                "full_name": name,
                "phone": phone,
                "address": "Test Address, Bangalore",
                "aadhaar_number": "123456789012",
                "pan_number": "ABCDE1234F",
                "driving_license_number": "KA0320110012345",
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
                "vehicle_number": "KA01TEST123",
                "vehicle_model": "Test Vehicle",
                "vehicle_year": 2020
            },
            "vehicle_documents": {
                "rc_front": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "rc_back": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "insurance": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "permit": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "pollution_certificate": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
            },
            "vehicle_photos": {
                "front_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "back_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "left_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "right_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/driver/onboard",
                json=driver_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("driver_id")
        except Exception as e:
            print(f"    Failed to create test driver: {str(e)}")
        
        return None
    
    def approve_driver(self, driver_id):
        """Helper: Approve a driver"""
        try:
            approval_data = {
                "driver_id": driver_id,
                "approval_status": "approved"
            }
            
            response = requests.put(
                f"{self.api_base}/admin/driver/approve",
                json=approval_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            return response.status_code == 200 and response.json().get("success")
        except:
            return False
    
    def reject_driver(self, driver_id):
        """Helper: Reject a driver"""
        try:
            rejection_data = {
                "driver_id": driver_id,
                "approval_status": "rejected",
                "rejection_reason": "Test rejection"
            }
            
            response = requests.put(
                f"{self.api_base}/admin/driver/approve",
                json=rejection_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            return response.status_code == 200 and response.json().get("success")
        except:
            return False
    
    def delete_driver(self, driver_id, expected_status):
        """Helper: Delete a driver and verify success"""
        try:
            response = requests.delete(
                f"{self.api_base}/admin/driver/{driver_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"    ✅ Successfully deleted {expected_status} driver {driver_id}")
                    return True
                else:
                    print(f"    ❌ Delete failed: {data.get('message')}")
                    return False
            else:
                print(f"    ❌ Delete HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"    ❌ Delete request failed: {str(e)}")
            return False
    
    def test_3_driver_status_by_phone(self):
        """Test 3: GET /api/driver/phone/{phone}/status"""
        print("🔍 TEST 3: DRIVER STATUS CHECK BY PHONE")
        
        # Test 3a: Non-existing phone - should return NOT_FOUND
        print("  Test 3a: Non-existing phone")
        non_existing_phone = "9999999999"
        
        try:
            response = requests.get(
                f"{self.api_base}/driver/phone/{non_existing_phone}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("status") == "NOT_FOUND" and not data.get("found"):
                    print(f"    ✅ Correctly returned NOT_FOUND for phone {non_existing_phone}")
                else:
                    self.log_result(
                        "Driver Status by Phone - Not Found",
                        False,
                        f"Expected NOT_FOUND, got: {data.get('status')}, found: {data.get('found')}"
                    )
                    return False
            else:
                self.log_result(
                    "Driver Status by Phone - Not Found",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Driver Status by Phone - Not Found",
                False,
                f"Request failed: {str(e)}"
            )
            return False
        
        # Test 3b: Existing driver phone - should return their status
        print("  Test 3b: Existing driver phone")
        if self.created_drivers:
            # Use the first created driver
            test_driver_id = self.created_drivers[0]
            test_phone = "9876543201"  # Phone from first test
            
            try:
                response = requests.get(
                    f"{self.api_base}/driver/phone/{test_phone}/status",
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("found"):
                        status = data.get("status")
                        driver_id = data.get("driver_id")
                        
                        if status in ["PENDING", "APPROVED", "REJECTED"] and driver_id == test_driver_id:
                            print(f"    ✅ Correctly returned status {status} for existing driver {driver_id}")
                        else:
                            self.log_result(
                                "Driver Status by Phone - Existing",
                                False,
                                f"Unexpected response: status={status}, driver_id={driver_id}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Driver Status by Phone - Existing",
                            False,
                            f"Expected found=True, got: {data.get('found')}"
                        )
                        return False
                else:
                    self.log_result(
                        "Driver Status by Phone - Existing",
                        False,
                        f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                    return False
            except Exception as e:
                self.log_result(
                    "Driver Status by Phone - Existing",
                    False,
                    f"Request failed: {str(e)}"
                )
                return False
        else:
            print("    ⚠️ No created drivers to test with")
        
        self.log_result(
            "Driver Status Check by Phone",
            True,
            "Both NOT_FOUND and existing driver status checks working correctly"
        )
        return True
    
    def test_4_wallet_add_balance(self):
        """Test 4: POST /api/wallet/add-money"""
        print("🔍 TEST 4: WALLET ADD BALANCE")
        
        if not self.created_drivers:
            self.log_result(
                "Wallet Add Balance",
                False,
                "No created drivers to test wallet with"
            )
            return False
        
        test_driver_id = self.created_drivers[0]
        test_amount = 1500.0
        
        # First, get current wallet balance
        try:
            response = requests.get(
                f"{self.api_base}/wallet/{test_driver_id}",
                timeout=30
            )
            
            initial_balance = 0.0
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    wallet = data.get("wallet", {})
                    initial_balance = wallet.get("balance", 0.0)
                    print(f"    Initial wallet balance: ₹{initial_balance}")
        except Exception as e:
            print(f"    Warning: Could not get initial balance: {str(e)}")
        
        # Add money to wallet
        try:
            wallet_data = {
                "user_id": test_driver_id,
                "amount": test_amount
            }
            
            response = requests.post(
                f"{self.api_base}/wallet/add-money",
                json=wallet_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    new_balance = data.get("new_balance")
                    expected_balance = initial_balance + test_amount
                    
                    if abs(new_balance - expected_balance) < 0.01:  # Allow for floating point precision
                        print(f"    ✅ Successfully added ₹{test_amount}, new balance: ₹{new_balance}")
                        
                        # Verify by getting wallet again
                        try:
                            verify_response = requests.get(
                                f"{self.api_base}/wallet/{test_driver_id}",
                                timeout=30
                            )
                            
                            if verify_response.status_code == 200:
                                verify_data = verify_response.json()
                                if verify_data.get("success"):
                                    wallet = verify_data.get("wallet", {})
                                    actual_balance = wallet.get("balance", 0.0)
                                    
                                    if abs(actual_balance - expected_balance) < 0.01:
                                        self.log_result(
                                            "Wallet Add Balance",
                                            True,
                                            f"Successfully added ₹{test_amount} to wallet. Balance updated from ₹{initial_balance} to ₹{actual_balance}",
                                            {"initial_balance": initial_balance, "amount_added": test_amount, "final_balance": actual_balance}
                                        )
                                        return True
                                    else:
                                        self.log_result(
                                            "Wallet Add Balance",
                                            False,
                                            f"Balance verification failed. Expected ₹{expected_balance}, got ₹{actual_balance}"
                                        )
                                        return False
                        except Exception as e:
                            self.log_result(
                                "Wallet Add Balance",
                                False,
                                f"Balance verification request failed: {str(e)}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Wallet Add Balance",
                            False,
                            f"Balance mismatch. Expected ₹{expected_balance}, got ₹{new_balance}"
                        )
                        return False
                else:
                    self.log_result(
                        "Wallet Add Balance",
                        False,
                        f"Add money failed: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_result(
                    "Wallet Add Balance",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Wallet Add Balance",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_5_driver_profile_complete(self):
        """Test 5: GET /api/driver/{driver_id}/profile-complete"""
        print("🔍 TEST 5: DRIVER PROFILE COMPLETE")
        
        if not self.created_drivers:
            self.log_result(
                "Driver Profile Complete",
                False,
                "No created drivers to test profile with"
            )
            return False
        
        test_driver_id = self.created_drivers[0]
        
        try:
            response = requests.get(
                f"{self.api_base}/driver/{test_driver_id}/profile-complete",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    driver = data.get("driver", {})
                    
                    # Verify essential fields are present
                    required_fields = [
                        "driver_id", "full_name", "phone", "vehicle_type", 
                        "vehicle_number", "approval_status"
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in driver:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        # Check for vehicle info specifically
                        has_vehicle_info = (
                            driver.get("vehicle_type") and 
                            driver.get("vehicle_number") and 
                            driver.get("vehicle_model")
                        )
                        
                        if has_vehicle_info:
                            self.log_result(
                                "Driver Profile Complete",
                                True,
                                f"Successfully retrieved complete driver profile including vehicle info for {test_driver_id}",
                                {
                                    "driver_id": driver.get("driver_id"),
                                    "full_name": driver.get("full_name"),
                                    "vehicle_type": driver.get("vehicle_type"),
                                    "vehicle_number": driver.get("vehicle_number"),
                                    "approval_status": driver.get("approval_status")
                                }
                            )
                            return True
                        else:
                            self.log_result(
                                "Driver Profile Complete",
                                False,
                                "Driver profile missing vehicle information"
                            )
                            return False
                    else:
                        self.log_result(
                            "Driver Profile Complete",
                            False,
                            f"Driver profile missing required fields: {', '.join(missing_fields)}"
                        )
                        return False
                else:
                    self.log_result(
                        "Driver Profile Complete",
                        False,
                        f"Profile retrieval failed: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_result(
                    "Driver Profile Complete",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Driver Profile Complete",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all critical driver system API tests"""
        print("🚀 VK DROP TAXI - CRITICAL DRIVER SYSTEM APIs TESTING")
        print("=" * 70)
        print()
        
        # Test 1: Driver Registration (Complete Onboarding)
        driver_id = self.test_1_driver_registration_complete_onboarding()
        
        # Test 2: Delete Driver (All Statuses)
        self.test_2_delete_driver_all_statuses()
        
        # Test 3: Driver Status Check by Phone
        self.test_3_driver_status_by_phone()
        
        # Test 4: Wallet Add Balance
        self.test_4_wallet_add_balance()
        
        # Test 5: Driver Profile Complete
        self.test_5_driver_profile_complete()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 CRITICAL DRIVER SYSTEM APIs TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show created drivers
        if self.created_drivers:
            print("🆔 CREATED DRIVER IDs:")
            for driver_id in self.created_drivers:
                print(f"   • {driver_id}")
            print()
        
        # Show failed tests
        failed_results = [result for result in self.test_results if not result['success']]
        if failed_results:
            print("❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
            print()
        else:
            print("🎉 ALL CRITICAL DRIVER SYSTEM APIs WORKING PERFECTLY!")
            print()
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = CriticalDriverTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)