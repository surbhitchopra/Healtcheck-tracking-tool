#!/usr/bin/env python3
"""
Test the dashboard API directly to see what data is being returned
"""
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from HealthCheck_app.views import api_customer_dashboard_customers

def test_dashboard_api():
    """Test the dashboard API to see what data is returned"""
    print("🚀 TESTING DASHBOARD API DIRECTLY")
    print("=" * 60)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/customer-dashboard/customers/')
    
    # Get or create a user for testing
    user, created = User.objects.get_or_create(username='testuser')
    request.user = user
    
    print("📡 Calling api_customer_dashboard_customers...")
    
    try:
        # Call the API function directly
        response = api_customer_dashboard_customers(request)
        
        # Parse the response
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            data = json.loads(content)
            
            print(f"✅ API Response Status: {response.status_code}")
            print(f"📊 Response Status: {data.get('status', 'unknown')}")
            
            if data.get('status') == 'success':
                customers = data.get('customers', {})
                print(f"👥 Found {len(customers)} customers in API response")
                
                # Check specific customers that we know have data
                target_customers = ['BSNL', 'Tata']
                
                for customer_name in target_customers:
                    if customer_name in customers:
                        customer_data = customers[customer_name]
                        print(f"\n🏢 CUSTOMER: {customer_name}")
                        print(f"   📊 Total runs: {customer_data.get('runs', 'N/A')}")
                        print(f"   🌐 Networks count: {customer_data.get('networks_count', 'N/A')}")
                        print(f"   📅 Last run date: {customer_data.get('last_run_date', 'N/A')}")
                        
                        # Check monthly data
                        monthly_runs = customer_data.get('monthly_runs', [])
                        print(f"   📅 Monthly runs array: {monthly_runs}")
                        
                        # Check networks with runs
                        networks_with_runs = customer_data.get('networks_with_runs', [])
                        print(f"   🔗 Networks with runs: {len(networks_with_runs)}")
                        
                        for i, network in enumerate(networks_with_runs[:3]):  # Show first 3 networks
                            print(f"     Network {i+1}: {network.get('name', 'Unknown')}")
                            print(f"       Runs: {network.get('runs', 'N/A')}")
                            print(f"       Monthly data: {network.get('monthly_runs', [])}")
                            print(f"       Last run: {network.get('last_run_date', 'N/A')}")
                    else:
                        print(f"\n❌ CUSTOMER: {customer_name} - NOT FOUND in API response")
                
                # Show all customer names returned
                print(f"\n📋 All customers returned by API:")
                for name in customers.keys():
                    print(f"   - {name}")
                    
            else:
                print(f"❌ API returned error: {data.get('message', 'Unknown error')}")
                
        else:
            print(f"❌ No response content available")
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        import traceback
        traceback.print_exc()

def test_with_date_filter():
    """Test the API with date filtering"""
    print(f"\n🔍 TESTING WITH DATE FILTER")
    print("=" * 60)
    
    factory = RequestFactory()
    request = factory.get('/api/customer-dashboard/customers/', {
        'start_date': '2025-01-01',
        'end_date': '2025-12-31'
    })
    
    user, created = User.objects.get_or_create(username='testuser')
    request.user = user
    
    print("📡 Calling API with date filter (2025-01-01 to 2025-12-31)...")
    
    try:
        response = api_customer_dashboard_customers(request)
        
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            data = json.loads(content)
            
            customers = data.get('customers', {})
            print(f"👥 Found {len(customers)} customers with date filter")
            
            # Check BSNL specifically
            if 'BSNL' in customers:
                bsnl_data = customers['BSNL']
                print(f"\n🏢 BSNL with date filter:")
                print(f"   Runs: {bsnl_data.get('runs', 'N/A')}")
                print(f"   Monthly runs: {bsnl_data.get('monthly_runs', [])}")
                
                networks = bsnl_data.get('networks_with_runs', [])
                for network in networks[:2]:  # First 2 networks
                    print(f"   Network: {network.get('name', 'Unknown')}")
                    print(f"     Monthly: {network.get('monthly_runs', [])}")
            
    except Exception as e:
        print(f"❌ Error with date filter: {e}")

if __name__ == '__main__':
    test_dashboard_api()
    test_with_date_filter()
    print("\n✅ API test completed!")