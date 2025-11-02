import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from views import customer_dashboard_excel
from django.test import RequestFactory
import json

# Create a test request
factory = RequestFactory()
request = factory.get('/customer-dashboard/excel/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

try:
    print("🔄 Testing Excel API endpoint...")
    response = customer_dashboard_excel(request)
    
    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response type: {type(response)}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        try:
            data = json.loads(content)
            print(f"✅ JSON response received")
            print(f"📊 Success: {data.get('success', 'N/A')}")
            print(f"📊 Total customers: {data.get('total_customers', 'N/A')}")
            print(f"📊 Customer keys: {list(data.get('customers', {}).keys())[:5]}...")  # First 5 keys
            
            if data.get('customers'):
                sample_customer = list(data['customers'].values())[0]
                print(f"📋 Sample customer structure: {list(sample_customer.keys())}")
                
        except json.JSONDecodeError:
            print(f"❌ Response is not JSON. Content preview: {content[:200]}")
    else:
        print(f"❌ Error response: {response.content.decode('utf-8')[:200]}")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")
    import traceback
    traceback.print_exc()