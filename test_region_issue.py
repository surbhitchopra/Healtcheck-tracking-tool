#!/usr/bin/env python3
"""
Test script to reproduce the region validation issue
Customer: BSNL North DWDM
File: Something with "East" region
Expected: Should fail with region mismatch error
"""

import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.views import validate_customer_technology_match

def test_region_mismatch_issue():
    """Test the region validation issue that's causing problems"""
    
    print("🧪 TESTING REGION VALIDATION ISSUE")
    print("=" * 50)
    
    # Test case 1: Customer with North region, file with East region
    customer_name = "BSNL North DWDM"
    east_filename = "BSNL_East_DWDM_Reports_20250115.xlsx"
    
    print(f"🔍 Customer: '{customer_name}'")
    print(f"🔍 Filename: '{east_filename}'")
    print()
    
    # Test the validation
    print("Testing validation...")
    result = validate_customer_technology_match(customer_name, east_filename)
    
    print(f"✅ Valid: {result['valid']}")
    if not result['valid']:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Match Info: {result.get('match_info', 'N/A')}")
    
    print()
    print("=" * 50)
    
    # Test case 2: Same customer with North region file (should work)
    north_filename = "BSNL_North_DWDM_Reports_20250115.xlsx"
    
    print(f"🔍 Customer: '{customer_name}'")
    print(f"🔍 Filename: '{north_filename}'")
    print()
    
    print("Testing validation...")
    result2 = validate_customer_technology_match(customer_name, north_filename)
    
    print(f"✅ Valid: {result2['valid']}")
    if not result2['valid']:
        print(f"❌ Error: {result2['error']}")
    else:
        print(f"✅ Match Info: {result2.get('match_info', 'N/A')}")
    
    print()
    print("=" * 50)
    
    # Test case 3: Customer with no region, file with East region (should work)
    generic_customer = "BSNL DWDM"
    
    print(f"🔍 Customer: '{generic_customer}'")
    print(f"🔍 Filename: '{east_filename}'")
    print()
    
    print("Testing validation...")
    result3 = validate_customer_technology_match(generic_customer, east_filename)
    
    print(f"✅ Valid: {result3['valid']}")
    if not result3['valid']:
        print(f"❌ Error: {result3['error']}")
    else:
        print(f"✅ Match Info: {result3.get('match_info', 'N/A')}")

if __name__ == "__main__":
    test_region_mismatch_issue()
