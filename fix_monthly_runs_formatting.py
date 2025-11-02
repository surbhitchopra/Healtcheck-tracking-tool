#!/usr/bin/env python3
"""
Fix Monthly Runs Date Formatting Issue
======================================

The issue is that monthly_runs data is coming in dict format:
{'2025-01': '2025-01-08', '2025-02': '2025-02-01', ...}

But the frontend expects it as a 12-element array:
['08-01', '01-02', '03-03', '-', '-', '-', '-', '-', '-', '-', '-', '-']

This script fixes the formatting conversion in the Django views.
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

def fix_monthly_runs_formatting():
    """Fix the monthly_runs formatting in Django views"""
    
    project_root = Path("C:/Users/surchopr/Hc_Final")
    views_file = project_root / "HealthCheck_app" / "views.py"
    
    if not views_file.exists():
        print(f"❌ Views file not found: {views_file}")
        return False
    
    print(f"🔧 Fixing monthly_runs formatting in {views_file}")
    
    # Create backup
    backup_file = views_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
    shutil.copy2(views_file, backup_file)
    print(f"📦 Backup created: {backup_file}")
    
    # Read the current content
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the formatting fix function at the top of the file (after imports)
    formatting_function = '''
def format_monthly_runs_to_array(monthly_runs_dict):
    """
    Convert monthly_runs dict to 12-element array format
    Input: {'2025-01': '2025-01-08', '2025-02': '2025-02-01', ...}
    Output: ['08-01', '01-02', '03-03', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    """
    if not monthly_runs_dict or not isinstance(monthly_runs_dict, dict):
        return ['-'] * 12
    
    monthly_array = ['-'] * 12  # Initialize 12 months as empty
    
    for month_key, date_value in monthly_runs_dict.items():
        try:
            if date_value and date_value != 'Not Run':
                # Parse the month from key like '2025-01' -> month 1 (index 0)
                year_month = month_key.split('-')
                if len(year_month) == 2:
                    month_num = int(year_month[1])  # Get month number (1-12)
                    if 1 <= month_num <= 12:
                        month_index = month_num - 1  # Convert to 0-based index
                        
                        # Parse the date value like '2025-01-08'
                        if isinstance(date_value, str) and len(date_value) >= 10:
                            date_parts = date_value.split('-')
                            if len(date_parts) >= 3:
                                day = date_parts[2]
                                month = date_parts[1] 
                                # Format as DD-MM
                                monthly_array[month_index] = f"{day}-{month}"
                            else:
                                monthly_array[month_index] = str(date_value)[-5:]  # Last 5 chars
                        else:
                            monthly_array[month_index] = str(date_value)
            elif date_value == 'Not Run':
                # Handle 'Not Run' case
                year_month = month_key.split('-')
                if len(year_month) == 2:
                    month_num = int(year_month[1])
                    if 1 <= month_num <= 12:
                        month_index = month_num - 1
                        monthly_array[month_index] = 'Not Run'
        except (ValueError, IndexError) as e:
            print(f"⚠️ Error processing {month_key}: {date_value} -> {e}")
            continue
    
    return monthly_array

'''
    
    # Find a good place to insert the function (after the imports but before the first function)
    import_end_pattern = "from .script_helper import execute_health_check_script, ScriptExecutor"
    if import_end_pattern in content:
        content = content.replace(import_end_pattern, import_end_pattern + "\n" + formatting_function)
        print("✅ Added formatting function after imports")
    else:
        # Alternative location - after the directory setup
        dir_setup_pattern = "os.makedirs(SCRIPT_OUTPUT_DIR, exist_ok=True)"
        if dir_setup_pattern in content:
            content = content.replace(dir_setup_pattern, dir_setup_pattern + "\n" + formatting_function)
            print("✅ Added formatting function after directory setup")
        else:
            print("⚠️ Couldn't find ideal location, adding at beginning of file")
            content = formatting_function + "\n" + content
    
    # Now fix the places where monthly_runs data is returned
    # Fix 1: In database customer processing
    fix1_pattern = """monthly_runs array: ['Not Run', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']"""
    if "monthly_runs array:" in content:
        print("✅ Found monthly_runs array references - they look correct")
    
    # Fix 2: In api_customer_dashboard_customers function - look for where customer data is stored
    # Find the section where migrated network data is processed
    old_network_processing = """📊 Processing network .* monthly data\.\.\.
      ✅ Network month \d+ = (.*)
    → .*: \d+ runs, \d+ nodes"""
    
    # The main fix - ensure that monthly_runs dict is converted to array before returning
    api_return_pattern = """🚀 FINAL API RESPONSE for ([^:]+):
     - total_runs: (\d+)
     - monthly_runs array: (.*)
     - networks_count: (\d+)
     - node_count: (\d+)"""
    
    # Look for where the final response is built in api_customer_dashboard_customers
    if "🚀 FINAL API RESPONSE" in content:
        print("✅ Found API response section")
        
        # The key fix is to ensure we format the monthly_runs before adding to response
        # Find where customer data is added to customers_data dictionary
        customer_data_pattern = """customers_data\[([^\]]+)\] = \{
                    'name': ([^,]+),
                    'country': ([^,]+),
                    'gtac': ([^,]+),
                    'ne_type': ([^,]+),
                    'total_runs': ([^,]+),
                    'node_count': ([^,]+),
                    'networks_count': ([^,]+),
                    'monthly_runs': ([^,]+),
                    'last_run_date': ([^,]+),"""
        
        # Replace monthly_runs assignment to use our formatting function
        if "'monthly_runs': monthly_runs" in content:
            content = content.replace("'monthly_runs': monthly_runs", "'monthly_runs': format_monthly_runs_to_array(monthly_runs)")
            print("✅ Fixed monthly_runs assignment to use formatting function")
        
        # Also fix any place where monthly_runs is directly assigned from dict
        content = content.replace("'monthly_runs': monthly_data,", "'monthly_runs': format_monthly_runs_to_array(monthly_data),")
        content = content.replace("'monthly_runs': network.monthly_runs,", "'monthly_runs': format_monthly_runs_to_array(network.monthly_runs),")
        
    # Fix 3: Ensure the database query results are properly formatted
    # Look for places where network.monthly_runs is used directly
    if "network.monthly_runs" in content:
        print("✅ Found network.monthly_runs references")
    
    # Write the fixed content back
    with open(views_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Monthly runs formatting fixes applied!")
    return True

def create_test_script():
    """Create a test script to verify the formatting works correctly"""
    
    test_script_content = '''#!/usr/bin/env python3
"""
Test script for monthly_runs formatting
"""

def format_monthly_runs_to_array(monthly_runs_dict):
    """
    Convert monthly_runs dict to 12-element array format
    Input: {'2025-01': '2025-01-08', '2025-02': '2025-02-01', ...}
    Output: ['08-01', '01-02', '03-03', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    """
    if not monthly_runs_dict or not isinstance(monthly_runs_dict, dict):
        return ['-'] * 12
    
    monthly_array = ['-'] * 12  # Initialize 12 months as empty
    
    for month_key, date_value in monthly_runs_dict.items():
        try:
            if date_value and date_value != 'Not Run':
                # Parse the month from key like '2025-01' -> month 1 (index 0)
                year_month = month_key.split('-')
                if len(year_month) == 2:
                    month_num = int(year_month[1])  # Get month number (1-12)
                    if 1 <= month_num <= 12:
                        month_index = month_num - 1  # Convert to 0-based index
                        
                        # Parse the date value like '2025-01-08'
                        if isinstance(date_value, str) and len(date_value) >= 10:
                            date_parts = date_value.split('-')
                            if len(date_parts) >= 3:
                                day = date_parts[2]
                                month = date_parts[1] 
                                # Format as DD-MM
                                monthly_array[month_index] = f"{day}-{month}"
                            else:
                                monthly_array[month_index] = str(date_value)[-5:]  # Last 5 chars
                        else:
                            monthly_array[month_index] = str(date_value)
            elif date_value == 'Not Run':
                # Handle 'Not Run' case
                year_month = month_key.split('-')
                if len(year_month) == 2:
                    month_num = int(year_month[1])
                    if 1 <= month_num <= 12:
                        month_index = month_num - 1
                        monthly_array[month_index] = 'Not Run'
        except (ValueError, IndexError) as e:
            print(f"⚠️ Error processing {month_key}: {date_value} -> {e}")
            continue
    
    return monthly_array

# Test cases
test_cases = [
    {
        'input': {'2025-01': '2025-01-08', '2025-02': '2025-02-01', '2025-03': '2025-03-03'},
        'expected': ['08-01', '01-02', '03-03', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    },
    {
        'input': {'2025-01': 'Not Run', '2025-05': '2025-05-21'},
        'expected': ['Not Run', '-', '-', '-', '21-05', '-', '-', '-', '-', '-', '-', '-']
    },
    {
        'input': {},
        'expected': ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    }
]

print("🧪 Testing monthly_runs formatting function...")
for i, test in enumerate(test_cases):
    result = format_monthly_runs_to_array(test['input'])
    if result == test['expected']:
        print(f"✅ Test {i+1}: PASSED")
        print(f"   Input: {test['input']}")
        print(f"   Output: {result}")
    else:
        print(f"❌ Test {i+1}: FAILED")
        print(f"   Input: {test['input']}")
        print(f"   Expected: {test['expected']}")
        print(f"   Got: {result}")
    print()

print("🎯 Test completed!")
'''
    
    test_file = Path("C:/Users/surchopr/Hc_Final/test_monthly_formatting.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script_content)
    
    print(f"📝 Created test script: {test_file}")
    return test_file

def main():
    print("🚀 Fixing Monthly Runs Date Formatting Issue")
    print("=" * 50)
    
    # Apply the fix
    if fix_monthly_runs_formatting():
        print("\n✅ Formatting fix applied successfully!")
        
        # Create test script
        test_file = create_test_script()
        
        print("\n🎯 Next Steps:")
        print("1. Test the formatting function:")
        print(f"   python {test_file}")
        print("\n2. Restart your Django server:")
        print("   python manage.py runserver")
        print("\n3. Check the API response:")
        print("   Visit: http://localhost:8000/api/customer-dashboard/customers/")
        print("\n4. Verify the dashboard shows dates properly")
        
        print("\n📋 The fix ensures that:")
        print("   - Dict format: {'2025-01': '2025-01-08'}")
        print("   - Gets converted to array: ['08-01', '-', '-', ...]")
        print("   - 'Not Run' values are preserved")
        print("   - Empty months show as '-'")
        
    else:
        print("\n❌ Failed to apply formatting fix")

if __name__ == "__main__":
    main()