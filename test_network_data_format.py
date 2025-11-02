#!/usr/bin/env python3
"""
Quick test to see exactly what network data format the API is returning
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

def test_network_data_format():
    """Test exactly what network data is being returned"""
    print("🔍 TESTING NETWORK DATA FORMAT IN API RESPONSE")
    print("=" * 70)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/customer-dashboard/customers/')
    
    # Get or create a user for testing
    user, created = User.objects.get_or_create(username='testuser')
    request.user = user
    
    try:
        # Call the API function directly
        response = api_customer_dashboard_customers(request)
        
        # Parse the response
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            data = json.loads(content)
            
            if data.get('status') == 'success':
                customers = data.get('customers', {})
                print(f"✅ Found {len(customers)} customers")
                
                # Focus on BSNL as example
                if 'BSNL' in customers:
                    bsnl_data = customers['BSNL']
                    print(f"\n🏢 BSNL DATA STRUCTURE:")
                    print(f"   📊 Total runs: {bsnl_data.get('runs', 'N/A')}")
                    print(f"   📊 Networks count: {bsnl_data.get('networks_count', 'N/A')}")
                    
                    # Check networks array structure
                    networks = bsnl_data.get('networks', [])
                    print(f"   🔗 Networks array: {len(networks)} items")
                    
                    if networks:
                        print(f"\n📡 FIRST NETWORK STRUCTURE:")
                        first_network = networks[0]
                        for key, value in first_network.items():
                            if key == 'monthly_runs':
                                print(f"   {key}: {value[:3]}... (showing first 3 months)")
                            else:
                                print(f"   {key}: {value}")
                    
                    # Check network_runs structure (alternative format)
                    network_runs = bsnl_data.get('network_runs', {})
                    print(f"\n📡 NETWORK_RUNS STRUCTURE:")
                    for network_name, runs in list(network_runs.items())[:3]:
                        print(f"   {network_name}: {runs}")
                    
                    # Check monthly_runs array
                    monthly_runs = bsnl_data.get('monthly_runs', [])
                    print(f"\n📅 CUSTOMER-LEVEL MONTHLY ARRAY:")
                    print(f"   Length: {len(monthly_runs)}")
                    print(f"   Content: {monthly_runs}")
                    
                    print(f"\n🔍 ALL BSNL KEYS:")
                    for key in sorted(bsnl_data.keys()):
                        print(f"   - {key}")
                
                else:
                    print("❌ BSNL not found in response")
                    print(f"Available customers: {list(customers.keys())}")
            
        else:
            print("❌ No response content")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_network_data_format()
    print("\n✅ Test completed!")