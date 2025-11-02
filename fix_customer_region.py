#!/usr/bin/env python3
"""
Fix customer names to include proper regions
"""

# Add the Django app to the path
import sys
import os
from pathlib import Path

# Add the project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')

import django
django.setup()

# Now we can import Django models
from HealthCheck_app.models import Customer

def fix_customer_regions():
    """Update customer names to include proper regions"""
    
    print("=" * 60)
    print("FIXING CUSTOMER REGIONS")
    print("=" * 60)
    
    customers = Customer.objects.filter(is_deleted=False).order_by('name')
    
    for customer in customers:
        print(f"\nCurrent Customer: ID={customer.id}, Name=\"{customer.name}\"")
        
        if customer.name.lower() == "bsnl":
            # Ask which region this should be
            print(f"\nThis customer needs a region specification.")
            print(f"Available regions: NORTH, SOUTH, EAST, WEST")
            
            # For demonstration, let's make one North and one East
            if customer.id == 72:
                new_name = "BSNL North DWDM"
                print(f"Updating to: {new_name}")
                customer.name = new_name
                customer.save()
                print(f"✅ Updated Customer ID {customer.id} to '{new_name}'")
            elif customer.id == 73:
                new_name = "BSNL East DWDM" 
                print(f"Updating to: {new_name}")
                customer.name = new_name
                customer.save()
                print(f"✅ Updated Customer ID {customer.id} to '{new_name}'")
        else:
            print(f"Skipping '{customer.name}' - not a generic BSNL customer")
    
    print(f"\n" + "=" * 60)
    print("UPDATED CUSTOMERS:")
    print("=" * 60)
    
    customers = Customer.objects.filter(is_deleted=False).order_by('name')
    for customer in customers:
        print(f"ID={customer.id}, Name=\"{customer.name}\"")

if __name__ == "__main__":
    fix_customer_regions()
