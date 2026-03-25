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
    
    def test_kyc_system(self):
        """Test comprehensive KYC system end-to-end"""
        print("\n=== Testing KYC System End-to-End ===")
        
        # Test 1: Driver KYC Registration with comprehensive data
        try:
            from datetime import date, timedelta
            
            # Future dates for document expiry
            future_date = (date.today() + timedelta(days=365)).isoformat()
            
            kyc_data = {
                "phone": "+919876543299",
                "personal_details": {
                    "full_name": "Arjun Sharma",
                    "mobile_number": "+919876543299",
                    "full_address": "123 MG Road, Bangalore, Karnataka 560001",
                    "aadhaar_number": "123456789012",
                    "pan_number": "ABCDE1234F",
                    "driving_license_number": "KA0520110012345",
                    "driving_experience_years": 5,
                    "driver_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                },
                "bank_details": {
                    "account_holder_name": "Arjun Sharma",
                    "bank_name": "State Bank of India",
                    "account_number": "12345678901234",
                    "ifsc_code": "SBIN0001234",
                    "branch_name": "MG Road Branch"
                },
                "vehicle_details": {
                    "vehicle_type": "sedan",
                    "vehicle_number": "KA01AB1234",
                    "vehicle_model": "Honda City",
                    "vehicle_year": 2020
                },
                "documents": {
                    "aadhaar_card": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                        "back_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "pan_card": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "driving_license": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                        "back_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "rc_book": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "insurance": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "fitness_certificate": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "permit": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    },
                    "pollution_certificate": {
                        "front_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    }
                },
                "document_expiry": {
                    "insurance_expiry": future_date,
                    "fc_expiry": future_date,
                    "permit_expiry": future_date,
                    "pollution_expiry": future_date,
                    "license_expiry": future_date
                },
                "driver_vehicle_photo": {
                    "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                }
            }
            
            response = self.session.post(f"{self.base_url}/driver/register-kyc", json=kyc_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("driver_id"):
                    kyc_driver_id = data["driver_id"]
                    approval_status = data.get("approval_status")
                    self.test_data["kyc_driver_id"] = kyc_driver_id
                    self.log_result("KYC Driver Registration", True, 
                        f"KYC driver registered with ID: {kyc_driver_id}, Status: {approval_status}")
                    
                    # Verify wallet was created with minimum balance requirement
                    wallet_response = self.session.get(f"{self.base_url}/wallet/{kyc_driver_id}")
                    if wallet_response.status_code == 200:
                        wallet_data = wallet_response.json()
                        min_balance = wallet_data.get("wallet", {}).get("minimum_balance_required")
                        if min_balance == 1000.0:
                            self.log_result("KYC Wallet Creation", True, "Wallet created with minimum_balance_required=1000")
                        else:
                            self.log_result("KYC Wallet Creation", False, f"Expected minimum_balance_required=1000, got {min_balance}")
                    else:
                        self.log_result("KYC Wallet Creation", False, "Failed to retrieve wallet")
                else:
                    self.log_result("KYC Driver Registration", False, "Invalid response format", data)
            else:
                self.log_result("KYC Driver Registration", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("KYC Driver Registration", False, f"Exception: {str(e)}")
        
        # Test 2: Test validation errors
        try:
            invalid_kyc_data = {
                "phone": "+919876543298",
                "personal_details": {
                    "full_name": "Test Driver",
                    "mobile_number": "+919876543298",
                    "full_address": "Test Address",
                    "aadhaar_number": "12345",  # Invalid - should be 12 digits
                    "pan_number": "ABC123",     # Invalid - should be 10 chars
                    "driving_license_number": "TEST123",
                    "driving_experience_years": 3,
                    "driver_photo": "data:image/jpeg;base64,test"
                },
                "bank_details": {
                    "account_holder_name": "Test Driver",
                    "bank_name": "Test Bank",
                    "account_number": "123",    # Invalid - too short
                    "ifsc_code": "TEST123",     # Invalid - should be 11 chars
                    "branch_name": "Test Branch"
                },
                "vehicle_details": {
                    "vehicle_type": "sedan",
                    "vehicle_number": "TEST123",
                    "vehicle_model": "Test Car",
                    "vehicle_year": 2020
                },
                "documents": {
                    "aadhaar_card": {"front_image": "test"},
                    "pan_card": {"front_image": "test"},
                    "driving_license": {"front_image": "test"},
                    "rc_book": {"front_image": "test"},
                    "insurance": {"front_image": "test"},
                    "fitness_certificate": {"front_image": "test"},
                    "permit": {"front_image": "test"},
                    "pollution_certificate": {"front_image": "test"}
                },
                "document_expiry": {
                    "insurance_expiry": "2025-12-31",
                    "fc_expiry": "2025-12-31",
                    "permit_expiry": "2025-12-31",
                    "pollution_expiry": "2025-12-31",
                    "license_expiry": "2025-12-31"
                },
                "driver_vehicle_photo": {"photo": "test"}
            }
            
            response = self.session.post(f"{self.base_url}/driver/register-kyc", json=invalid_kyc_data)
            
            if response.status_code == 400:
                self.log_result("KYC Validation Tests", True, "Correctly rejected invalid data")
            else:
                self.log_result("KYC Validation Tests", False, f"Should return 400, got {response.status_code}")
        except Exception as e:
            self.log_result("KYC Validation Tests", False, f"Exception: {str(e)}")
        
        # Test 3: Get pending drivers for verification
        try:
            response = self.session.get(f"{self.base_url}/admin/drivers/pending-verification")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("pending_drivers"), list):
                    pending_count = len(data["pending_drivers"])
                    # Check if our KYC driver is in the list
                    kyc_driver_found = False
                    if "kyc_driver_id" in self.test_data:
                        for driver in data["pending_drivers"]:
                            if driver.get("driver_id") == self.test_data["kyc_driver_id"]:
                                kyc_driver_found = True
                                break
                    
                    if kyc_driver_found:
                        self.log_result("Get Pending Drivers", True, f"Found {pending_count} pending drivers including our KYC driver")
                    else:
                        self.log_result("Get Pending Drivers", True, f"Found {pending_count} pending drivers")
                else:
                    self.log_result("Get Pending Drivers", False, "Invalid response format", data)
            else:
                self.log_result("Get Pending Drivers", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Pending Drivers", False, f"Exception: {str(e)}")
        
        # Test 4: Get driver details for verification
        if "kyc_driver_id" in self.test_data:
            try:
                kyc_driver_id = self.test_data["kyc_driver_id"]
                response = self.session.get(f"{self.base_url}/admin/driver/{kyc_driver_id}/verification-view")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("driver", {}).get("driver_id") == kyc_driver_id:
                        driver_data = data["driver"]
                        has_personal_details = "personal_details" in driver_data
                        has_bank_details = "bank_details" in driver_data
                        has_documents = "documents" in driver_data
                        has_expiry_alerts = "expiry_alerts" in driver_data
                        
                        if all([has_personal_details, has_bank_details, has_documents, has_expiry_alerts]):
                            self.log_result("Get Driver Verification View", True, "Complete driver details retrieved with expiry alerts")
                        else:
                            missing = []
                            if not has_personal_details: missing.append("personal_details")
                            if not has_bank_details: missing.append("bank_details")
                            if not has_documents: missing.append("documents")
                            if not has_expiry_alerts: missing.append("expiry_alerts")
                            self.log_result("Get Driver Verification View", False, f"Missing fields: {missing}")
                    else:
                        self.log_result("Get Driver Verification View", False, "Driver data mismatch", data)
                else:
                    self.log_result("Get Driver Verification View", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Driver Verification View", False, f"Exception: {str(e)}")
        
        # Test 5: Approve driver
        if "kyc_driver_id" in self.test_data:
            try:
                kyc_driver_id = self.test_data["kyc_driver_id"]
                response = self.session.put(f"{self.base_url}/admin/driver/approve", 
                    json={"driver_id": kyc_driver_id, "approval_status": "approved"})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Approve KYC Driver", True, "KYC driver approved successfully")
                        self.test_data["kyc_driver_approved"] = True
                    else:
                        self.log_result("Approve KYC Driver", False, "Approval failed", data)
                else:
                    self.log_result("Approve KYC Driver", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Approve KYC Driver", False, f"Exception: {str(e)}")
        
        # Test 6: Verify driver status changed to approved
        if "kyc_driver_id" in self.test_data and self.test_data.get("kyc_driver_approved"):
            try:
                kyc_driver_id = self.test_data["kyc_driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{kyc_driver_id}/profile-complete")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        driver = data.get("driver", {})
                        approval_status = driver.get("approval_status")
                        if approval_status == "approved":
                            self.log_result("Verify Driver Status Change", True, "Driver status successfully changed to 'approved'")
                        else:
                            self.log_result("Verify Driver Status Change", False, f"Expected 'approved', got '{approval_status}'")
                    else:
                        self.log_result("Verify Driver Status Change", False, "Failed to get driver profile", data)
                else:
                    self.log_result("Verify Driver Status Change", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Verify Driver Status Change", False, f"Exception: {str(e)}")
        
        # Test 7: Get complete driver profile
        if "kyc_driver_id" in self.test_data:
            try:
                kyc_driver_id = self.test_data["kyc_driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{kyc_driver_id}/profile-complete")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("driver"):
                        driver = data["driver"]
                        has_all_sections = all(key in driver for key in [
                            "personal_details", "bank_details", "vehicle_details", 
                            "documents", "document_expiry", "expiry_alerts"
                        ])
                        
                        if has_all_sections:
                            self.log_result("Get Complete Driver Profile", True, "Complete KYC profile retrieved successfully")
                        else:
                            self.log_result("Get Complete Driver Profile", False, "Missing profile sections")
                    else:
                        self.log_result("Get Complete Driver Profile", False, "Invalid response format", data)
                else:
                    self.log_result("Get Complete Driver Profile", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Complete Driver Profile", False, f"Exception: {str(e)}")
        
        # Test 8: Get expiry alerts
        if "kyc_driver_id" in self.test_data:
            try:
                kyc_driver_id = self.test_data["kyc_driver_id"]
                response = self.session.get(f"{self.base_url}/driver/{kyc_driver_id}/expiry-alerts")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "expiry_alerts" in data:
                        alerts = data["expiry_alerts"]
                        has_all_expiries = "all_expiries" in alerts
                        has_critical_alerts = "critical_alerts" in alerts
                        
                        if has_all_expiries and has_critical_alerts:
                            critical_count = len(alerts.get("critical_alerts", []))
                            self.log_result("Get Expiry Alerts", True, f"Expiry alerts retrieved, {critical_count} critical alerts")
                        else:
                            self.log_result("Get Expiry Alerts", False, "Missing expiry alert fields")
                    else:
                        self.log_result("Get Expiry Alerts", False, "Invalid response format", data)
                else:
                    self.log_result("Get Expiry Alerts", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Get Expiry Alerts", False, f"Exception: {str(e)}")
        
        # Test 9: Test auth flow with expiry alerts
        try:
            response = self.session.post(f"{self.base_url}/auth/verify-otp", 
                json={"phone": "+919876543299", "otp": "123456", "role": "driver"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and not data.get("new_user"):
                    user_data = data.get("user", {})
                    has_expiry_alerts = "expiry_alerts" in user_data
                    
                    if has_expiry_alerts:
                        self.log_result("Auth with Expiry Alerts", True, "Driver auth returned expiry alerts")
                    else:
                        self.log_result("Auth with Expiry Alerts", False, "Missing expiry alerts in auth response")
                else:
                    self.log_result("Auth with Expiry Alerts", False, "Should return existing user with expiry alerts", data)
            else:
                self.log_result("Auth with Expiry Alerts", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Auth with Expiry Alerts", False, f"Exception: {str(e)}")

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
        
        # NEW: Test KYC System
        self.test_kyc_system()
        
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