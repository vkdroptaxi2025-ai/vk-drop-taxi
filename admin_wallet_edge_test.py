#!/usr/bin/env python3
"""
VK Drop Taxi - Admin Wallet Edge Case Testing
Testing edge cases for the Admin Wallet functionality, specifically testing deduction that would go below zero.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
TIMEOUT = 30
DRIVER_ID = "VKDRV1025"

def log_test(message, status="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def get_current_balance():
    """Get current wallet balance"""
    try:
        response = requests.get(f"{BASE_URL}/admin/driver/{DRIVER_ID}/full", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'driver' in data:
                return data['driver'].get('wallet_balance', 0)
    except:
        pass
    return None

def test_deduct_more_than_balance():
    """Test deducting more money than available - should not go below 0"""
    log_test("🔍 Testing DEDUCT operation that exceeds current balance")
    
    # Get current balance first
    current_balance = get_current_balance()
    if current_balance is None:
        log_test("❌ FAILED: Could not get current balance", "ERROR")
        return False
    
    log_test(f"Current balance: ₹{current_balance}")
    
    # Try to deduct more than current balance
    deduct_amount = current_balance + 1000  # Deduct more than available
    
    payload = {
        "driver_id": DRIVER_ID,
        "amount": deduct_amount,
        "type": "deduct"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/wallet/update", 
            json=payload, 
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        log_test(f"Request: Deduct ₹{deduct_amount} from ₹{current_balance}")
        log_test(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            log_test(f"❌ FAILED: Expected 200, got {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        log_test(f"Response Data: {json.dumps(data, indent=2)}")
        
        if not data.get('success'):
            log_test("❌ FAILED: Response success is not True", "ERROR")
            return False
        
        new_balance = data.get('new_balance', -1)
        
        # Verify balance didn't go negative
        if new_balance < 0:
            log_test(f"❌ FAILED: Balance went negative: ₹{new_balance}", "ERROR")
            return False
        
        # Verify balance is 0 (since we deducted more than available)
        if new_balance != 0:
            log_test(f"❌ FAILED: Expected balance to be ₹0, got ₹{new_balance}", "ERROR")
            return False
        
        log_test(f"✅ PASSED: Balance correctly capped at ₹0 when deducting ₹{deduct_amount} from ₹{current_balance}")
        return True
        
    except Exception as e:
        log_test(f"❌ FAILED: Error - {str(e)}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test("🚀 Starting VK Drop Taxi Admin Wallet Edge Case Testing")
    log_test(f"Base URL: {BASE_URL}")
    log_test(f"Target Driver ID: {DRIVER_ID}")
    
    # Test edge case: deduct more than balance
    log_test("\n" + "="*80)
    log_test("EDGE CASE TEST: Deduct more than available balance")
    log_test("="*80)
    
    success = test_deduct_more_than_balance()
    
    # Summary
    log_test("\n" + "="*80)
    log_test("EDGE CASE TEST SUMMARY")
    log_test("="*80)
    
    if success:
        log_test("✅ Edge case test PASSED - Balance correctly prevented from going negative")
        log_test("🟢 OVERALL STATUS: PASSED", "SUCCESS")
        sys.exit(0)
    else:
        log_test("❌ Edge case test FAILED")
        log_test("🔴 OVERALL STATUS: FAILED", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()