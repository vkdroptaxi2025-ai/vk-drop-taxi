#!/usr/bin/env python3
"""
VK Drop Taxi Backend API Testing Suite
Tests all backend APIs for the taxi booking application
"""

import requests
import json
import uuid
from datetime import datetime
import os

# Get backend URL from frontend env
BACKEND_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

class VKDropTaxiTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_data = {}
        self.results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_auth_apis(self):
        """Test authentication APIs"""
        print("\n=== Testing Auth APIs ===")
        
        # Test 1: Send OTP for customer
        try:
            response = self.session.post(f"{self.base_url}/auth/send-otp", 
                json={"phone": "+919876543210", "role": "customer"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("otp_mock") == "123456":
                    self.log_result("Send OTP (Customer)", True, "Mock OTP 123456 returned")
                else:
                    self.log_result("Send OTP (Customer)", False, "Invalid response format", data)
            else:
                self.log_result("Send OTP (Customer)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Send OTP (Customer)", False, f"Exception: {str(e)}")
        
        # Test 2: Send OTP for driver
        try:
            response = self.session.post(f"{self.base_url}/auth/send-otp", 
                json={"phone": "+919876543211", "role": "driver"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("otp_mock") == "123456":
                    self.log_result("Send OTP (Driver)", True, "Mock OTP 123456 returned")
                else:
                    self.log_result("Send OTP (Driver)", False, "Invalid response format", data)
            else:
                self.log_result("Send OTP (Driver)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Send OTP (Driver)", False, f"Exception: {str(e)}")
        
        # Test 3: Verify OTP for new customer
        try:
            response = self.session.post(f"{self.base_url}/auth/verify-otp", 
                json={"phone": "+919876543210", "otp": "123456", "role": "customer"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("new_user"):
                    self.log_result("Verify OTP (New Customer)", True, "New user detected correctly")
                    self.test_data["customer_phone"] = "+919876543210"
                else:
                    self.log_result("Verify OTP (New Customer)", False, "Should return new_user=True", data)
            else:
                self.log_result("Verify OTP (New Customer)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify OTP (New Customer)", False, f"Exception: {str(e)}")
        
        # Test 4: Verify OTP for new driver
        try:
            response = self.session.post(f"{self.base_url}/auth/verify-otp", 
                json={"phone": "+919876543211", "otp": "123456", "role": "driver"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("new_user"):
                    self.log_result("Verify OTP (New Driver)", True, "New user detected correctly")
                    self.test_data["driver_phone"] = "+919876543211"
                else:
                    self.log_result("Verify OTP (New Driver)", False, "Should return new_user=True", data)
            else:
                self.log_result("Verify OTP (New Driver)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify OTP (New Driver)", False, f"Exception: {str(e)}")
        
        # Test 5: Verify invalid OTP
        try:
            response = self.session.post(f"{self.base_url}/auth/verify-otp", 
                json={"phone": "+919876543210", "otp": "000000", "role": "customer"})
            
            if response.status_code == 400:
                self.log_result("Verify Invalid OTP", True, "Correctly rejected invalid OTP")
            else:
                self.log_result("Verify Invalid OTP", False, f"Should return 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Verify Invalid OTP", False, f"Exception: {str(e)}")
    
    def test_customer_apis(self):
        """Test customer APIs"""
        print("\n=== Testing Customer APIs ===")
        
        # Test 1: Register customer
        try:
            customer_data = {
                "phone": self.test_data.get("customer_phone", "+919876543210"),
                "name": "Rajesh Kumar",
                "location": {
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "address": "Connaught Place, New Delhi"
                }
            }
            
            response = self.session.post(f"{self.base_url}/customer/register", json=customer_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("user", {}).get("user_id"):
                    customer_id = data["user"]["user_id"]
                    self.test_data["customer_id"] = customer_id
                    self.log_result("Customer Registration", True, f"Customer registered with ID: {customer_id}")
                else:
                    self.log_result("Customer Registration", False, "Invalid response format", data)
            else:
                self.log_result("Customer Registration", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Customer Registration", False, f"Exception: {str(e)}")
        
        # Test 2: Get customer profile
        if "customer_id" in self.test_data:
            try:
                customer_id = self.test_data["customer_id"]
                response = self.session.get(f"{self.base_url}/customer/{customer_id}/profile")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("user", {}).get("name") == "Rajesh Kumar":
                        self.log_result("Get Customer Profile", True, "Profile retrieved successfully")
                    else:
                        self.log_result("Get Customer Profile", False, "Profile data mismatch", data)
                else:
                    self.log_result("Get Customer Profile", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Customer Profile", False, f"Exception: {str(e)}")
        
        # Test 3: Get customer bookings (should be empty initially)
        if "customer_id" in self.test_data:
            try:
                customer_id = self.test_data["customer_id"]
                response = self.session.get(f"{self.base_url}/customer/{customer_id}/bookings")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and isinstance(data.get("bookings"), list):
                        self.log_result("Get Customer Bookings", True, f"Retrieved {len(data['bookings'])} bookings")
                    else:
                        self.log_result("Get Customer Bookings", False, "Invalid response format", data)
                else:
                    self.log_result("Get Customer Bookings", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Customer Bookings", False, f"Exception: {str(e)}")
    
    def test_driver_apis(self):
        """Test driver APIs"""
        print("\n=== Testing Driver APIs ===")
        
        # Test 1: Register driver
        try:
            driver_data = {
                "phone": self.test_data.get("driver_phone", "+919876543211"),
                "name": "Suresh Singh",
                "vehicle_type": "sedan",
                "vehicle_number": "DL01AB1234",
                "license_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "rc_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
            }
            
            response = self.session.post(f"{self.base_url}/driver/register", json=driver_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("driver", {}).get("driver_id"):
                    driver_id = data["driver"]["driver_id"]
                    self.test_data["driver_id"] = driver_id
                    approval_status = data["driver"].get("approval_status")
                    self.log_result("Driver Registration", True, f"Driver registered with ID: {driver_id}, Status: {approval_status}")
                else:
                    self.log_result("Driver Registration", False, "Invalid response format", data)
            else:
                self.log_result("Driver Registration", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Driver Registration", False, f"Exception: {str(e)}")
        
        # Test 2: Get driver profile
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{driver_id}/profile")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("driver", {}).get("name") == "Suresh Singh":
                        self.log_result("Get Driver Profile", True, "Profile retrieved successfully")
                    else:
                        self.log_result("Get Driver Profile", False, "Profile data mismatch", data)
                else:
                    self.log_result("Get Driver Profile", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Driver Profile", False, f"Exception: {str(e)}")
        
        # Test 3: Try to set driver online (should fail - not approved yet)
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.put(f"{self.base_url}/driver/{driver_id}/status", 
                    json={"is_online": True})
                
                if response.status_code == 403:
                    self.log_result("Set Driver Online (Unapproved)", True, "Correctly rejected unapproved driver")
                else:
                    self.log_result("Set Driver Online (Unapproved)", False, f"Should return 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Set Driver Online (Unapproved)", False, f"Exception: {str(e)}")
        
        # Test 4: Get driver rides (should be empty)
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{driver_id}/rides")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and isinstance(data.get("rides"), list):
                        self.log_result("Get Driver Rides", True, f"Retrieved {len(data['rides'])} rides")
                    else:
                        self.log_result("Get Driver Rides", False, "Invalid response format", data)
                else:
                    self.log_result("Get Driver Rides", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Driver Rides", False, f"Exception: {str(e)}")
        
        # Test 5: Get pending rides (should be empty)
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{driver_id}/pending-rides")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and isinstance(data.get("pending_rides"), list):
                        self.log_result("Get Pending Rides", True, f"Retrieved {len(data['pending_rides'])} pending rides")
                    else:
                        self.log_result("Get Pending Rides", False, "Invalid response format", data)
                else:
                    self.log_result("Get Pending Rides", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Pending Rides", False, f"Exception: {str(e)}")
        
        # Test 6: Get driver earnings
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{driver_id}/earnings")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "total_earnings" in data:
                        self.log_result("Get Driver Earnings", True, f"Earnings: ₹{data.get('total_earnings', 0)}")
                    else:
                        self.log_result("Get Driver Earnings", False, "Invalid response format", data)
                else:
                    self.log_result("Get Driver Earnings", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Driver Earnings", False, f"Exception: {str(e)}")
    
    def test_admin_apis(self):
        """Test admin APIs"""
        print("\n=== Testing Admin APIs ===")
        
        # Test 1: Get all drivers
        try:
            response = self.session.get(f"{self.base_url}/admin/drivers")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("drivers"), list):
                    drivers_count = len(data["drivers"])
                    self.log_result("Get All Drivers", True, f"Retrieved {drivers_count} drivers")
                else:
                    self.log_result("Get All Drivers", False, "Invalid response format", data)
            else:
                self.log_result("Get All Drivers", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get All Drivers", False, f"Exception: {str(e)}")
        
        # Test 2: Approve driver
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.put(f"{self.base_url}/admin/approve-driver", 
                    json={"driver_id": driver_id, "approval_status": "approved"})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Approve Driver", True, "Driver approved successfully")
                        self.test_data["driver_approved"] = True
                    else:
                        self.log_result("Approve Driver", False, "Approval failed", data)
                else:
                    self.log_result("Approve Driver", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Approve Driver", False, f"Exception: {str(e)}")
        
        # Test 3: Get all customers
        try:
            response = self.session.get(f"{self.base_url}/admin/customers")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("customers"), list):
                    customers_count = len(data["customers"])
                    self.log_result("Get All Customers", True, f"Retrieved {customers_count} customers")
                else:
                    self.log_result("Get All Customers", False, "Invalid response format", data)
            else:
                self.log_result("Get All Customers", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get All Customers", False, f"Exception: {str(e)}")
        
        # Test 4: Get all bookings
        try:
            response = self.session.get(f"{self.base_url}/admin/bookings")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("bookings"), list):
                    bookings_count = len(data["bookings"])
                    self.log_result("Get All Bookings", True, f"Retrieved {bookings_count} bookings")
                else:
                    self.log_result("Get All Bookings", False, "Invalid response format", data)
            else:
                self.log_result("Get All Bookings", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get All Bookings", False, f"Exception: {str(e)}")
        
        # Test 5: Get admin stats
        try:
            response = self.session.get(f"{self.base_url}/admin/stats")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "stats" in data:
                    stats = data["stats"]
                    self.log_result("Get Admin Stats", True, 
                        f"Customers: {stats.get('total_customers')}, Drivers: {stats.get('total_drivers')}, Bookings: {stats.get('total_bookings')}")
                else:
                    self.log_result("Get Admin Stats", False, "Invalid response format", data)
            else:
                self.log_result("Get Admin Stats", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Admin Stats", False, f"Exception: {str(e)}")
        
        # Test 6: Get tariffs
        try:
            response = self.session.get(f"{self.base_url}/admin/tariffs")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("tariffs"), list):
                    tariffs_count = len(data["tariffs"])
                    self.log_result("Get Tariffs", True, f"Retrieved {tariffs_count} tariff settings")
                else:
                    self.log_result("Get Tariffs", False, "Invalid response format", data)
            else:
                self.log_result("Get Tariffs", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Tariffs", False, f"Exception: {str(e)}")
        
        # Test 7: Update tariff
        try:
            response = self.session.put(f"{self.base_url}/admin/update-tariff", 
                json={"vehicle_type": "sedan", "rate_per_km": 15.0, "minimum_fare": 350.0})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Update Tariff", True, "Tariff updated successfully")
                else:
                    self.log_result("Update Tariff", False, "Update failed", data)
            else:
                self.log_result("Update Tariff", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update Tariff", False, f"Exception: {str(e)}")
    
    def test_driver_status_after_approval(self):
        """Test driver status update after approval"""
        print("\n=== Testing Driver Status (Post-Approval) ===")
        
        if "driver_id" in self.test_data and self.test_data.get("driver_approved"):
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.put(f"{self.base_url}/driver/{driver_id}/status", 
                    json={"is_online": True})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("is_online"):
                        self.log_result("Set Driver Online (Approved)", True, "Driver set online successfully")
                        self.test_data["driver_online"] = True
                    else:
                        self.log_result("Set Driver Online (Approved)", False, "Failed to set online", data)
                else:
                    self.log_result("Set Driver Online (Approved)", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Set Driver Online (Approved)", False, f"Exception: {str(e)}")
    
    def test_booking_apis(self):
        """Test booking APIs"""
        print("\n=== Testing Booking APIs ===")
        
        # Test 1: Create booking (requires approved online driver)
        if "customer_id" in self.test_data and self.test_data.get("driver_online"):
            try:
                booking_data = {
                    "customer_id": self.test_data["customer_id"],
                    "pickup": {
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "address": "Connaught Place, New Delhi"
                    },
                    "drop": {
                        "latitude": 28.5355,
                        "longitude": 77.3910,
                        "address": "Noida Sector 18"
                    },
                    "vehicle_type": "sedan"
                }
                
                response = self.session.post(f"{self.base_url}/booking/create", json=booking_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("booking", {}).get("booking_id"):
                        booking_id = data["booking"]["booking_id"]
                        fare = data["booking"].get("fare")
                        distance = data["booking"].get("distance")
                        self.test_data["booking_id"] = booking_id
                        self.log_result("Create Booking", True, 
                            f"Booking created: {booking_id}, Fare: ₹{fare}, Distance: {distance}km")
                    else:
                        self.log_result("Create Booking", False, "Invalid response format", data)
                else:
                    self.log_result("Create Booking", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Create Booking", False, f"Exception: {str(e)}")
        elif not self.test_data.get("driver_online"):
            self.log_result("Create Booking", False, "No online driver available for booking")
        
        # Test 2: Get booking details
        if "booking_id" in self.test_data:
            try:
                booking_id = self.test_data["booking_id"]
                response = self.session.get(f"{self.base_url}/booking/{booking_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("booking", {}).get("booking_id") == booking_id:
                        self.log_result("Get Booking Details", True, "Booking details retrieved successfully")
                    else:
                        self.log_result("Get Booking Details", False, "Booking data mismatch", data)
                else:
                    self.log_result("Get Booking Details", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Booking Details", False, f"Exception: {str(e)}")
        
        # Test 3: Update booking status to accepted
        if "booking_id" in self.test_data:
            try:
                booking_id = self.test_data["booking_id"]
                response = self.session.put(f"{self.base_url}/booking/update", 
                    json={"booking_id": booking_id, "status": "accepted"})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Accept Booking", True, "Booking accepted successfully")
                    else:
                        self.log_result("Accept Booking", False, "Failed to accept booking", data)
                else:
                    self.log_result("Accept Booking", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Accept Booking", False, f"Exception: {str(e)}")
        
        # Test 4: Update booking status to ongoing
        if "booking_id" in self.test_data:
            try:
                booking_id = self.test_data["booking_id"]
                response = self.session.put(f"{self.base_url}/booking/update", 
                    json={"booking_id": booking_id, "status": "ongoing"})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Start Ride", True, "Ride started successfully")
                    else:
                        self.log_result("Start Ride", False, "Failed to start ride", data)
                else:
                    self.log_result("Start Ride", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Start Ride", False, f"Exception: {str(e)}")
        
        # Test 5: Update booking status to completed
        if "booking_id" in self.test_data:
            try:
                booking_id = self.test_data["booking_id"]
                response = self.session.put(f"{self.base_url}/booking/update", 
                    json={"booking_id": booking_id, "status": "completed"})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Complete Ride", True, "Ride completed successfully")
                        self.test_data["ride_completed"] = True
                    else:
                        self.log_result("Complete Ride", False, "Failed to complete ride", data)
                else:
                    self.log_result("Complete Ride", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Complete Ride", False, f"Exception: {str(e)}")
    
    def test_wallet_apis(self):
        """Test wallet APIs"""
        print("\n=== Testing Wallet APIs ===")
        
        # Test 1: Get customer wallet
        if "customer_id" in self.test_data:
            try:
                customer_id = self.test_data["customer_id"]
                response = self.session.get(f"{self.base_url}/wallet/{customer_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "wallet" in data:
                        balance = data["wallet"].get("balance", 0)
                        self.log_result("Get Customer Wallet", True, f"Wallet balance: ₹{balance}")
                    else:
                        self.log_result("Get Customer Wallet", False, "Invalid response format", data)
                else:
                    self.log_result("Get Customer Wallet", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Customer Wallet", False, f"Exception: {str(e)}")
        
        # Test 2: Add money to customer wallet
        if "customer_id" in self.test_data:
            try:
                customer_id = self.test_data["customer_id"]
                response = self.session.post(f"{self.base_url}/wallet/add-money", 
                    json={"user_id": customer_id, "amount": 1000.0})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        new_balance = data.get("new_balance", 0)
                        self.log_result("Add Money to Wallet", True, f"Money added, new balance: ₹{new_balance}")
                    else:
                        self.log_result("Add Money to Wallet", False, "Failed to add money", data)
                else:
                    self.log_result("Add Money to Wallet", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Add Money to Wallet", False, f"Exception: {str(e)}")
        
        # Test 3: Get driver wallet
        if "driver_id" in self.test_data:
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.get(f"{self.base_url}/wallet/{driver_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "wallet" in data:
                        balance = data["wallet"].get("balance", 0)
                        self.log_result("Get Driver Wallet", True, f"Wallet balance: ₹{balance}")
                    else:
                        self.log_result("Get Driver Wallet", False, "Invalid response format", data)
                else:
                    self.log_result("Get Driver Wallet", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Driver Wallet", False, f"Exception: {str(e)}")
        
        # Test 4: Driver withdrawal request (after completing ride)
        if "driver_id" in self.test_data and self.test_data.get("ride_completed"):
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.post(f"{self.base_url}/wallet/withdraw", 
                    json={"driver_id": driver_id, "amount": 100.0})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Driver Withdrawal Request", True, "Withdrawal request submitted")
                    else:
                        self.log_result("Driver Withdrawal Request", False, "Failed to submit withdrawal", data)
                else:
                    self.log_result("Driver Withdrawal Request", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Driver Withdrawal Request", False, f"Exception: {str(e)}")
    
    def test_post_completion_checks(self):
        """Test APIs after ride completion"""
        print("\n=== Testing Post-Completion Checks ===")
        
        # Check updated driver earnings
        if "driver_id" in self.test_data and self.test_data.get("ride_completed"):
            try:
                driver_id = self.test_data["driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{driver_id}/earnings")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        total_earnings = data.get("total_earnings", 0)
                        total_rides = data.get("total_rides", 0)
                        self.log_result("Check Updated Earnings", True, 
                            f"Total rides: {total_rides}, Total earnings: ₹{total_earnings}")
                    else:
                        self.log_result("Check Updated Earnings", False, "Invalid response format", data)
                else:
                    self.log_result("Check Updated Earnings", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Check Updated Earnings", False, f"Exception: {str(e)}")
        
        # Check updated admin stats
        try:
            response = self.session.get(f"{self.base_url}/admin/stats")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "stats" in data:
                    stats = data["stats"]
                    self.log_result("Check Updated Admin Stats", True, 
                        f"Completed bookings: {stats.get('completed_bookings')}, Revenue: ₹{stats.get('total_revenue')}")
                else:
                    self.log_result("Check Updated Admin Stats", False, "Invalid response format", data)
            else:
                self.log_result("Check Updated Admin Stats", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Check Updated Admin Stats", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"🚀 Starting VK Drop Taxi Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in sequence
        self.test_auth_apis()
        self.test_customer_apis()
        self.test_driver_apis()
        self.test_admin_apis()
        self.test_driver_status_after_approval()
        self.test_booking_apis()
        self.test_wallet_apis()
        self.test_post_completion_checks()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        failed = sum(1 for r in self.results if not r["success"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed/total*100,
            "results": self.results
        }

if __name__ == "__main__":
    tester = VKDropTaxiTester()
    results = tester.run_all_tests()