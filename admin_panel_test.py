#!/usr/bin/env python3
"""
VK Drop Taxi - ADMIN PANEL Testing Suite
Tests the critical admin panel functionality as requested:
1. Admin driver approval
2. Admin driver rejection  
3. Admin delete pending driver
4. Admin delete approved driver
5. Admin delete rejected driver
6. Admin wallet add
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "https://ride-dispatch-app.preview.emergentagent.com/api"

class VKDropTaxiAdminTester:
    def __init__(self):
        self.api_base = API_BASE
        self.test_results = []
        self.created_drivers = []
        
    def log_result(self, test_name, success, details):
        """Log test result with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"    Details: {details}")
        print()
    
    def create_test_driver(self, phone_suffix):
        """Helper method to create a test driver"""
        driver_data = {
            "basic_details": {
                "full_name": f"Test Driver {phone_suffix}",
                "phone": f"987654{phone_suffix:04d}",
                "address": "123 Test Road, Bangalore, Karnataka 560001",
                "aadhaar_number": "123456789012",
                "pan_number": "ABCDE1234F",
                "driving_license_number": f"KA032011{phone_suffix:05d}",
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
                    driver_id = data.get("driver_id")
                    self.created_drivers.append(driver_id)
                    return driver_id
        except Exception as e:
            print(f"Failed to create test driver: {str(e)}")
        
        return None
    
    def verify_driver_status(self, driver_id, expected_status):
        """Helper method to verify driver status"""
        try:
            response = requests.get(
                f"{self.api_base}/driver/{driver_id}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    actual_status = data.get("approval_status")
                    return actual_status == expected_status
        except Exception:
            pass
        
        return False
    
    def verify_driver_deleted(self, phone):
        """Helper method to verify driver is deleted by checking phone status"""
        try:
            response = requests.get(
                f"{self.api_base}/driver/phone/{phone}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("status") == "NOT_FOUND" and not data.get("found")
        except Exception:
            pass
        
        return False
    
    def test_admin_driver_approval(self):
        """Test 1: ADMIN DRIVER APPROVAL"""
        print("🔍 TEST 1: ADMIN DRIVER APPROVAL")
        
        # Step 1: Create a new driver
        driver_id = self.create_test_driver(1001)
        if not driver_id:
            self.log_result("Admin Driver Approval", False, "Failed to create test driver")
            return False
        
        # Step 2: Approve the driver
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
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Step 3: Verify status changed to 'approved'
                    if self.verify_driver_status(driver_id, "approved"):
                        self.log_result(
                            "Admin Driver Approval",
                            True,
                            f"Driver {driver_id} successfully approved and status verified"
                        )
                        return True
                    else:
                        self.log_result(
                            "Admin Driver Approval",
                            False,
                            f"Driver approval API succeeded but status verification failed"
                        )
                else:
                    self.log_result(
                        "Admin Driver Approval",
                        False,
                        f"Driver approval failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Admin Driver Approval",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Admin Driver Approval",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_admin_driver_rejection(self):
        """Test 2: ADMIN DRIVER REJECTION"""
        print("🔍 TEST 2: ADMIN DRIVER REJECTION")
        
        # Step 1: Create a new driver
        driver_id = self.create_test_driver(1002)
        if not driver_id:
            self.log_result("Admin Driver Rejection", False, "Failed to create test driver")
            return False
        
        # Step 2: Reject the driver
        try:
            rejection_data = {
                "driver_id": driver_id,
                "approval_status": "rejected",
                "rejection_reason": "Test rejection - Documents not clear"
            }
            
            response = requests.put(
                f"{self.api_base}/admin/driver/approve",
                json=rejection_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Step 3: Verify status changed to 'rejected'
                    if self.verify_driver_status(driver_id, "rejected"):
                        self.log_result(
                            "Admin Driver Rejection",
                            True,
                            f"Driver {driver_id} successfully rejected and status verified"
                        )
                        return True
                    else:
                        self.log_result(
                            "Admin Driver Rejection",
                            False,
                            f"Driver rejection API succeeded but status verification failed"
                        )
                else:
                    self.log_result(
                        "Admin Driver Rejection",
                        False,
                        f"Driver rejection failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Admin Driver Rejection",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Admin Driver Rejection",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_admin_delete_pending_driver(self):
        """Test 3: ADMIN DELETE PENDING DRIVER"""
        print("🔍 TEST 3: ADMIN DELETE PENDING DRIVER")
        
        # Step 1: Create a new driver (will be 'pending' by default)
        driver_id = self.create_test_driver(1003)
        if not driver_id:
            self.log_result("Admin Delete Pending Driver", False, "Failed to create test driver")
            return False
        
        # Get the phone number for verification
        phone = f"98765410{1003:02d}"
        
        # Step 2: Delete the driver
        try:
            response = requests.delete(
                f"{self.api_base}/admin/driver/{driver_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Step 3: Verify driver is deleted
                    if self.verify_driver_deleted(phone):
                        self.log_result(
                            "Admin Delete Pending Driver",
                            True,
                            f"Pending driver {driver_id} successfully deleted and verified"
                        )
                        return True
                    else:
                        self.log_result(
                            "Admin Delete Pending Driver",
                            False,
                            f"Driver deletion API succeeded but verification failed"
                        )
                else:
                    self.log_result(
                        "Admin Delete Pending Driver",
                        False,
                        f"Driver deletion failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Admin Delete Pending Driver",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Admin Delete Pending Driver",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_admin_delete_approved_driver(self):
        """Test 4: ADMIN DELETE APPROVED DRIVER"""
        print("🔍 TEST 4: ADMIN DELETE APPROVED DRIVER")
        
        # Step 1: Create a new driver
        driver_id = self.create_test_driver(1004)
        if not driver_id:
            self.log_result("Admin Delete Approved Driver", False, "Failed to create test driver")
            return False
        
        # Get the phone number for verification
        phone = f"98765410{1004:02d}"
        
        # Step 2: Approve the driver first
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
            
            if response.status_code != 200 or not response.json().get("success"):
                self.log_result("Admin Delete Approved Driver", False, "Failed to approve driver first")
                return False
        except Exception as e:
            self.log_result("Admin Delete Approved Driver", False, f"Failed to approve driver: {str(e)}")
            return False
        
        # Step 3: Delete the approved driver
        try:
            response = requests.delete(
                f"{self.api_base}/admin/driver/{driver_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Step 4: Verify driver is deleted
                    if self.verify_driver_deleted(phone):
                        self.log_result(
                            "Admin Delete Approved Driver",
                            True,
                            f"Approved driver {driver_id} successfully deleted and verified"
                        )
                        return True
                    else:
                        self.log_result(
                            "Admin Delete Approved Driver",
                            False,
                            f"Driver deletion API succeeded but verification failed"
                        )
                else:
                    self.log_result(
                        "Admin Delete Approved Driver",
                        False,
                        f"Driver deletion failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Admin Delete Approved Driver",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Admin Delete Approved Driver",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_admin_delete_rejected_driver(self):
        """Test 5: ADMIN DELETE REJECTED DRIVER"""
        print("🔍 TEST 5: ADMIN DELETE REJECTED DRIVER")
        
        # Step 1: Create a new driver
        driver_id = self.create_test_driver(1005)
        if not driver_id:
            self.log_result("Admin Delete Rejected Driver", False, "Failed to create test driver")
            return False
        
        # Get the phone number for verification
        phone = f"98765410{1005:02d}"
        
        # Step 2: Reject the driver first
        try:
            rejection_data = {
                "driver_id": driver_id,
                "approval_status": "rejected",
                "rejection_reason": "Test rejection for deletion"
            }
            
            response = requests.put(
                f"{self.api_base}/admin/driver/approve",
                json=rejection_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code != 200 or not response.json().get("success"):
                self.log_result("Admin Delete Rejected Driver", False, "Failed to reject driver first")
                return False
        except Exception as e:
            self.log_result("Admin Delete Rejected Driver", False, f"Failed to reject driver: {str(e)}")
            return False
        
        # Step 3: Delete the rejected driver
        try:
            response = requests.delete(
                f"{self.api_base}/admin/driver/{driver_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Step 4: Verify driver is deleted
                    if self.verify_driver_deleted(phone):
                        self.log_result(
                            "Admin Delete Rejected Driver",
                            True,
                            f"Rejected driver {driver_id} successfully deleted and verified"
                        )
                        return True
                    else:
                        self.log_result(
                            "Admin Delete Rejected Driver",
                            False,
                            f"Driver deletion API succeeded but verification failed"
                        )
                else:
                    self.log_result(
                        "Admin Delete Rejected Driver",
                        False,
                        f"Driver deletion failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Admin Delete Rejected Driver",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Admin Delete Rejected Driver",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_admin_wallet_add(self):
        """Test 6: ADMIN WALLET ADD"""
        print("🔍 TEST 6: ADMIN WALLET ADD")
        
        # Step 1: Use an existing driver (create one if needed)
        driver_id = self.create_test_driver(1006)
        if not driver_id:
            self.log_result("Admin Wallet Add", False, "Failed to create test driver")
            return False
        
        # Step 2: Get initial wallet balance
        initial_balance = 0.0
        try:
            response = requests.get(
                f"{self.api_base}/wallet/{driver_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    wallet_data = data.get("wallet", {})
                    initial_balance = wallet_data.get("balance", 0.0)
        except Exception:
            pass  # Continue with initial_balance = 0.0
        
        # Step 3: Add money to wallet
        add_amount = 1500.0
        try:
            wallet_data = {
                "user_id": driver_id,
                "amount": add_amount
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
                    
                    # Step 4: Verify balance increased
                    try:
                        response = requests.get(
                            f"{self.api_base}/wallet/{driver_id}",
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            verify_data = response.json()
                            if verify_data.get("success"):
                                wallet_info = verify_data.get("wallet", {})
                                current_balance = wallet_info.get("balance", 0.0)
                                
                                expected_balance = initial_balance + add_amount
                                if abs(current_balance - expected_balance) < 0.01:  # Allow for floating point precision
                                    self.log_result(
                                        "Admin Wallet Add",
                                        True,
                                        f"Successfully added ₹{add_amount} to driver {driver_id} wallet. Balance: ₹{initial_balance} → ₹{current_balance}"
                                    )
                                    return True
                                else:
                                    self.log_result(
                                        "Admin Wallet Add",
                                        False,
                                        f"Balance verification failed. Expected: ₹{expected_balance}, Actual: ₹{current_balance}"
                                    )
                            else:
                                self.log_result(
                                    "Admin Wallet Add",
                                    False,
                                    f"Wallet balance verification failed: {verify_data.get('message', 'Unknown error')}"
                                )
                        else:
                            self.log_result(
                                "Admin Wallet Add",
                                False,
                                f"Wallet balance verification HTTP error: {response.status_code}"
                            )
                    except Exception as e:
                        self.log_result(
                            "Admin Wallet Add",
                            False,
                            f"Wallet balance verification request failed: {str(e)}"
                        )
                else:
                    self.log_result(
                        "Admin Wallet Add",
                        False,
                        f"Wallet add money failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Admin Wallet Add",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Admin Wallet Add",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def run_all_tests(self):
        """Run all admin panel tests"""
        print("🚀 VK DROP TAXI - ADMIN PANEL TESTING SUITE")
        print("=" * 60)
        print("Testing 6 critical admin panel endpoints:")
        print("1. Admin driver approval")
        print("2. Admin driver rejection")
        print("3. Admin delete pending driver")
        print("4. Admin delete approved driver")
        print("5. Admin delete rejected driver")
        print("6. Admin wallet add")
        print("=" * 60)
        print()
        
        # Run all tests
        test_results = []
        test_results.append(self.test_admin_driver_approval())
        test_results.append(self.test_admin_driver_rejection())
        test_results.append(self.test_admin_delete_pending_driver())
        test_results.append(self.test_admin_delete_approved_driver())
        test_results.append(self.test_admin_delete_rejected_driver())
        test_results.append(self.test_admin_wallet_add())
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 ADMIN PANEL TEST SUMMARY")
        print("=" * 60)
        
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
            print("🆔 CREATED TEST DRIVERS:")
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
            print("🎉 ALL TESTS PASSED! Admin panel functionality is working correctly.")
            print()
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = VKDropTaxiAdminTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)