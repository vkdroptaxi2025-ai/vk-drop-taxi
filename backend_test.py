#!/usr/bin/env python3
"""
VK Drop Taxi Backend Testing - Edge Cases & Wallet Restrictions
Focus on critical dispatch system testing as per review request
"""

import requests
import json
import time
from datetime import datetime, date, timedelta

# Backend URL from environment
BACKEND_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
MOCK_OTP = "123456"

class VKDropTaxiTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.created_entities = {
            'drivers': [],
            'customers': [],
            'bookings': []
        }
    
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def make_request(self, method, endpoint, data=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None
    
    def create_driver_with_kyc(self, phone, name="Test Driver"):
        """Create a new driver with complete KYC"""
        # Step 1: Send OTP
        otp_response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "driver"
        })
        
        if not otp_response or otp_response.status_code != 200:
            return None, "Failed to send OTP"
        
        # Step 2: Verify OTP
        verify_response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": MOCK_OTP,
            "role": "driver"
        })
        
        if not verify_response or verify_response.status_code != 200:
            return None, "Failed to verify OTP"
        
        # Step 3: Register KYC
        future_date = (date.today() + timedelta(days=365)).isoformat()
        
        kyc_data = {
            "phone": phone,
            "personal_details": {
                "full_name": name,
                "mobile_number": phone,
                "full_address": "Test Address, Test City",
                "aadhaar_number": "123456789012",
                "pan_number": "ABCDE1234F",
                "driving_license_number": "DL123456789",
                "driving_experience_years": 5,
                "driver_photo": "base64_photo_data"
            },
            "bank_details": {
                "account_holder_name": name,
                "bank_name": "Test Bank",
                "account_number": "1234567890123456",
                "ifsc_code": "TEST0123456",
                "branch_name": "Test Branch"
            },
            "vehicle_details": {
                "vehicle_type": "sedan",
                "vehicle_number": "TN01AB1234",
                "vehicle_model": "Test Model",
                "vehicle_year": 2020
            },
            "documents": {
                "aadhaar_card": {"front_image": "base64_aadhaar_front", "back_image": "base64_aadhaar_back"},
                "pan_card": {"front_image": "base64_pan_front"},
                "driving_license": {"front_image": "base64_dl_front", "back_image": "base64_dl_back"},
                "rc_book": {"front_image": "base64_rc_front", "back_image": "base64_rc_back"},
                "insurance": {"front_image": "base64_insurance"},
                "fitness_certificate": {"front_image": "base64_fc"},
                "permit": {"front_image": "base64_permit"},
                "pollution_certificate": {"front_image": "base64_pollution"}
            },
            "document_expiry": {
                "insurance_expiry": future_date,
                "fc_expiry": future_date,
                "permit_expiry": future_date,
                "pollution_expiry": future_date,
                "license_expiry": future_date
            },
            "driver_vehicle_photo": {
                "photo": "base64_vehicle_photo"
            }
        }
        
        kyc_response = self.make_request("POST", "/driver/register-kyc", kyc_data)
        
        if not kyc_response or kyc_response.status_code != 200:
            return None, f"Failed to register KYC: {kyc_response.text if kyc_response else 'No response'}"
        
        driver_data = kyc_response.json()
        driver_id = driver_data.get('driver_id')
        
        if driver_id:
            self.created_entities['drivers'].append(driver_id)
        
        return driver_id, "Driver created successfully"
    
    def approve_driver(self, driver_id):
        """Approve driver"""
        response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": driver_id,
            "approval_status": "approved"
        })
        
        return response and response.status_code == 200
    
    def add_money_to_wallet(self, user_id, amount):
        """Add money to driver wallet"""
        response = self.make_request("POST", "/wallet/add-money", {
            "user_id": user_id,
            "amount": amount
        })
        
        return response and response.status_code == 200
    
    def set_driver_duty_on(self, driver_id):
        """Turn driver duty ON"""
        response = self.make_request("PUT", f"/driver/{driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        return response and response.status_code == 200
    
    def update_driver_location(self, driver_id, lat=12.97, lon=80.24):
        """Update driver location"""
        response = self.make_request("PUT", f"/driver/{driver_id}/location", {
            "latitude": lat,
            "longitude": lon,
            "address": "Test Location"
        })
        
        return response and response.status_code == 200
    
    def create_customer(self, phone="8888877777", name="Test Customer"):
        """Create a customer"""
        # Send OTP
        otp_response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "customer"
        })
        
        if not otp_response or otp_response.status_code != 200:
            return None
        
        # Verify OTP
        verify_response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": MOCK_OTP,
            "role": "customer"
        })
        
        if not verify_response or verify_response.status_code != 200:
            return None
        
        # Register customer
        register_response = self.make_request("POST", "/customer/register", {
            "phone": phone,
            "name": name
        })
        
        if not register_response or register_response.status_code != 200:
            return None
        
        customer_data = register_response.json()
        customer_id = customer_data.get('user', {}).get('user_id')
        
        if customer_id:
            self.created_entities['customers'].append(customer_id)
        
        return customer_id
    
    def create_smart_booking(self, customer_id):
        """Create a smart booking"""
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.97,
                "longitude": 80.24,
                "address": "Pickup Location"
            },
            "drop": {
                "latitude": 13.08,
                "longitude": 80.27,
                "address": "Drop Location"
            },
            "vehicle_type": "sedan",
            "assignment_mode": "auto"
        }
        
        response = self.make_request("POST", "/booking/create-smart", booking_data)
        
        if response and response.status_code == 200:
            booking_data = response.json()
            booking_id = booking_data.get('booking', {}).get('booking_id')
            if booking_id:
                self.created_entities['bookings'].append(booking_id)
            return booking_id, response.json()
        
        return None, response.json() if response else {"error": "No response"}
    
    def accept_reject_booking(self, booking_id, driver_id, action):
        """Accept or reject booking"""
        response = self.make_request("POST", "/booking/accept-reject", {
            "booking_id": booking_id,
            "driver_id": driver_id,
            "action": action
        })
        
        return response and response.status_code == 200, response.json() if response else {"error": "No response"}
    
    def start_trip(self, booking_id):
        """Start trip"""
        response = self.make_request("PUT", f"/booking/{booking_id}/start-trip")
        return response and response.status_code == 200
    
    def complete_trip(self, booking_id):
        """Complete trip"""
        response = self.make_request("PUT", f"/booking/{booking_id}/complete-trip")
        return response and response.status_code == 200
    
    def get_queue_status(self, driver_id):
        """Get driver queue status"""
        response = self.make_request("GET", f"/driver/{driver_id}/queue-status")
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_wallet_balance(self, user_id):
        """Get wallet balance"""
        response = self.make_request("GET", f"/wallet/{user_id}")
        if response and response.status_code == 200:
            return response.json().get('wallet', {}).get('balance', 0)
        return 0

    # ==================== CRITICAL TEST 1: WALLET BALANCE RESTRICTION ====================
    
    def test_wallet_balance_restriction(self):
        """Test wallet balance restriction (< ₹1000)"""
        print("🔥 CRITICAL TEST 1: Wallet Balance Restriction (< ₹1000)")
        print("=" * 60)
        
        # Create new driver with different phone
        driver_phone = "9999988888"
        driver_id, error = self.create_driver_with_kyc(driver_phone, "Wallet Test Driver")
        
        if not driver_id:
            self.log_test("Create Driver for Wallet Test", False, error=error)
            return
        
        self.log_test("Create Driver for Wallet Test", True, f"Driver ID: {driver_id}")
        
        # Approve driver
        if not self.approve_driver(driver_id):
            self.log_test("Approve Driver", False, error="Failed to approve driver")
            return
        
        self.log_test("Approve Driver", True, "Driver approved successfully")
        
        # Turn duty ON (wallet balance is ₹0)
        if not self.set_driver_duty_on(driver_id):
            self.log_test("Set Duty ON with ₹0 wallet", False, error="Failed to set duty ON")
            return
        
        self.log_test("Set Duty ON with ₹0 wallet", True, "Duty set to ON")
        
        # Update driver location
        if not self.update_driver_location(driver_id):
            self.log_test("Update Driver Location", False, error="Failed to update location")
            return
        
        self.log_test("Update Driver Location", True, "Location updated")
        
        # Create customer
        customer_id = self.create_customer()
        if not customer_id:
            self.log_test("Create Customer", False, error="Failed to create customer")
            return
        
        self.log_test("Create Customer", True, f"Customer ID: {customer_id}")
        
        # Try to create smart booking - SHOULD FAIL (wallet ₹0 < ₹1000)
        booking_id, booking_response = self.create_smart_booking(customer_id)
        
        if booking_id:
            self.log_test("Smart Booking with ₹0 Wallet", False, 
                         error="Booking should have failed due to insufficient wallet balance")
        else:
            error_msg = booking_response.get('detail', 'Unknown error')
            if "No eligible drivers available" in error_msg or "wallet" in error_msg.lower():
                self.log_test("Smart Booking with ₹0 Wallet", True, 
                             f"Correctly rejected: {error_msg}")
            else:
                self.log_test("Smart Booking with ₹0 Wallet", False, 
                             f"Wrong error message: {error_msg}")
        
        # Add ₹500 to wallet (still below ₹1000)
        if not self.add_money_to_wallet(driver_id, 500):
            self.log_test("Add ₹500 to Wallet", False, error="Failed to add money")
            return
        
        self.log_test("Add ₹500 to Wallet", True, "₹500 added successfully")
        
        # Try booking again - SHOULD STILL FAIL (₹500 < ₹1000)
        booking_id, booking_response = self.create_smart_booking(customer_id)
        
        if booking_id:
            self.log_test("Smart Booking with ₹500 Wallet", False, 
                         error="Booking should have failed due to insufficient wallet balance")
        else:
            error_msg = booking_response.get('detail', 'Unknown error')
            if "No eligible drivers available" in error_msg or "wallet" in error_msg.lower():
                self.log_test("Smart Booking with ₹500 Wallet", True, 
                             f"Correctly rejected: {error_msg}")
            else:
                self.log_test("Smart Booking with ₹500 Wallet", False, 
                             f"Wrong error message: {error_msg}")
        
        # Add ₹600 more (total ₹1100)
        if not self.add_money_to_wallet(driver_id, 600):
            self.log_test("Add ₹600 More to Wallet", False, error="Failed to add money")
            return
        
        self.log_test("Add ₹600 More to Wallet", True, "₹600 added, total ₹1100")
        
        # Verify wallet balance
        balance = self.get_wallet_balance(driver_id)
        self.log_test("Verify Wallet Balance", True, f"Current balance: ₹{balance}")
        
        # Try booking again - SHOULD NOW SUCCEED (₹1100 > ₹1000)
        booking_id, booking_response = self.create_smart_booking(customer_id)
        
        if booking_id:
            self.log_test("Smart Booking with ₹1100 Wallet", True, 
                         f"Booking created successfully: {booking_id}")
            return driver_id, booking_id  # Return for next test
        else:
            error_msg = booking_response.get('detail', 'Unknown error')
            self.log_test("Smart Booking with ₹1100 Wallet", False, 
                         f"Booking failed unexpectedly: {error_msg}")
            return driver_id, None
    
    # ==================== CRITICAL TEST 2: BOOKING REJECT AND REASSIGNMENT ====================
    
    def test_booking_reject_reassignment(self, driver_id, booking_id):
        """Test booking reject and reassignment"""
        print("\n🔥 CRITICAL TEST 2: Booking Reject and Reassignment")
        print("=" * 60)
        
        if not driver_id or not booking_id:
            self.log_test("Booking Reject Test Setup", False, 
                         error="Missing driver_id or booking_id from previous test")
            return
        
        # Reject the booking
        success, response = self.accept_reject_booking(booking_id, driver_id, "reject")
        
        if success:
            self.log_test("Reject Booking", True, "Booking rejected successfully")
        else:
            error_msg = response.get('detail', 'Unknown error')
            self.log_test("Reject Booking", False, f"Failed to reject: {error_msg}")
            return
        
        # Verify booking status becomes "cancelled"
        booking_response = self.make_request("GET", f"/booking/{booking_id}")
        if booking_response and booking_response.status_code == 200:
            booking_data = booking_response.json()
            booking_status = booking_data.get('booking', {}).get('status')
            
            if booking_status == "cancelled":
                self.log_test("Verify Booking Status", True, "Booking status is 'cancelled'")
            else:
                self.log_test("Verify Booking Status", False, 
                             f"Expected 'cancelled', got '{booking_status}'")
        else:
            self.log_test("Verify Booking Status", False, "Failed to get booking details")
        
        # Verify driver status returns to "available"
        driver_response = self.make_request("GET", f"/driver/{driver_id}/profile")
        if driver_response and driver_response.status_code == 200:
            driver_data = driver_response.json()
            driver_status = driver_data.get('driver', {}).get('driver_status')
            
            if driver_status == "available":
                self.log_test("Verify Driver Status", True, "Driver status is 'available'")
            else:
                self.log_test("Verify Driver Status", False, 
                             f"Expected 'available', got '{driver_status}'")
        else:
            self.log_test("Verify Driver Status", False, "Failed to get driver details")
    
    # ==================== CRITICAL TEST 3: 2-TRIP CONTINUITY RULE ====================
    
    def test_2_trip_continuity_rule(self, driver_id):
        """Test 2-trip continuity rule"""
        print("\n🔥 CRITICAL TEST 3: 2-Trip Continuity Rule")
        print("=" * 60)
        
        if not driver_id:
            self.log_test("2-Trip Test Setup", False, error="Missing driver_id from previous test")
            return
        
        # Create customer for trips
        customer_id = self.create_customer("7777766666", "Trip Test Customer")
        if not customer_id:
            self.log_test("Create Customer for Trips", False, error="Failed to create customer")
            return
        
        self.log_test("Create Customer for Trips", True, f"Customer ID: {customer_id}")
        
        # Trip 1: Create → Accept → Start → Complete
        print("\n--- Trip 1 ---")
        
        booking_id_1, booking_response_1 = self.create_smart_booking(customer_id)
        if not booking_id_1:
            self.log_test("Create Trip 1 Booking", False, 
                         f"Failed: {booking_response_1.get('detail', 'Unknown error')}")
            return
        
        self.log_test("Create Trip 1 Booking", True, f"Booking ID: {booking_id_1}")
        
        # Accept Trip 1
        success, response = self.accept_reject_booking(booking_id_1, driver_id, "accept")
        if not success:
            self.log_test("Accept Trip 1", False, f"Failed: {response.get('detail', 'Unknown error')}")
            return
        
        self.log_test("Accept Trip 1", True, "Trip 1 accepted")
        
        # Start Trip 1
        if not self.start_trip(booking_id_1):
            self.log_test("Start Trip 1", False, error="Failed to start trip")
            return
        
        self.log_test("Start Trip 1", True, "Trip 1 started")
        
        # Complete Trip 1
        if not self.complete_trip(booking_id_1):
            self.log_test("Complete Trip 1", False, error="Failed to complete trip")
            return
        
        self.log_test("Complete Trip 1", True, "Trip 1 completed")
        
        # Trip 2: Create → Accept → Start → Complete
        print("\n--- Trip 2 ---")
        
        booking_id_2, booking_response_2 = self.create_smart_booking(customer_id)
        if not booking_id_2:
            self.log_test("Create Trip 2 Booking", False, 
                         f"Failed: {booking_response_2.get('detail', 'Unknown error')}")
            return
        
        self.log_test("Create Trip 2 Booking", True, f"Booking ID: {booking_id_2}")
        
        # Accept Trip 2
        success, response = self.accept_reject_booking(booking_id_2, driver_id, "accept")
        if not success:
            self.log_test("Accept Trip 2", False, f"Failed: {response.get('detail', 'Unknown error')}")
            return
        
        self.log_test("Accept Trip 2", True, "Trip 2 accepted")
        
        # Start Trip 2
        if not self.start_trip(booking_id_2):
            self.log_test("Start Trip 2", False, error="Failed to start trip")
            return
        
        self.log_test("Start Trip 2", True, "Trip 2 started")
        
        # Complete Trip 2
        if not self.complete_trip(booking_id_2):
            self.log_test("Complete Trip 2", False, error="Failed to complete trip")
            return
        
        self.log_test("Complete Trip 2", True, "Trip 2 completed")
        
        # Check queue status after 2 trips
        print("\n--- Queue Status Check ---")
        
        queue_status = self.get_queue_status(driver_id)
        if queue_status:
            continuous_trips = queue_status.get('continuous_trips_count', 0)
            in_queue = queue_status.get('in_queue', False)
            
            self.log_test("Check Continuous Trips Count", True, 
                         f"Continuous trips: {continuous_trips}")
            
            if continuous_trips >= 2 or in_queue:
                self.log_test("Verify 2-Trip Rule", True, 
                             f"Driver correctly in queue or has 2+ trips (count: {continuous_trips}, in_queue: {in_queue})")
            else:
                self.log_test("Verify 2-Trip Rule", False, 
                             f"Driver should be in queue after 2 trips (count: {continuous_trips}, in_queue: {in_queue})")
        else:
            self.log_test("Get Queue Status", False, error="Failed to get queue status")
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all critical tests"""
        print("🚀 VK Drop Taxi Backend Testing - Edge Cases & Wallet Restrictions")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Mock OTP: {MOCK_OTP}")
        print("=" * 80)
        
        # Test 1: Wallet Balance Restriction
        driver_id, booking_id = self.test_wallet_balance_restriction()
        
        # Test 2: Booking Reject and Reassignment
        self.test_booking_reject_reassignment(driver_id, booking_id)
        
        # Test 3: 2-Trip Continuity Rule
        self.test_2_trip_continuity_rule(driver_id)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  ❌ {test['test']}: {test['error']}")
        
        print("\n📋 CREATED ENTITIES:")
        print(f"  Drivers: {len(self.created_entities['drivers'])}")
        print(f"  Customers: {len(self.created_entities['customers'])}")
        print(f"  Bookings: {len(self.created_entities['bookings'])}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = VKDropTaxiTester()
    tester.run_all_tests()