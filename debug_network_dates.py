#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

print("🔍 DEBUG: Checking database network structure...")
print("=" * 60)

customers = Customer.objects.filter(is_deleted=False)[:5]  # First 5 customers

for customer in customers:
    print(f"\n📊 CUSTOMER: {customer.name}")
    print(f"   Network Name: {customer.network_name}")
    print(f"   Total Runs: {customer.total_runs}")
    print(f"   Monthly Runs: {customer.monthly_runs}")
    
    # Check if monthly_runs has data
    if customer.monthly_runs:
        print("   📅 Monthly data found:")
        for month_key, date_value in customer.monthly_runs.items():
            if date_value and date_value != '-':
                print(f"      {month_key}: {date_value}")
    else:
        print("   ❌ No monthly_runs data")
    
    print("   " + "-" * 50)

print("\n🎯 SUMMARY:")
print(f"   Total customers checked: {customers.count()}")
print("   Looking for months array in API response...")