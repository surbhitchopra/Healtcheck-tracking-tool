#!/usr/bin/env python
"""
Test the monthly data processing logic in isolation
"""

def process_monthly_data(monthly_runs_dict):
    """Process monthly_runs data exactly like the working debug script"""
    monthly_array = ['-'] * 12
    
    print(f"Input: {monthly_runs_dict}")
    
    if monthly_runs_dict and isinstance(monthly_runs_dict, dict):
        for month_key, month_value in monthly_runs_dict.items():
            print(f"  Processing {month_key} = {month_value}")
            
            # SIMPLE validation - just check if it has data
            clean_value = str(month_value).strip() if month_value else ''
            
            if clean_value and clean_value not in ['-', '', 'null', 'None', 'Not Started', 'No Report']:
                # Convert date keys - check if it's like '2025-05' (May) or just '5'
                try:
                    if '-' in month_key:
                        # Format: '2025-05' -> extract month number
                        month_num = int(month_key.split('-')[1])
                    else:
                        # Format: '5' -> direct month number
                        month_num = int(month_key)
                    
                    month_index = month_num - 1  # Convert to 0-based index
                    
                    if 0 <= month_index < 12:
                        # Clean the date value (remove year if present)
                        if '-' in clean_value:
                            parts = clean_value.split('-')
                            if len(parts) == 3:  # 2025-01-08
                                clean_value = f"{parts[2]}-{parts[1]}"  # 08-01
                            elif len(parts) == 2:  # Already clean
                                pass
                        
                        monthly_array[month_index] = clean_value
                        print(f"    ✅ Set month {month_num} (index {month_index}) = {clean_value}")
                except (ValueError, IndexError) as e:
                    print(f"    ❌ Error parsing month {month_key}: {e}")
    
    return monthly_array

# Test with BSNL data from our debug output
bsnl_test_data = {
    '2025-01': '2025-01-30',
    '2025-02': 'No Report',
    '2025-03': 'No Report', 
    '2025-04': '2025-04-16',
    '2025-05': 'No Report',
    '2025-06': '2025-06-22',
    '2025-07': '2025-07-26',
    '2025-08': '2025-08-14'
}

print("🧪 TESTING BSNL SOUTH ZONE DATA:")
print("=" * 40)
result = process_monthly_data(bsnl_test_data)
print(f"\nResult: {result}")

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
print("\nFormatted:")
for i, val in enumerate(result):
    if val != '-':
        print(f"  {months[i]}: {val}")

# Test aggregation from multiple networks (like BSNL has 8 networks)
print("\n" + "="*50)
print("🧪 TESTING AGGREGATION FROM MULTIPLE NETWORKS:")
print("="*50)

# Sample data from multiple BSNL networks
networks_data = [
    # BSNL_East_Zone_DWDM
    {'2025-05': '2025-05-15', '2025-06': '2025-06-13', '2025-07': '2025-07-08'},
    # BSNL_North_Zone_DWDM  
    {'2025-05': '2025-05-03', '2025-06': '2025-06-12', '2025-07': '2025-07-08', '2025-08': '2025-08-26'},
    # BSNL_South_Zone_DWDM
    {'2025-01': '2025-01-30', '2025-04': '2025-04-16', '2025-06': '2025-06-22', '2025-07': '2025-07-26', '2025-08': '2025-08-14'},
    # BSNL_West_Zone_DWDM
    {'2025-03': '2025-03-14', '2025-06': '2025-06-13', '2025-07': '2025-07-24', '2025-08': '2025-08-09'}
]

# Aggregate like customer-level processing
customer_monthly_array = ['-'] * 12

for i, network_data in enumerate(networks_data):
    print(f"\nProcessing Network {i+1}:")
    network_result = process_monthly_data(network_data)
    
    # Merge into customer array (last valid date wins)
    for month_idx, month_val in enumerate(network_result):
        if month_val != '-':
            customer_monthly_array[month_idx] = month_val

print(f"\n🎯 FINAL CUSTOMER AGGREGATED ARRAY:")
print(f"   {customer_monthly_array}")

print("\nFinal formatted result:")
for i, val in enumerate(customer_monthly_array):
    if val != '-':
        print(f"  {months[i]}: {val}")
        
print(f"\nTotal months with data: {sum(1 for x in customer_monthly_array if x != '-')}")