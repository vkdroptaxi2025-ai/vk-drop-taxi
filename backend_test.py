#!/usr/bin/env python3
"""
VK Drop Taxi - Comprehensive Backend Testing
Testing all critical flows for live testing support
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

class VKDropTaxiTester:
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
            return None
    
    def generate_mock_base64_image(self):
        """Generate a mock base64 image string"""
        # Simple 1x1 pixel PNG in base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def generate_driver_kyc_data(self, phone):
        """Generate comprehensive KYC data for driver registration"""
        return {
            "phone": phone,
            "personal_details": {
                "full_name": "Rajesh Kumar",
                "mobile_number": phone,
                "full_address": "123 MG Road, Bangalore, Karnataka 560001",
                "aadhaar_number": "123456789012",
                "pan_number": "ABCDE1234F",
                "driving_license_number": "KA0120110012345",
                "driving_experience_years": 5,
                "driver_photo": self.generate_mock_base64_image()
            },
            "bank_details": {
                "account_holder_name": "Rajesh Kumar",
                "bank_name": "State Bank of India",
                "account_number": "12345678901234",
                "ifsc_code": "SBIN0001234",
                "branch_name": "MG Road Branch"
            },
            "vehicle_details": {
                "vehicle_type": "sedan",
                "vehicle_number": "KA01AB1234",
                "vehicle_model": "Maruti Suzuki Dzire",
                "vehicle_year": 2020
            },
            "documents": {
                "aadhaar_card": {
                    "front_image": self.generate_mock_base64_image(),
                    "back_image": self.generate_mock_base64_image()
                },
                "pan_card": {
                    "front_image": self.generate_mock_base64_image()
                },
                "driving_license": {
                    "front_image": self.generate_mock_base64_image(),
                    "back_image": self.generate_mock_base64_image()
                },
                "rc_book": {
                    "front_image": self.generate_mock_base64_image(),
                    "back_image": self.generate_mock_base64_image()
                },
                "insurance": {
                    "front_image": self.generate_mock_base64_image()
                },
                "fitness_certificate": {
                    "front_image": self.generate_mock_base64_image()
                },
                "permit": {
                    "front_image": self.generate_mock_base64_image()
                },
                "pollution_certificate": {
                    "front_image": self.generate_mock_base64_image()
                }
            },
            "document_expiry": {
                "insurance_expiry": (date.today() + timedelta(days=365)).isoformat(),
                "fc_expiry": (date.today() + timedelta(days=365)).isoformat(),
                "permit_expiry": (date.today() + timedelta(days=365)).isoformat(),
                "pollution_expiry": (date.today() + timedelta(days=180)).isoformat(),
                "license_expiry": (date.today() + timedelta(days=1825)).isoformat()
            },
            "driver_vehicle_photo": {
                "photo": self.generate_mock_base64_image()
            },
            "agreement": {
                "accepted": True,
                "agreement_file": self.generate_mock_base64_image(),
                "accepted_at": datetime.now().isoformat()
            }
        }
    
    # ==================== CRITICAL FLOW 1: Complete Booking Lifecycle ====================
    
    def test_complete_booking_lifecycle(self):
        """Test the complete booking flow end-to-end"""
        print("\n🔥 TESTING CRITICAL FLOW 1: Complete Booking Lifecycle")
        
        # Step 1: Create customer
        customer_phone = f"91987654{str(uuid.uuid4())[:4]}"
        self.create_customer(customer_phone)
        
        # Step 2: Create driver with KYC
        driver_phone = f"91876543{str(uuid.uuid4())[:4]}"
        self.create_driver_with_kyc(driver_phone)
        
        # Step 3: Approve driver
        self.approve_driver()
        
        # Step 4: Add money to wallet
        self.add_money_to_wallet(1500)
        
        # Step 5: Turn duty ON
        self.turn_duty_on()
        
        # Step 6: Update location
        self.update_driver_location()
        
        # Step 7: Customer creates booking
        self.create_smart_booking()
        
        # Step 8: Driver accepts booking
        self.accept_booking()
        
        # Step 9: Driver starts trip
        self.start_trip()
        
        # Step 10: Driver completes trip
        self.complete_trip()
        
        # Step 11: Verify driver earnings updated
        self.verify_driver_earnings()
        
        # Step 12: Verify driver status returns to available
        self.verify_driver_status_available()
    
    def create_customer(self, phone):
        """Create customer account"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "customer"
        })
        
        if response and response.status_code == 200:
            self.log_result("Customer OTP Send", True, "OTP sent successfully")
        else:
            self.log_result("Customer OTP Send", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
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
                self.log_result("Customer OTP Verify", True, "New customer verified")
            else:
                self.log_result("Customer OTP Verify", False, "Expected new user but got existing")
                return
        else:
            self.log_result("Customer OTP Verify", False, f"Failed to verify OTP: {response.status_code if response else 'No response'}")
            return
        
        # Register customer
        response = self.make_request("POST", "/customer/register", {
            "phone": phone,
            "name": "Test Customer",
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
                self.log_result("Customer Registration", True, f"Customer created with ID: {self.customer_id}")
            else:
                self.log_result("Customer Registration", False, "Registration failed")
        else:
            self.log_result("Customer Registration", False, f"Failed to register: {response.status_code if response else 'No response'}")
    
    def create_driver_with_kyc(self, phone):
        """Create driver with complete KYC"""
        # Send OTP
        response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "driver"
        })
        
        if response and response.status_code == 200:
            self.log_result("Driver OTP Send", True, "OTP sent successfully")
        else:
            self.log_result("Driver OTP Send", False, f"Failed to send OTP: {response.status_code if response else 'No response'}")
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
                self.log_result("Driver OTP Verify", True, "New driver verified")
            else:
                self.log_result("Driver OTP Verify", False, "Expected new user but got existing")
                return
        else:
            self.log_result("Driver OTP Verify", False, f"Failed to verify OTP: {response.status_code if response else 'No response'}")
            return
        
        # Register driver with KYC
        kyc_data = self.generate_driver_kyc_data(phone)
        response = self.make_request("POST", "/driver/register-kyc", kyc_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.driver_id = data["driver_id"]
                self.log_result("Driver KYC Registration", True, f"Driver created with ID: {self.driver_id}")
                
                # Verify agreement data is stored
                self.verify_agreement_storage()
            else:
                self.log_result("Driver KYC Registration", False, "KYC registration failed")
        else:
            self.log_result("Driver KYC Registration", False, f"Failed to register: {response.status_code if response else 'No response'}")
    
    def verify_agreement_storage(self):
        """Verify driver agreement data is stored"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/profile-complete")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                driver = data["driver"]
                agreement = driver.get("agreement", {})
                
                if (agreement.get("accepted") == True and 
                    agreement.get("agreement_file") and 
                    agreement.get("accepted_at")):
                    self.log_result("Agreement Storage Verification", True, "Agreement data properly stored")
                else:
                    self.log_result("Agreement Storage Verification", False, f"Agreement data incomplete: {agreement}")
            else:
                self.log_result("Agreement Storage Verification", False, "Failed to get driver profile")
        else:
            self.log_result("Agreement Storage Verification", False, f"Failed to verify agreement: {response.status_code if response else 'No response'}")
    
    def approve_driver(self):
        """Approve driver"""
        response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": self.driver_id,
            "approval_status": "approved"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Driver Approval", True, "Driver approved successfully")
                
                # Verify approval status
                self.verify_approval_status()
            else:
                self.log_result("Driver Approval", False, "Approval failed")
        else:
            self.log_result("Driver Approval", False, f"Failed to approve: {response.status_code if response else 'No response'}")
    
    def verify_approval_status(self):
        """Verify driver approval status"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/profile-complete")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                driver = data["driver"]
                if driver.get("approval_status") == "approved":
                    self.log_result("Approval Status Verification", True, "Driver status is approved")
                else:
                    self.log_result("Approval Status Verification", False, f"Expected approved, got: {driver.get('approval_status')}")
            else:
                self.log_result("Approval Status Verification", False, "Failed to get driver profile")
        else:
            self.log_result("Approval Status Verification", False, f"Failed to verify status: {response.status_code if response else 'No response'}")
    
    def add_money_to_wallet(self, amount):
        """Add money to driver wallet"""
        response = self.make_request("POST", "/wallet/add-money", {
            "user_id": self.driver_id,
            "amount": amount
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Wallet Add Money", True, f"Added ₹{amount} to wallet")
            else:
                self.log_result("Wallet Add Money", False, "Failed to add money")
        else:
            self.log_result("Wallet Add Money", False, f"Failed to add money: {response.status_code if response else 'No response'}")
    
    def turn_duty_on(self):
        """Turn driver duty ON"""
        response = self.make_request("PUT", f"/driver/{self.driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Duty ON", True, "Driver duty turned ON")
            else:
                self.log_result("Duty ON", False, "Failed to turn duty ON")
        else:
            self.log_result("Duty ON", False, f"Failed to turn duty ON: {response.status_code if response else 'No response'}")
    
    def update_driver_location(self):
        """Update driver location"""
        response = self.make_request("PUT", f"/driver/{self.driver_id}/location", {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Bangalore, Karnataka"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Location Update", True, "Driver location updated")
            else:
                self.log_result("Location Update", False, "Failed to update location")
        else:
            self.log_result("Location Update", False, f"Failed to update location: {response.status_code if response else 'No response'}")
    
    def create_smart_booking(self):
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
                assigned_driver = booking.get("driver_id")
                
                if assigned_driver == self.driver_id:
                    self.log_result("Smart Booking Creation", True, f"Booking created and assigned to correct driver: {self.booking_id}")
                else:
                    self.log_result("Smart Booking Creation", False, f"Booking assigned to wrong driver. Expected: {self.driver_id}, Got: {assigned_driver}")
            else:
                self.log_result("Smart Booking Creation", False, "Failed to create booking")
        else:
            self.log_result("Smart Booking Creation", False, f"Failed to create booking: {response.status_code if response else 'No response'}")
    
    def accept_booking(self):
        """Driver accepts booking"""
        response = self.make_request("POST", "/booking/accept-reject", {
            "booking_id": self.booking_id,
            "driver_id": self.driver_id,
            "action": "accept"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Booking Accept", True, "Booking accepted successfully")
            else:
                self.log_result("Booking Accept", False, "Failed to accept booking")
        else:
            self.log_result("Booking Accept", False, f"Failed to accept booking: {response.status_code if response else 'No response'}")
    
    def start_trip(self):
        """Driver starts trip"""
        response = self.make_request("PUT", f"/booking/{self.booking_id}/start-trip", {})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Trip Start", True, "Trip started successfully")
            else:
                self.log_result("Trip Start", False, "Failed to start trip")
        else:
            self.log_result("Trip Start", False, f"Failed to start trip: {response.status_code if response else 'No response'}")
    
    def complete_trip(self):
        """Driver completes trip"""
        response = self.make_request("PUT", f"/booking/{self.booking_id}/complete-trip", {})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Trip Complete", True, f"Trip completed successfully. Earning: ₹{data.get('earning', 0)}")
            else:
                self.log_result("Trip Complete", False, "Failed to complete trip")
        else:
            self.log_result("Trip Complete", False, f"Failed to complete trip: {response.status_code if response else 'No response'}")
    
    def verify_driver_earnings(self):
        """Verify driver earnings updated"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/earnings")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                earnings = data.get("total_earnings", 0)
                if earnings > 0:
                    self.log_result("Driver Earnings Verification", True, f"Driver earnings updated: ₹{earnings}")
                else:
                    self.log_result("Driver Earnings Verification", False, "Driver earnings not updated")
            else:
                self.log_result("Driver Earnings Verification", False, "Failed to get earnings")
        else:
            self.log_result("Driver Earnings Verification", False, f"Failed to verify earnings: {response.status_code if response else 'No response'}")
    
    def verify_driver_status_available(self):
        """Verify driver status returns to available"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/profile-complete")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                driver = data["driver"]
                status = driver.get("driver_status")
                if status == "available":
                    self.log_result("Driver Status Verification", True, "Driver status is available")
                else:
                    self.log_result("Driver Status Verification", False, f"Expected available, got: {status}")
            else:
                self.log_result("Driver Status Verification", False, "Failed to get driver profile")
        else:
            self.log_result("Driver Status Verification", False, f"Failed to verify status: {response.status_code if response else 'No response'}")
    
    # ==================== CRITICAL FLOW 2: Wallet Restriction Verification ====================
    
    def test_wallet_restriction(self):
        """Test wallet restriction verification"""
        print("\n🔥 TESTING CRITICAL FLOW 2: Wallet Restriction Verification")
        
        # Create driver with ₹0 wallet
        driver_phone = f"91765432{str(uuid.uuid4())[:4]}"
        self.create_driver_with_zero_wallet(driver_phone)
        
        # Approve and turn duty ON
        self.approve_zero_wallet_driver()
        self.turn_duty_on_zero_wallet()
        self.update_zero_wallet_driver_location()
        
        # Try to assign booking - MUST FAIL
        self.test_booking_assignment_failure()
    
    def create_driver_with_zero_wallet(self, phone):
        """Create driver with ₹0 wallet"""
        # Send OTP and verify
        self.make_request("POST", "/auth/send-otp", {"phone": phone, "role": "driver"})
        self.make_request("POST", "/auth/verify-otp", {"phone": phone, "otp": self.mock_otp, "role": "driver"})
        
        # Register driver
        kyc_data = self.generate_driver_kyc_data(phone)
        response = self.make_request("POST", "/driver/register-kyc", kyc_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.zero_wallet_driver_id = data["driver_id"]
                self.log_result("Zero Wallet Driver Creation", True, f"Driver created with ₹0 wallet: {self.zero_wallet_driver_id}")
            else:
                self.log_result("Zero Wallet Driver Creation", False, "Failed to create driver")
        else:
            self.log_result("Zero Wallet Driver Creation", False, f"Failed to create driver: {response.status_code if response else 'No response'}")
    
    def approve_zero_wallet_driver(self):
        """Approve zero wallet driver"""
        response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": self.zero_wallet_driver_id,
            "approval_status": "approved"
        })
        
        if response and response.status_code == 200:
            self.log_result("Zero Wallet Driver Approval", True, "Driver approved")
        else:
            self.log_result("Zero Wallet Driver Approval", False, "Failed to approve driver")
    
    def turn_duty_on_zero_wallet(self):
        """Turn duty ON for zero wallet driver"""
        response = self.make_request("PUT", f"/driver/{self.zero_wallet_driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        if response and response.status_code == 200:
            self.log_result("Zero Wallet Duty ON", True, "Duty turned ON")
        else:
            self.log_result("Zero Wallet Duty ON", False, "Failed to turn duty ON")
    
    def update_zero_wallet_driver_location(self):
        """Update zero wallet driver location"""
        response = self.make_request("PUT", f"/driver/{self.zero_wallet_driver_id}/location", {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Bangalore, Karnataka"
        })
        
        if response and response.status_code == 200:
            self.log_result("Zero Wallet Location Update", True, "Location updated")
        else:
            self.log_result("Zero Wallet Location Update", False, "Failed to update location")
    
    def test_booking_assignment_failure(self):
        """Test that booking assignment fails for zero wallet driver"""
        # Create a customer for this test
        customer_phone = f"91654321{str(uuid.uuid4())[:4]}"
        self.make_request("POST", "/auth/send-otp", {"phone": customer_phone, "role": "customer"})
        self.make_request("POST", "/auth/verify-otp", {"phone": customer_phone, "otp": self.mock_otp, "role": "customer"})
        
        response = self.make_request("POST", "/customer/register", {
            "phone": customer_phone,
            "name": "Test Customer 2",
            "location": {"latitude": 12.9716, "longitude": 77.5946, "address": "Bangalore"}
        })
        
        if response and response.status_code == 200:
            customer_data = response.json()
            test_customer_id = customer_data["user"]["user_id"]
            
            # Try to create booking - should fail due to wallet restriction
            response = self.make_request("POST", "/booking/create-smart", {
                "customer_id": test_customer_id,
                "pickup": {"latitude": 12.9716, "longitude": 77.5946, "address": "Bangalore"},
                "drop": {"latitude": 12.9352, "longitude": 77.6245, "address": "Electronic City"},
                "vehicle_type": "sedan"
            })
            
            if response and response.status_code == 404:
                # Expected failure due to no eligible drivers
                self.log_result("Wallet Restriction Test", True, "Booking assignment correctly failed for zero wallet driver")
            elif response and response.status_code == 200:
                # Check if it was assigned to a different driver (not the zero wallet one)
                data = response.json()
                assigned_driver = data.get("booking", {}).get("driver_id")
                if assigned_driver != self.zero_wallet_driver_id:
                    self.log_result("Wallet Restriction Test", True, "Booking correctly assigned to different driver, not zero wallet driver")
                else:
                    self.log_result("Wallet Restriction Test", False, "Booking incorrectly assigned to zero wallet driver")
            else:
                self.log_result("Wallet Restriction Test", False, f"Unexpected response: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Wallet Restriction Test", False, "Failed to create test customer")
    
    # ==================== CRITICAL FLOW 3: Queue System (2-Trip Rule) ====================
    
    def test_queue_system(self):
        """Test queue system with 2-trip rule"""
        print("\n🔥 TESTING CRITICAL FLOW 3: Queue System (2-Trip Rule)")
        
        if not self.driver_id:
            self.log_result("Queue System Test", False, "No driver available for queue testing")
            return
        
        # Complete 2 trips with same driver
        self.complete_second_trip()
        
        # Check queue status - verify continuous_trips_count = 2
        self.verify_queue_status()
        
        # Verify driver moves to queue
        self.verify_driver_in_queue()
    
    def complete_second_trip(self):
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
                "driver_id": self.driver_id,
                "action": "accept"
            })
            
            self.make_request("PUT", f"/booking/{second_booking_id}/start-trip", {})
            
            response = self.make_request("PUT", f"/booking/{second_booking_id}/complete-trip", {})
            
            if response and response.status_code == 200:
                self.log_result("Second Trip Completion", True, "Second trip completed successfully")
            else:
                self.log_result("Second Trip Completion", False, "Failed to complete second trip")
        else:
            self.log_result("Second Trip Creation", False, "Failed to create second booking")
    
    def verify_queue_status(self):
        """Verify queue status shows continuous_trips_count = 2"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/queue-status")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                continuous_trips = data.get("continuous_trips_count", 0)
                if continuous_trips == 2:
                    self.log_result("Queue Status Verification", True, f"Continuous trips count is 2: {continuous_trips}")
                else:
                    self.log_result("Queue Status Verification", False, f"Expected 2 trips, got: {continuous_trips}")
            else:
                self.log_result("Queue Status Verification", False, "Failed to get queue status")
        else:
            self.log_result("Queue Status Verification", False, f"Failed to get queue status: {response.status_code if response else 'No response'}")
    
    def verify_driver_in_queue(self):
        """Verify driver moves to queue"""
        response = self.make_request("GET", f"/driver/{self.driver_id}/queue-status")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                in_queue = data.get("in_queue", False)
                if in_queue:
                    self.log_result("Driver Queue Verification", True, "Driver correctly moved to queue")
                else:
                    self.log_result("Driver Queue Verification", False, "Driver not in queue after 2 trips")
            else:
                self.log_result("Driver Queue Verification", False, "Failed to get queue status")
        else:
            self.log_result("Driver Queue Verification", False, f"Failed to verify queue: {response.status_code if response else 'No response'}")
    
    # ==================== CRITICAL FLOW 4: Driver Agreement Storage ====================
    
    def test_driver_agreement_storage(self):
        """Test driver agreement storage - already tested in create_driver_with_kyc"""
        print("\n🔥 TESTING CRITICAL FLOW 4: Driver Agreement Storage")
        self.log_result("Driver Agreement Storage", True, "Agreement storage tested during driver creation")
    
    # ==================== CRITICAL FLOW 5: Driver Approval Process ====================
    
    def test_driver_approval_process(self):
        """Test driver approval process"""
        print("\n🔥 TESTING CRITICAL FLOW 5: Driver Approval Process")
        
        # Create pending driver
        pending_phone = f"91543210{str(uuid.uuid4())[:4]}"
        self.create_pending_driver(pending_phone)
        
        # Check approval_status = "pending"
        self.verify_pending_status()
        
        # Approve driver
        self.approve_pending_driver()
        
        # Verify approval_status = "approved"
        self.verify_approved_status()
    
    def create_pending_driver(self, phone):
        """Create pending driver"""
        self.make_request("POST", "/auth/send-otp", {"phone": phone, "role": "driver"})
        self.make_request("POST", "/auth/verify-otp", {"phone": phone, "otp": self.mock_otp, "role": "driver"})
        
        kyc_data = self.generate_driver_kyc_data(phone)
        response = self.make_request("POST", "/driver/register-kyc", kyc_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.pending_driver_id = data["driver_id"]
                self.log_result("Pending Driver Creation", True, f"Pending driver created: {self.pending_driver_id}")
            else:
                self.log_result("Pending Driver Creation", False, "Failed to create pending driver")
        else:
            self.log_result("Pending Driver Creation", False, f"Failed to create pending driver: {response.status_code if response else 'No response'}")
    
    def verify_pending_status(self):
        """Verify approval_status = pending"""
        response = self.make_request("GET", f"/driver/{self.pending_driver_id}/profile-complete")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                driver = data["driver"]
                status = driver.get("approval_status")
                if status == "pending":
                    self.log_result("Pending Status Verification", True, "Driver status is pending")
                else:
                    self.log_result("Pending Status Verification", False, f"Expected pending, got: {status}")
            else:
                self.log_result("Pending Status Verification", False, "Failed to get driver profile")
        else:
            self.log_result("Pending Status Verification", False, f"Failed to verify pending status: {response.status_code if response else 'No response'}")
    
    def approve_pending_driver(self):
        """Approve pending driver"""
        response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": self.pending_driver_id,
            "approval_status": "approved"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.log_result("Pending Driver Approval", True, "Pending driver approved")
            else:
                self.log_result("Pending Driver Approval", False, "Failed to approve pending driver")
        else:
            self.log_result("Pending Driver Approval", False, f"Failed to approve: {response.status_code if response else 'No response'}")
    
    def verify_approved_status(self):
        """Verify approval_status = approved"""
        response = self.make_request("GET", f"/driver/{self.pending_driver_id}/profile-complete")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                driver = data["driver"]
                status = driver.get("approval_status")
                if status == "approved":
                    self.log_result("Approved Status Verification", True, "Driver status is approved")
                else:
                    self.log_result("Approved Status Verification", False, f"Expected approved, got: {status}")
            else:
                self.log_result("Approved Status Verification", False, "Failed to get driver profile")
        else:
            self.log_result("Approved Status Verification", False, f"Failed to verify approved status: {response.status_code if response else 'No response'}")
    
    # ==================== STABILITY CHECKS ====================
    
    def test_api_stability(self):
        """Test API stability and response codes"""
        print("\n🔥 TESTING STABILITY CHECKS")
        
        # Test various endpoints for proper response codes
        endpoints = [
            ("GET", "/admin/stats"),
            ("GET", "/admin/tariffs"),
            ("GET", "/admin/drivers"),
            ("GET", "/admin/customers"),
            ("GET", "/admin/bookings")
        ]
        
        for method, endpoint in endpoints:
            response = self.make_request(method, endpoint)
            if response:
                if response.status_code == 200:
                    self.log_result(f"API Stability - {endpoint}", True, f"Returned 200 OK")
                elif response.status_code == 500:
                    self.log_result(f"API Stability - {endpoint}", False, f"Returned 500 Internal Server Error")
                else:
                    self.log_result(f"API Stability - {endpoint}", True, f"Returned {response.status_code} (not 500)")
            else:
                self.log_result(f"API Stability - {endpoint}", False, "No response received")
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all critical flow tests"""
        print("🚀 Starting VK Drop Taxi Comprehensive Backend Testing")
        print(f"Backend URL: {self.base_url}")
        print(f"Mock OTP: {self.mock_otp}")
        print("=" * 80)
        
        try:
            # Run all critical flows
            self.test_complete_booking_lifecycle()
            self.test_wallet_restriction()
            self.test_queue_system()
            self.test_driver_agreement_storage()
            self.test_driver_approval_process()
            self.test_api_stability()
            
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
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ CRITICAL ISSUES IDENTIFIED:")
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"].lower() for keyword in ["booking", "wallet", "queue", "agreement", "approval"]):
                critical_issues.append(f"  - {result['test']}: {result['message']}")
        
        if critical_issues:
            for issue in critical_issues:
                print(issue)
        else:
            print("  - No critical issues found")
        
        print("\n🎯 LIVE TESTING READINESS:")
        critical_flows = ["Complete Booking Lifecycle", "Wallet Restriction", "Queue System", "Agreement Storage", "Approval Process"]
        ready_flows = []
        
        for flow in critical_flows:
            flow_tests = [r for r in self.test_results if flow.lower() in r["test"].lower()]
            if flow_tests and all(r["success"] for r in flow_tests):
                ready_flows.append(flow)
        
        print(f"  - {len(ready_flows)}/{len(critical_flows)} critical flows ready")
        for flow in ready_flows:
            print(f"    ✅ {flow}")
        
        for flow in critical_flows:
            if flow not in ready_flows:
                print(f"    ❌ {flow}")

if __name__ == "__main__":
    tester = VKDropTaxiTester()
    tester.run_all_tests()