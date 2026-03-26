#!/usr/bin/env python3
"""
VK Drop Taxi - Driver Reset and Delete Functionality Testing
Tests the specific driver reset and delete functionality as requested.
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "https://ride-dispatch-app.preview.emergentagent.com/api"

class DriverResetDeleteTester:
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
        """Create a test driver for testing purposes"""
        driver_data = {
            "basic_details": {
                "full_name": f"Test Driver {phone_suffix}",
                "phone": f"987654{phone_suffix:04d}",
                "address": "123 Test Road, Bangalore, Karnataka 560001",
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
                "right_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
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
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    driver_id = data.get("driver_id")
                    self.created_drivers.append(driver_id)
                    return driver_id, driver_data["basic_details"]["phone"]
                else:
                    print(f"Driver creation failed: {data.get('message', 'Unknown error')}")
                    return None, None
            else:
                print(f"Driver creation HTTP error: {response.status_code}: {response.text}")
                return None, None
        except Exception as e:
            print(f"Driver creation request failed: {str(e)}")
            return None, None
    
    def approve_driver(self, driver_id):
        """Approve a driver"""
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
                return data.get("success", False)
            else:
                print(f"Driver approval HTTP error: {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Driver approval request failed: {str(e)}")
            return False
    
    def get_driver_status(self, driver_id):
        """Get driver status by ID"""
        try:
            response = requests.get(
                f"{self.api_base}/driver/{driver_id}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("approval_status")
            else:
                print(f"Get driver status HTTP error: {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Get driver status request failed: {str(e)}")
            return None
    
    def get_driver_status_by_phone(self, phone):
        """Get driver status by phone"""
        try:
            response = requests.get(
                f"{self.api_base}/driver/phone/{phone}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("status"), data.get("found", False)
            else:
                print(f"Get driver status by phone HTTP error: {response.status_code}: {response.text}")
                return None, False
        except Exception as e:
            print(f"Get driver status by phone request failed: {str(e)}")
            return None, False
    
    def reset_driver(self, driver_id):
        """Reset driver status from approved back to pending"""
        try:
            response = requests.put(
                f"{self.api_base}/admin/driver/reset/{driver_id}",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                print(f"Reset driver HTTP error: {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Reset driver request failed: {str(e)}")
            return False
    
    def delete_driver(self, driver_id):
        """Delete driver completely"""
        try:
            response = requests.delete(
                f"{self.api_base}/admin/driver/{driver_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                print(f"Delete driver HTTP error: {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Delete driver request failed: {str(e)}")
            return False
    
    def reject_driver(self, driver_id):
        """Reject an approved driver"""
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
                return data.get("success", False)
            else:
                print(f"Reject driver HTTP error: {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Reject driver request failed: {str(e)}")
            return False
    
    def test_reset_driver(self):
        """Test 1: Reset driver functionality"""
        print("🔍 TEST 1: RESET DRIVER FUNCTIONALITY")
        
        # Step 1: Create a new driver
        print("  Step 1: Creating new driver...")
        driver_id, phone = self.create_test_driver(1001)
        if not driver_id:
            self.log_result("Reset Driver Test", False, "Failed to create test driver")
            return False
        
        print(f"    ✅ Driver created: {driver_id}")
        
        # Step 2: Approve the driver
        print("  Step 2: Approving driver...")
        if not self.approve_driver(driver_id):
            self.log_result("Reset Driver Test", False, "Failed to approve driver")
            return False
        
        print(f"    ✅ Driver approved")
        
        # Step 3: Verify driver is approved
        status = self.get_driver_status(driver_id)
        if status != "approved":
            self.log_result("Reset Driver Test", False, f"Driver status is {status}, expected 'approved'")
            return False
        
        print(f"    ✅ Driver status verified as approved")
        
        # Step 4: Reset the driver
        print("  Step 4: Resetting driver status...")
        if not self.reset_driver(driver_id):
            self.log_result("Reset Driver Test", False, "Failed to reset driver status")
            return False
        
        print(f"    ✅ Driver reset successful")
        
        # Step 5: Verify driver status changed to pending
        status = self.get_driver_status(driver_id)
        if status != "pending":
            self.log_result("Reset Driver Test", False, f"Driver status is {status}, expected 'pending' after reset")
            return False
        
        self.log_result("Reset Driver Test", True, f"Driver {driver_id} successfully reset from 'approved' to 'pending'")
        return True
    
    def test_delete_driver(self):
        """Test 2: Delete driver functionality"""
        print("🔍 TEST 2: DELETE DRIVER FUNCTIONALITY")
        
        # Step 1: Create a new driver
        print("  Step 1: Creating new driver...")
        driver_id, phone = self.create_test_driver(1002)
        if not driver_id:
            self.log_result("Delete Driver Test", False, "Failed to create test driver")
            return False
        
        print(f"    ✅ Driver created: {driver_id} with phone {phone}")
        
        # Step 2: Verify driver exists by phone
        status, found = self.get_driver_status_by_phone(phone)
        if not found or status != "PENDING":
            self.log_result("Delete Driver Test", False, f"Driver not found or wrong status: found={found}, status={status}")
            return False
        
        print(f"    ✅ Driver verified to exist with status {status}")
        
        # Step 3: Delete the driver
        print("  Step 3: Deleting driver...")
        if not self.delete_driver(driver_id):
            self.log_result("Delete Driver Test", False, "Failed to delete driver")
            return False
        
        print(f"    ✅ Driver deletion successful")
        
        # Step 4: Verify driver is deleted (should return NOT_FOUND)
        status, found = self.get_driver_status_by_phone(phone)
        if found or status != "NOT_FOUND":
            self.log_result("Delete Driver Test", False, f"Driver still exists after deletion: found={found}, status={status}")
            return False
        
        self.log_result("Delete Driver Test", True, f"Driver {driver_id} successfully deleted and verified as NOT_FOUND")
        return True
    
    def test_reject_approved_driver(self):
        """Test 3: Reject approved driver functionality"""
        print("🔍 TEST 3: REJECT APPROVED DRIVER FUNCTIONALITY")
        
        # Step 1: Create a new driver
        print("  Step 1: Creating new driver...")
        driver_id, phone = self.create_test_driver(1003)
        if not driver_id:
            self.log_result("Reject Approved Driver Test", False, "Failed to create test driver")
            return False
        
        print(f"    ✅ Driver created: {driver_id}")
        
        # Step 2: Approve the driver
        print("  Step 2: Approving driver...")
        if not self.approve_driver(driver_id):
            self.log_result("Reject Approved Driver Test", False, "Failed to approve driver")
            return False
        
        print(f"    ✅ Driver approved")
        
        # Step 3: Verify driver is approved
        status = self.get_driver_status(driver_id)
        if status != "approved":
            self.log_result("Reject Approved Driver Test", False, f"Driver status is {status}, expected 'approved'")
            return False
        
        print(f"    ✅ Driver status verified as approved")
        
        # Step 4: Reject the approved driver
        print("  Step 4: Rejecting approved driver...")
        if not self.reject_driver(driver_id):
            self.log_result("Reject Approved Driver Test", False, "Failed to reject approved driver")
            return False
        
        print(f"    ✅ Driver rejection successful")
        
        # Step 5: Verify driver status changed to rejected
        status = self.get_driver_status(driver_id)
        if status != "rejected":
            self.log_result("Reject Approved Driver Test", False, f"Driver status is {status}, expected 'rejected' after rejection")
            return False
        
        self.log_result("Reject Approved Driver Test", True, f"Driver {driver_id} successfully rejected from 'approved' to 'rejected'")
        return True
    
    def run_all_tests(self):
        """Run all driver reset and delete tests"""
        print("🚀 VK DROP TAXI - DRIVER RESET & DELETE TESTING SUITE")
        print("=" * 70)
        print()
        
        # Test 1: Reset Driver
        test1_result = self.test_reset_driver()
        
        # Test 2: Delete Driver
        test2_result = self.test_delete_driver()
        
        # Test 3: Reject Approved Driver
        test3_result = self.test_reject_approved_driver()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show individual test results
        print("📋 INDIVIDUAL TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status} {result['test']}")
        print()
        
        # Show failed tests details
        failed_results = [result for result in self.test_results if not result['success']]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
            print()
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = DriverResetDeleteTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)