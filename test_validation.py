#!/usr/bin/env python3
"""
Test script to validate the customer technology match function
with region mismatch scenarios
"""

# Add the Django app to the path
import sys
import os
from pathlib import Path

# Add the project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')

import django
django.setup()

# Now we can import Django models and functions
from HealthCheck_app.views import validate_customer_technology_match

def test_region_mismatch():
    """Test the validation function with region mismatches"""
    
    print("=" * 60)
    print("TESTING REGION MISMATCH VALIDATION")
    print("=" * 60)
    
    # Test Case 1: North customer with South file
    print("\n🧪 TEST CASE 1: North DWDM customer with South filename")
    customer_name = "BSNL North DWDM"
    filename = "BSNL_South_DWDM_HealthCheck_Report.xlsx"
    
    result = validate_customer_technology_match(customer_name, filename)
    
    print(f"Customer: {customer_name}")
    print(f"Filename: {filename}")
    print(f"Expected: valid=False (region mismatch)")
    print(f"Actual Result: {result}")
    
    if result['valid']:
        print("❌ VALIDATION BUG CONFIRMED: Function returned valid=True for region mismatch!")
    else:
        print("✅ Validation working correctly: Region mismatch detected")
    
    print("\n" + "-" * 40)
    
    # Test Case 2: South customer with North file  
    print("\n🧪 TEST CASE 2: South DWDM customer with North filename")
    customer_name = "BSNL South DWDM"
    filename = "BSNL_North_DWDM_HealthCheck_Report.xlsx"
    
    result = validate_customer_technology_match(customer_name, filename)
    
    print(f"Customer: {customer_name}")
    print(f"Filename: {filename}")
    print(f"Expected: valid=False (region mismatch)")
    print(f"Actual Result: {result}")
    
    if result['valid']:
        print("❌ VALIDATION BUG CONFIRMED: Function returned valid=True for region mismatch!")
    else:
        print("✅ Validation working correctly: Region mismatch detected")
    
    print("\n" + "-" * 40)
    
    # Test Case 3: Correct match (should pass)
    print("\n🧪 TEST CASE 3: North DWDM customer with matching North filename")
    customer_name = "BSNL North DWDM"
    filename = "BSNL_North_DWDM_HealthCheck_Report.xlsx"
    
    result = validate_customer_technology_match(customer_name, filename)
    
    print(f"Customer: {customer_name}")
    print(f"Filename: {filename}")
    print(f"Expected: valid=True (correct match)")
    print(f"Actual Result: {result}")
    
    if result['valid']:
        print("✅ Validation working correctly: Correct match accepted")
    else:
        print("❌ VALIDATION BUG: Function returned valid=False for correct match!")
    
    print("\n" + "=" * 60)
    
    # Test Case 4: Generic customer without region
    print("\n🧪 TEST CASE 4: Generic customer (no region) with region-specific file")
    customer_name = "BSNL DWDM"  # No region specified
    filename = "BSNL_South_DWDM_HealthCheck_Report.xlsx"
    
    result = validate_customer_technology_match(customer_name, filename)
    
    print(f"Customer: {customer_name}")
    print(f"Filename: {filename}")
    print(f"Expected: valid=True (generic customer can accept any region)")
    print(f"Actual Result: {result}")
    
    if result['valid']:
        print("✅ Validation working correctly: Generic customer accepted region file")
    else:
        print("❌ VALIDATION BUG: Generic customer rejected region-specific file!")


if __name__ == "__main__":
    test_region_mismatch()
