#!/usr/bin/env python3
"""
VK Drop Taxi - Core Dispatch Features Test
Testing the Phase 2 & 3 features with existing data
"""

import requests
import json

BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

def make_request(method, endpoint, data=None):
    """Make HTTP request"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        print(f"{method} {endpoint} -> {response.status_code}")
        return response.json(), response.status_code == 200
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None, False

def test_core_dispatch():
    print("🚀 Testing VK Drop Taxi Core Dispatch Features")
    print("=" * 60)
    
    # Get existing customer and driver
    print("\n1. Getting existing data...")
    customers_data, success = make_request("GET", "/admin/customers")
    if success and customers_data.get("customers"):
        customer_id = customers_data["customers"][0]["user_id"]
        print(f"✅ Found customer: {customer_id}")
    else:
        print("❌ No customers found")
        return
    
    drivers_data, success = make_request("GET", "/admin/drivers")
    if success and drivers_data.get("drivers"):
        approved_drivers = [d for d in drivers_data["drivers"] if d.get("approval_status") == "approved"]
        if approved_drivers:
            driver_id = approved_drivers[0]["driver_id"]
            print(f"✅ Found approved driver: {driver_id}")
        else:
            print("❌ No approved drivers found")
            return
    else:
        print("❌ No drivers found")
        return
    
    # Test 1: Driver Duty Toggle
    print("\n2. Testing Driver Duty Toggle...")
    data, success = make_request("PUT", f"/driver/{driver_id}/duty-status", {
        "duty_on": True,
        "go_home_mode": False
    })
    if success:
        print("✅ Driver duty ON successful")
    else:
        print("❌ Driver duty ON failed")
        return
    
    # Test 2: Driver Location Update
    print("\n3. Testing Driver Location Update...")
    data, success = make_request("PUT", f"/driver/{driver_id}/location", {
        "latitude": 12.97,
        "longitude": 80.24,
        "address": "Test Location, Chennai"
    })
    if success:
        print("✅ Driver location update successful")
    else:
        print("❌ Driver location update failed")
    
    # Test 3: Add money to driver wallet
    print("\n4. Testing Driver Wallet...")
    data, success = make_request("POST", "/wallet/add-money", {
        "user_id": driver_id,
        "amount": 1500
    })
    if success:
        print("✅ Driver wallet funded with ₹1500")
    else:
        print("❌ Failed to fund driver wallet")
    
    # Test 4: Smart Booking Creation
    print("\n5. Testing Smart Booking Creation...")
    booking_data, success = make_request("POST", "/booking/create-smart", {
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
    
    if success and booking_data.get("success"):
        booking = booking_data["booking"]
        booking_id = booking["booking_id"]
        assigned_driver = booking["driver_id"]
        fare = booking.get("fare", 0)
        distance = booking.get("distance", 0)
        
        print(f"✅ Smart booking created: {booking_id}")
        print(f"   Driver: {assigned_driver}, Distance: {distance}km, Fare: ₹{fare}")
        
        # Test 5: Accept Booking
        print("\n6. Testing Accept Booking...")
        data, success = make_request("POST", "/booking/accept-reject", {
            "booking_id": booking_id,
            "driver_id": assigned_driver,
            "action": "accept"
        })
        if success:
            print("✅ Booking accepted")
            
            # Test 6: Start Trip
            print("\n7. Testing Start Trip...")
            data, success = make_request("PUT", f"/booking/{booking_id}/start-trip", {})
            if success:
                print("✅ Trip started")
                
                # Test 7: Complete Trip
                print("\n8. Testing Complete Trip...")
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
        if booking_data:
            print(f"   Error: {booking_data}")
    
    # Test 8: Queue Status
    print("\n9. Testing Queue Status...")
    data, success = make_request("GET", f"/driver/{driver_id}/queue-status")
    if success:
        queue_position = data.get("queue_position")
        continuous_trips = data.get("continuous_trips_count", 0)
        in_queue = data.get("in_queue", False)
        print(f"✅ Queue Status: Position={queue_position}, Continuous Trips={continuous_trips}, In Queue={in_queue}")
    else:
        print("❌ Failed to get queue status")
    
    # Test 9: Tariff System
    print("\n10. Testing Tariff System...")
    data, success = make_request("GET", "/admin/tariffs")
    if success:
        tariffs = data.get("tariffs", [])
        print(f"✅ Retrieved {len(tariffs)} tariff rates")
        for tariff in tariffs:
            vehicle_type = tariff.get("vehicle_type")
            rate = tariff.get("rate_per_km")
            min_fare = tariff.get("minimum_fare")
            print(f"   {vehicle_type}: ₹{rate}/km, Min: ₹{min_fare}")
    else:
        print("❌ Failed to get tariffs")
    
    # Test 10: Manual Assignment
    print("\n11. Testing Manual Assignment...")
    data, success = make_request("POST", "/booking/create-smart", {
        "customer_id": customer_id,
        "pickup": {
            "latitude": 13.00,
            "longitude": 80.27,
            "address": "Manual Assignment Pickup"
        },
        "drop": {
            "latitude": 13.11,
            "longitude": 80.30,
            "address": "Manual Assignment Drop"
        },
        "vehicle_type": "sedan",
        "assignment_mode": "manual",
        "manual_driver_id": driver_id
    })
    
    if success and data.get("success"):
        booking = data["booking"]
        assigned_driver = booking.get("driver_id")
        if assigned_driver == driver_id:
            print("✅ Manual assignment successful")
        else:
            print(f"❌ Manual assignment failed: expected {driver_id}, got {assigned_driver}")
    else:
        print("❌ Failed to create booking with manual assignment")
    
    print("\n" + "=" * 60)
    print("🏁 Core Dispatch Testing Complete")

if __name__ == "__main__":
    test_core_dispatch()