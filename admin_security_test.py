#!/usr/bin/env python3
"""
VK Drop Taxi - Admin Security Testing (FOCUSED)
Testing the NEW admin security feature specifically
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8001/api"
MOCK_OTP = "123456"

def test_admin_security():
    """Test admin security restrictions"""
    print("🔥 TESTING ADMIN SECURITY (NEW FEATURE)")
    
    results = []
    
    # Test 1: Authorized admin phone (9345538164) + OTP 123456 → Should succeed
    print("\n1. Testing authorized admin login (9345538164)...")
    try:
        # Send OTP
        response = requests.post(f"{BASE_URL}/auth/send-otp", json={
            "phone": "9345538164",
            "role": "admin"
        }, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ OTP sent successfully")
            
            # Verify OTP - Should succeed
            response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
                "phone": "9345538164",
                "otp": MOCK_OTP,
                "role": "admin"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("user", {}).get("role") == "admin":
                    print("   ✅ PASS: Authorized admin login successful")
                    results.append(("Authorized Admin Login", True, "Login successful"))
                else:
                    print(f"   ❌ FAIL: Login failed: {data}")
                    results.append(("Authorized Admin Login", False, f"Login failed: {data}"))
            else:
                print(f"   ❌ FAIL: OTP verify failed: {response.status_code}")
                results.append(("Authorized Admin Login", False, f"OTP verify failed: {response.status_code}"))
        else:
            print(f"   ❌ FAIL: OTP send failed: {response.status_code}")
            results.append(("Authorized Admin Login", False, f"OTP send failed: {response.status_code}"))
    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        results.append(("Authorized Admin Login", False, f"Exception: {e}"))
    
    # Test 2: Unauthorized phone (9876543210) + OTP 123456 → Should get "Access Denied" (403)
    print("\n2. Testing unauthorized admin login (9876543210)...")
    try:
        # Send OTP
        response = requests.post(f"{BASE_URL}/auth/send-otp", json={
            "phone": "9876543210",
            "role": "admin"
        }, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ OTP sent successfully")
            
            # Verify OTP - Should get 403 Access Denied
            response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
                "phone": "9876543210",
                "otp": MOCK_OTP,
                "role": "admin"
            }, timeout=5)
            
            if response.status_code == 403:
                data = response.json()
                if "Access Denied" in data.get("detail", ""):
                    print("   ✅ PASS: Correctly denied access with 403")
                    results.append(("Unauthorized Admin Login 1", True, "Correctly denied access"))
                else:
                    print(f"   ❌ FAIL: Wrong error message: {data}")
                    results.append(("Unauthorized Admin Login 1", False, f"Wrong error message: {data}"))
            else:
                print(f"   ❌ FAIL: Expected 403, got: {response.status_code}")
                results.append(("Unauthorized Admin Login 1", False, f"Expected 403, got: {response.status_code}"))
        else:
            print(f"   ❌ FAIL: OTP send failed: {response.status_code}")
            results.append(("Unauthorized Admin Login 1", False, f"OTP send failed: {response.status_code}"))
    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        results.append(("Unauthorized Admin Login 1", False, f"Exception: {e}"))
    
    # Test 3: Another unauthorized phone (1234567890) + OTP 123456 → Should get "Access Denied" (403)
    print("\n3. Testing unauthorized admin login (1234567890)...")
    try:
        # Send OTP
        response = requests.post(f"{BASE_URL}/auth/send-otp", json={
            "phone": "1234567890",
            "role": "admin"
        }, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ OTP sent successfully")
            
            # Verify OTP - Should get 403 Access Denied
            response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
                "phone": "1234567890",
                "otp": MOCK_OTP,
                "role": "admin"
            }, timeout=5)
            
            if response.status_code == 403:
                data = response.json()
                if "Access Denied" in data.get("detail", ""):
                    print("   ✅ PASS: Correctly denied access with 403")
                    results.append(("Unauthorized Admin Login 2", True, "Correctly denied access"))
                else:
                    print(f"   ❌ FAIL: Wrong error message: {data}")
                    results.append(("Unauthorized Admin Login 2", False, f"Wrong error message: {data}"))
            else:
                print(f"   ❌ FAIL: Expected 403, got: {response.status_code}")
                results.append(("Unauthorized Admin Login 2", False, f"Expected 403, got: {response.status_code}"))
        else:
            print(f"   ❌ FAIL: OTP send failed: {response.status_code}")
            results.append(("Unauthorized Admin Login 2", False, f"OTP send failed: {response.status_code}"))
    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        results.append(("Unauthorized Admin Login 2", False, f"Exception: {e}"))
    
    # Test 4: Verify customer login still works normally
    print("\n4. Testing customer login still works...")
    try:
        test_phone = "9191919191"
        
        # Send OTP
        response = requests.post(f"{BASE_URL}/auth/send-otp", json={
            "phone": test_phone,
            "role": "customer"
        }, timeout=5)
        
        if response.status_code == 200:
            # Verify OTP
            response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
                "phone": test_phone,
                "otp": MOCK_OTP,
                "role": "customer"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("   ✅ PASS: Customer login working normally")
                    results.append(("Customer Login Still Works", True, "Customer login working"))
                else:
                    print(f"   ❌ FAIL: Customer login issue: {data}")
                    results.append(("Customer Login Still Works", False, f"Customer login issue: {data}"))
            else:
                print(f"   ❌ FAIL: Customer OTP verify failed: {response.status_code}")
                results.append(("Customer Login Still Works", False, f"OTP verify failed: {response.status_code}"))
        else:
            print(f"   ❌ FAIL: Customer OTP send failed: {response.status_code}")
            results.append(("Customer Login Still Works", False, f"OTP send failed: {response.status_code}"))
    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        results.append(("Customer Login Still Works", False, f"Exception: {e}"))
    
    # Test 5: Verify driver login still works normally
    print("\n5. Testing driver login still works...")
    try:
        test_phone = "9292929292"
        
        # Send OTP
        response = requests.post(f"{BASE_URL}/auth/send-otp", json={
            "phone": test_phone,
            "role": "driver"
        }, timeout=5)
        
        if response.status_code == 200:
            # Verify OTP
            response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
                "phone": test_phone,
                "otp": MOCK_OTP,
                "role": "driver"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("   ✅ PASS: Driver login working normally")
                    results.append(("Driver Login Still Works", True, "Driver login working"))
                else:
                    print(f"   ❌ FAIL: Driver login issue: {data}")
                    results.append(("Driver Login Still Works", False, f"Driver login issue: {data}"))
            else:
                print(f"   ❌ FAIL: Driver OTP verify failed: {response.status_code}")
                results.append(("Driver Login Still Works", False, f"OTP verify failed: {response.status_code}"))
        else:
            print(f"   ❌ FAIL: Driver OTP send failed: {response.status_code}")
            results.append(("Driver Login Still Works", False, f"OTP send failed: {response.status_code}"))
    except Exception as e:
        print(f"   ❌ FAIL: Exception: {e}")
        results.append(("Driver Login Still Works", False, f"Exception: {e}"))
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 ADMIN SECURITY TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = len([r for r in results if r[1]])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for test_name, success, message in results:
            if not success:
                print(f"  - {test_name}: {message}")
    
    print("\n✅ ADMIN SECURITY STATUS:")
    admin_tests = [r for r in results if "Admin Login" in r[0]]
    if admin_tests:
        admin_passed = len([r for r in admin_tests if r[1]])
        admin_total = len(admin_tests)
        status = "✅ WORKING" if admin_passed == admin_total else "❌ ISSUES"
        print(f"  {status} Admin Security: {admin_passed}/{admin_total} tests passed")
    
    return results

if __name__ == "__main__":
    test_admin_security()