#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime

# Add the project directory to the Python path
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now we can import Django models
from HealthCheck_app.models import Customer

def check_bsnl_east_dwdm():
    """Check BSNL East DWDM network data and recent runs"""
    print("=== CHECKING BSNL EAST DWDM OCTOBER RUN ===\n")
    
    try:
        # Look for BSNL networks
        bsnl_customers = Customer.objects.filter(name__icontains='bsnl')
        print(f"Found {bsnl_customers.count()} BSNL customers")
        
        for customer in bsnl_customers:
            print(f"\n📋 Customer: {customer.name}")
            print(f"   Network: {customer.network_name}")
            print(f"   Monthly runs: {customer.monthly_runs}")
            print(f"   Total runs: {customer.total_runs}")
            print(f"   Setup status: {customer.setup_status}")
            print(f"   Created: {customer.created_at}")
            
            # Check if this is East DWDM
            if 'east' in customer.network_name.lower() or 'dwdm' in customer.network_name.lower():
                print(f"   🎯 FOUND EAST DWDM: {customer.network_name}")
                
                # Check October data specifically
                if customer.monthly_runs and isinstance(customer.monthly_runs, dict):
                    october_keys = [key for key in customer.monthly_runs.keys() if '10' in key or 'oct' in key.lower()]
                    print(f"   October keys found: {october_keys}")
                    
                    for key in october_keys:
                        print(f"   📅 {key}: {customer.monthly_runs[key]}")
            
            # Check recent runs through sessions
            sessions = customer.healthchecksession_set.all().order_by('-created_at')[:5]
            if sessions.exists():
                print(f"   📊 Recent sessions ({sessions.count()}):")
                for i, session in enumerate(sessions):
                    print(f"     {i+1}. {session.created_at.strftime('%Y-%m-%d %H:%M')} - {session.session_type}")
            
        print("\n" + "="*50)
        
        # Also check for any October runs across all customers
        print("\n🔍 CHECKING ALL OCTOBER DATA:")
        all_customers = Customer.objects.all()
        
        october_customers = []
        for customer in all_customers:
            if customer.monthly_runs and isinstance(customer.monthly_runs, dict):
                october_data = {}
                for key, value in customer.monthly_runs.items():
                    if ('2024-10' in key or '2025-10' in key) and value and value != 'Not Started':
                        october_data[key] = value
                
                if october_data:
                    october_customers.append({
                        'customer': customer,
                        'october_data': october_data
                    })
        
        print(f"\nFound {len(october_customers)} customers with October data:")
        for item in october_customers:
            customer = item['customer']
            october_data = item['october_data']
            print(f"\n📋 {customer.name} - {customer.network_name}")
            for key, value in october_data.items():
                print(f"   📅 {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    check_bsnl_east_dwdm()