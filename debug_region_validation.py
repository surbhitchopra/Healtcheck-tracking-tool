#!/usr/bin/env python3
"""
Debug script for region validation issue
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

def test_region_validation_debug():
    """Test the specific region validation issue"""
    
    print("=" * 60)
    print("DEBUG: REGION VALIDATION ISSUE")
    print("=" * 60)
    
    # Test Case: User's actual scenario
    print("\n🧪 USER'S REPORTED ISSUE:")
    customer_name = "BSNL North DWDM"
    filename = "BSNL_East_DWDM_Report.xlsx"  # East file to North customer
    
    print(f"Customer: {customer_name}")
    print(f"Filename: {filename}")
    print(f"Expected: Should FAIL (North customer cannot upload East files)")
    
    result = validate_customer_technology_match(customer_name, filename)
    print(f"Actual Result: {result}")
    
    if result['valid']:
        print("❌ BUG CONFIRMED: Validation incorrectly passed!")
        print("🔍 ANALYSIS: The function should detect North vs East mismatch")
    else:
        print("✅ Validation working correctly")
        print("🤔 This suggests the issue might be elsewhere")
    
    print("\n" + "-" * 50)
    
    # Test some variations to understand the issue
    test_cases = [
        ("BSNL North DWDM", "BSNL_South_DWDM_Report.xlsx"),
        ("BSNL East DWDM", "BSNL_North_DWDM_Report.xlsx"), 
        ("BSNL West DWDM", "BSNL_East_DWDM_Report.xlsx"),
        ("BSNL North DWDM", "BSNL_North_DWDM_Report.xlsx"),  # Should pass
        ("BSNL DWDM", "BSNL_East_DWDM_Report.xlsx"),  # Generic should pass
    ]
    
    print("\n🧪 ADDITIONAL TEST CASES:")
    for i, (customer, filename) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {customer} <- {filename}")
        result = validate_customer_technology_match(customer, filename)
        status = "✅ PASS" if result['valid'] else "❌ FAIL"
        print(f"Result: {status}")
        if not result['valid']:
            print(f"Reason: {result['error'][:100]}...")

if __name__ == "__main__":
    test_region_validation_debug()
