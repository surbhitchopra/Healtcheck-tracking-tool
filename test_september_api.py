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

def test_september_api():
    """Test API with September 2025 filter - should return data"""
    
    print("🧪 Testing API with September 2025 Filter")
    print("=" * 50)
    
    factory = RequestFactory()
    
    # Test with September 2025 filter
    print("🗓️ Testing API WITH September 2025 date filter...")
    request_sep = factory.get('/get-excel-summary-data/?start_date=2025-09-01&end_date=2025-09-30')
    response_sep = get_excel_summary_data(request_sep)
    response_sep_data = response_sep.content.decode('utf-8')
    
    try:
        import json
        data_sep = json.loads(response_sep_data)
        
        print(f"✅ September API Success: {data_sep.get('success')}")
        print(f"📊 September Networks: {data_sep.get('total_networks')}")
        print(f"💬 September Message: {data_sep.get('message')}")
        
        if data_sep.get('total_networks', 0) > 0:
            print(f"🎉 SUCCESS! September 2025 returns {data_sep.get('total_networks')} networks")
            
            # Show sample data
            customers = data_sep.get('customers', {})
            for i, (key, customer) in enumerate(list(customers.items())[:2]):
                print(f"\n🏢 {i+1}. {customer.get('Customer')} - {customer.get('Network')}")
                print(f"   Total Runs: {customer.get('total_runs')}")
                print(f"   Months: {customer.get('months')}")
        else:
            print(f"❌ Even September 2025 returns no data!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Raw response: {response_sep_data[:500]}...")

if __name__ == "__main__":
    test_september_api()