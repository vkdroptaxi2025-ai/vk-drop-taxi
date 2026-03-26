#!/usr/bin/env python3
"""
VK Drop Taxi - Branded ID Testing Suite
Tests the complete VK Drop Taxi system with branded IDs as requested.
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "https://ride-dispatch-app.preview.emergentagent.com/api"

class VKDropTaxiTester:
    def __init__(self):
        self.api_base = API_BASE
        self.test_results = []
        self.created_drivers = []
        self.created_customers = []
        self.created_bookings = []
        
    def log_result(self, test_name, success, details, expected_format=None, actual_id=None):
        """Log test result with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if expected_format:
            result["expected_format"] = expected_format
        if actual_id:
            result["actual_id"] = actual_id
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if actual_id:
            print(f"    Generated ID: {actual_id}")
        print(f"    Details: {details}")
        print()
    
    def test_driver_registration_branded_id(self):
        """Test 1: Register new driver and verify VKDRV branded ID format"""
        print("🔍 TEST 1: DRIVER REGISTRATION WITH BRANDED ID")
        
        # Test data for comprehensive driver onboarding
        driver_data = {
            "basic_details": {
                "full_name": "Rajesh Kumar",
                "phone": "9876543288",
                "address": "123 MG Road, Bangalore, Karnataka 560001",
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
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    driver_id = data.get("driver_id")
                    
                    # Check if driver_id follows VKDRV format
                    if driver_id and driver_id.startswith("VKDRV") and len(driver_id) >= 8:
                        # Extract number part
                        number_part = driver_id[5:]  # Remove "VKDRV" prefix
                        if number_part.isdigit() and int(number_part) >= 1001:
                            self.created_drivers.append(driver_id)
                            self.log_result(
                                "Driver Registration with Branded ID",
                                True,
                                f"Driver registered successfully with branded ID format",
                                "VKDRV1001, VKDRV1002, etc.",
                                driver_id
                            )
                            return driver_id
                        else:
                            self.log_result(
                                "Driver Registration with Branded ID",
                                False,
                                f"Driver ID number part invalid: {number_part}",
                                "VKDRV1001, VKDRV1002, etc.",
                                driver_id
                            )
                    else:
                        self.log_result(
                            "Driver Registration with Branded ID",
                            False,
                            f"Driver ID format incorrect: {driver_id}",
                            "VKDRV1001, VKDRV1002, etc.",
                            driver_id
                        )
                else:
                    self.log_result(
                        "Driver Registration with Branded ID",
                        False,
                        f"Registration failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Driver Registration with Branded ID",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Driver Registration with Branded ID",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_customer_registration_branded_id(self):
        """Test 2: Register new customer and verify VKCST branded ID format"""
        print("🔍 TEST 2: CUSTOMER REGISTRATION WITH BRANDED ID")
        
        customer_data = {
            "phone": "9123456788",
            "name": "Priya Sharma",
            "location": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Koramangala, Bangalore, Karnataka"
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/customer/register",
                json=customer_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user_data = data.get("user", {})
                    customer_id = user_data.get("user_id")
                    
                    # Check if customer_id follows VKCST format
                    if customer_id and customer_id.startswith("VKCST") and len(customer_id) >= 8:
                        # Extract number part
                        number_part = customer_id[5:]  # Remove "VKCST" prefix
                        if number_part.isdigit() and int(number_part) >= 1001:
                            self.created_customers.append(customer_id)
                            self.log_result(
                                "Customer Registration with Branded ID",
                                True,
                                f"Customer registered successfully with branded ID format",
                                "VKCST1001, VKCST1002, etc.",
                                customer_id
                            )
                            return customer_id
                        else:
                            self.log_result(
                                "Customer Registration with Branded ID",
                                False,
                                f"Customer ID number part invalid: {number_part}",
                                "VKCST1001, VKCST1002, etc.",
                                customer_id
                            )
                    else:
                        self.log_result(
                            "Customer Registration with Branded ID",
                            False,
                            f"Customer ID format incorrect: {customer_id}",
                            "VKCST1001, VKCST1002, etc.",
                            customer_id
                        )
                else:
                    self.log_result(
                        "Customer Registration with Branded ID",
                        False,
                        f"Registration failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_result(
                    "Customer Registration with Branded ID",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Customer Registration with Branded ID",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_driver_status_by_phone_not_found(self):
        """Test 3: Check driver status by phone for non-existing phone"""
        print("🔍 TEST 3: DRIVER STATUS BY PHONE - NOT FOUND")
        
        non_existing_phone = "9999999999"
        
        try:
            response = requests.get(
                f"{self.api_base}/driver/phone/{non_existing_phone}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("status") == "NOT_FOUND" and not data.get("found"):
                    self.log_result(
                        "Driver Status by Phone - Not Found",
                        True,
                        f"Correctly returned NOT_FOUND for non-existing phone {non_existing_phone}"
                    )
                    return True
                else:
                    self.log_result(
                        "Driver Status by Phone - Not Found",
                        False,
                        f"Expected NOT_FOUND status, got: {data.get('status')}"
                    )
            else:
                self.log_result(
                    "Driver Status by Phone - Not Found",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Driver Status by Phone - Not Found",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_driver_status_by_phone_pending(self, driver_phone):
        """Test 4: Check driver status by phone for registered driver"""
        print("🔍 TEST 4: DRIVER STATUS BY PHONE - PENDING")
        
        try:
            response = requests.get(
                f"{self.api_base}/driver/phone/{driver_phone}/status",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("found") and data.get("status") == "PENDING":
                    self.log_result(
                        "Driver Status by Phone - Pending",
                        True,
                        f"Correctly returned PENDING status for registered driver {driver_phone}"
                    )
                    return True
                else:
                    self.log_result(
                        "Driver Status by Phone - Pending",
                        False,
                        f"Expected PENDING status, got: {data.get('status')}, found: {data.get('found')}"
                    )
            else:
                self.log_result(
                    "Driver Status by Phone - Pending",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Driver Status by Phone - Pending",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_booking_creation_branded_id(self, customer_id):
        """Test 5: Create booking and verify VKBK branded ID format"""
        print("🔍 TEST 5: BOOKING CREATION WITH BRANDED ID")
        
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Koramangala, Bangalore"
            },
            "drop": {
                "latitude": 12.9352,
                "longitude": 77.6245,
                "address": "Whitefield, Bangalore"
            },
            "vehicle_type": "sedan"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/booking/create-smart",
                json=booking_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    booking_info = data.get("booking", {})
                    booking_id = booking_info.get("booking_id")
                    
                    # Check if booking_id follows VKBK format
                    if booking_id and booking_id.startswith("VKBK") and len(booking_id) >= 7:
                        # Extract number part
                        number_part = booking_id[4:]  # Remove "VKBK" prefix
                        if number_part.isdigit() and int(number_part) >= 1001:
                            self.created_bookings.append(booking_id)
                            self.log_result(
                                "Booking Creation with Branded ID",
                                True,
                                f"Booking created successfully with branded ID format",
                                "VKBK1001, VKBK1002, etc.",
                                booking_id
                            )
                            return booking_id
                        else:
                            self.log_result(
                                "Booking Creation with Branded ID",
                                False,
                                f"Booking ID number part invalid: {number_part}",
                                "VKBK1001, VKBK1002, etc.",
                                booking_id
                            )
                    else:
                        self.log_result(
                            "Booking Creation with Branded ID",
                            False,
                            f"Booking ID format incorrect: {booking_id}",
                            "VKBK1001, VKBK1002, etc.",
                            booking_id
                        )
                else:
                    self.log_result(
                        "Booking Creation with Branded ID",
                        False,
                        f"Booking creation failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                # Handle specific error cases
                if response.status_code == 404:
                    self.log_result(
                        "Booking Creation with Branded ID",
                        False,
                        "No drivers available for booking assignment"
                    )
                else:
                    self.log_result(
                        "Booking Creation with Branded ID",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
        except Exception as e:
            self.log_result(
                "Booking Creation with Branded ID",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_full_flow(self):
        """Test 6: Complete flow - Register driver, approve, create booking, accept"""
        print("🔍 TEST 6: FULL FLOW TEST")
        
        # Step 1: Register a new driver
        print("  Step 1: Registering new driver...")
        driver_data = {
            "basic_details": {
                "full_name": "Suresh Reddy",
                "phone": "9988776699",
                "address": "456 Brigade Road, Bangalore, Karnataka 560025",
                "aadhaar_number": "987654321098",
                "pan_number": "ZYXWV9876E",
                "driving_license_number": "KA0320110098765",
                "driving_experience_years": 8
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
                "vehicle_type": "suv",
                "vehicle_number": "KA02CD5678",
                "vehicle_model": "Mahindra XUV500",
                "vehicle_year": 2019
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
                "amount": 1000,
                "screenshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
            }
        }
        
        flow_driver_id = None
        flow_customer_id = None
        flow_booking_id = None
        
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
                    flow_driver_id = data.get("driver_id")
                    if flow_driver_id and flow_driver_id.startswith("VKDRV"):
                        print(f"    ✅ Driver registered with ID: {flow_driver_id}")
                    else:
                        self.log_result("Full Flow Test", False, "Driver registration failed - invalid ID format")
                        return
                else:
                    self.log_result("Full Flow Test", False, f"Driver registration failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Driver registration HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Driver registration request failed: {str(e)}")
            return
        
        # Step 2: Approve the driver
        print("  Step 2: Approving driver...")
        try:
            approval_data = {
                "driver_id": flow_driver_id,
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
                    print(f"    ✅ Driver approved successfully")
                else:
                    self.log_result("Full Flow Test", False, f"Driver approval failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Driver approval HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Driver approval request failed: {str(e)}")
            return
        
        # Step 3: Add money to driver wallet (minimum ₹1000 required)
        print("  Step 3: Adding money to driver wallet...")
        try:
            wallet_data = {
                "user_id": flow_driver_id,
                "amount": 2000.0
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
                    print(f"    ✅ Wallet topped up with ₹2000")
                else:
                    self.log_result("Full Flow Test", False, f"Wallet top-up failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Wallet top-up HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Wallet top-up request failed: {str(e)}")
            return
        
        # Step 4: Set driver duty ON
        print("  Step 4: Setting driver duty ON...")
        try:
            duty_data = {
                "duty_on": True,
                "go_home_mode": False
            }
            
            response = requests.put(
                f"{self.api_base}/driver/{flow_driver_id}/duty-status",
                json=duty_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"    ✅ Driver duty set to ON")
                else:
                    self.log_result("Full Flow Test", False, f"Driver duty update failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Driver duty update HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Driver duty update request failed: {str(e)}")
            return
        
        # Step 5: Update driver location
        print("  Step 5: Updating driver location...")
        try:
            location_data = {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Koramangala, Bangalore"
            }
            
            response = requests.put(
                f"{self.api_base}/driver/{flow_driver_id}/location",
                json=location_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"    ✅ Driver location updated")
                else:
                    self.log_result("Full Flow Test", False, f"Driver location update failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Driver location update HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Driver location update request failed: {str(e)}")
            return
        
        # Step 6: Register a customer
        print("  Step 6: Registering customer...")
        customer_data = {
            "phone": "9111222399",
            "name": "Anita Gupta",
            "location": {
                "latitude": 12.9352,
                "longitude": 77.6245,
                "address": "Whitefield, Bangalore"
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/customer/register",
                json=customer_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user_data = data.get("user", {})
                    flow_customer_id = user_data.get("user_id")
                    if flow_customer_id and flow_customer_id.startswith("VKCST"):
                        print(f"    ✅ Customer registered with ID: {flow_customer_id}")
                    else:
                        self.log_result("Full Flow Test", False, "Customer registration failed - invalid ID format")
                        return
                else:
                    self.log_result("Full Flow Test", False, f"Customer registration failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Customer registration HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Customer registration request failed: {str(e)}")
            return
        
        # Step 7: Create booking
        print("  Step 7: Creating booking...")
        booking_data = {
            "customer_id": flow_customer_id,
            "pickup": {
                "latitude": 12.9352,
                "longitude": 77.6245,
                "address": "Whitefield, Bangalore"
            },
            "drop": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Koramangala, Bangalore"
            },
            "vehicle_type": "suv"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/booking/create-smart",
                json=booking_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    booking_info = data.get("booking", {})
                    flow_booking_id = booking_info.get("booking_id")
                    if flow_booking_id and flow_booking_id.startswith("VKBK"):
                        print(f"    ✅ Booking created with ID: {flow_booking_id}")
                    else:
                        self.log_result("Full Flow Test", False, "Booking creation failed - invalid ID format")
                        return
                else:
                    self.log_result("Full Flow Test", False, f"Booking creation failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Booking creation HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Booking creation request failed: {str(e)}")
            return
        
        # Step 8: Accept booking
        print("  Step 8: Accepting booking...")
        try:
            accept_data = {
                "booking_id": flow_booking_id,
                "driver_id": flow_driver_id,
                "action": "accept"
            }
            
            response = requests.post(
                f"{self.api_base}/booking/accept-reject",
                json=accept_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"    ✅ Booking accepted successfully")
                    
                    # Full flow completed successfully
                    self.log_result(
                        "Full Flow Test",
                        True,
                        f"Complete flow successful: Driver {flow_driver_id} → Customer {flow_customer_id} → Booking {flow_booking_id} → Accepted"
                    )
                    return True
                else:
                    self.log_result("Full Flow Test", False, f"Booking acceptance failed: {data.get('message')}")
                    return
            else:
                self.log_result("Full Flow Test", False, f"Booking acceptance HTTP error: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Full Flow Test", False, f"Booking acceptance request failed: {str(e)}")
            return
        
        return False
    
    def run_all_tests(self):
        """Run all branded ID tests"""
        print("🚀 VK DROP TAXI - BRANDED ID TESTING SUITE")
        print("=" * 60)
        print()
        
        # Test 1: Driver Registration with Branded ID
        driver_id = self.test_driver_registration_branded_id()
        
        # Test 2: Customer Registration with Branded ID
        customer_id = self.test_customer_registration_branded_id()
        
        # Test 3: Driver Status by Phone - Not Found
        self.test_driver_status_by_phone_not_found()
        
        # Test 4: Driver Status by Phone - Pending (if driver was registered)
        if driver_id:
            self.test_driver_status_by_phone_pending("9876543288")
        
        # Test 5: Booking Creation with Branded ID (if customer was registered)
        if customer_id:
            self.test_booking_creation_branded_id(customer_id)
        
        # Test 6: Full Flow Test
        self.test_full_flow()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show generated IDs
        if self.created_drivers or self.created_customers or self.created_bookings:
            print("🆔 GENERATED BRANDED IDs:")
            if self.created_drivers:
                print(f"   Drivers: {', '.join(self.created_drivers)}")
            if self.created_customers:
                print(f"   Customers: {', '.join(self.created_customers)}")
            if self.created_bookings:
                print(f"   Bookings: {', '.join(self.created_bookings)}")
            print()
        
        # Show failed tests
        failed_results = [result for result in self.test_results if not result['success']]
        if failed_results:
            print("❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
            print()
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = VKDropTaxiTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)