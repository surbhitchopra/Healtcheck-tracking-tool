#!/usr/bin/env python
from datetime import datetime

# Test the fixed formatting logic directly
def test_date_formatting():
    """Test the new date formatting logic"""
    print("🧪 TESTING FIXED DATE FORMATTING LOGIC")
    print("=" * 50)
    
    # Test cases from BSNL data
    test_cases = [
        ('Not Started', 'Not Started'),  # Should remain unchanged
        ('No Report', 'No Report'),      # Should remain unchanged
        ('2025-03-14', '14-Mar'),        # Should format properly
        ('2025-06-13', '13-Jun'),        # Should format properly
        ('2025-07-24', '24-Jul'),        # Should format properly
        ('2025-08-09', '9-Aug'),         # Should format properly
    ]
    
    for input_value, expected_output in test_cases:
        print(f"\n🔧 Testing: '{input_value}'")
        
        # Apply the same logic as the fixed views.py
        date_str = str(input_value).strip()
        
        if date_str in ['Not Started', 'Not Run', 'No Report']:
            # Show status messages as-is
            result = date_str
            print(f"   Status case: '{result}'")
        else:
            try:
                # Try to parse as date and format it properly
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Use custom formatting to avoid truncation
                month_abbr = date_obj.strftime('%b')  # Full month abbreviation
                result = f"{date_obj.day}-{month_abbr}"
                print(f"   Date case: '{result}'")
            except ValueError:
                # If parsing fails, show the raw value
                result = date_str
                print(f"   Raw case: '{result}'")
        
        # Check if result matches expected
        if result == expected_output:
            print(f"   ✅ CORRECT: '{result}'")
        else:
            print(f"   ❌ WRONG: Expected '{expected_output}', got '{result}'")

    print(f"\n💡 Expected BSNL_West_Zone_OTN months after fix:")
    west_otn_months = ['Not Started', 'Not Started', '2025-03-14', 'No Report', 'No Report', '2025-06-13', '2025-07-24', '2025-08-09']
    expected_result = []
    
    for i, month_value in enumerate(west_otn_months):
        if not month_value:
            expected_result.append('-')
            continue
            
        date_str = str(month_value).strip()
        if date_str in ['Not Started', 'Not Run', 'No Report']:
            expected_result.append(date_str)
        else:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_abbr = date_obj.strftime('%b')
                expected_result.append(f"{date_obj.day}-{month_abbr}")
            except ValueError:
                expected_result.append(date_str)
    
    # Pad to 12 months
    while len(expected_result) < 12:
        expected_result.append('-')
    
    print(f"   Expected array: {expected_result}")
    print(f"\n🎯 This should now show in dashboard instead of dashes!")

if __name__ == "__main__":
    test_date_formatting()