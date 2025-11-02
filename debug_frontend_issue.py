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
import json

print("🔍 FINAL DEBUG - WHY NETWORKS STILL SHOW DASHES")
print("=" * 70)

# Test the actual API response that the frontend receives
from django.test import Client
client = Client()

try:
    print("🌐 Testing actual API endpoint...")
    response = client.get('/api/customer-dashboard/customers/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response Status: {response.status_code}")
        
        # Find BSNL customer in actual API response
        bsnl_customer = None
        for customer_key, customer_data in data.get('customers', {}).items():
            if 'BSNL' in customer_data.get('name', ''):
                bsnl_customer = customer_data
                break
        
        if bsnl_customer:
            print(f"\n📊 BSNL Customer API Data:")
            print(f"   Customer Key: {customer_key}")
            print(f"   Name: {bsnl_customer.get('name')}")
            print(f"   Networks Count: {len(bsnl_customer.get('networks', []))}")
            
            print(f"\n🌐 Individual Networks in API Response:")
            for i, network in enumerate(bsnl_customer.get('networks', [])[:3]):
                print(f"   Network {i+1}: {network.get('network_name', 'Unknown')}")
                print(f"      Has 'months' key: {'months' in network}")
                print(f"      Has 'monthly_runs' key: {'monthly_runs' in network}")
                
                if 'months' in network:
                    months_data = network['months']
                    print(f"      Months type: {type(months_data)}")
                    if isinstance(months_data, list):
                        print(f"      Months length: {len(months_data)}")
                        print(f"      First 6 months: {months_data[:6]}")
                        actual_dates = sum(1 for m in months_data if m not in ['-', 'Not Started', 'No Report'])
                        print(f"      Actual dates count: {actual_dates}")
                    else:
                        print(f"      Months data: {months_data}")
                
                if 'monthly_runs' in network:
                    monthly_runs = network['monthly_runs']
                    print(f"      Monthly runs: {monthly_runs}")
        else:
            print("❌ BSNL customer not found in API response!")
            print(f"Available customers: {list(data.get('customers', {}).keys())}")
    
    elif response.status_code == 302:
        print(f"❌ API Redirect (302) - Authentication or URL issue")
        print("   The API endpoint might require authentication or have URL issues")
        
        # Try direct function call instead
        print(f"\n🔄 Trying direct function import...")
        
        from HealthCheck_app.views import api_customer_dashboard_customers
        from django.http import HttpRequest
        
        # Create a fake request
        request = HttpRequest()
        request.method = 'GET'
        
        # Call the function directly
        direct_response = api_customer_dashboard_customers(request)
        
        if hasattr(direct_response, 'content'):
            import json
            content = json.loads(direct_response.content.decode('utf-8'))
            
            print(f"✅ Direct function call successful")
            
            # Find BSNL customer
            bsnl_customer = None
            for customer_key, customer_data in content.get('customers', {}).items():
                if 'BSNL' in customer_data.get('name', ''):
                    bsnl_customer = customer_data
                    break
            
            if bsnl_customer:
                print(f"\n📊 BSNL Direct Response:")
                print(f"   Networks: {len(bsnl_customer.get('networks', []))}")
                
                # Check first network's months data
                if bsnl_customer.get('networks'):
                    first_network = bsnl_customer['networks'][0]
                    print(f"   First network: {first_network.get('network_name')}")
                    print(f"   First network months: {first_network.get('months', 'NO MONTHS KEY')}")
                    
                    if 'months' in first_network and isinstance(first_network['months'], list):
                        months = first_network['months']
                        print(f"   ✅ Months array exists: {months}")
                        actual_dates = sum(1 for m in months if m not in ['-', 'Not Started', 'No Report'])
                        print(f"   Actual dates in array: {actual_dates}")
                        
                        if actual_dates > 0:
                            print(f"\n🎯 THE BACKEND IS WORKING CORRECTLY!")
                            print(f"   Individual networks DO have months arrays with dates")
                            print(f"   The issue is 100% in the frontend JavaScript")
                        else:
                            print(f"\n⚠️ Months array exists but no actual dates")
                    else:
                        print(f"   ❌ No months array found in network data")
        else:
            print(f"❌ Direct function call failed")
    
    else:
        print(f"❌ API Response Status: {response.status_code}")
        
except Exception as e:
    print(f"❌ API Test Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n💡 DIAGNOSIS SUMMARY:")
print("1. If backend shows months arrays with dates = Frontend JavaScript issue")
print("2. If backend shows no months arrays = Backend API issue") 
print("3. If 302 redirect = Authentication/URL issue")

print(f"\n🔧 NEXT STEPS:")
print("1. Check browser console (F12) for JavaScript errors")
print("2. Check if dashboard is calling correct API endpoint")
print("3. Verify that frontend JavaScript is actually running the fixed code")