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

def check_recent_customers():
    """Check recently added customers"""
    print("🔍 CHECKING RECENTLY ADDED CUSTOMERS")
    print("=" * 50)
    
    # Get the 10 most recent customers
    recent_customers = Customer.objects.filter(is_deleted=False).order_by('-id')[:10]
    
    print(f"Last 10 customers added:")
    
    for customer in recent_customers:
        print(f"\n📋 Customer ID {customer.id}: {customer.name}")
        print(f"   Network: {customer.network_name}")
        print(f"   Created: {customer.created_at}")
        print(f"   Has monthly_runs: {bool(customer.monthly_runs)}")
        
        if customer.monthly_runs:
            # Check which months have data
            months_with_data = list(customer.monthly_runs.keys())
            print(f"   Months with data: {months_with_data}")
            
            # Check October specifically
            if '2025-10' in customer.monthly_runs:
                oct_value = customer.monthly_runs['2025-10']
                print(f"   ✅ October 2025: {oct_value}")
            else:
                print(f"   ❌ No October 2025 data")
        else:
            print(f"   ❌ No monthly_runs data at all")
    
    # Also check for any customers created today
    today = datetime.now().date()
    today_customers = Customer.objects.filter(
        created_at__date=today,
        is_deleted=False
    ).order_by('-created_at')
    
    if today_customers:
        print(f"\n🆕 CUSTOMERS CREATED TODAY ({today}):")
        for customer in today_customers:
            print(f"\n📋 Customer ID {customer.id}: {customer.name}")
            print(f"   Network: {customer.network_name}")
            print(f"   Created: {customer.created_at}")
            print(f"   monthly_runs: {customer.monthly_runs}")

if __name__ == "__main__":
    check_recent_customers()