#!/usr/bin/env python3
"""
VK Drop Taxi - Admin Wallet Functionality Testing
Testing the Admin Wallet functionality for VK Drop Taxi as requested in the review.

Test endpoints:
1. GET /api/admin/driver/VKDRV1025/full - Verify response includes wallet_balance field
2. POST /api/admin/wallet/update - Test ADD operation
3. POST /api/admin/wallet/update - Test DEDUCT operation  
4. GET /api/admin/driver/VKDRV1025/full again - Verify wallet_balance reflects changes
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
TIMEOUT = 30
DRIVER_ID = "VKDRV1025"

def log_test(message, status="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_get_driver_full_details(test_name="Initial"):
    """
    Test GET /api/admin/driver/VKDRV1025/full
    Verify response includes wallet_balance field and success: true
    """
    log_test(f"🔍 Testing GET /api/admin/driver/{DRIVER_ID}/full ({test_name})")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/driver/{DRIVER_ID}/full", timeout=TIMEOUT)
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Size: {len(response.content)} bytes ({len(response.content)/1024:.2f} KB)")
        
        if response.status_code != 200:
            log_test(f"❌ FAILED: Expected 200, got {response.status_code}", "ERROR")
            log_test(f"Response: {response.text}", "ERROR")
            return False, None
        
        data = response.json()
        
        # Check response structure
        if not data.get('success'):
            log_test("❌ FAILED: Response success is not True", "ERROR")
            return False, None
        
        if 'driver' not in data:
            log_test("❌ FAILED: No 'driver' field in response", "ERROR")
            return False, None
        
        driver = data['driver']
        
        # Check for wallet_balance field
        if 'wallet_balance' not in driver:
            log_test("❌ FAILED: No 'wallet_balance' field in driver response", "ERROR")
            return False, None
        
        wallet_balance = driver['wallet_balance']
        log_test(f"✅ PASSED: Found wallet_balance field: ₹{wallet_balance}")
        log_test(f"✅ PASSED: Response has success: true")
        
        # Log driver basic info
        log_test(f"Driver Info: {driver.get('full_name', 'N/A')} ({driver.get('driver_id', 'N/A')})")
        log_test(f"Phone: {driver.get('phone', 'N/A')}")
        log_test(f"Approval Status: {driver.get('approval_status', 'N/A')}")
        
        return True, wallet_balance
        
    except requests.exceptions.RequestException as e:
        log_test(f"❌ FAILED: Request error - {str(e)}", "ERROR")
        return False, None
    except json.JSONDecodeError as e:
        log_test(f"❌ FAILED: JSON decode error - {str(e)}", "ERROR")
        return False, None
    except Exception as e:
        log_test(f"❌ FAILED: Unexpected error - {str(e)}", "ERROR")
        return False, None

def test_wallet_add_operation(amount=500):
    """
    Test POST /api/admin/wallet/update - ADD operation
    Body: {"driver_id": "VKDRV1025", "amount": 500, "type": "add"}
    Verify returns success: true, previous_balance, new_balance, amount, type
    """
    log_test(f"🔍 Testing POST /api/admin/wallet/update - ADD ₹{amount}")
    
    payload = {
        "driver_id": DRIVER_ID,
        "amount": amount,
        "type": "add"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/wallet/update", 
            json=payload, 
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        log_test(f"Request Payload: {json.dumps(payload, indent=2)}")
        log_test(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            log_test(f"❌ FAILED: Expected 200, got {response.status_code}", "ERROR")
            log_test(f"Response: {response.text}", "ERROR")
            return False, None, None
        
        data = response.json()
        log_test(f"Response Data: {json.dumps(data, indent=2)}")
        
        # Check response structure
        if not data.get('success'):
            log_test("❌ FAILED: Response success is not True", "ERROR")
            return False, None, None
        
        # Check required fields
        required_fields = ['previous_balance', 'new_balance', 'amount', 'type']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            log_test(f"❌ FAILED: Missing required fields: {missing_fields}", "ERROR")
            return False, None, None
        
        # Verify values
        previous_balance = data['previous_balance']
        new_balance = data['new_balance']
        returned_amount = data['amount']
        returned_type = data['type']
        
        log_test(f"✅ PASSED: Response has success: true")
        log_test(f"✅ PASSED: Previous balance: ₹{previous_balance}")
        log_test(f"✅ PASSED: New balance: ₹{new_balance}")
        log_test(f"✅ PASSED: Amount: ₹{returned_amount}")
        log_test(f"✅ PASSED: Type: {returned_type}")
        
        # Verify calculation
        expected_new_balance = previous_balance + amount
        if abs(new_balance - expected_new_balance) < 0.01:  # Allow for floating point precision
            log_test(f"✅ PASSED: Balance calculation correct: {previous_balance} + {amount} = {new_balance}")
        else:
            log_test(f"❌ FAILED: Balance calculation incorrect: {previous_balance} + {amount} should be {expected_new_balance}, got {new_balance}", "ERROR")
            return False, None, None
        
        return True, previous_balance, new_balance
        
    except requests.exceptions.RequestException as e:
        log_test(f"❌ FAILED: Request error - {str(e)}", "ERROR")
        return False, None, None
    except json.JSONDecodeError as e:
        log_test(f"❌ FAILED: JSON decode error - {str(e)}", "ERROR")
        return False, None, None
    except Exception as e:
        log_test(f"❌ FAILED: Unexpected error - {str(e)}", "ERROR")
        return False, None, None

def test_wallet_deduct_operation(amount=200):
    """
    Test POST /api/admin/wallet/update - DEDUCT operation
    Body: {"driver_id": "VKDRV1025", "amount": 200, "type": "deduct"}
    Verify returns success: true, new_balance = previous_balance - 200 (but not below 0)
    """
    log_test(f"🔍 Testing POST /api/admin/wallet/update - DEDUCT ₹{amount}")
    
    payload = {
        "driver_id": DRIVER_ID,
        "amount": amount,
        "type": "deduct"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/wallet/update", 
            json=payload, 
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        log_test(f"Request Payload: {json.dumps(payload, indent=2)}")
        log_test(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            log_test(f"❌ FAILED: Expected 200, got {response.status_code}", "ERROR")
            log_test(f"Response: {response.text}", "ERROR")
            return False, None, None
        
        data = response.json()
        log_test(f"Response Data: {json.dumps(data, indent=2)}")
        
        # Check response structure
        if not data.get('success'):
            log_test("❌ FAILED: Response success is not True", "ERROR")
            return False, None, None
        
        # Check required fields
        required_fields = ['previous_balance', 'new_balance', 'amount', 'type']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            log_test(f"❌ FAILED: Missing required fields: {missing_fields}", "ERROR")
            return False, None, None
        
        # Verify values
        previous_balance = data['previous_balance']
        new_balance = data['new_balance']
        returned_amount = data['amount']
        returned_type = data['type']
        
        log_test(f"✅ PASSED: Response has success: true")
        log_test(f"✅ PASSED: Previous balance: ₹{previous_balance}")
        log_test(f"✅ PASSED: New balance: ₹{new_balance}")
        log_test(f"✅ PASSED: Amount: ₹{returned_amount}")
        log_test(f"✅ PASSED: Type: {returned_type}")
        
        # Verify calculation (should not go below 0)
        expected_new_balance = max(0, previous_balance - amount)
        if abs(new_balance - expected_new_balance) < 0.01:  # Allow for floating point precision
            log_test(f"✅ PASSED: Balance calculation correct: max(0, {previous_balance} - {amount}) = {new_balance}")
        else:
            log_test(f"❌ FAILED: Balance calculation incorrect: max(0, {previous_balance} - {amount}) should be {expected_new_balance}, got {new_balance}", "ERROR")
            return False, None, None
        
        # Verify balance doesn't go negative
        if new_balance < 0:
            log_test(f"❌ FAILED: Balance went negative: {new_balance}", "ERROR")
            return False, None, None
        else:
            log_test(f"✅ PASSED: Balance correctly prevented from going negative")
        
        return True, previous_balance, new_balance
        
    except requests.exceptions.RequestException as e:
        log_test(f"❌ FAILED: Request error - {str(e)}", "ERROR")
        return False, None, None
    except json.JSONDecodeError as e:
        log_test(f"❌ FAILED: JSON decode error - {str(e)}", "ERROR")
        return False, None, None
    except Exception as e:
        log_test(f"❌ FAILED: Unexpected error - {str(e)}", "ERROR")
        return False, None, None

def main():
    """Main test execution"""
    log_test("🚀 Starting VK Drop Taxi Admin Wallet Functionality Testing")
    log_test(f"Base URL: {BASE_URL}")
    log_test(f"Target Driver ID: {DRIVER_ID}")
    
    test_results = []
    
    # Test 1: Get initial driver details and wallet balance
    log_test("\n" + "="*80)
    log_test("TEST 1: GET /api/admin/driver/VKDRV1025/full (Initial)")
    log_test("="*80)
    
    initial_success, initial_balance = test_get_driver_full_details("Initial")
    if initial_success:
        test_results.append("✅ Initial driver details test PASSED")
        log_test(f"Initial wallet balance: ₹{initial_balance}")
    else:
        test_results.append("❌ Initial driver details test FAILED")
        log_test("❌ Cannot proceed with wallet tests without initial balance", "ERROR")
        # Print summary and exit
        log_test("\n" + "="*80)
        log_test("TEST SUMMARY")
        log_test("="*80)
        for result in test_results:
            log_test(result)
        log_test("🔴 OVERALL STATUS: FAILED - Cannot access driver details", "ERROR")
        sys.exit(1)
    
    # Test 2: Add money to wallet
    log_test("\n" + "="*80)
    log_test("TEST 2: POST /api/admin/wallet/update - ADD ₹500")
    log_test("="*80)
    
    add_success, add_prev_balance, add_new_balance = test_wallet_add_operation(500)
    if add_success:
        test_results.append("✅ Wallet ADD operation test PASSED")
    else:
        test_results.append("❌ Wallet ADD operation test FAILED")
    
    # Test 3: Deduct money from wallet
    log_test("\n" + "="*80)
    log_test("TEST 3: POST /api/admin/wallet/update - DEDUCT ₹200")
    log_test("="*80)
    
    deduct_success, deduct_prev_balance, deduct_new_balance = test_wallet_deduct_operation(200)
    if deduct_success:
        test_results.append("✅ Wallet DEDUCT operation test PASSED")
    else:
        test_results.append("❌ Wallet DEDUCT operation test FAILED")
    
    # Test 4: Get final driver details to verify changes
    log_test("\n" + "="*80)
    log_test("TEST 4: GET /api/admin/driver/VKDRV1025/full (Final)")
    log_test("="*80)
    
    final_success, final_balance = test_get_driver_full_details("Final")
    if final_success:
        test_results.append("✅ Final driver details test PASSED")
        
        # Verify the balance reflects the changes
        if add_success and deduct_success:
            expected_final_balance = initial_balance + 500 - 200  # +300 from initial
            if abs(final_balance - expected_final_balance) < 0.01:
                log_test(f"✅ PASSED: Final balance verification - Expected: ₹{expected_final_balance}, Got: ₹{final_balance}")
                test_results.append("✅ Balance change verification PASSED")
            else:
                log_test(f"❌ FAILED: Final balance verification - Expected: ₹{expected_final_balance}, Got: ₹{final_balance}", "ERROR")
                test_results.append("❌ Balance change verification FAILED")
        else:
            log_test("⚠️  Cannot verify balance changes due to previous test failures", "WARN")
    else:
        test_results.append("❌ Final driver details test FAILED")
    
    # Summary
    log_test("\n" + "="*80)
    log_test("TEST SUMMARY")
    log_test("="*80)
    
    for result in test_results:
        log_test(result)
    
    # Determine overall success
    failed_tests = [r for r in test_results if "❌" in r]
    passed_tests = [r for r in test_results if "✅" in r]
    
    log_test(f"\nOverall Results: {len(passed_tests)} PASSED, {len(failed_tests)} FAILED")
    
    # Detailed balance tracking
    if initial_success and final_success:
        balance_change = final_balance - initial_balance
        log_test(f"\nBalance Tracking:")
        log_test(f"  Initial Balance: ₹{initial_balance}")
        log_test(f"  Final Balance: ₹{final_balance}")
        log_test(f"  Net Change: ₹{balance_change}")
        log_test(f"  Expected Change: ₹300 (if both operations succeeded)")
    
    if failed_tests:
        log_test("🔴 OVERALL STATUS: FAILED", "ERROR")
        sys.exit(1)
    else:
        log_test("🟢 OVERALL STATUS: PASSED", "SUCCESS")
        sys.exit(0)

if __name__ == "__main__":
    main()