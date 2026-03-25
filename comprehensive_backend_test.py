#!/usr/bin/env python3
"""
VK Drop Taxi Comprehensive Backend Testing
Testing all 6 scenarios as requested in the review request
"""

import requests
import json
import time
from datetime import datetime, date, timedelta

# Backend URL from environment
BACKEND_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
MOCK_OTP = "123456"

class VKDropTaxiComprehensiveTester:
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
            print(f"Request error: {e}")
            return None

    # ==================== SCENARIO 1: Complete Customer Booking Flow ====================
    
    def test_scenario_1_complete_booking_flow(self):
        """Test Scenario 1: Complete Customer Booking Flow"""
        print("🚀 SCENARIO 1: Complete Customer Booking Flow")
        print("=" * 60)
        
        # Step 1: Create a new customer
        print("--- Step 1: Create Customer ---")
        customer_phone = "7777700001"
        
        # Send OTP
        otp_response = self.make_request("POST", "/auth/send-otp", {
            "phone": customer_phone,
            "role": "customer"
        })
        
        if not otp_response or otp_response.status_code != 200:
            self.log_test("Customer Send OTP", False, error=f"Failed: {otp_response.text if otp_response else 'No response'}")
            return None
        
        self.log_test("Customer Send OTP", True, "OTP sent successfully")
        
        # Verify OTP
        verify_response = self.make_request("POST", "/auth/verify-otp", {
            "phone": customer_phone,
            "otp": MOCK_OTP,
            "role": "customer"
        })
        
        if not verify_response or verify_response.status_code != 200:
            self.log_test("Customer Verify OTP", False, error=f"Failed: {verify_response.text if verify_response else 'No response'}")
            return None
        
        self.log_test("Customer Verify OTP", True, "OTP verified successfully")
        
        # Register customer
        register_response = self.make_request("POST", "/customer/register", {
            "phone": customer_phone,
            "name": "Test Customer Flow"
        })
        
        if not register_response or register_response.status_code != 200:
            self.log_test("Customer Register", False, error=f"Failed: {register_response.text if register_response else 'No response'}")
            return None
        
        customer_data = register_response.json()
        customer_id = customer_data.get('user', {}).get('user_id')
        
        if not customer_id:
            self.log_test("Customer Register", False, error="No customer_id returned")
            return None
        
        self.log_test("Customer Register", True, f"Customer created: {customer_id}")
        self.created_entities['customers'].append(customer_id)
        
        # Step 2: Create a new driver with KYC
        print("--- Step 2: Create Driver with KYC ---")
        driver_phone = "7777700002"
        driver_id = self.create_driver_with_kyc(driver_phone, "Test Driver Flow")
        
        if not driver_id:
            return None
        
        # Step 3: Approve the driver
        print("--- Step 3: Approve Driver ---")
        approve_response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": driver_id,
            "approval_status": "approved"
        })
        
        if not approve_response or approve_response.status_code != 200:
            self.log_test("Approve Driver", False, error=f"Failed: {approve_response.text if approve_response else 'No response'}")
            return None
        
        self.log_test("Approve Driver", True, "Driver approved successfully")
        
        # Step 4: Add money to driver wallet (₹1500)
        print("--- Step 4: Add Money to Driver Wallet ---")
        wallet_response = self.make_request("POST", "/wallet/add-money", {
            "user_id": driver_id,
            "amount": 1500
        })
        
        if not wallet_response or wallet_response.status_code != 200:
            self.log_test("Add Money to Wallet", False, error=f"Failed: {wallet_response.text if wallet_response else 'No response'}")
            return None
        
        self.log_test("Add Money to Wallet", True, "₹1500 added to driver wallet")
        
        # Step 5: Driver goes online
        print("--- Step 5: Driver Goes Online ---")
        duty_response = self.make_request("PUT", f"/driver/{driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        if not duty_response or duty_response.status_code != 200:
            self.log_test("Driver Duty ON", False, error=f"Failed: {duty_response.text if duty_response else 'No response'}")
            return None
        
        self.log_test("Driver Duty ON", True, "Driver is now online")
        
        # Update driver location
        location_response = self.make_request("PUT", f"/driver/{driver_id}/location", {
            "latitude": 12.97,
            "longitude": 80.24,
            "address": "Test Location"
        })
        
        if not location_response or location_response.status_code != 200:
            self.log_test("Update Driver Location", False, error=f"Failed: {location_response.text if location_response else 'No response'}")
            return None
        
        self.log_test("Update Driver Location", True, "Driver location updated")
        
        # Step 6: Customer creates a booking
        print("--- Step 6: Customer Creates Booking ---")
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.97,
                "longitude": 80.24,
                "address": "Pickup Point"
            },
            "drop": {
                "latitude": 13.08,
                "longitude": 80.27,
                "address": "Drop Point"
            },
            "vehicle_type": "sedan",
            "assignment_mode": "auto"
        }
        
        booking_response = self.make_request("POST", "/booking/create-smart", booking_data)
        
        if not booking_response or booking_response.status_code != 200:
            self.log_test("Create Smart Booking", False, error=f"Failed: {booking_response.text if booking_response else 'No response'}")
            return None
        
        booking_result = booking_response.json()
        booking_id = booking_result.get('booking', {}).get('booking_id')
        assigned_driver = booking_result.get('booking', {}).get('assigned_driver_id')
        booking_status = booking_result.get('booking', {}).get('status')
        
        if not booking_id:
            self.log_test("Create Smart Booking", False, error="No booking_id returned")
            return None
        
        self.log_test("Create Smart Booking", True, f"Booking created: {booking_id}")
        self.log_test("Verify Driver Assignment", assigned_driver == driver_id, f"Assigned driver: {assigned_driver}")
        self.log_test("Verify Booking Status", booking_status == "requested", f"Status: {booking_status}")
        
        self.created_entities['bookings'].append(booking_id)
        
        # Step 7: Driver accepts booking
        print("--- Step 7: Driver Accepts Booking ---")
        accept_response = self.make_request("POST", "/booking/accept-reject", {
            "booking_id": booking_id,
            "driver_id": driver_id,
            "action": "accept"
        })
        
        if not accept_response or accept_response.status_code != 200:
            self.log_test("Driver Accept Booking", False, error=f"Failed: {accept_response.text if accept_response else 'No response'}")
            return None
        
        self.log_test("Driver Accept Booking", True, "Booking accepted by driver")
        
        # Verify status changes to "accepted"
        booking_check = self.make_request("GET", f"/booking/{booking_id}")
        if booking_check and booking_check.status_code == 200:
            booking_data = booking_check.json()
            status = booking_data.get('booking', {}).get('status')
            self.log_test("Verify Status After Accept", status == "accepted", f"Status: {status}")
        
        # Step 8: Driver starts trip
        print("--- Step 8: Driver Starts Trip ---")
        start_response = self.make_request("PUT", f"/booking/{booking_id}/start-trip")
        
        if not start_response or start_response.status_code != 200:
            self.log_test("Start Trip", False, error=f"Failed: {start_response.text if start_response else 'No response'}")
            return None
        
        self.log_test("Start Trip", True, "Trip started successfully")
        
        # Verify status changes to "ongoing"
        booking_check = self.make_request("GET", f"/booking/{booking_id}")
        if booking_check and booking_check.status_code == 200:
            booking_data = booking_check.json()
            status = booking_data.get('booking', {}).get('status')
            self.log_test("Verify Status After Start", status == "ongoing", f"Status: {status}")
        
        # Step 9: Driver completes trip
        print("--- Step 9: Driver Completes Trip ---")
        complete_response = self.make_request("PUT", f"/booking/{booking_id}/complete-trip")
        
        if not complete_response or complete_response.status_code != 200:
            self.log_test("Complete Trip", False, error=f"Failed: {complete_response.text if complete_response else 'No response'}")
            return None
        
        self.log_test("Complete Trip", True, "Trip completed successfully")
        
        # Verify status changes to "completed"
        booking_check = self.make_request("GET", f"/booking/{booking_id}")
        if booking_check and booking_check.status_code == 200:
            booking_data = booking_check.json()
            status = booking_data.get('booking', {}).get('status')
            self.log_test("Verify Status After Complete", status == "completed", f"Status: {status}")
        
        # Verify driver earnings updated
        driver_check = self.make_request("GET", f"/driver/{driver_id}/profile")
        if driver_check and driver_check.status_code == 200:
            driver_data = driver_check.json()
            earnings = driver_data.get('driver', {}).get('total_earnings', 0)
            self.log_test("Verify Driver Earnings Updated", earnings > 0, f"Total earnings: ₹{earnings}")
        
        return {
            'customer_id': customer_id,
            'driver_id': driver_id,
            'booking_id': booking_id
        }

    # ==================== SCENARIO 2: Wallet Restriction (< ₹1000) ====================
    
    def test_scenario_2_wallet_restriction(self):
        """Test Scenario 2: Wallet Restriction (< ₹1000)"""
        print("\n🚀 SCENARIO 2: Wallet Restriction (< ₹1000)")
        print("=" * 60)
        
        # Step 1: Create another driver with low wallet
        print("--- Step 1: Create Driver with Low Wallet ---")
        driver_phone = "7777700003"
        driver_id = self.create_driver_with_kyc(driver_phone, "Low Wallet Driver")
        
        if not driver_id:
            return
        
        # Approve driver
        approve_response = self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": driver_id,
            "approval_status": "approved"
        })
        
        if not approve_response or approve_response.status_code != 200:
            self.log_test("Approve Low Wallet Driver", False, error="Failed to approve driver")
            return
        
        self.log_test("Approve Low Wallet Driver", True, "Driver approved")
        
        # Add only ₹500 to wallet (below ₹1000 threshold)
        wallet_response = self.make_request("POST", "/wallet/add-money", {
            "user_id": driver_id,
            "amount": 500
        })
        
        if wallet_response and wallet_response.status_code == 200:
            self.log_test("Add ₹500 to Wallet", True, "₹500 added (below threshold)")
        else:
            self.log_test("Add ₹500 to Wallet", False, error="Failed to add money")
            return
        
        # Step 2: Turn duty on
        print("--- Step 2: Turn Duty ON ---")
        duty_response = self.make_request("PUT", f"/driver/{driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        if duty_response and duty_response.status_code == 200:
            self.log_test("Turn Duty ON", True, "Driver duty turned ON")
        else:
            self.log_test("Turn Duty ON", False, error="Failed to turn duty ON")
            return
        
        # Update location
        location_response = self.make_request("PUT", f"/driver/{driver_id}/location", {
            "latitude": 12.97,
            "longitude": 80.24,
            "address": "Test Location"
        })
        
        # Step 3: Create customer and try booking - should FAIL
        print("--- Step 3: Try Booking (Should FAIL) ---")
        customer_phone = "7777700004"
        customer_id = self.create_customer(customer_phone, "Wallet Test Customer")
        
        if not customer_id:
            return
        
        # Try to create booking
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.97,
                "longitude": 80.24,
                "address": "Pickup Point"
            },
            "drop": {
                "latitude": 13.08,
                "longitude": 80.27,
                "address": "Drop Point"
            },
            "vehicle_type": "sedan",
            "assignment_mode": "auto"
        }
        
        booking_response = self.make_request("POST", "/booking/create-smart", booking_data)
        
        if booking_response and booking_response.status_code == 200:
            self.log_test("Booking with Low Wallet Driver", False, error="Booking should have failed due to wallet restriction")
        else:
            error_msg = booking_response.json().get('detail', 'Unknown error') if booking_response else 'No response'
            if "No eligible drivers available" in error_msg or "wallet" in error_msg.lower():
                self.log_test("Booking with Low Wallet Driver", True, f"Correctly rejected: {error_msg}")
            else:
                self.log_test("Booking with Low Wallet Driver", False, f"Wrong error message: {error_msg}")

    # ==================== SCENARIO 3: Queue System (2-Trip Rule) ====================
    
    def test_scenario_3_queue_system(self):
        """Test Scenario 3: Queue System (2-Trip Rule)"""
        print("\n🚀 SCENARIO 3: Queue System (2-Trip Rule)")
        print("=" * 60)
        
        # Create driver and customer for queue testing
        driver_phone = "7777700005"
        driver_id = self.create_driver_with_kyc(driver_phone, "Queue Test Driver")
        
        if not driver_id:
            return
        
        # Approve and setup driver
        self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": driver_id,
            "approval_status": "approved"
        })
        
        self.make_request("POST", "/wallet/add-money", {
            "user_id": driver_id,
            "amount": 1500
        })
        
        self.make_request("PUT", f"/driver/{driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        self.make_request("PUT", f"/driver/{driver_id}/location", {
            "latitude": 12.97,
            "longitude": 80.24,
            "address": "Test Location"
        })
        
        customer_phone = "7777700006"
        customer_id = self.create_customer(customer_phone, "Queue Test Customer")
        
        if not customer_id:
            return
        
        # Complete 2 trips
        for trip_num in range(1, 3):
            print(f"--- Trip {trip_num} ---")
            
            # Create booking
            booking_data = {
                "customer_id": customer_id,
                "pickup": {
                    "latitude": 12.97,
                    "longitude": 80.24,
                    "address": "Pickup Point"
                },
                "drop": {
                    "latitude": 13.08,
                    "longitude": 80.27,
                    "address": "Drop Point"
                },
                "vehicle_type": "sedan",
                "assignment_mode": "auto"
            }
            
            booking_response = self.make_request("POST", "/booking/create-smart", booking_data)
            
            if not booking_response or booking_response.status_code != 200:
                self.log_test(f"Create Trip {trip_num} Booking", False, error="Failed to create booking")
                continue
            
            booking_result = booking_response.json()
            booking_id = booking_result.get('booking', {}).get('booking_id')
            
            if not booking_id:
                self.log_test(f"Create Trip {trip_num} Booking", False, error="No booking_id returned")
                continue
            
            self.log_test(f"Create Trip {trip_num} Booking", True, f"Booking created: {booking_id}")
            
            # Accept booking
            accept_response = self.make_request("POST", "/booking/accept-reject", {
                "booking_id": booking_id,
                "driver_id": driver_id,
                "action": "accept"
            })
            
            if accept_response and accept_response.status_code == 200:
                self.log_test(f"Accept Trip {trip_num}", True, "Booking accepted")
            else:
                self.log_test(f"Accept Trip {trip_num}", False, error="Failed to accept")
                continue
            
            # Start trip
            start_response = self.make_request("PUT", f"/booking/{booking_id}/start-trip")
            
            if start_response and start_response.status_code == 200:
                self.log_test(f"Start Trip {trip_num}", True, "Trip started")
            else:
                self.log_test(f"Start Trip {trip_num}", False, error="Failed to start")
                continue
            
            # Complete trip
            complete_response = self.make_request("PUT", f"/booking/{booking_id}/complete-trip")
            
            if complete_response and complete_response.status_code == 200:
                self.log_test(f"Complete Trip {trip_num}", True, "Trip completed")
            else:
                self.log_test(f"Complete Trip {trip_num}", False, error="Failed to complete")
                continue
        
        # Check queue status after 2 trips
        print("--- Check Queue Status ---")
        queue_response = self.make_request("GET", f"/driver/{driver_id}/queue-status")
        
        if queue_response and queue_response.status_code == 200:
            queue_data = queue_response.json()
            continuous_trips = queue_data.get('continuous_trips_count', 0)
            in_queue = queue_data.get('in_queue', False)
            
            self.log_test("Get Queue Status", True, f"Continuous trips: {continuous_trips}, In queue: {in_queue}")
            
            if continuous_trips >= 2:
                self.log_test("Verify 2-Trip Rule", True, f"Driver has completed {continuous_trips} trips")
            else:
                self.log_test("Verify 2-Trip Rule", False, f"Expected 2+ trips, got {continuous_trips}")
        else:
            self.log_test("Get Queue Status", False, error="Failed to get queue status")

    # ==================== SCENARIO 4: Reject and Reassignment ====================
    
    def test_scenario_4_reject_reassignment(self):
        """Test Scenario 4: Reject and Reassignment"""
        print("\n🚀 SCENARIO 4: Reject and Reassignment")
        print("=" * 60)
        
        # Create driver and customer
        driver_phone = "7777700007"
        driver_id = self.create_driver_with_kyc(driver_phone, "Reject Test Driver")
        
        if not driver_id:
            return
        
        # Setup driver
        self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": driver_id,
            "approval_status": "approved"
        })
        
        self.make_request("POST", "/wallet/add-money", {
            "user_id": driver_id,
            "amount": 1500
        })
        
        self.make_request("PUT", f"/driver/{driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        self.make_request("PUT", f"/driver/{driver_id}/location", {
            "latitude": 12.97,
            "longitude": 80.24,
            "address": "Test Location"
        })
        
        customer_phone = "7777700008"
        customer_id = self.create_customer(customer_phone, "Reject Test Customer")
        
        if not customer_id:
            return
        
        # Step 1: Create a booking for driver
        print("--- Step 1: Create Booking ---")
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.97,
                "longitude": 80.24,
                "address": "Pickup Point"
            },
            "drop": {
                "latitude": 13.08,
                "longitude": 80.27,
                "address": "Drop Point"
            },
            "vehicle_type": "sedan",
            "assignment_mode": "auto"
        }
        
        booking_response = self.make_request("POST", "/booking/create-smart", booking_data)
        
        if not booking_response or booking_response.status_code != 200:
            self.log_test("Create Booking for Reject Test", False, error="Failed to create booking")
            return
        
        booking_result = booking_response.json()
        booking_id = booking_result.get('booking', {}).get('booking_id')
        
        if not booking_id:
            self.log_test("Create Booking for Reject Test", False, error="No booking_id returned")
            return
        
        self.log_test("Create Booking for Reject Test", True, f"Booking created: {booking_id}")
        
        # Step 2: Driver rejects
        print("--- Step 2: Driver Rejects Booking ---")
        reject_response = self.make_request("POST", "/booking/accept-reject", {
            "booking_id": booking_id,
            "driver_id": driver_id,
            "action": "reject"
        })
        
        if reject_response and reject_response.status_code == 200:
            self.log_test("Reject Booking", True, "Booking rejected successfully")
        else:
            error_msg = reject_response.json().get('detail', 'Unknown error') if reject_response else 'No response'
            self.log_test("Reject Booking", False, f"Failed to reject: {error_msg}")
            return
        
        # Step 3: Verify booking status is "cancelled"
        print("--- Step 3: Verify Booking Status ---")
        booking_check = self.make_request("GET", f"/booking/{booking_id}")
        
        if booking_check and booking_check.status_code == 200:
            booking_data = booking_check.json()
            status = booking_data.get('booking', {}).get('status')
            
            if status == "cancelled":
                self.log_test("Verify Booking Status", True, "Booking status is 'cancelled'")
            else:
                self.log_test("Verify Booking Status", False, f"Expected 'cancelled', got '{status}'")
        else:
            self.log_test("Verify Booking Status", False, error="Failed to get booking details")
        
        # Step 4: Verify driver status returns to "available"
        print("--- Step 4: Verify Driver Status ---")
        driver_check = self.make_request("GET", f"/driver/{driver_id}/profile")
        
        if driver_check and driver_check.status_code == 200:
            driver_data = driver_check.json()
            driver_status = driver_data.get('driver', {}).get('driver_status')
            
            if driver_status == "available":
                self.log_test("Verify Driver Status", True, "Driver status is 'available'")
            else:
                self.log_test("Verify Driver Status", False, f"Expected 'available', got '{driver_status}'")
        else:
            self.log_test("Verify Driver Status", False, error="Failed to get driver details")

    # ==================== SCENARIO 5: Admin Manual Assignment ====================
    
    def test_scenario_5_admin_manual_assignment(self):
        """Test Scenario 5: Admin Manual Assignment"""
        print("\n🚀 SCENARIO 5: Admin Manual Assignment")
        print("=" * 60)
        
        # Create driver and customer
        driver_phone = "7777700009"
        driver_id = self.create_driver_with_kyc(driver_phone, "Manual Assignment Driver")
        
        if not driver_id:
            return
        
        # Setup driver
        self.make_request("PUT", "/admin/driver/approve", {
            "driver_id": driver_id,
            "approval_status": "approved"
        })
        
        self.make_request("POST", "/wallet/add-money", {
            "user_id": driver_id,
            "amount": 1500
        })
        
        self.make_request("PUT", f"/driver/{driver_id}/duty-status", {
            "duty_on": True,
            "go_home_mode": False
        })
        
        self.make_request("PUT", f"/driver/{driver_id}/location", {
            "latitude": 12.97,
            "longitude": 80.24,
            "address": "Test Location"
        })
        
        customer_phone = "7777700010"
        customer_id = self.create_customer(customer_phone, "Manual Assignment Customer")
        
        if not customer_id:
            return
        
        # Step 1: Create booking with manual assignment
        print("--- Step 1: Create Manual Assignment Booking ---")
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.97,
                "longitude": 80.24,
                "address": "Pickup Point"
            },
            "drop": {
                "latitude": 13.08,
                "longitude": 80.27,
                "address": "Drop Point"
            },
            "vehicle_type": "sedan",
            "assignment_mode": "manual",
            "manual_driver_id": driver_id
        }
        
        booking_response = self.make_request("POST", "/booking/create-smart", booking_data)
        
        if not booking_response or booking_response.status_code != 200:
            self.log_test("Create Manual Assignment Booking", False, error=f"Failed: {booking_response.text if booking_response else 'No response'}")
            return
        
        booking_result = booking_response.json()
        booking_id = booking_result.get('booking', {}).get('booking_id')
        assigned_driver = booking_result.get('booking', {}).get('assigned_driver_id')
        
        if not booking_id:
            self.log_test("Create Manual Assignment Booking", False, error="No booking_id returned")
            return
        
        self.log_test("Create Manual Assignment Booking", True, f"Booking created: {booking_id}")
        
        # Step 2: Verify specified driver is assigned
        print("--- Step 2: Verify Manual Assignment ---")
        if assigned_driver == driver_id:
            self.log_test("Verify Manual Assignment", True, f"Correct driver assigned: {assigned_driver}")
        else:
            self.log_test("Verify Manual Assignment", False, f"Expected {driver_id}, got {assigned_driver}")

    # ==================== SCENARIO 6: Driver Agreement Validation ====================
    
    def test_scenario_6_driver_agreement_validation(self):
        """Test Scenario 6: Driver Agreement Validation"""
        print("\n🚀 SCENARIO 6: Driver Agreement Validation")
        print("=" * 60)
        
        # Create driver with agreement
        driver_phone = "7777700011"
        driver_id = self.create_driver_with_kyc_and_agreement(driver_phone, "Agreement Test Driver")
        
        if not driver_id:
            return
        
        # Verify agreement data is stored
        print("--- Verify Agreement Data Storage ---")
        driver_response = self.make_request("GET", f"/driver/{driver_id}/profile")
        
        if driver_response and driver_response.status_code == 200:
            driver_data = driver_response.json()
            driver_info = driver_data.get('driver', {})
            
            # Check if agreement data exists
            agreement_accepted = driver_info.get('agreement_accepted', False)
            agreement_timestamp = driver_info.get('agreement_timestamp')
            
            if agreement_accepted:
                self.log_test("Verify Agreement Accepted", True, f"Agreement accepted: {agreement_accepted}")
            else:
                self.log_test("Verify Agreement Accepted", False, "Agreement not found or not accepted")
            
            if agreement_timestamp:
                self.log_test("Verify Agreement Timestamp", True, f"Agreement timestamp: {agreement_timestamp}")
            else:
                self.log_test("Verify Agreement Timestamp", False, "Agreement timestamp not found")
        else:
            self.log_test("Get Driver Profile", False, error="Failed to get driver profile")

    # ==================== HELPER METHODS ====================
    
    def create_driver_with_kyc(self, phone, name="Test Driver"):
        """Create a new driver with complete KYC"""
        # Send OTP
        otp_response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "driver"
        })
        
        if not otp_response or otp_response.status_code != 200:
            self.log_test(f"Driver Send OTP ({phone})", False, error="Failed to send OTP")
            return None
        
        self.log_test(f"Driver Send OTP ({phone})", True, "OTP sent successfully")
        
        # Verify OTP
        verify_response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": MOCK_OTP,
            "role": "driver"
        })
        
        if not verify_response or verify_response.status_code != 200:
            self.log_test(f"Driver Verify OTP ({phone})", False, error="Failed to verify OTP")
            return None
        
        self.log_test(f"Driver Verify OTP ({phone})", True, "OTP verified successfully")
        
        # Register KYC
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
            self.log_test(f"Driver KYC Registration ({phone})", False, error=f"Failed: {kyc_response.text if kyc_response else 'No response'}")
            return None
        
        driver_data = kyc_response.json()
        driver_id = driver_data.get('driver_id')
        
        if driver_id:
            self.created_entities['drivers'].append(driver_id)
            self.log_test(f"Driver KYC Registration ({phone})", True, f"Driver created: {driver_id}")
        else:
            self.log_test(f"Driver KYC Registration ({phone})", False, error="No driver_id returned")
        
        return driver_id
    
    def create_driver_with_kyc_and_agreement(self, phone, name="Test Driver"):
        """Create a new driver with complete KYC and agreement"""
        # Send OTP
        otp_response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "driver"
        })
        
        if not otp_response or otp_response.status_code != 200:
            self.log_test(f"Driver Send OTP ({phone})", False, error="Failed to send OTP")
            return None
        
        self.log_test(f"Driver Send OTP ({phone})", True, "OTP sent successfully")
        
        # Verify OTP
        verify_response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": MOCK_OTP,
            "role": "driver"
        })
        
        if not verify_response or verify_response.status_code != 200:
            self.log_test(f"Driver Verify OTP ({phone})", False, error="Failed to verify OTP")
            return None
        
        self.log_test(f"Driver Verify OTP ({phone})", True, "OTP verified successfully")
        
        # Register KYC with agreement
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
            },
            "agreement": {
                "accepted": True,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        kyc_response = self.make_request("POST", "/driver/register-kyc", kyc_data)
        
        if not kyc_response or kyc_response.status_code != 200:
            self.log_test(f"Driver KYC Registration with Agreement ({phone})", False, error=f"Failed: {kyc_response.text if kyc_response else 'No response'}")
            return None
        
        driver_data = kyc_response.json()
        driver_id = driver_data.get('driver_id')
        
        if driver_id:
            self.created_entities['drivers'].append(driver_id)
            self.log_test(f"Driver KYC Registration with Agreement ({phone})", True, f"Driver created: {driver_id}")
        else:
            self.log_test(f"Driver KYC Registration with Agreement ({phone})", False, error="No driver_id returned")
        
        return driver_id
    
    def create_customer(self, phone, name="Test Customer"):
        """Create a customer"""
        # Send OTP
        otp_response = self.make_request("POST", "/auth/send-otp", {
            "phone": phone,
            "role": "customer"
        })
        
        if not otp_response or otp_response.status_code != 200:
            self.log_test(f"Customer Send OTP ({phone})", False, error="Failed to send OTP")
            return None
        
        self.log_test(f"Customer Send OTP ({phone})", True, "OTP sent successfully")
        
        # Verify OTP
        verify_response = self.make_request("POST", "/auth/verify-otp", {
            "phone": phone,
            "otp": MOCK_OTP,
            "role": "customer"
        })
        
        if not verify_response or verify_response.status_code != 200:
            self.log_test(f"Customer Verify OTP ({phone})", False, error="Failed to verify OTP")
            return None
        
        self.log_test(f"Customer Verify OTP ({phone})", True, "OTP verified successfully")
        
        # Register customer
        register_response = self.make_request("POST", "/customer/register", {
            "phone": phone,
            "name": name
        })
        
        if not register_response or register_response.status_code != 200:
            self.log_test(f"Customer Register ({phone})", False, error="Failed to register customer")
            return None
        
        customer_data = register_response.json()
        customer_id = customer_data.get('user', {}).get('user_id')
        
        if customer_id:
            self.created_entities['customers'].append(customer_id)
            self.log_test(f"Customer Register ({phone})", True, f"Customer created: {customer_id}")
        else:
            self.log_test(f"Customer Register ({phone})", False, error="No customer_id returned")
        
        return customer_id

    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_scenarios(self):
        """Run all test scenarios"""
        print("🚀 VK Drop Taxi Comprehensive Backend Testing")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Mock OTP: {MOCK_OTP}")
        print("=" * 80)
        
        # Run all scenarios
        self.test_scenario_1_complete_booking_flow()
        self.test_scenario_2_wallet_restriction()
        self.test_scenario_3_queue_system()
        self.test_scenario_4_reject_reassignment()
        self.test_scenario_5_admin_manual_assignment()
        self.test_scenario_6_driver_agreement_validation()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
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
    tester = VKDropTaxiComprehensiveTester()
    tester.run_all_scenarios()