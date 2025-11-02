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

print("🔍 DIAGNOSING BSNL NETWORK DATA STRUCTURE")
print("=" * 60)

# Find BSNL customer
bsnl_customers = Customer.objects.filter(name__icontains='BSNL', is_deleted=False)

if not bsnl_customers.exists():
    print("❌ No BSNL customers found!")
    print("\n📋 Available customers:")
    for customer in Customer.objects.filter(is_deleted=False)[:10]:
        print(f"   - {customer.name}")
    sys.exit(1)

bsnl_customer = bsnl_customers.first()
print(f"🎯 Found BSNL customer: {bsnl_customer.name}")
print(f"   Customer ID: {bsnl_customer.id}")
print(f"   Total runs: {bsnl_customer.total_runs}")
print(f"   Network name: {bsnl_customer.network_name}")
print(f"   Monthly runs: {bsnl_customer.monthly_runs}")

# Check for individual networks (stored as Customer objects with different network_name)
networks = Customer.objects.filter(name=bsnl_customer.name, is_deleted=False).exclude(id=bsnl_customer.id)
print(f"\n📡 Found {networks.count()} individual networks for {bsnl_customer.name}:")

for network in networks:
    print(f"\n   🔧 {network.network_name}")
    print(f"      Network ID: {network.id}")
    print(f"      Total runs: {network.total_runs}")
    print(f"      Network type: {network.network_type}")
    print(f"      Monthly runs: {network.monthly_runs}")
    print(f"      Setup status: {network.setup_status}")
    
    # Check if monthly_runs has any data
    if network.monthly_runs:
        if isinstance(network.monthly_runs, dict):
            print(f"      📅 Monthly data (dict format):")
            for month_key, date_value in network.monthly_runs.items():
                if date_value and date_value != '-':
                    print(f"         {month_key}: {date_value}")
        elif isinstance(network.monthly_runs, list):
            print(f"      📅 Monthly data (array format):")
            for i, date_value in enumerate(network.monthly_runs):
                if date_value and date_value != '-':
                    print(f"         Month {i+1}: {date_value}")
    else:
        print(f"      ❌ No monthly_runs data")

print(f"\n🔍 SUMMARY:")
print(f"   Customer-level monthly runs: {bool(bsnl_customer.monthly_runs)}")
print(f"   Individual networks: {networks.count()}")
print(f"   Networks with total_runs > 0: {networks.filter(total_runs__gt=0).count()}")
print(f"   Networks with monthly_runs data: {networks.exclude(monthly_runs__exact=dict()).count()}")

# Check what data structure the API would send
print(f"\n🌐 API DATA STRUCTURE CHECK:")
print(f"   Customer monthly_runs type: {type(bsnl_customer.monthly_runs)}")

if networks.exists():
    sample_network = networks.first()
    print(f"   Sample network monthly_runs type: {type(sample_network.monthly_runs)}")
    
    # Show what the API response would look like
    api_networks = []
    for network in networks[:3]:  # First 3 networks
        network_data = {
            'name': network.network_name,
            'total_runs': network.total_runs,
            'monthly_runs': network.monthly_runs,
            'setup_status': network.setup_status,
            'network_type': network.network_type
        }
        api_networks.append(network_data)
    
    print(f"\n🔧 Sample API network data:")
    for network_data in api_networks:
        print(f"   {network_data['name']}:")
        print(f"      total_runs: {network_data['total_runs']}")
        print(f"      setup_status: {network_data['setup_status']}")
        print(f"      monthly_runs: {network_data['monthly_runs']}")

print(f"\n💡 RECOMMENDED ACTION:")
if networks.filter(total_runs__gt=0).exists():
    if networks.exclude(monthly_runs__exact=dict()).exists():
        print("   ✅ Networks have data - Issue likely in frontend rendering")
        print("   🔧 Apply JavaScript fix to force display network dates")
    else:
        print("   ⚠️ Networks have total_runs but no monthly_runs data")
        print("   🔧 Need to populate network-level monthly_runs from customer data")
else:
    print("   ❌ Networks have no total_runs - Data issue in database")
    print("   🔧 Need to distribute customer runs to networks")
