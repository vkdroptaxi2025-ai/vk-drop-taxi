#!/usr/bin/env python3
"""
VK Drop Taxi - Detailed Admin Panel Driver API Analysis
Analyzing the document structure and verifying all requirements
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://ride-dispatch-app.preview.emergentagent.com/api"
TIMEOUT = 30

def log_test(message, status="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def analyze_driver_structures():
    """Analyze different driver document structures in the system"""
    log_test("🔍 Analyzing driver document structures in the system")
    
    try:
        # Get all drivers
        response = requests.get(f"{BASE_URL}/admin/drivers", timeout=TIMEOUT)
        if response.status_code != 200:
            log_test(f"❌ Failed to get drivers list: {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        drivers = data.get('drivers', [])
        
        log_test(f"Found {len(drivers)} drivers to analyze")
        
        # Analyze first few drivers for document structure
        structures_found = {}
        
        for i, driver in enumerate(drivers[:5]):  # Check first 5 drivers
            driver_id = driver.get('driver_id', f'driver_{i}')
            log_test(f"\n--- Analyzing Driver {driver_id} ---")
            
            # Get full details
            full_response = requests.get(f"{BASE_URL}/admin/driver/{driver_id}/full", timeout=TIMEOUT)
            if full_response.status_code != 200:
                log_test(f"❌ Failed to get full details for {driver_id}: {full_response.status_code}", "ERROR")
                continue
            
            full_data = full_response.json()
            full_driver = full_data.get('driver', {})
            
            # Check document structure
            structure_type = "unknown"
            
            # Check for nested structure
            if 'driver_documents' in full_driver or 'vehicle_documents' in full_driver:
                structure_type = "nested"
                log_test(f"✅ {driver_id}: Uses NESTED document structure")
                
                if 'driver_documents' in full_driver:
                    driver_docs = full_driver['driver_documents']
                    log_test(f"   Driver documents: {list(driver_docs.keys()) if isinstance(driver_docs, dict) else type(driver_docs)}")
                
                if 'vehicle_documents' in full_driver:
                    vehicle_docs = full_driver['vehicle_documents']
                    log_test(f"   Vehicle documents: {list(vehicle_docs.keys()) if isinstance(vehicle_docs, dict) else type(vehicle_docs)}")
                
                if 'driver_photos' in full_driver:
                    driver_photos = full_driver['driver_photos']
                    log_test(f"   Driver photos: {list(driver_photos.keys()) if isinstance(driver_photos, dict) else type(driver_photos)}")
                
                if 'vehicle_photos' in full_driver:
                    vehicle_photos = full_driver['vehicle_photos']
                    log_test(f"   Vehicle photos: {list(vehicle_photos.keys()) if isinstance(vehicle_photos, dict) else type(vehicle_photos)}")
            
            # Check for flat structure
            elif any(field in full_driver for field in ['aadhaar_front', 'aadhaar_back', 'license_front', 'license_back']):
                structure_type = "flat"
                log_test(f"✅ {driver_id}: Uses FLAT document structure")
                
                # List flat document fields
                flat_doc_fields = []
                for field in ['aadhaar_front', 'aadhaar_back', 'license_front', 'license_back', 
                             'rc_front', 'rc_back', 'insurance', 'permit', 'pollution_certificate',
                             'driver_photo', 'driver_with_vehicle_photo', 'vehicle_front_photo', 
                             'vehicle_back_photo', 'vehicle_left_photo', 'vehicle_right_photo',
                             'payment_screenshot']:
                    if field in full_driver and full_driver[field]:
                        flat_doc_fields.append(field)
                
                log_test(f"   Flat document fields: {flat_doc_fields}")
            
            structures_found[driver_id] = structure_type
            
            # Count base64 images
            response_text = full_response.text
            base64_count = response_text.count('data:image')
            log_test(f"   Base64 images found: {base64_count}")
        
        log_test(f"\n--- Structure Summary ---")
        for driver_id, structure in structures_found.items():
            log_test(f"{driver_id}: {structure}")
        
        return True
        
    except Exception as e:
        log_test(f"❌ Error analyzing structures: {str(e)}", "ERROR")
        return False

def test_comprehensive_requirements():
    """Test all the specific requirements from the review request"""
    log_test("🔍 Testing comprehensive requirements")
    
    results = {
        "list_lightweight": False,
        "list_no_base64": False,
        "list_has_names": False,
        "full_details_success": False,
        "full_details_has_documents": False,
        "full_details_has_photos": False
    }
    
    try:
        # Test 1: GET /api/admin/drivers - List view
        log_test("\n--- Testing List View Requirements ---")
        response = requests.get(f"{BASE_URL}/admin/drivers", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            drivers = data.get('drivers', [])
            
            # Check lightweight (response size)
            response_size_kb = len(response.content) / 1024
            if response_size_kb < 100:  # Less than 100KB is considered lightweight
                results["list_lightweight"] = True
                log_test(f"✅ List API is lightweight: {response_size_kb:.2f} KB")
            else:
                log_test(f"❌ List API is not lightweight: {response_size_kb:.2f} KB", "ERROR")
            
            # Check no base64 images
            base64_count = response.text.count('data:image')
            if base64_count == 0:
                results["list_no_base64"] = True
                log_test("✅ List API contains NO base64 images")
            else:
                log_test(f"❌ List API contains {base64_count} base64 images", "ERROR")
            
            # Check has names in full_name field
            if drivers and 'full_name' in drivers[0]:
                results["list_has_names"] = True
                log_test("✅ List API returns names in 'full_name' field")
                log_test(f"   Sample names: {[d.get('full_name', 'N/A') for d in drivers[:3]]}")
            else:
                log_test("❌ List API does not have 'full_name' field", "ERROR")
        
        # Test 2: GET /api/admin/driver/{driver_id}/full - Full details view
        if drivers:
            log_test("\n--- Testing Full Details View Requirements ---")
            test_driver_id = drivers[0]['driver_id']
            
            full_response = requests.get(f"{BASE_URL}/admin/driver/{test_driver_id}/full", timeout=TIMEOUT)
            
            if full_response.status_code == 200:
                results["full_details_success"] = True
                log_test("✅ Full details API returns SUCCESS")
                
                full_data = full_response.json()
                driver = full_data.get('driver', {})
                
                # Check for documents (either nested or flat structure)
                document_fields_found = []
                
                # Check nested structure
                if 'driver_documents' in driver:
                    document_fields_found.append('driver_documents')
                if 'vehicle_documents' in driver:
                    document_fields_found.append('vehicle_documents')
                
                # Check flat structure
                flat_doc_fields = ['aadhaar_front', 'aadhaar_back', 'license_front', 'license_back',
                                 'rc_front', 'rc_back', 'insurance', 'permit', 'pollution_certificate']
                found_flat_docs = [field for field in flat_doc_fields if field in driver and driver[field]]
                
                if document_fields_found or found_flat_docs:
                    results["full_details_has_documents"] = True
                    log_test("✅ Full details API includes documents")
                    if document_fields_found:
                        log_test(f"   Nested document fields: {document_fields_found}")
                    if found_flat_docs:
                        log_test(f"   Flat document fields: {found_flat_docs}")
                else:
                    log_test("❌ Full details API missing documents", "ERROR")
                
                # Check for photos (either nested or flat structure)
                photo_fields_found = []
                
                # Check nested structure
                if 'driver_photos' in driver:
                    photo_fields_found.append('driver_photos')
                if 'vehicle_photos' in driver:
                    photo_fields_found.append('vehicle_photos')
                
                # Check flat structure
                flat_photo_fields = ['driver_photo', 'driver_with_vehicle_photo', 'vehicle_front_photo',
                                   'vehicle_back_photo', 'vehicle_left_photo', 'vehicle_right_photo']
                found_flat_photos = [field for field in flat_photo_fields if field in driver and driver[field]]
                
                if photo_fields_found or found_flat_photos:
                    results["full_details_has_photos"] = True
                    log_test("✅ Full details API includes photos")
                    if photo_fields_found:
                        log_test(f"   Nested photo fields: {photo_fields_found}")
                    if found_flat_photos:
                        log_test(f"   Flat photo fields: {found_flat_photos}")
                else:
                    log_test("❌ Full details API missing photos", "ERROR")
                
                # Check payment screenshot
                if 'payment_screenshot' in driver and driver['payment_screenshot']:
                    log_test("✅ Full details API includes payment screenshot")
                elif 'payment' in driver and isinstance(driver['payment'], dict) and 'screenshot' in driver['payment']:
                    log_test("✅ Full details API includes payment screenshot (nested)")
                else:
                    log_test("⚠️  Full details API missing payment screenshot (may be optional)", "WARN")
            
            else:
                log_test(f"❌ Full details API failed: {full_response.status_code}", "ERROR")
    
    except Exception as e:
        log_test(f"❌ Error in comprehensive testing: {str(e)}", "ERROR")
    
    return results

def main():
    """Main execution"""
    log_test("🚀 Starting Detailed Admin Panel Driver API Analysis")
    log_test(f"Base URL: {BASE_URL}")
    
    # Analyze document structures
    log_test("\n" + "="*60)
    log_test("DOCUMENT STRUCTURE ANALYSIS")
    log_test("="*60)
    analyze_driver_structures()
    
    # Test comprehensive requirements
    log_test("\n" + "="*60)
    log_test("COMPREHENSIVE REQUIREMENTS TESTING")
    log_test("="*60)
    results = test_comprehensive_requirements()
    
    # Summary
    log_test("\n" + "="*60)
    log_test("FINAL VERIFICATION SUMMARY")
    log_test("="*60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    log_test(f"Requirements Status ({passed_tests}/{total_tests} passed):")
    
    for requirement, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        log_test(f"  {requirement}: {status}")
    
    if passed_tests == total_tests:
        log_test("\n🟢 ALL REQUIREMENTS VERIFIED SUCCESSFULLY", "SUCCESS")
        sys.exit(0)
    else:
        log_test(f"\n🔴 {total_tests - passed_tests} REQUIREMENTS FAILED", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()