#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

print("🔍 DEBUGGING VIEWS.PY ISSUE - Why BSNL networks show dashes")
print("=" * 70)

# Get BSNL networks
bsnl_networks = Customer.objects.filter(name='BSNL', is_deleted=False)

print(f"📊 Found {bsnl_networks.count()} BSNL networks")

# Check the current endpoint being used
print(f"\n🔧 Testing which API endpoint is being used...")

# Let's simulate the actual API call that the frontend makes
from django.test import Client
from django.urls import reverse

client = Client()

try:
    # Try the main API endpoint
    response = client.get('/api/customer-dashboard/customers/')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API endpoint working: {response.status_code}")
        
        # Find BSNL customer in response
        bsnl_customer = None
        for customer_key, customer_data in data.get('customers', {}).items():
            if 'BSNL' in customer_data.get('name', ''):
                bsnl_customer = customer_data
                break
        
        if bsnl_customer:
            print(f"\n📋 BSNL Customer API Response:")
            print(f"   Name: {bsnl_customer.get('name')}")
            print(f"   Networks count: {len(bsnl_customer.get('networks', []))}")
            print(f"   Customer level months: {bsnl_customer.get('months', [])}")
            
            print(f"\n🌐 Individual Networks:")
            for i, network in enumerate(bsnl_customer.get('networks', [])[:3]):  # First 3 networks
                print(f"   {i+1}. {network.get('network_name', 'Unknown')}")
                print(f"      Runs: {network.get('runs', 0)}")
                print(f"      Months: {network.get('months', [])}")
                
                # Check if months array has any data
                months_array = network.get('months', [])
                has_data = any(month != '-' for month in months_array)
                print(f"      Has dates: {'✅ YES' if has_data else '❌ NO - ALL DASHES'}")
        else:
            print(f"❌ BSNL customer not found in API response!")
            print(f"Available customers: {list(data.get('customers', {}).keys())}")
    else:
        print(f"❌ API endpoint failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")

# Let's check the actual URL pattern being used
print(f"\n🔗 Checking URL patterns...")
try:
    from django.urls import resolve
    from django.conf import settings
    
    # Check what view function is handling the request
    resolver = resolve('/api/customer-dashboard/customers/')
    print(f"   View function: {resolver.func.__name__}")
    print(f"   View module: {resolver.func.__module__}")
    
except Exception as e:
    print(f"   URL resolution error: {e}")

print(f"\n💡 DIAGNOSIS:")
print("   1. Check if the correct API endpoint is being called")
print("   2. Verify the view function is processing BSNL networks correctly")
print("   3. Ensure individual networks get their own months array")

print(f"\n🔧 NEXT STEPS:")
print("   1. Identify the exact view function being called")
print("   2. Fix the logic that populates individual network months")
print("   3. Ensure BSNL networks get their database monthly_runs data")