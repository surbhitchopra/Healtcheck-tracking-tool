#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer
from HealthCheck_app.views import format_monthly_runs_to_array

print("🔍 CHECKING API RESPONSE FOR BSNL NETWORKS")
print("=" * 60)

# Get all BSNL networks
bsnl_networks = Customer.objects.filter(name='BSNL', is_deleted=False)

print(f"📊 Found {bsnl_networks.count()} BSNL networks in database")

# Simulate what the API endpoint returns
customers_data = {}

for network in bsnl_networks:
    print(f"\n🌐 Processing: {network.network_name}")
    print(f"   Raw monthly_runs: {network.monthly_runs}")
    
    # Format monthly_runs the same way views.py does
    formatted_monthly_runs = format_monthly_runs_to_array(network.monthly_runs) if network.monthly_runs else ['-'] * 12
    
    print(f"   Formatted for API: {formatted_monthly_runs}")
    
    # Create the network data structure as it would appear in API
    network_data = {
        'network_name': network.network_name,
        'total_runs': network.total_runs,
        'monthly_runs': formatted_monthly_runs,
        'setup_status': network.setup_status,
        'network_type': network.network_type
    }
    
    # Add to customers data (grouped by customer name)
    if 'BSNL' not in customers_data:
        customers_data['BSNL'] = {
            'name': 'BSNL',
            'networks': [],
            'monthly_runs': None  # This will be set from the main BSNL customer
        }
    
    customers_data['BSNL']['networks'].append(network_data)

# Get the main BSNL customer entry (the one that shows in customer row)
main_bsnl = bsnl_networks.first()  # The first one is typically the main customer
customers_data['BSNL']['monthly_runs'] = format_monthly_runs_to_array(main_bsnl.monthly_runs) if main_bsnl.monthly_runs else ['-'] * 12
customers_data['BSNL']['total_runs'] = main_bsnl.total_runs

print(f"\n📋 COMPLETE API RESPONSE STRUCTURE:")
print(f"Customer Level:")
print(f"   Name: {customers_data['BSNL']['name']}")
print(f"   Total runs: {customers_data['BSNL']['total_runs']}")
print(f"   Monthly runs: {customers_data['BSNL']['monthly_runs']}")
print(f"   Networks count: {len(customers_data['BSNL']['networks'])}")

print(f"\nNetwork Level Details:")
for network in customers_data['BSNL']['networks']:
    print(f"   🔧 {network['network_name']}:")
    print(f"      Total runs: {network['total_runs']}")
    print(f"      Monthly runs: {network['monthly_runs']}")
    
    # Check if monthly_runs has actual dates vs dashes
    has_dates = any(date != '-' and date != 'Not Started' and date != 'No Report' for date in network['monthly_runs'])
    print(f"      Has actual dates: {'✅ YES' if has_dates else '❌ NO'}")

print(f"\n🚨 PROBLEM DIAGNOSIS:")
networks_with_data = sum(1 for net in customers_data['BSNL']['networks'] 
                        if any(date not in ['-', 'Not Started', 'No Report'] for date in net['monthly_runs']))
print(f"   Networks with actual date data: {networks_with_data}/{len(customers_data['BSNL']['networks'])}")

if networks_with_data == 0:
    print("   ❌ PROBLEM: No networks have formatted date data!")
    print("   🔧 SOLUTION: Fix the format_monthly_runs_to_array function")
else:
    print("   ✅ Networks have date data - frontend issue")

# Show the exact format that should be sent to frontend
print(f"\n💡 EXPECTED FRONTEND FORMAT FOR BSNL_West_Zone_OTN:")
west_otn = next((net for net in customers_data['BSNL']['networks'] if 'West_Zone_OTN' in net['network_name']), None)
if west_otn:
    print(f"   Should show: {west_otn['monthly_runs']}")
    expected = ['Not Started', 'Not Started', '14-Mar', 'No Report', 'No Report', '13-Jun', '24-Jul', '9-Aug', '-', '-', '-', '-']
    print(f"   Expected:    {expected}")
else:
    print("   ❌ BSNL_West_Zone_OTN not found in networks!")