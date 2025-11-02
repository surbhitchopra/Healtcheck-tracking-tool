#!/usr/bin/env python3
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
