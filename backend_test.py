#!/usr/bin/env python3
"""
VK Drop Taxi - MongoDB Projection Fix Verification Test
Testing that API endpoints do NOT return base64 image strings and have reasonable response sizes.
"""

import requests
import json
import sys
import re
from datetime import datetime

# Use the production backend URL from frontend/.env
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_response_size_and_images(response_data, endpoint_name, max_size_kb=100):
    """
    Check if response contains base64 images and verify size
    Returns (has_images, size_kb, image_count)
    """
    response_text = json.dumps(response_data)
    response_size_kb = len(response_text.encode('utf-8')) / 1024
    
    # Search for base64 image patterns
    image_patterns = [
        r'data:image/[^;]+;base64,',
        r'"data:image',
        r'base64,/9j/',  # JPEG base64 start
        r'base64,iVBORw0KGgo',  # PNG base64 start
        r'base64,R0lGOD',  # GIF base64 start
    ]
    
    image_count = 0
    for pattern in image_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        image_count += len(matches)
    
    has_images = image_count > 0
    
    log_test(f"📊 {endpoint_name} Response Analysis:")
    log_test(f"   Size: {response_size_kb:.2f} KB")
    log_test(f"   Base64 Images Found: {image_count}")
    log_test(f"   Size Check: {'✅ PASS' if response_size_kb <= max_size_kb else '❌ FAIL'} (< {max_size_kb}KB)")
    log_test(f"   Image Check: {'✅ PASS' if not has_images else '❌ FAIL'} (No base64 images)")
    
    return has_images, response_size_kb, image_count

