#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(r'C:\Users\surchopr\Hc_Final')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now import Django models
from HealthCheck_app.models import Customer

def debug_monthly_runs():
    """Check the actual format of monthly_runs data"""
    print("🔍 DEBUGGING MONTHLY RUNS DATA FORMAT")
    print("=" * 50)
    
    # Get all customers with monthly_runs data
    customers = Customer.objects.filter(is_deleted=False).exclude(monthly_runs={})
    
    print(f"Found {customers.count()} customers with monthly_runs data")
    
    for customer in customers:
        print(f"\n📋 Customer: {customer.name} (ID: {customer.id})")
        print(f"   Network: {customer.network_name}")
        print(f"   monthly_runs type: {type(customer.monthly_runs)}")
        print(f"   monthly_runs value: {customer.monthly_runs}")
        
        if customer.monthly_runs:
            for key, value in customer.monthly_runs.items():
                print(f"      Key: '{key}' (type: {type(key)}) -> Value: '{value}' (type: {type(value)})")

if __name__ == "__main__":
    debug_monthly_runs()