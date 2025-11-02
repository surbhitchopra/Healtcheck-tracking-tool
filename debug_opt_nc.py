#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from your_app.models import Customer
from datetime import datetime

# Check OPT_NC customer data
print("🔍 Checking OPT_NC customer data...")

opt_nc_customers = Customer.objects.filter(name__icontains='OPT_NC', is_deleted=False)
print(f"Found {opt_nc_customers.count()} OPT_NC customers")

for customer in opt_nc_customers:
    print(f"\n📊 Customer: {customer.name}")
    print(f"Network: {customer.network_name}")
    print(f"Total Runs: {customer.total_runs}")
    print(f"Monthly Runs: {customer.monthly_runs}")
    
    # Check October 2024 specifically
    if customer.monthly_runs:
        oct_key = "2024-10"
        if oct_key in customer.monthly_runs:
            print(f"October 2024: {customer.monthly_runs[oct_key]}")
        else:
            print("October 2024: Not found in monthly_runs")
            # Check all available months
            print("Available months:", list(customer.monthly_runs.keys()))

print("\n✅ Debug complete")