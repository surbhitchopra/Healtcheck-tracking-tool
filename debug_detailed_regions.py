#!/usr/bin/env python
"""
Detailed debugging of region validation behavior
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Import the validation function
from HealthCheck_app.views import validate_customer_technology_match

def debug_region_detection():
    """Debug region detection logic step by step"""
    
    print("=" * 80)
    print("DETAILED REGION VALIDATION DEBUGGING")
    print("=" * 80)
    
    # Test cases that should FAIL (cross-region uploads)
    test_cases = [
        ("BSNL North DWDM", "BSNL_East_DWDM_Report.xlsx", False),
        ("BSNL North DWDM", "BSNL_East_Zone_Report.xlsx", False),
        ("BSNL East DWDM", "BSNL_North_DWDM_Report.xlsx", False),
        ("BSNL South Zone", "BSNL_West_Reports.xlsx", False),
        ("BSNL West Circle", "BSNL_South_Network_Report.xlsx", False),
    ]
    
    # Test cases that should PASS (same region uploads)
    pass_cases = [
        ("BSNL North DWDM", "BSNL_North_DWDM_Report.xlsx", True),
        ("BSNL East Zone", "BSNL_East_Network_Report.xlsx", True),
        ("BSNL South DWDM", "BSNL_South_Zone_Report.xlsx", True),
        ("BSNL West Circle", "BSNL_West_Reports.xlsx", True),
    ]
    
    all_cases = test_cases + pass_cases
    
    failed_validations = []
    
    for customer_name, filename, expected_valid in all_cases:
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {customer_name} <- {filename}")
        print(f"   Expected: {'✅ PASS' if expected_valid else '❌ FAIL'}")
        
        # Call validation
        result = validate_customer_technology_match(customer_name, filename)
        actual_valid = result['valid']
        
        # Check if result matches expectation
        if actual_valid == expected_valid:
            status = "✅ CORRECT"
            print(f"   Actual: {'✅ PASS' if actual_valid else '❌ FAIL'} - {status}")
        else:
            status = "🚨 WRONG!"
            print(f"   Actual: {'✅ PASS' if actual_valid else '❌ FAIL'} - {status}")
            failed_validations.append((customer_name, filename, expected_valid, actual_valid))
        
        # Show detailed error for failed cases
        if not actual_valid:
            error_preview = result['error'][:150].replace('\n', ' ')
            print(f"   Error: {error_preview}...")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    if failed_validations:
        print(f"🚨 FOUND {len(failed_validations)} VALIDATION ISSUES:")
        for customer, filename, expected, actual in failed_validations:
            print(f"   - {customer} <- {filename}")
            print(f"     Expected: {'PASS' if expected else 'FAIL'}, Got: {'PASS' if actual else 'FAIL'}")
    else:
        print("✅ ALL VALIDATIONS WORKING CORRECTLY!")
    
    return failed_validations

if __name__ == "__main__":
    debug_region_detection()
