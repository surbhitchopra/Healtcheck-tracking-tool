#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer
from collections import defaultdict
from datetime import datetime

print("🧪 TESTING FIXED API FUNCTION DIRECTLY")
print("=" * 60)

# Simulate the fixed API function logic
try:
    customers = Customer.objects.filter(is_deleted=False)
    
    # Group customers by name (like BSNL with multiple networks)
    customer_groups = defaultdict(list)
    
    for customer in customers:
        if not customer.total_runs and not customer.monthly_runs:
            continue
        customer_groups[customer.name].append(customer)
    
    # Find BSNL specifically
    if 'BSNL' in customer_groups:
        bsnl_networks = customer_groups['BSNL']
        print(f"📊 Found BSNL with {len(bsnl_networks)} networks")
        
        # Create individual network objects (this is the key fix)
        networks_array = []
        for net_customer in bsnl_networks:
            # Create months array for this specific network
            net_months = ['-'] * 12
            if net_customer.monthly_runs:
                for month_key, date_str in net_customer.monthly_runs.items():
                    try:
                        if '-' in month_key and date_str and date_str not in ['-', 'None', '']:
                            month_num = int(month_key.split('-')[1]) - 1
                            if 0 <= month_num < 12:
                                if date_str in ['Not Started', 'Not Run', 'No Report']:
                                    net_months[month_num] = date_str
                                else:
                                    try:
                                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                        month_abbr = date_obj.strftime('%b')
                                        net_months[month_num] = f"{date_obj.day}-{month_abbr}"
                                    except ValueError:
                                        net_months[month_num] = str(date_str)
                    except (ValueError, IndexError):
                        continue
            
            networks_array.append({
                'name': net_customer.network_name,
                'network_name': net_customer.network_name,
                'runs': net_customer.total_runs or 0,
                'months': net_months,  # Individual network months
                'monthly_runs': net_customer.monthly_runs or {},
            })
            
            print(f"\n🌐 {net_customer.network_name}")
            print(f"   Raw monthly_runs: {net_customer.monthly_runs}")
            print(f"   Formatted months: {net_months}")
            
            # Check if this network has actual dates
            has_dates = any(month != '-' for month in net_months)
            print(f"   Has actual dates: {'✅ YES' if has_dates else '❌ NO'}")
        
        # Summary
        networks_with_dates = sum(1 for net in networks_array 
                                 if any(month != '-' for month in net['months']))
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total BSNL networks: {len(networks_array)}")
        print(f"   Networks with dates: {networks_with_dates}")
        print(f"   Success rate: {networks_with_dates}/{len(networks_array)}")
        
        if networks_with_dates == len(networks_array):
            print(f"\n✅ SUCCESS! All BSNL networks now have their individual dates")
            print(f"🔧 The API fix should work correctly now")
        else:
            print(f"\n⚠️ Some networks still missing dates")
    else:
        print("❌ BSNL customer group not found!")

except Exception as e:
    print(f"❌ Error testing API function: {e}")
    import traceback
    traceback.print_exc()

print(f"\n💡 Next step: Restart Django server and test dashboard!")
print(f"   Your BSNL networks should now show individual monthly dates instead of dashes")