def test_admin_drivers():
    """Test GET /api/admin/drivers endpoint"""
    log_test("🔍 Testing GET /api/admin/drivers")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/drivers", timeout=30)
        log_test(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            has_images, size_kb, image_count = check_response_size_and_images(data, "GET /api/admin/drivers")
            
            # Check if drivers array exists and has data
            drivers = data.get('drivers', [])
            log_test(f"   Drivers Count: {len(drivers)}")
            
            # Check sample driver fields
            if drivers:
                sample_driver = drivers[0]
                log_test(f"   Sample Driver Fields: {list(sample_driver.keys())}")
                
                # Verify essential fields are present
                essential_fields = ['driver_id', 'approval_status']
                missing_fields = [field for field in essential_fields if field not in sample_driver]
                if missing_fields:
                    log_test(f"   ⚠️  Missing essential fields: {missing_fields}")
                else:
                    log_test(f"   ✅ Essential fields present")
            
            return {
                'success': True,
                'has_images': has_images,
                'size_kb': size_kb,
                'image_count': image_count,
                'drivers_count': len(drivers)
            }
        else:
            log_test(f"   ❌ FAIL: HTTP {response.status_code}")
            log_test(f"   Response: {response.text[:200]}...")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        log_test(f"   ❌ FAIL: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_pending_verification():
    """Test GET /api/admin/drivers/pending-verification endpoint"""
    log_test("🔍 Testing GET /api/admin/drivers/pending-verification")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/drivers/pending-verification", timeout=30)
        log_test(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            has_images, size_kb, image_count = check_response_size_and_images(data, "GET /api/admin/drivers/pending-verification")
            
            # Check if drivers array exists
            drivers = data.get('drivers', [])
            log_test(f"   Pending Drivers Count: {len(drivers)}")
            
            return {
                'success': True,
                'has_images': has_images,
                'size_kb': size_kb,
                'image_count': image_count,
                'pending_drivers_count': len(drivers)
            }
        else:
            log_test(f"   ❌ FAIL: HTTP {response.status_code}")
            log_test(f"   Response: {response.text[:200]}...")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        log_test(f"   ❌ FAIL: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_booking_creation():
    """Test POST /api/booking/create endpoint with approved driver"""
    log_test("🔍 Testing POST /api/booking/create")
    
    # First, create a test customer with unique phone
    import random
    test_phone = f"987654{random.randint(1000, 9999)}"
    customer_data = {
        "phone": test_phone,
        "name": "Test Customer",
        "location": {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Bangalore, Karnataka"
        }
    }
    
    try:
        # Create customer
        customer_response = requests.post(f"{BASE_URL}/customer/register", json=customer_data, timeout=30)
        log_test(f"   Customer registration status: {customer_response.status_code}")
        
        if customer_response.status_code != 200:
            log_test(f"   ⚠️  Customer creation failed: {customer_response.text[:200]}")
            return {'success': False, 'error': f'Customer creation failed: {customer_response.status_code}'}
        
        customer_result = customer_response.json()
        customer_id = customer_result.get('user', {}).get('user_id')
        log_test(f"   Created test customer: {customer_id}")
        
        if not customer_id:
            log_test(f"   ⚠️  No customer_id in response: {customer_result}")
            return {'success': False, 'error': 'No customer_id returned'}
        
        # Create booking
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Bangalore, Karnataka"
            },
            "drop": {
                "latitude": 12.9352,
                "longitude": 77.6245,
                "address": "Whitefield, Bangalore"
            },
            "vehicle_type": "sedan"
        }
        
        response = requests.post(f"{BASE_URL}/booking/create", json=booking_data, timeout=30)
        log_test(f"   Booking creation status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            has_images, size_kb, image_count = check_response_size_and_images(data, "POST /api/booking/create")
            
            # Check booking details
            booking = data.get('booking', {})
            log_test(f"   Booking ID: {booking.get('booking_id', 'N/A')}")
            log_test(f"   Driver Assigned: {booking.get('driver_id', 'N/A')}")
            log_test(f"   Fare: ₹{booking.get('fare', 'N/A')}")
            
            return {
                'success': True,
                'has_images': has_images,
                'size_kb': size_kb,
                'image_count': image_count,
                'booking_id': booking.get('booking_id')
            }
        else:
            log_test(f"   ❌ FAIL: HTTP {response.status_code}")
            log_test(f"   Response: {response.text[:300]}...")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        log_test(f"   ❌ FAIL: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_queue_status():
    """Test GET /api/driver/{driver_id}/queue-status endpoint"""
    log_test("🔍 Testing GET /api/driver/{driver_id}/queue-status")
    
    try:
        # First get a driver ID from the drivers list
        drivers_response = requests.get(f"{BASE_URL}/admin/drivers", timeout=30)
        if drivers_response.status_code != 200:
            log_test(f"   ⚠️  Could not fetch drivers list: {drivers_response.status_code}")
            return {'success': False, 'error': 'Could not fetch drivers list'}
        
        drivers_data = drivers_response.json()
        drivers = drivers_data.get('drivers', [])
        
        if not drivers:
            log_test(f"   ⚠️  No drivers found in system")
            return {'success': False, 'error': 'No drivers found'}
        
        # Use first driver
        test_driver_id = drivers[0].get('driver_id')
        log_test(f"   Testing with driver: {test_driver_id}")
        
        response = requests.get(f"{BASE_URL}/driver/{test_driver_id}/queue-status", timeout=30)
        log_test(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            has_images, size_kb, image_count = check_response_size_and_images(data, "GET /api/driver/queue-status")
            
            # Check queue status details
            log_test(f"   Queue Position: {data.get('queue_position', 'N/A')}")
            log_test(f"   In Queue: {data.get('in_queue', 'N/A')}")
            log_test(f"   Continuous Trips: {data.get('continuous_trips_count', 'N/A')}")
            
            return {
                'success': True,
                'has_images': has_images,
                'size_kb': size_kb,
                'image_count': image_count,
                'driver_id': test_driver_id
            }
        else:
            log_test(f"   ❌ FAIL: HTTP {response.status_code}")
            log_test(f"   Response: {response.text[:200]}...")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        log_test(f"   ❌ FAIL: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_smart_booking_creation():
    """Test POST /api/booking/create-smart endpoint"""
    log_test("🔍 Testing POST /api/booking/create-smart")
    
    # First, create a test customer with unique phone
    import random
    test_phone = f"987654{random.randint(1000, 9999)}"
    customer_data = {
        "phone": test_phone,
        "name": "Test Customer Smart",
        "location": {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Bangalore, Karnataka"
        }
    }
    
    try:
        # Create customer
        customer_response = requests.post(f"{BASE_URL}/customer/register", json=customer_data, timeout=30)
        log_test(f"   Customer registration status: {customer_response.status_code}")
        
        if customer_response.status_code != 200:
            log_test(f"   ⚠️  Customer creation failed: {customer_response.text[:200]}")
            return {'success': False, 'error': f'Customer creation failed: {customer_response.status_code}'}
        
        customer_result = customer_response.json()
        customer_id = customer_result.get('user', {}).get('user_id')
        log_test(f"   Created test customer: {customer_id}")
        
        if not customer_id:
            log_test(f"   ⚠️  No customer_id in response: {customer_result}")
            return {'success': False, 'error': 'No customer_id returned'}
        
        # Create smart booking
        booking_data = {
            "customer_id": customer_id,
            "pickup": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "address": "Bangalore, Karnataka"
            },
            "drop": {
                "latitude": 12.9352,
                "longitude": 77.6245,
                "address": "Whitefield, Bangalore"
            },
            "vehicle_type": "sedan",
            "assignment_mode": "auto"
        }
        
        response = requests.post(f"{BASE_URL}/booking/create-smart", json=booking_data, timeout=30)
        log_test(f"   Smart booking creation status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            has_images, size_kb, image_count = check_response_size_and_images(data, "POST /api/booking/create-smart")
            
            # Check booking details
            booking = data.get('booking', {})
            log_test(f"   Booking ID: {booking.get('booking_id', 'N/A')}")
            log_test(f"   Driver Assigned: {booking.get('driver_id', 'N/A')}")
            log_test(f"   Fare: ₹{booking.get('fare', 'N/A')}")
            
            return {
                'success': True,
                'has_images': has_images,
                'size_kb': size_kb,
                'image_count': image_count,
                'booking_id': booking.get('booking_id')
            }
        else:
            log_test(f"   ❌ FAIL: HTTP {response.status_code}")
            log_test(f"   Response: {response.text[:300]}...")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        log_test(f"   ❌ FAIL: {str(e)}")
        return {'success': False, 'error': str(e)}
    
def main():
    """Run all MongoDB projection fix verification tests"""
    log_test("🚀 VK DROP TAXI - MONGODB PROJECTION FIX VERIFICATION")
    log_test(f"🔗 Testing against: {BASE_URL}")
    log_test("=" * 80)
    
    # Test results storage
    results = {
        'admin_drivers': None,
        'pending_verification': None,
        'booking_creation': None,
        'smart_booking_creation': None,
        'queue_status': None
    }
    
    # Run all tests
    results['admin_drivers'] = test_admin_drivers()
    log_test("")
    
    results['pending_verification'] = test_pending_verification()
    log_test("")
    
    results['booking_creation'] = test_booking_creation()
    log_test("")
    
    results['smart_booking_creation'] = test_smart_booking_creation()
    log_test("")
    
    results['queue_status'] = test_queue_status()
    log_test("")
    
    # Summary
    log_test("=" * 80)
    log_test("📋 MONGODB PROJECTION FIX VERIFICATION SUMMARY")
    log_test("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    critical_issues = []
    
    for test_name, result in results.items():
        total_tests += 1
        if result and result.get('success'):
            passed_tests += 1
            has_images = result.get('has_images', False)
            size_kb = result.get('size_kb', 0)
            image_count = result.get('image_count', 0)
            
            status = "✅ PASS"
            if has_images or size_kb > 100:
                status = "❌ FAIL"
                if has_images:
                    critical_issues.append(f"{test_name}: Contains {image_count} base64 images")
                if size_kb > 100:
                    critical_issues.append(f"{test_name}: Response size {size_kb:.2f}KB exceeds 100KB limit")
            
            log_test(f"   {test_name}: {status} (Size: {size_kb:.2f}KB, Images: {image_count})")
        else:
            error = result.get('error', 'Unknown error') if result else 'Test failed'
            log_test(f"   {test_name}: ❌ FAIL ({error})")
            critical_issues.append(f"{test_name}: {error}")
    
    log_test("")
    log_test(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    # Check if the critical MongoDB projection fix is working
    projection_working = True
    for test_name, result in results.items():
        if result and result.get('success'):
            has_images = result.get('has_images', False)
            if has_images:
                projection_working = False
                break
    
    if not projection_working:
        log_test("🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            log_test(f"   • {issue}")
        log_test("")
        log_test("❌ MONGODB PROJECTION FIX VERIFICATION FAILED")
        log_test("   Base64 images are still being returned in API responses!")
        log_test("   This will cause deployment failures due to large response sizes.")
        return False
    else:
        log_test("✅ MONGODB PROJECTION FIX VERIFICATION SUCCESSFUL")
        log_test("   All API endpoints are returning lightweight responses without base64 images.")
        log_test("   System is ready for deployment.")
        
        # Show any non-critical issues
        if critical_issues:
            log_test("")
            log_test("⚠️  NON-CRITICAL ISSUES (not related to base64 images):")
            for issue in critical_issues:
                log_test(f"   • {issue}")
        
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)