#!/usr/bin/env python3
"""
Test HC Tracker and Ignore file validation
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
from HealthCheck_app.views import validate_file_type_match, validate_section_specific_upload, validate_customer_technology_match

def test_hc_tracker_validation():
    """Test HC Tracker and Ignore file validation"""
    
    print("=" * 70)
    print("TESTING HC TRACKER AND IGNORE FILE VALIDATION")
    print("=" * 70)
    
    # Test cases
    test_cases = [
        {
            'filename': 'BSNL_North_DWDM_HC_Issues_Tracker.xlsx',
            'expected_type': 'TRACKER',
            'upload_section': 'tracker_upload',
            'customer': 'BSNL North DWDM',
            'description': 'HC Issues Tracker file in Tracker section'
        },
        {
            'filename': 'Bsnl_north_dwdm_ignored_test_cases.txt', 
            'expected_type': 'IGNORE',
            'upload_section': 'ignore_upload',
            'customer': 'BSNL North DWDM',
            'description': 'Ignore test cases file in Ignore section'
        },
        {
            'filename': 'BSNL_North_DWDM_HC_Issues_Tracker.xlsx',
            'expected_type': 'IGNORE',
            'upload_section': 'ignore_upload', 
            'customer': 'BSNL North DWDM',
            'description': 'HC Tracker file wrongly uploaded to Ignore section (should fail)'
        },
        {
            'filename': 'Bsnl_north_dwdm_ignored_test_cases.txt',
            'expected_type': 'TRACKER',
            'upload_section': 'tracker_upload',
            'customer': 'BSNL North DWDM', 
            'description': 'Ignore file wrongly uploaded to Tracker section (should fail)'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test['description']}")
        print(f"File: {test['filename']}")
        print(f"Expected Type: {test['expected_type']}")
        print(f"Upload Section: {test['upload_section']}")
        print(f"Customer: {test['customer']}")
        
        # Test file type validation
        print("\n1️⃣ Testing file type validation...")
        file_type_result = validate_file_type_match(test['filename'], test['expected_type'])
        if file_type_result['valid']:
            print("   ✅ File type validation: PASSED")
        else:
            print(f"   ❌ File type validation: FAILED - {file_type_result['error'][:100]}...")
        
        # Test section validation
        print("2️⃣ Testing section validation...")
        section_result = validate_section_specific_upload(
            test['customer'], test['filename'], test['upload_section'], test['expected_type']
        )
        if section_result['valid']:
            print("   ✅ Section validation: PASSED")
        else:
            print(f"   ❌ Section validation: FAILED - {section_result['error'][:100]}...")
        
        # Test customer validation
        print("3️⃣ Testing customer validation...")
        customer_result = validate_customer_technology_match(test['customer'], test['filename'])
        if customer_result['valid']:
            print("   ✅ Customer validation: PASSED")
        else:
            print(f"   ❌ Customer validation: FAILED - {customer_result['error'][:100]}...")
        
        # Overall result
        all_passed = file_type_result['valid'] and section_result['valid'] and customer_result['valid']
        print(f"\n📊 OVERALL RESULT: {'✅ PASS' if all_passed else '❌ FAIL'}")
        print("-" * 70)

if __name__ == "__main__":
    test_hc_tracker_validation()
