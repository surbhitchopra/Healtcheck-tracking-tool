#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from django.test import RequestFactory
from views import get_excel_summary_data

def test_dashboard_api():
    """Test the dashboard API directly to see what data it returns"""
    
    print("🧪 Testing Dashboard API Directly")
    print("=" * 50)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/get-excel-summary-data/')
    
    # Call the API without date filters
    print("🔍 Testing API WITHOUT date filters...")
    response = get_excel_summary_data(request)
    response_data = response.content.decode('utf-8')
    
    try:
        import json
        data = json.loads(response_data)
        
        print(f"✅ API Response Success: {data.get('success')}")
        print(f"📊 Total Networks: {data.get('total_networks')}")
        print(f"💬 Message: {data.get('message')}")
        
        # Check first few customers
        customers = data.get('customers', {})
        print(f"\n🏢 Sample Customer Data:")
        
        for i, (key, customer) in enumerate(list(customers.items())[:3]):
            print(f"\n{i+1}. Key: {key}")
            print(f"   Customer: {customer.get('Customer')}")
            print(f"   Network: {customer.get('Network')}")
            print(f"   Total Runs: {customer.get('total_runs')}")
            print(f"   Months: {customer.get('months')[:6]}...")  # Show first 6 months
            
            # Check if networks array has data
            networks = customer.get('networks', [])
            if networks:
                print(f"   Network[0] Runs: {networks[0].get('runs')}")
                print(f"   Network[0] Monthly: {networks[0].get('months')[:3]}...")
    
    except Exception as e:
        print(f"❌ Error parsing API response: {e}")
        print(f"Raw response: {response_data[:500]}...")
    
    # Test with October date filter
    print(f"\n🗓️ Testing API WITH October 2025 date filter...")
    request_with_dates = factory.get('/get-excel-summary-data/?start_date=2025-10-01&end_date=2025-10-31')
    response_filtered = get_excel_summary_data(request_with_dates)
    response_filtered_data = response_filtered.content.decode('utf-8')
    
    try:
        data_filtered = json.loads(response_filtered_data)
        print(f"✅ Filtered API Success: {data_filtered.get('success')}")
        print(f"📊 Filtered Networks: {data_filtered.get('total_networks')}")
        print(f"💬 Filtered Message: {data_filtered.get('message')}")
        
        if data_filtered.get('total_networks', 0) == 0:
            print(f"⚠️ NO DATA returned for October 2025 filter - this explains dashboard issue!")
        
    except Exception as e:
        print(f"❌ Error parsing filtered API response: {e}")
        print(f"Raw filtered response: {response_filtered_data[:500]}...")

if __name__ == "__main__":
    test_dashboard_api()