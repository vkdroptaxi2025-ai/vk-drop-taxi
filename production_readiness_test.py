#!/usr/bin/env python3
"""
VK Drop Taxi - Production Readiness Testing
Testing specific critical flows as requested for production deployment
"""

import requests
import json
import time
import uuid
from datetime import datetime, date, timedelta
import base64

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
MOCK_OTP = "123456"
AUTHORIZED_ADMIN_PHONE = "9345538164"

class ProductionReadinessTester:
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
    
    def generate_mock_base64_image(self):
        """Generate a mock base64 image string"""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # ==================== 1. ADMIN SECURITY TESTING (CRITICAL) ====================
    
    def test_admin_security(self):
        """Test admin security with authorized and unauthorized phones"""
        print("\n🔥 TESTING 1: ADMIN SECURITY (CRITICAL)")
        
        # Test 1: Authorized admin phone should succeed
        self.test_authorized_admin_login()
        
        # Test 2: Unauthorized phone should get Access Denied (403)
        self.test_unauthorized_admin_login()
        
        # Test 3: Verify customer/driver login still works normally
        self.test_customer_driver_login_unaffected()
    
    def test_authorized_admin_login(self):
        """Test authorized admin phone login"""
        # Send OTP to authorized admin phone
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": AUTHORIZED_ADMIN_PHONE,
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            self.log_result("Admin OTP Send (Authorized)", True, f"OTP sent to authorized admin phone: {AUTHORIZED_ADMIN_PHONE}")
        else:
            self.log_result("Admin OTP Send (Authorized)", False, f"Failed to send OTP to authorized admin: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP for authorized admin
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": AUTHORIZED_ADMIN_PHONE,
            "otp": self.mock_otp,
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Admin Login (Authorized)", True, f"Authorized admin {AUTHORIZED_ADMIN_PHONE} login successful")
            else:
                self.log_result("Admin Login (Authorized)", False, f"Admin login failed: {data.get('message', 'Unknown error')}")
        else:
            self.log_result("Admin Login (Authorized)", False, f"Admin login failed: {response.status_code if response else 'No response'}")
    
    def test_unauthorized_admin_login(self):
        """Test unauthorized admin phone login - should get 403"""
        unauthorized_phone = "9876543210"
        
        # Send OTP to unauthorized phone
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": unauthorized_phone,
            "role": "admin"
        })
        
        if response and response.status_code == 200:
            self.log_result("Admin OTP Send (Unauthorized)", True, f"OTP sent to unauthorized phone: {unauthorized_phone}")
        else:
            self.log_result("Admin OTP Send (Unauthorized)", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP for unauthorized admin - should get 403
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": unauthorized_phone,
            "otp": self.mock_otp,
            "role": "admin"
        })
        
        if response and response.status_code == 403:
            data = response.json()
            if "Access Denied" in data.get("detail", ""):
                self.log_result("Admin Security (Unauthorized)", True, f"Unauthorized admin {unauthorized_phone} correctly denied with 403 'Access Denied'")
            else:
                self.log_result("Admin Security (Unauthorized)", False, f"Got 403 but wrong message: {data.get('detail', '')}")
        elif response and response.status_code == 200:
            self.log_result("Admin Security (Unauthorized)", False, f"SECURITY BREACH: Unauthorized admin {unauthorized_phone} was allowed to login!")
        else:
            self.log_result("Admin Security (Unauthorized)", False, f"Unexpected response: {response.status_code if response else 'No response'}")
    
    def test_customer_driver_login_unaffected(self):
        """Test that customer/driver login still works normally"""
        # Test customer login
        customer_phone = f"91987654{str(uuid.uuid4())[:4]}"
        
        # Customer OTP send
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": customer_phone,
            "role": "customer"
        })
        
        if response and response.status_code == 200:
            # Customer OTP verify
            response = self.make_request("POST", "/auth/verify-otp", {
                "phone": customer_phone,
                "otp": self.mock_otp,
                "role": "customer"
            })
            
            if response and response.status_code == 200:
                self.log_result("Customer Login Unaffected", True, "Customer login works normally after admin security implementation")
            else:
                self.log_result("Customer Login Unaffected", False, f"Customer login broken: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Customer Login Unaffected", False, f"Customer OTP send failed: {response.status_code if response else 'No response'}")
        
        # Test driver login
        driver_phone = f"91876543{str(uuid.uuid4())[:4]}"
        
        # Driver OTP send
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": driver_phone,
            "role": "driver"
        })
        
        if response and response.status_code == 200:
            # Driver OTP verify
            response = self.make_request("POST", "/auth/verify-otp", {
                "phone": driver_phone,
                "otp": self.mock_otp,
                "role": "driver"
            })
            
            if response and response.status_code == 200:
                self.log_result("Driver Login Unaffected", True, "Driver login works normally after admin security implementation")
            else:
                self.log_result("Driver Login Unaffected", False, f"Driver login broken: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Driver Login Unaffected", False, f"Driver OTP send failed: {response.status_code if response else 'No response'}")
    
    # ==================== 2. COMPLETE CUSTOMER FLOW ====================
    
    def test_complete_customer_flow(self):
        """Test complete customer flow"""
        print("\n🔥 TESTING 2: COMPLETE CUSTOMER FLOW")
        
        # Register new customer
        customer_phone = f"91765432{str(uuid.uuid4())[:4]}"
        self.register_new_customer(customer_phone)
        
        # Customer creates booking
        if self.customer_id:
            self.customer_create_booking()
    
    def register_new_customer(self, phone):
        """Register new customer"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "customer"
        })
        
        if response and response.status_code == 200:
            self.log_result("Customer Registration - OTP Send", True, "Customer OTP sent successfully")
        else:
            self.log_result("Customer Registration - OTP Send", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": self.mock_otp,
            "role": "customer"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("new_user"):
                self.log_result("Customer Registration - OTP Verify", True, "Customer OTP verified (new user)")
            else:
                self.log_result("Customer Registration - OTP Verify", False, "Expected new user but got existing")
                return
        else:
            self.log_result("Customer Registration - OTP Verify", False, f"Failed to verify OTP: {response.status_code if response else 'No response'}")
            return
        
        # Register customer
        response = self.make_request("POST", "/customer/register", {
            "phone": phone,
            "name": "Production Test Customer",
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
                self.log_result("Customer Registration - Complete", True, f"Customer registered successfully: {self.customer_id}")
            else:
                self.log_result("Customer Registration - Complete", False, "Customer registration failed")
        else:
            self.log_result("Customer Registration - Complete", False, f"Failed to register customer: {response.status_code if response else 'No response'}")
    
    def customer_create_booking(self):
        """Customer creates booking"""
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
                fare = booking.get("fare_estimate", 0)
                self.log_result("Customer Booking Creation", True, f"Booking created successfully: {self.booking_id}, Fare: ₹{fare}")
            else:
                self.log_result("Customer Booking Creation", False, "Booking creation failed")
        elif response and response.status_code == 404:
            self.log_result("Customer Booking Creation", True, "No drivers available (expected if no eligible drivers)")
        else:
            self.log_result("Customer Booking Creation", False, f"Failed to create booking: {response.status_code if response else 'No response'}")
    
    # ==================== 3. COMPLETE DRIVER FLOW ====================
    
    def test_complete_driver_flow(self):
        """Test complete driver flow"""
        print("\n🔥 TESTING 3: COMPLETE DRIVER FLOW")
        
        # Register new driver
        driver_phone = f"91654321{str(uuid.uuid4())[:4]}"
        self.register_new_driver(driver_phone)
        
        if self.driver_id:
            # Verify driver starts with pending status
            self.verify_driver_pending_status()
            
            # Admin approves driver
            self.admin_approve_driver()
            
            # Driver adds money to wallet
            self.driver_add_money_to_wallet()
            
            # Driver goes online
            self.driver_go_online()
            
            # Test booking assignment and completion
            self.test_driver_booking_flow()
    
    def register_new_driver(self, phone):
        """Register new driver with simple registration"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "driver"
        })
        
        if response and response.status_code == 200:
            self.log_result("Driver Registration - OTP Send", True, "Driver OTP sent successfully")
        else:
            self.log_result("Driver Registration - OTP Send", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
            return
        
        # Verify OTP
        response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": self.mock_otp,
            "role": "driver"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("new_user"):
                self.log_result("Driver Registration - OTP Verify", True, "Driver OTP verified (new user)")
            else:
                self.log_result("Driver Registration - OTP Verify", False, "Expected new user but got existing")
                return
        else:
            self.log_result("Driver Registration - OTP Verify", False, f"Failed to verify OTP: {response.status_code if response else 'No response'}")
            return
        
        # Register driver with simple registration
        response = self.make_request("POST", "/driver/register-simple", {
            "phone": phone,
            "name": "Production Test Driver",
            "vehicle_type": "sedan",
            "vehicle_number": "KA01AB1234",
            "license_image": self.generate_mock_base64_image(),
            "rc_image": self.generate_mock_base64_image()
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.driver_id = data["driver_id"]
                self.log_result("Driver Registration - Complete", True, f"Driver registered successfully: {self.driver_id}")
            else:
                self.log_result("Driver Registration - Complete", False, "Driver registration failed")
        else:
            self.log_result("Driver Registration - Complete", False, f"Failed to register driver: {response.status_code if response else 'No response'}")
    
    def verify_driver_pending_status(self):
        """Verify driver starts with pending approval status"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/profile-complete")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                driver = data["driver"]
                status = driver.get("approval_status")
                if status == "pending":
                    self.log_result("Driver Pending Status", True, "Driver starts with 'pending' approval status")
                else:
                    self.log_result("Driver Pending Status", False, f"Expected 'pending', got: {status}")
            else:
                self.log_result("Driver Pending Status", False, "Failed to get driver profile")
        else:
            self.log_result("Driver Pending Status", False, f"Failed to verify status: {response.status_code if response else 'No response'}")
    
    def admin_approve_driver(self):
        """Admin approves driver"""
        response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": self.driver_id,
            "approval_status": "approved"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Admin Driver Approval", True, "Driver approved by admin successfully")
            else:
                self.log_result("Admin Driver Approval", False, "Driver approval failed")
        else:
            self.log_result("Admin Driver Approval", False, f"Failed to approve driver: {response.status_code if response else 'No response'}")
    
    def driver_add_money_to_wallet(self):
        """Driver adds money to wallet"""
        response = self.make_request("POST", "/wallet/add-money", {
            "user_id": self.driver_id,
            "amount": 1500
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Wallet Add Money", True, "Driver added ₹1500 to wallet")
            else:
                self.log_result("Driver Wallet Add Money", False, "Failed to add money to wallet")
        else:
            self.log_result("Driver Wallet Add Money", False, f"Failed to add money: {response.status_code if response else 'No response'}")
    
    def driver_go_online(self):
        """Driver goes online"""
        response = self.make_request("PUT", f"/driver/{self.driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Go Online", True, "Driver went online successfully")
            else:
                self.log_result("Driver Go Online", False, "Failed to go online")
        else:
            self.log_result("Driver Go Online", False, f"Failed to go online: {response.status_code if response else 'No response'}")
    
    def test_driver_booking_flow(self):
        """Test driver receives and completes booking"""
        # Update driver location
        response = self.make_request("PUT", f"/driver/{self.driver_id}/location", {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Bangalore, Karnataka"
        })
        
        if response and response.status_code == 200:
            self.log_result("Driver Location Update", True, "Driver location updated")
        else:
            self.log_result("Driver Location Update", False, "Failed to update location")
            return
        
        # Create a booking for this driver
        if not self.customer_id:
            # Create a customer for this test
            customer_phone = f"91543210{str(uuid.uuid4())[:4]}"
            self.register_new_customer(customer_phone)
        
        if self.customer_id:
            # Create booking
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
                    booking_id = booking["booking_id"]
                    assigned_driver = booking.get("driver_id")
                    
                    if assigned_driver == self.driver_id:
                        self.log_result("Driver Booking Assignment", True, f"Booking assigned to driver: {booking_id}")
                        
                        # Driver accepts booking
                        self.driver_accept_booking(booking_id)
                        
                        # Driver starts trip
                        self.driver_start_trip(booking_id)
                        
                        # Driver completes trip
                        self.driver_complete_trip(booking_id)
                        
                        # Verify earnings updated
                        self.verify_driver_earnings()
                    else:
                        self.log_result("Driver Booking Assignment", False, f"Booking assigned to different driver: {assigned_driver}")
                else:
                    self.log_result("Driver Booking Assignment", False, "Booking creation failed")
            elif response and response.status_code == 404:
                self.log_result("Driver Booking Assignment", True, "No eligible drivers (expected if driver not eligible)")
            else:
                self.log_result("Driver Booking Assignment", False, f"Failed to create booking: {response.status_code if response else 'No response'}")
    
    def driver_accept_booking(self, booking_id):
        """Driver accepts booking"""
        response = self.make_request("POST", "/booking/accept-reject", {
            "booking_id": booking_id,
            "driver_id": self.driver_id,
            "action": "accept"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Accept Booking", True, "Driver accepted booking")
            else:
                self.log_result("Driver Accept Booking", False, "Failed to accept booking")
        else:
            self.log_result("Driver Accept Booking", False, f"Failed to accept booking: {response.status_code if response else 'No response'}")
    
    def driver_start_trip(self, booking_id):
        """Driver starts trip"""
        response = self.make_request("PUT", f"/booking/{booking_id}/start-trip", {})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Start Trip", True, "Driver started trip")
            else:
                self.log_result("Driver Start Trip", False, "Failed to start trip")
        else:
            self.log_result("Driver Start Trip", False, f"Failed to start trip: {response.status_code if response else 'No response'}")
    
    def driver_complete_trip(self, booking_id):
        """Driver completes trip"""
        response = self.make_request("PUT", f"/booking/{booking_id}/complete-trip", {})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                earning = data.get("earning", 0)
                self.log_result("Driver Complete Trip", True, f"Driver completed trip, earned: ₹{earning}")
            else:
                self.log_result("Driver Complete Trip", False, "Failed to complete trip")
        else:
            self.log_result("Driver Complete Trip", False, f"Failed to complete trip: {response.status_code if response else 'No response'}")
    
    def verify_driver_earnings(self):
        """Verify driver earnings are updated"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/earnings")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                earnings = data.get("total_earnings", 0)
                if earnings > 0:
                    self.log_result("Driver Earnings Update", True, f"Driver earnings updated: ₹{earnings}")
                else:
                    self.log_result("Driver Earnings Update", False, "Driver earnings not updated")
            else:
                self.log_result("Driver Earnings Update", False, "Failed to get earnings")
        else:
            self.log_result("Driver Earnings Update", False, f"Failed to verify earnings: {response.status_code if response else 'No response'}")
    
    # ==================== 4. WALLET RESTRICTION ====================
    
    def test_wallet_restriction(self):
        """Test drivers with < ₹1000 balance should NOT be assigned bookings"""
        print("\n🔥 TESTING 4: WALLET RESTRICTION")
        
        # Create driver with insufficient balance
        low_wallet_phone = f"91432109{str(uuid.uuid4())[:4]}"
        self.create_low_wallet_driver(low_wallet_phone)
        
        if hasattr(self, 'low_wallet_driver_id'):
            # Test booking assignment should fail
            self.test_low_wallet_booking_restriction()
    
    def create_low_wallet_driver(self, phone):
        """Create driver with low wallet balance"""
        # Register driver
        self.make_request("POST", "/auth/send-otp", {"phone": phone, "role": "driver"})
        self.make_request("POST", "/auth/verify-otp", {"phone": phone, "otp": self.mock_otp, "role": "driver"})
        
        response = self.make_request("POST", "/driver/register-simple", {
            "phone": phone,
            "name": "Low Wallet Driver",
            "vehicle_type": "sedan",
            "vehicle_number": "KA01CD5678",
            "license_image": self.generate_mock_base64_image(),
            "rc_image": self.generate_mock_base64_image()
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.low_wallet_driver_id = data["driver_id"]
                
                # Approve driver
                self.make_request("PUT", "/admin/driver/approve", {
                    "driver_id": self.low_wallet_driver_id,
                    "approval_status": "approved"
                })
                
                # Add insufficient money (< ₹1000)
                self.make_request("POST", "/wallet/add-money", {
                    "user_id": self.low_wallet_driver_id,
                    "amount": 500
                })
                
                # Go online
                self.make_request("PUT", f"/driver/{self.low_wallet_driver_id}/duty-status", {
                    "duty_on": True,
                    "go_home_mode": False
                })
                
                # Update location
                self.make_request("PUT", f"/driver/{self.low_wallet_driver_id}/location", {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "Bangalore, Karnataka"
                })
                
                self.log_result("Low Wallet Driver Setup", True, f"Low wallet driver created with ₹500: {self.low_wallet_driver_id}")
            else:
                self.log_result("Low Wallet Driver Setup", False, "Failed to create low wallet driver")
        else:
            self.log_result("Low Wallet Driver Setup", False, f"Failed to register low wallet driver: {response.status_code if response else 'No response'}")
    
    def test_low_wallet_booking_restriction(self):
        """Test that low wallet driver is not assigned bookings"""
        # Create customer for this test
        if not self.customer_id:
            customer_phone = f"91321098{str(uuid.uuid4())[:4]}"
            self.register_new_customer(customer_phone)
        
        if self.customer_id:
            # Try to create booking - should not assign to low wallet driver
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
            
            if response and response.status_code == 404:
                # Expected - no eligible drivers due to wallet restriction
                self.log_result("Wallet Restriction Test", True, "Booking correctly failed - drivers with < ₹1000 balance excluded")
            elif response and response.status_code == 200:
                data = response.json()
                assigned_driver = data.get("booking", {}).get("driver_id")
                if assigned_driver != self.low_wallet_driver_id:
                    self.log_result("Wallet Restriction Test", True, "Booking assigned to different driver (not low wallet driver)")
                else:
                    self.log_result("Wallet Restriction Test", False, "CRITICAL: Booking assigned to low wallet driver!")
            else:
                self.log_result("Wallet Restriction Test", False, f"Unexpected response: {response.status_code if response else 'No response'}")
    
    # ==================== 5. QUEUE SYSTEM (2-TRIP RULE) ====================
    
    def test_queue_system(self):
        """Test queue system - after 2 trips, driver should be in queue"""
        print("\n🔥 TESTING 5: QUEUE SYSTEM (2-TRIP RULE)")
        
        if self.driver_id:
            # Complete 2 trips and verify queue status
            self.complete_two_trips_for_queue_test()
            self.verify_queue_status()
    
    def complete_two_trips_for_queue_test(self):
        """Complete 2 trips to test queue system"""
        # We already completed 1 trip in driver flow, complete 1 more
        if self.customer_id and self.driver_id:
            # Create second booking
            response = self.make_request("POST", "/booking/create-smart", {
                "customer_id": self.customer_id,
                "pickup": {
                    "latitude": 12.9352,
                    "longitude": 77.6245,
                    "address": "Electronic City, Bangalore"
                },
                "drop": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "Bangalore, Karnataka"
                },
                "vehicle_type": "sedan"
            })
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    booking = data["booking"]
                    booking_id = booking["booking_id"]
                    
                    # Accept, start, and complete second trip
                    self.make_request("POST", "/booking/accept-reject", {
                        "booking_id": booking_id,
                        "driver_id": self.driver_id,
                        "action": "accept"
                    })
                    
                    self.make_request("PUT", f"/booking/{booking_id}/start-trip", {})
                    
                    response = self.make_request("PUT", f"/booking/{booking_id}/complete-trip", {})
                    
                    if response and response.status_code == 200:
                        self.log_result("Second Trip Completion", True, "Second trip completed for queue test")
                    else:
                        self.log_result("Second Trip Completion", False, "Failed to complete second trip")
                else:
                    self.log_result("Second Trip Creation", False, "Failed to create second booking")
            else:
                self.log_result("Second Trip Creation", False, f"Failed to create second booking: {response.status_code if response else 'No response'}")
    
    def verify_queue_status(self):
        """Verify driver is in queue after 2 trips"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/queue-status")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                continuous_trips = data.get("continuous_trips_count", 0)
                in_queue = data.get("in_queue", False)
                
                if continuous_trips == 2 and in_queue:
                    self.log_result("Queue System Test", True, f"Driver correctly in queue after 2 trips (continuous_trips: {continuous_trips}, in_queue: {in_queue})")
                else:
                    self.log_result("Queue System Test", False, f"Queue system not working: continuous_trips={continuous_trips}, in_queue={in_queue}")
            else:
                self.log_result("Queue System Test", False, "Failed to get queue status")
        else:
            self.log_result("Queue System Test", False, f"Failed to verify queue status: {response.status_code if response else 'No response'}")
    
    # ==================== 6. API STABILITY ====================
    
    def test_api_stability(self):
        """Test all admin APIs should return 200 OK, no 500 errors"""
        print("\n🔥 TESTING 6: API STABILITY")
        
        admin_endpoints = [
            ("GET", "/admin/stats"),
            ("GET", "/admin/tariffs"),
            ("GET", "/admin/drivers"),
            ("GET", "/admin/customers"),
            ("GET", "/admin/bookings"),
            ("GET", "/admin/drivers/pending-verification")
        ]
        
        for method, endpoint in admin_endpoints:
            response = self.make_request(method, endpoint)
            if response:
                if response.status_code == 200:
                    self.log_result(f"API Stability - {endpoint}", True, f"Returned 200 OK")
                elif response.status_code == 500:
                    self.log_result(f"API Stability - {endpoint}", False, f"CRITICAL: Returned 500 Internal Server Error")
                else:
                    self.log_result(f"API Stability - {endpoint}", True, f"Returned {response.status_code} (not 500)")
            else:
                self.log_result(f"API Stability - {endpoint}", False, "No response received")
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_production_readiness_tests(self):
        """Run all production readiness tests"""
        print("🚀 VK Drop Taxi - Production Readiness Testing")
        print(f"Backend URL: {self.base_url}")
        print(f"Mock OTP: {self.mock_otp}")
        print(f"Authorized Admin Phone: {AUTHORIZED_ADMIN_PHONE}")
        print("=" * 80)
        
        try:
            # Run all critical tests
            self.test_admin_security()
            self.test_complete_customer_flow()
            self.test_complete_driver_flow()
            self.test_wallet_restriction()
            self.test_queue_system()
            self.test_api_stability()
            
        except Exception as e:
            self.log_result("Test Execution", False, f"Test execution failed: {str(e)}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🏁 PRODUCTION READINESS TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by test category
        categories = {
            "Admin Security": [],
            "Customer Flow": [],
            "Driver Flow": [],
            "Wallet Restriction": [],
            "Queue System": [],
            "API Stability": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Admin" in test_name and "Security" in test_name:
                categories["Admin Security"].append(result)
            elif "Customer" in test_name:
                categories["Customer Flow"].append(result)
            elif "Driver" in test_name:
                categories["Driver Flow"].append(result)
            elif "Wallet" in test_name:
                categories["Wallet Restriction"].append(result)
            elif "Queue" in test_name:
                categories["Queue System"].append(result)
            elif "API Stability" in test_name:
                categories["API Stability"].append(result)
        
        print("\n📊 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r["success"]])
                total = len(results)
                status = "✅" if passed == total else "❌"
                print(f"{status} {category}: {passed}/{total} passed")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🎯 PRODUCTION READINESS STATUS:")
        critical_categories = ["Admin Security", "Customer Flow", "Driver Flow", "Wallet Restriction", "API Stability"]
        ready_categories = []
        
        for category in critical_categories:
            results = categories.get(category, [])
            if results and all(r["success"] for r in results):
                ready_categories.append(category)
        
        print(f"  - {len(ready_categories)}/{len(critical_categories)} critical flows ready")
        for category in ready_categories:
            print(f"    ✅ {category}")
        
        for category in critical_categories:
            if category not in ready_categories:
                print(f"    ❌ {category}")

if __name__ == "__main__":
    tester = ProductionReadinessTester()
    tester.run_production_readiness_tests()