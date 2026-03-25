#!/usr/bin/env python3
"""
VK Drop Taxi - Admin Security & Critical Flow Testing
Focus on NEW admin security feature and comprehensive end-to-end testing
"""

import requests
import json
import time
import uuid
from datetime import datetime, date, timedelta
import base64

# Configuration - Using correct URL from review request
BASE_URL = "http://localhost:8001/api"
MOCK_OTP = "123456"

class VKDropTaxiAdminSecurityTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.mock_otp = MOCK_OTP
        self.test_results = []
        self.customer_id = None
        self.driver_id = None
        self.booking_id = None
        
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
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def generate_mock_base64_image(self):
        """Generate a mock base64 image string"""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # ==================== CRITICAL TEST 1: Admin Security (NEW - MUST TEST) ====================
    
    def test_admin_security(self):
        """Test admin login security restrictions"""
        print("\n🔥 TESTING CRITICAL FLOW 1: Admin Security (NEW - MUST TEST)")
        
        # Test 1: Authorized admin phone (9345538164) + OTP 123456 → Should succeed
        self.test_authorized_admin_login()
        
        # Test 2: Unauthorized phone (9876543210) + OTP 123456 → Should get "Access Denied" (403)
        self.test_unauthorized_admin_login_1()
        
        # Test 3: Another unauthorized phone (1234567890) + OTP 123456 → Should get "Access Denied" (403)
        self.test_unauthorized_admin_login_2()
        
        # Test 4: Verify customer/driver login still works normally
        self.test_customer_login_still_works()
        self.test_driver_login_still_works()
    
    def test_authorized_admin_login(self):
        """Test authorized admin login"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": "9345538164",
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            self.log_result("Admin OTP Send (Authorized)", True, "OTP sent successfully")
        else:
            self.log_result("Admin OTP Send (Authorized)", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP - Should succeed
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": "9345538164",
            "otp": self.mock_otp,
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("user", {}).get("role") == "admin":
                self.log_result("Admin Login (Authorized)", True, "Authorized admin login successful")
            else:
                self.log_result("Admin Login (Authorized)", False, f"Login failed: {data}")
        else:
            self.log_result("Admin Login (Authorized)", False, f"Failed to verify OTP: {response.status_code if response else 'No response'}")
    
    def test_unauthorized_admin_login_1(self):
        """Test unauthorized admin login - phone 9876543210"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": "9876543210",
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            self.log_result("Admin OTP Send (Unauthorized 1)", True, "OTP sent successfully")
        else:
            self.log_result("Admin OTP Send (Unauthorized 1)", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP - Should get 403 Access Denied
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": "9876543210",
            "otp": self.mock_otp,
            "role": "admin"
        })
        
        if response and response.status_code == 403:
            data = response.json()
            if "Access Denied" in data.get("detail", ""):
                self.log_result("Admin Login (Unauthorized 1)", True, "Correctly denied access with 403")
            else:
                self.log_result("Admin Login (Unauthorized 1)", False, f"Wrong error message: {data}")
        else:
            self.log_result("Admin Login (Unauthorized 1)", False, f"Expected 403, got: {response.status_code if response else 'No response'}")
    
    def test_unauthorized_admin_login_2(self):
        """Test unauthorized admin login - phone 1234567890"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": "1234567890",
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            self.log_result("Admin OTP Send (Unauthorized 2)", True, "OTP sent successfully")
        else:
            self.log_result("Admin OTP Send (Unauthorized 2)", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP - Should get 403 Access Denied
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": "1234567890",
            "otp": self.mock_otp,
            "role": "admin"
        })
        
        if response and response.status_code == 403:
            data = response.json()
            if "Access Denied" in data.get("detail", ""):
                self.log_result("Admin Login (Unauthorized 2)", True, "Correctly denied access with 403")
            else:
                self.log_result("Admin Login (Unauthorized 2)", False, f"Wrong error message: {data}")
        else:
            self.log_result("Admin Login (Unauthorized 2)", False, f"Expected 403, got: {response.status_code if response else 'No response'}")
    
    def test_customer_login_still_works(self):
        """Test that customer login still works normally"""
        test_phone = f"91987654{str(uuid.uuid4())[:4]}"
        
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": test_phone,
            "role": "customer"
        })
        
        if response and response.status_code == 200:
            # Verify OTP
            response = self.make_request("POST", "/auth/verify-otp", {
                "phone": test_phone,
                "otp": self.mock_otp,
                "role": "customer"
            })
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("new_user"):
                    self.log_result("Customer Login Still Works", True, "Customer login working normally")
                else:
                    self.log_result("Customer Login Still Works", False, f"Customer login issue: {data}")
            else:
                self.log_result("Customer Login Still Works", False, f"Customer OTP verify failed: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Customer Login Still Works", False, f"Customer OTP send failed: {response.status_code if response else 'No response'}")
    
    def test_driver_login_still_works(self):
        """Test that driver login still works normally"""
        test_phone = f"91876543{str(uuid.uuid4())[:4]}"
        
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": test_phone,
            "role": "driver"
        })
        
        if response and response.status_code == 200:
            # Verify OTP
            response = self.make_request("POST", "/auth/verify-otp", {
                "phone": test_phone,
                "otp": self.mock_otp,
                "role": "driver"
            })
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("new_user"):
                    self.log_result("Driver Login Still Works", True, "Driver login working normally")
                else:
                    self.log_result("Driver Login Still Works", False, f"Driver login issue: {data}")
            else:
                self.log_result("Driver Login Still Works", False, f"Driver OTP verify failed: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Driver Login Still Works", False, f"Driver OTP send failed: {response.status_code if response else 'No response'}")
    
    # ==================== CRITICAL TEST 2: Complete Booking Lifecycle ====================
    
    def test_complete_booking_lifecycle(self):
        """Test complete booking lifecycle as specified in review request"""
        print("\n🔥 TESTING CRITICAL FLOW 2: Complete Booking Lifecycle")
        
        # Step 1: Create customer (POST /api/customer/register)
        self.create_customer_for_booking()
        
        # Step 2: Create driver via simple registration (POST /api/driver/register-simple)
        self.create_driver_simple_registration()
        
        # Step 3: Approve driver (PUT /api/admin/driver/approve)
        self.approve_driver_for_booking()
        
        # Step 4: Add money to driver wallet (POST /api/wallet/{user_id}/add)
        self.add_money_to_driver_wallet()
        
        # Step 5: Set driver duty ON (PUT /api/driver/{id}/duty-status with {"is_on_duty": true})
        self.set_driver_duty_on()
        
        # Step 6: Update driver location (PUT /api/driver/{id}/location)
        self.update_driver_location_for_booking()
        
        # Step 7: Create smart booking (POST /api/booking/create-smart)
        self.create_smart_booking_lifecycle()
        
        # Step 8: Accept booking (POST /api/booking/accept-reject with {"booking_id": "...", "action": "accept"})
        self.accept_booking_lifecycle()
        
        # Step 9: Start trip (PUT /api/booking/{id}/start-trip)
        self.start_trip_lifecycle()
        
        # Step 10: Complete trip (PUT /api/booking/{id}/complete-trip)
        self.complete_trip_lifecycle()
        
        # Step 11: Verify driver earnings updated
        self.verify_driver_earnings_updated()
    
    def create_customer_for_booking(self):
        """Create customer for booking lifecycle test"""
        customer_phone = f"91987654{str(uuid.uuid4())[:4]}"
        
        # Send and verify OTP
        self.make_request("POST", "/auth/send-otp", {"phone": customer_phone, "role": "customer"})
        self.make_request("POST", "/auth/verify-otp", {"phone": customer_phone, "otp": self.mock_otp, "role": "customer"})
        
        # Register customer
        response = self.make_request("POST", "/customer/register", {
            "phone": customer_phone,
            "name": "Booking Test Customer",
            "location": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Bangalore, Karnataka"
            }
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.customer_id = data["user"]["user_id"]
                self.log_result("Customer Creation (Booking)", True, f"Customer created: {self.customer_id}")
            else:
                self.log_result("Customer Creation (Booking)", False, "Customer registration failed")
        else:
            self.log_result("Customer Creation (Booking)", False, f"Failed to create customer: {response.status_code if response else 'No response'}")
    
    def create_driver_simple_registration(self):
        """Create driver via legacy registration"""
        driver_phone = f"91876543{str(uuid.uuid4())[:4]}"
        
        # Send and verify OTP
        self.make_request("POST", "/auth/send-otp", {"phone": driver_phone, "role": "driver"})
        self.make_request("POST", "/auth/verify-otp", {"phone": driver_phone, "otp": self.mock_otp, "role": "driver"})
        
        # Legacy driver registration
        response = self.make_request("POST", "/driver/register", {
            "phone": driver_phone,
            "name": "Booking Test Driver",
            "vehicle_type": "sedan",
            "vehicle_number": "KA01AB1234",
            "license_image": self.generate_mock_base64_image(),
            "rc_image": self.generate_mock_base64_image()
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.driver_id = data["driver"]["driver_id"]
                self.log_result("Driver Legacy Registration", True, f"Driver created: {self.driver_id}")
            else:
                self.log_result("Driver Legacy Registration", False, "Driver registration failed")
        else:
            self.log_result("Driver Legacy Registration", False, f"Failed to create driver: {response.status_code if response else 'No response'}")
    
    def approve_driver_for_booking(self):
        """Approve driver for booking"""
        response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": self.driver_id,
            "approval_status": "approved"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Approval (Booking)", True, "Driver approved successfully")
            else:
                self.log_result("Driver Approval (Booking)", False, "Driver approval failed")
        else:
            self.log_result("Driver Approval (Booking)", False, f"Failed to approve driver: {response.status_code if response else 'No response'}")
    
    def add_money_to_driver_wallet(self):
        """Add money to driver wallet"""
        response = self.make_request("POST", "/wallet/add-money", {
            "user_id": self.driver_id,
            "amount": 1500
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Wallet Add Money (Booking)", True, "Added ₹1500 to driver wallet")
            else:
                self.log_result("Wallet Add Money (Booking)", False, "Failed to add money to wallet")
        else:
            self.log_result("Wallet Add Money (Booking)", False, f"Failed to add money: {response.status_code if response else 'No response'}")
    
    def set_driver_duty_on(self):
        """Set driver duty ON"""
        response = self.make_request("PUT", f"/driver/{self.driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Duty ON (Booking)", True, "Driver duty set to ON")
            else:
                self.log_result("Driver Duty ON (Booking)", False, "Failed to set duty ON")
        else:
            self.log_result("Driver Duty ON (Booking)", False, f"Failed to set duty: {response.status_code if response else 'No response'}")
    
    def update_driver_location_for_booking(self):
        """Update driver location"""
        response = self.make_request("PUT", f"/driver/{self.driver_id}/location", {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Bangalore, Karnataka"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Location Update (Booking)", True, "Driver location updated")
            else:
                self.log_result("Driver Location Update (Booking)", False, "Failed to update location")
        else:
            self.log_result("Driver Location Update (Booking)", False, f"Failed to update location: {response.status_code if response else 'No response'}")
    
    def create_smart_booking_lifecycle(self):
        """Create smart booking"""
        response = self.make_request("POST", "/booking/create-smart", {
            "customer_id": self.customer_id,
            "pickup": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Bangalore, Karnataka"
            },
            "drop": {
                "latitude": 12.9352,
                "longitude": 77.6245,
                "address": "Electronic City, Bangalore"
            },
            "vehicle_type": "sedan"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                booking = data["booking"]
                self.booking_id = booking["booking_id"]
                self.log_result("Smart Booking Creation (Lifecycle)", True, f"Booking created: {self.booking_id}")
            else:
                self.log_result("Smart Booking Creation (Lifecycle)", False, "Failed to create booking")
        else:
            self.log_result("Smart Booking Creation (Lifecycle)", False, f"Failed to create booking: {response.status_code if response else 'No response'}")
    
    def accept_booking_lifecycle(self):
        """Accept booking"""
        response = self.make_request("POST", "/booking/accept-reject", {
            "booking_id": self.booking_id,
            "action": "accept"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Booking Accept (Lifecycle)", True, "Booking accepted successfully")
            else:
                self.log_result("Booking Accept (Lifecycle)", False, "Failed to accept booking")
        else:
            self.log_result("Booking Accept (Lifecycle)", False, f"Failed to accept booking: {response.status_code if response else 'No response'}")
    
    def start_trip_lifecycle(self):
        """Start trip"""
        response = self.make_request("PUT", f"/booking/{self.booking_id}/start-trip", {})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Trip Start (Lifecycle)", True, "Trip started successfully")
            else:
                self.log_result("Trip Start (Lifecycle)", False, "Failed to start trip")
        else:
            self.log_result("Trip Start (Lifecycle)", False, f"Failed to start trip: {response.status_code if response else 'No response'}")
    
    def complete_trip_lifecycle(self):
        """Complete trip"""
        response = self.make_request("PUT", f"/booking/{self.booking_id}/complete-trip", {})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Trip Complete (Lifecycle)", True, f"Trip completed. Earning: ₹{data.get('earning', 0)}")
            else:
                self.log_result("Trip Complete (Lifecycle)", False, "Failed to complete trip")
        else:
            self.log_result("Trip Complete (Lifecycle)", False, f"Failed to complete trip: {response.status_code if response else 'No response'}")
    
    def verify_driver_earnings_updated(self):
        """Verify driver earnings updated"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/earnings")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                earnings = data.get("total_earnings", 0)
                if earnings > 0:
                    self.log_result("Driver Earnings Verification (Lifecycle)", True, f"Driver earnings updated: ₹{earnings}")
                else:
                    self.log_result("Driver Earnings Verification (Lifecycle)", False, "Driver earnings not updated")
            else:
                self.log_result("Driver Earnings Verification (Lifecycle)", False, "Failed to get earnings")
        else:
            self.log_result("Driver Earnings Verification (Lifecycle)", False, f"Failed to verify earnings: {response.status_code if response else 'No response'}")
    
    # ==================== CRITICAL TEST 3: Wallet Restriction ====================
    
    def test_wallet_restriction(self):
        """Test wallet restriction - drivers with balance < ₹1000 should NOT be assigned bookings"""
        print("\n🔥 TESTING CRITICAL FLOW 3: Wallet Restriction")
        
        # Create driver with wallet balance < ₹1000
        self.create_low_wallet_driver()
        
        # Verify they are NOT assigned bookings in smart dispatch
        self.verify_low_wallet_driver_not_assigned()
    
    def create_low_wallet_driver(self):
        """Create driver with low wallet balance"""
        driver_phone = f"91765432{str(uuid.uuid4())[:4]}"
        
        # Create and approve driver
        self.make_request("POST", "/auth/send-otp", {"phone": driver_phone, "role": "driver"})
        self.make_request("POST", "/auth/verify-otp", {"phone": driver_phone, "otp": self.mock_otp, "role": "driver"})
        
        response = self.make_request("POST", "/driver/register-simple", {
            "phone": driver_phone,
            "name": "Low Wallet Driver",
            "vehicle_type": "sedan",
            "vehicle_number": "KA01CD5678",
            "license_image": self.generate_mock_base64_image(),
            "rc_image": self.generate_mock_base64_image()
        })
        
        if response and response.status_code == 200:
            data = response.json()
            self.low_wallet_driver_id = data["driver"]["driver_id"]
            
            # Approve driver
            self.make_request("PUT", "/admin/driver/approve", {
                "driver_id": self.low_wallet_driver_id,
                "approval_status": "approved"
            })
            
            # Set duty ON and location
            self.make_request("PUT", f"/driver/{self.low_wallet_driver_id}/duty-status", {"is_on_duty": True})
            self.make_request("PUT", f"/driver/{self.low_wallet_driver_id}/location", {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Bangalore, Karnataka"
            })
            
            self.log_result("Low Wallet Driver Creation", True, f"Low wallet driver created: {self.low_wallet_driver_id}")
        else:
            self.log_result("Low Wallet Driver Creation", False, "Failed to create low wallet driver")
    
    def verify_low_wallet_driver_not_assigned(self):
        """Verify low wallet driver is not assigned bookings"""
        # Create customer for this test
        customer_phone = f"91654321{str(uuid.uuid4())[:4]}"
        self.make_request("POST", "/auth/send-otp", {"phone": customer_phone, "role": "customer"})
        self.make_request("POST", "/auth/verify-otp", {"phone": customer_phone, "otp": self.mock_otp, "role": "customer"})
        
        response = self.make_request("POST", "/customer/register", {
            "phone": customer_phone,
            "name": "Wallet Test Customer",
            "location": {"latitude": 12.9716, "longitude": 77.5946, "address": "Bangalore"}
        })
        
        if response and response.status_code == 200:
            customer_data = response.json()
            test_customer_id = customer_data["user"]["user_id"]
            
            # Try to create booking
            response = self.make_request("POST", "/booking/create-smart", {
                "customer_id": test_customer_id,
                "pickup": {"latitude": 12.9716, "longitude": 77.5946, "address": "Bangalore"},
                "drop": {"latitude": 12.9352, "longitude": 77.6245, "address": "Electronic City"},
                "vehicle_type": "sedan"
            })
            
            if response and response.status_code == 404:
                # Expected - no eligible drivers
                self.log_result("Wallet Restriction Test", True, "Correctly rejected low wallet driver - no eligible drivers found")
            elif response and response.status_code == 200:
                # Check if assigned to different driver
                data = response.json()
                assigned_driver = data.get("booking", {}).get("driver_id")
                if assigned_driver != self.low_wallet_driver_id:
                    self.log_result("Wallet Restriction Test", True, "Correctly assigned to different driver, not low wallet driver")
                else:
                    self.log_result("Wallet Restriction Test", False, "Incorrectly assigned to low wallet driver")
            else:
                self.log_result("Wallet Restriction Test", False, f"Unexpected response: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Wallet Restriction Test", False, "Failed to create test customer")
    
    # ==================== CRITICAL TEST 4: Queue System (2-trip rule) ====================
    
    def test_queue_system(self):
        """Test queue system - drivers moved to queue after 2 trips"""
        print("\n🔥 TESTING CRITICAL FLOW 4: Queue System (2-trip rule)")
        
        if not self.driver_id:
            self.log_result("Queue System Test", False, "No driver available for queue testing")
            return
        
        # Complete 2 trips with same driver
        self.complete_second_trip_for_queue()
        
        # Verify driver is moved to queue (in_queue: true, continuous_trips_count: 2)
        self.verify_driver_in_queue_after_2_trips()
    
    def complete_second_trip_for_queue(self):
        """Complete a second trip to trigger queue system"""
        # Create another booking
        response = self.make_request("POST", "/booking/create-smart", {
            "customer_id": self.customer_id,
            "pickup": {"latitude": 12.9352, "longitude": 77.6245, "address": "Electronic City"},
            "drop": {"latitude": 12.9716, "longitude": 77.5946, "address": "Bangalore"},
            "vehicle_type": "sedan"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            second_booking_id = data["booking"]["booking_id"]
            
            # Accept, start, and complete second trip
            self.make_request("POST", "/booking/accept-reject", {
                "booking_id": second_booking_id,
                "action": "accept"
            })
            
            self.make_request("PUT", f"/booking/{second_booking_id}/start-trip", {})
            
            response = self.make_request("PUT", f"/booking/{second_booking_id}/complete-trip", {})
            
            if response and response.status_code == 200:
                self.log_result("Second Trip Completion (Queue)", True, "Second trip completed successfully")
            else:
                self.log_result("Second Trip Completion (Queue)", False, "Failed to complete second trip")
        else:
            self.log_result("Second Trip Creation (Queue)", False, "Failed to create second booking")
    
    def verify_driver_in_queue_after_2_trips(self):
        """Verify driver is moved to queue after 2 trips"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/queue-status")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                continuous_trips = data.get("continuous_trips_count", 0)
                in_queue = data.get("in_queue", False)
                
                if continuous_trips == 2 and in_queue:
                    self.log_result("Queue System Verification", True, f"Driver correctly moved to queue: continuous_trips={continuous_trips}, in_queue={in_queue}")
                else:
                    self.log_result("Queue System Verification", False, f"Queue system not working: continuous_trips={continuous_trips}, in_queue={in_queue}")
            else:
                self.log_result("Queue System Verification", False, "Failed to get queue status")
        else:
            self.log_result("Queue System Verification", False, f"Failed to verify queue: {response.status_code if response else 'No response'}")
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all critical tests as specified in review request"""
        print("🚀 Starting VK Drop Taxi Admin Security & Critical Flow Testing")
        print(f"Backend URL: {self.base_url}")
        print(f"Mock OTP: {self.mock_otp}")
        print("=" * 80)
        
        try:
            # Run all critical tests as specified in review request
            self.test_admin_security()
            self.test_complete_booking_lifecycle()
            self.test_wallet_restriction()
            self.test_queue_system()
            
        except Exception as e:
            self.log_result("Test Execution", False, f"Test execution failed: {str(e)}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🏁 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ CRITICAL FLOWS STATUS:")
        flows = {
            "Admin Security": ["Admin Login", "Admin OTP"],
            "Booking Lifecycle": ["Customer Creation", "Driver", "Booking", "Trip"],
            "Wallet Restriction": ["Wallet Restriction"],
            "Queue System": ["Queue"]
        }
        
        for flow_name, keywords in flows.items():
            flow_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in keywords)]
            if flow_tests:
                passed = len([r for r in flow_tests if r["success"]])
                total = len(flow_tests)
                status = "✅" if passed == total else "❌"
                print(f"  {status} {flow_name}: {passed}/{total} tests passed")

if __name__ == "__main__":
    tester = VKDropTaxiAdminSecurityTester()
    tester.run_all_tests()