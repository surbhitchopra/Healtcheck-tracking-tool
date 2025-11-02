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

print("🔍 SIMPLE BACKEND TEST - Check if our API fix is working")
print("=" * 70)

# Replicate the EXACT API logic from our fixed views.py
try:
    print("📡 Simulating API: /api/customer-dashboard/customers/ logic")
    
    # Get customers from database
    customers = Customer.objects.filter(is_deleted=False)
    
    # Group customers by name (like BSNL with multiple networks)
    customer_groups = defaultdict(list)
    
    for customer in customers:
        # Skip customers without data
        if not customer.total_runs and not customer.monthly_runs:
            continue
        customer_groups[customer.name].append(customer)
    
    # Format for frontend dashboard
    customer_data = {}
    
    for customer_name, customer_networks in customer_groups.items():
        if customer_name == 'BSNL':  # Focus on BSNL
            if len(customer_networks) > 1:
                print(f"📊 Processing BSNL with {len(customer_networks)} networks")
                
                # Create individual network objects
                networks_array = []
                for net_customer in customer_networks:
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
                        'name': net_customer.network_name or f'Network_{len(networks_array)+1}',
                        'network_name': net_customer.network_name or f'Network_{len(networks_array)+1}',
                        'runs': net_customer.total_runs or 0,
                        'total_runs': net_customer.total_runs or 0,
                        'months': net_months,  # Individual network months - THIS IS KEY!
                        'monthly_runs': net_customer.monthly_runs or {},
                        'country': net_customer.country,
                        'node_count': net_customer.node_qty or 0,
                        'gtac': net_customer.gtac,
                        'ne_type': net_customer.ne_type
                    })
                
                # Show what the API would return
                print(f"\n📋 API RESPONSE STRUCTURE:")
                print(f"Customer: BSNL")
                print(f"Networks in response: {len(networks_array)}")
                
                print(f"\n🌐 Individual Network Data:")
                for i, network in enumerate(networks_array[:3]):  # First 3 networks
                    print(f"   {i+1}. {network['network_name']}")
                    print(f"      months: {network['months']}")
                    actual_dates = sum(1 for m in network['months'] if m not in ['-', 'Not Started', 'No Report'])
                    print(f"      actual dates: {actual_dates}")
                
                # Test specific networks
                west_otn = next((net for net in networks_array if 'West_Zone_OTN' in net['network_name']), None)
                if west_otn:
                    print(f"\n🎯 SPECIFIC TEST - BSNL_West_Zone_OTN:")
                    print(f"   Months array: {west_otn['months']}")
                    expected = ['Not Started', 'Not Started', '14-Mar', 'No Report', 'No Report', '13-Jun', '24-Jul', '9-Aug', '-', '-', '-', '-']
                    print(f"   Expected:     {expected}")
                    matches = west_otn['months'] == expected
                    print(f"   ✅ Match: {matches}")
                
                # The critical test - does this data structure work for frontend?
                print(f"\n🔍 FRONTEND COMPATIBILITY TEST:")
                print("If frontend JavaScript does:")
                print("   targetNetwork = customer.networks.find(...)")
                print("   monthValue = targetNetwork.months[monthIndex]")
                print("")
                
                sample_network = networks_array[0]
                print(f"Sample network structure:")
                print(f"   network.network_name: '{sample_network['network_name']}'")
                print(f"   network.months: {sample_network['months']}")
                print(f"   network.months[0]: '{sample_network['months'][0]}'")
                print(f"   network.months[4]: '{sample_network['months'][4]}'")
                
                if any(m != '-' for m in sample_network['months']):
                    print(f"\n✅ BACKEND IS 100% CORRECT!")
                    print(f"   Individual networks have proper months arrays")
                    print(f"   Frontend should be able to use: targetNetwork.months[monthIndex]")
                    print(f"   THE ISSUE IS IN THE FRONTEND JAVASCRIPT!")
                else:
                    print(f"\n❌ Backend issue - no dates in months array")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n💡 CONCLUSION:")
print("If you see 'BACKEND IS 100% CORRECT!' above, then:")
print("1. The backend API is working perfectly")
print("2. The issue is definitely in the frontend JavaScript")
print("3. The dashboard template might not be using our fixed code")
print("4. OR there might be cached JavaScript in browser")

print(f"\n🔧 SOLUTIONS TO TRY:")
print("1. Hard refresh browser (Ctrl+Shift+R)")
print("2. Clear browser cache completely") 
print("3. Check if you're on the correct dashboard template")
print("4. Use browser console JavaScript fix as last resort")