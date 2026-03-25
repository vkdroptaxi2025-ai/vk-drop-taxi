#!/usr/bin/env python3
"""
VK Drop Taxi - Core Dispatch System Testing (Simplified)
Testing with existing data from previous tests
"""

import requests
import json
import time
from datetime import datetime

# Test Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
MOCK_OTP = "123456"

def make_request(method, endpoint, data=None, expected_status=200):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"{method} {endpoint} -> {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text}")
            return None, False
        
        return response.json(), True
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None, False

def test_existing_data():
    """Test with existing data from previous tests"""
    print("🔍 Testing with existing data...")
    
    # Get existing drivers
    data, success = make_request("GET", "/admin/drivers")
    if success and data.get("success"):
        drivers = data.get("drivers", [])
        print(f"Found {len(drivers)} drivers")
        
        # Find an approved driver
        approved_driver = None
        for driver in drivers:
            if driver.get("approval_status") == "approved":
                approved_driver = driver
                break
        
        if approved_driver:
            driver_id = approved_driver["driver_id"]
            print(f"Using existing approved driver: {driver_id}")
            
            # Test driver duty toggle
            print("\n=== Testing Driver Duty Toggle ===")
            data, success = make_request("PUT", f"/driver/{driver_id}/duty-status", {
                "duty_on": True,
                "go_home_mode": False
            })
            if success:
                print("✅ Driver duty ON successful")
            else:
                print("❌ Driver duty ON failed")
            
            # Test location update
            print("\n=== Testing Driver Location Update ===")
            data, success = make_request("PUT", f"/driver/{driver_id}/location", {
                "latitude": 12.97,
                "longitude": 80.24,
                "address": "Test Location, Chennai"
            })
            if success:
                print("✅ Driver location update successful")
            else:
                print("❌ Driver location update failed")
            
            # Test queue status
            print("\n=== Testing Queue Status ===")
            data, success = make_request("GET", f"/driver/{driver_id}/queue-status")
            if success:
                queue_position = data.get("queue_position")
                continuous_trips = data.get("continuous_trips_count", 0)
                in_queue = data.get("in_queue", False)
                print(f"✅ Queue Status: Position={queue_position}, Continuous Trips={continuous_trips}, In Queue={in_queue}")
            else:
                print("❌ Queue status failed")
            
            return driver_id
        else:
            print("❌ No approved drivers found")
            return None
    else:
        print("❌ Failed to get drivers")
        return None

def test_tariff_system():
    """Test tariff system"""
    print("\n=== Testing Tariff System ===")
    
    # Get current tariffs
    data, success = make_request("GET", "/admin/tariffs")
    if success and data.get("success"):
        tariffs = data.get("tariffs", [])
        print(f"✅ Retrieved {len(tariffs)} tariff rates")
        
        for tariff in tariffs:
            vehicle_type = tariff.get("vehicle_type")
            rate = tariff.get("rate_per_km")
            min_fare = tariff.get("minimum_fare")
            print(f"   {vehicle_type}: ₹{rate}/km, Min: ₹{min_fare}")
        
        # Update sedan tariff to ₹14/km
        data, success = make_request("PUT", "/admin/update-tariff", {
            "vehicle_type": "sedan",
            "rate_per_km": 14,
            "minimum_fare": 300
        })
        if success:
            print("✅ Tariff updated to ₹14/km")
        else:
            print("❌ Failed to update tariff")
    else:
        print("❌ Failed to get tariffs")

def test_smart_booking_with_existing_data():
    """Test smart booking with existing customer and driver"""
    print("\n=== Testing Smart Booking with Existing Data ===")
    
    # Get existing customers
    data, success = make_request("GET", "/admin/customers")
    if success and data.get("success"):
        customers = data.get("customers", [])
        if customers:
            customer_id = customers[0]["customer_id"]
            print(f"Using existing customer: {customer_id}")
            
            # Try to create smart booking
            data, success = make_request("POST", "/booking/create-smart", {
                "customer_id": customer_id,
                "pickup": {
                    "latitude": 12.97,
                    "longitude": 80.24,
                    "address": "Pickup Point, Chennai"
                },
                "drop": {
                    "latitude": 13.08,
                    "longitude": 80.27,
                    "address": "Drop Point, Chennai"
                },
                "vehicle_type": "sedan",
                "assignment_mode": "auto"
            })
            
            if success and data.get("success"):
                booking = data["booking"]
                booking_id = booking["booking_id"]
                driver_id = booking["driver_id"]
                fare = booking.get("fare", 0)
                distance = booking.get("distance", 0)
                
                print(f"✅ Smart booking created: {booking_id}")
                print(f"   Driver: {driver_id}, Distance: {distance}km, Fare: ₹{fare}")
                
                # Test accept booking
                print("\n=== Testing Accept Booking ===")
                data, success = make_request("POST", "/booking/accept-reject", {
                    "booking_id": booking_id,
                    "driver_id": driver_id,
                    "action": "accept"
                })
                if success:
                    print("✅ Booking accepted")
                    
                    # Test start trip
                    print("\n=== Testing Start Trip ===")
                    data, success = make_request("PUT", f"/booking/{booking_id}/start-trip", {})
                    if success:
                        print("✅ Trip started")
                        
                        # Test complete trip
                        print("\n=== Testing Complete Trip ===")
                        data, success = make_request("PUT", f"/booking/{booking_id}/complete-trip", {})
                        if success:
                            earning = data.get("earning", 0)
                            print(f"✅ Trip completed, Driver earned: ₹{earning}")
                        else:
                            print("❌ Failed to complete trip")
                    else:
                        print("❌ Failed to start trip")
                else:
                    print("❌ Failed to accept booking")
            else:
                print("❌ Failed to create smart booking")
                if data:
                    print(f"   Error: {data}")
        else:
            print("❌ No customers found")
    else:
        print("❌ Failed to get customers")

def main():
    print("🚀 VK Drop Taxi Core Dispatch Testing (Simplified)")
    print("=" * 60)
    
    # Test tariff system first
    test_tariff_system()
    
    # Test with existing data
    driver_id = test_existing_data()
    
    if driver_id:
        # Test smart booking
        test_smart_booking_with_existing_data()
    
    print("\n" + "=" * 60)
    print("🏁 Core Dispatch Testing Complete")

if __name__ == "__main__":
    main()