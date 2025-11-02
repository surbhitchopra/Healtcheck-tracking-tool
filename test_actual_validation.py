#!/usr/bin/env python
"""
Test the actual validation that would happen during file upload
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

def test_real_world_scenario():
    """Test the exact scenario user reported"""
    
    print("=" * 60)
    print("TESTING REAL WORLD VALIDATION SCENARIO")
    print("=" * 60)
    
    # User's exact scenario
    customer_name = "BSNL North DWDM"
    filename = "BSNL_East_DWDM_Report.xlsx"
    
    print(f"\n🧪 TESTING:")
    print(f"   Customer: {customer_name}")
    print(f"   Filename: {filename}")
    print(f"   Expected: Should REJECT (North customer uploading East file)")
    
    # Call the actual validation function
    result = validate_customer_technology_match(customer_name, filename)
    
    print(f"\n🔍 VALIDATION RESULT:")
    print(f"   Valid: {result['valid']}")
    
    if result['valid']:
        print("   ✅ VALIDATION PASSED (FILE ACCEPTED)")
        print("   🚨 THIS IS THE BUG - SHOULD BE REJECTED!")
    else:
        print("   ❌ VALIDATION FAILED (FILE REJECTED)")
        print("   ✅ THIS IS CORRECT BEHAVIOR")
        print(f"\n📝 Error Message:")
        print(f"   {result['error'][:100]}...")
    
    print(f"\n{'='*60}")
    
    return result

if __name__ == "__main__":
    test_real_world_scenario()
