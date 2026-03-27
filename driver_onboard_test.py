#!/usr/bin/env python3
"""
VK Drop Taxi - Driver Onboarding API Test
Testing POST /api/driver/onboard endpoint with comprehensive payload
"""

import requests
import json
import sys
import time
from datetime import datetime

# Use the production backend URL from frontend/.env
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_test_payload():
    """Create comprehensive test payload for driver onboarding"""
    # Small placeholder base64 strings for images
    placeholder_image = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
    
    payload = {
        "basic_details": {
            "full_name": "Rajesh Kumar",
            "phone": "9876500001",
            "address": "123 MG Road, Bangalore, Karnataka 560001",
            "aadhaar_number": "123456789012",
            "pan_number": "ABCDE1234F",
            "driving_license_number": "KA0320110012345",
            "driving_experience_years": 5
        },
        "driver_photos": {
            "driver_photo": placeholder_image,
            "driver_with_vehicle_photo": placeholder_image
        },
        "driver_documents": {
            "aadhaar_front": placeholder_image,
            "aadhaar_back": placeholder_image,
            "license_front": placeholder_image,
            "license_back": placeholder_image
        },
        "vehicle_details": {
            "vehicle_type": "sedan",
            "vehicle_number": "KA01AB1234",
            "vehicle_model": "Maruti Suzuki Dzire",
            "vehicle_year": 2020
        },
        "vehicle_documents": {
            "rc_front": placeholder_image,
            "rc_back": placeholder_image,
            "insurance": placeholder_image,
            "permit": placeholder_image,
            "pollution_certificate": placeholder_image
        },
        "vehicle_photos": {
            "front_photo": placeholder_image,
            "back_photo": placeholder_image,
            "left_photo": placeholder_image,
            "right_photo": placeholder_image
        },
        "payment": {
            "amount": 500,
            "screenshot": placeholder_image
        }
    }
    
    return payload

def test_driver_onboard_api():
    """Test POST /api/driver/onboard endpoint"""
    log_test("🚀 TESTING DRIVER ONBOARDING API")
    log_test(f"🔗 Testing against: {BASE_URL}")
    log_test("=" * 80)
    
    # Create test payload
    log_test("📋 Creating comprehensive test payload...")
    payload = create_test_payload()
    log_test(f"   Phone number: {payload['basic_details']['phone']}")
    log_test(f"   Driver name: {payload['basic_details']['full_name']}")
    log_test(f"   Vehicle: {payload['vehicle_details']['vehicle_model']} ({payload['vehicle_details']['vehicle_number']})")
    log_test(f"   Payment amount: ₹{payload['payment']['amount']}")
    
    # Test the API endpoint
    log_test("")
    log_test("🔍 Testing POST /api/driver/onboard")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/driver/onboard",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        log_test(f"   Status Code: {response.status_code}")
        log_test(f"   Response Time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"   Response Size: {len(response.text)} bytes")
            
            # Verify response structure
            log_test("")
            log_test("✅ RESPONSE VERIFICATION:")
            
            # Check success field
            success = data.get('success', False)
            log_test(f"   ✓ success: {success}")
            
            # Check driver_id field
            driver_id = data.get('driver_id', '')
            if driver_id.startswith('VKDRV'):
                log_test(f"   ✓ driver_id: {driver_id} (correct VKDRV format)")
            else:
                log_test(f"   ❌ driver_id: {driver_id} (should start with VKDRV)")
            
            # Check approval_status field
            approval_status = data.get('approval_status', '')
            if approval_status == 'pending':
                log_test(f"   ✓ approval_status: {approval_status}")
            else:
                log_test(f"   ❌ approval_status: {approval_status} (should be 'pending')")
            
            # Check message field
            message = data.get('message', '')
            log_test(f"   ✓ message: {message}")
            
            # Check response time
            if response_time < 10:
                log_test(f"   ✓ Response time: {response_time:.2f}s (< 10s requirement)")
            else:
                log_test(f"   ⚠️  Response time: {response_time:.2f}s (exceeds 10s requirement)")
            
            # Overall verification
            log_test("")
            if (success and 
                driver_id.startswith('VKDRV') and 
                approval_status == 'pending' and
                response_time < 10):
                log_test("🎉 DRIVER ONBOARDING API TEST: ✅ PASSED")
                log_test("   All requirements met:")
                log_test("   • API returns 200 status ✓")
                log_test("   • Response contains success: true ✓")
                log_test("   • Response contains driver_id starting with 'VKDRV' ✓")
                log_test("   • Response contains approval_status: 'pending' ✓")
                log_test("   • Response time < 10 seconds ✓")
                
                return {
                    'success': True,
                    'driver_id': driver_id,
                    'approval_status': approval_status,
                    'response_time': response_time,
                    'test_phone': payload['basic_details']['phone']
                }
            else:
                log_test("❌ DRIVER ONBOARDING API TEST: FAILED")
                log_test("   Some requirements not met - see details above")
                return {
                    'success': False,
                    'error': 'Response validation failed',
                    'driver_id': driver_id,
                    'approval_status': approval_status,
                    'response_time': response_time
                }
        
        else:
            log_test(f"   ❌ FAIL: HTTP {response.status_code}")
            log_test(f"   Response: {response.text[:500]}...")
            return {
                'success': False,
                'error': f"HTTP {response.status_code}",
                'response_text': response.text[:500]
            }
            
    except Exception as e:
        log_test(f"   ❌ FAIL: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def test_driver_status_check(driver_id):
    """Test driver status check after onboarding"""
    log_test("")
    log_test("🔍 Testing driver status check...")
    
    try:
        response = requests.get(f"{BASE_URL}/driver/{driver_id}/status", timeout=10)
        log_test(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('approval_status', '')
            log_test(f"   ✓ Driver status: {status}")
            return True
        else:
            log_test(f"   ❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        log_test(f"   ❌ Status check error: {str(e)}")
        return False

def main():
    """Run driver onboarding API test"""
    log_test("🎯 VK DROP TAXI - DRIVER ONBOARDING API TEST")
    log_test("=" * 80)
    
    # Test the onboarding API
    result = test_driver_onboard_api()
    
    # If successful, test status check
    if result.get('success') and result.get('driver_id'):
        test_driver_status_check(result['driver_id'])
    
    log_test("")
    log_test("=" * 80)
    log_test("📋 TEST SUMMARY")
    log_test("=" * 80)
    
    if result.get('success'):
        log_test("✅ DRIVER ONBOARDING API TEST PASSED")
        log_test(f"   Driver ID: {result.get('driver_id')}")
        log_test(f"   Approval Status: {result.get('approval_status')}")
        log_test(f"   Response Time: {result.get('response_time', 0):.2f}s")
        log_test(f"   Test Phone: {result.get('test_phone')}")
        log_test("")
        log_test("🎯 VERIFICATION COMPLETE:")
        log_test("   • Endpoint responds correctly ✓")
        log_test("   • Returns proper driver_id format ✓")
        log_test("   • Sets approval_status to pending ✓")
        log_test("   • Response time within limits ✓")
        return True
    else:
        log_test("❌ DRIVER ONBOARDING API TEST FAILED")
        log_test(f"   Error: {result.get('error', 'Unknown error')}")
        if result.get('driver_id'):
            log_test(f"   Driver ID: {result.get('driver_id')}")
        if result.get('response_time'):
            log_test(f"   Response Time: {result.get('response_time'):.2f}s")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)