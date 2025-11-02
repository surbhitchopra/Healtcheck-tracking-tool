#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(r'C:\Users\surchopr\Hc_Final')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now import Django models
from HealthCheck_app.models import Customer

def check_october_data():
    """Check specifically for October 2025 data"""
    print("🔍 CHECKING OCTOBER 2025 DATA")
    print("=" * 50)
    
    # Get all customers
    all_customers = Customer.objects.filter(is_deleted=False)
    
    october_customers = []
    
    for customer in all_customers:
        if customer.monthly_runs:
            # Check if customer has October 2025 data
            has_october = '2025-10' in customer.monthly_runs
            if has_october:
                october_customers.append(customer)
    
    print(f"Found {len(october_customers)} customers with October 2025 data:")
    
    for customer in october_customers:
        print(f"\n📋 Customer: {customer.name}")
        print(f"   Network: {customer.network_name}")
        print(f"   October 2025 value: {customer.monthly_runs.get('2025-10')}")
        print(f"   Full monthly_runs: {customer.monthly_runs}")
    
    # Test the processing logic for October
    print(f"\n🔧 TESTING OCTOBER DATE PROCESSING:")
    for customer in october_customers:
        oct_value = customer.monthly_runs.get('2025-10')
        print(f"\nCustomer: {customer.name}")
        print(f"Raw October value: {repr(oct_value)}")
        
        # Apply the processing logic
        if oct_value and str(oct_value).strip() not in ['-', '', 'None', 'null']:
            date_str = str(oct_value).strip()
            if date_str in ['Not Started', 'Not Run', 'No Report']:
                result = date_str
                print(f"Status message: {result}")
            else:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    result = date_obj.strftime('%d-%b')
                    print(f"✅ Formatted date: {result}")
                except ValueError as e:
                    result = date_str
                    print(f"❌ Parse error: {e}, using raw: {result}")

if __name__ == "__main__":
    check_october_data()