#!/usr/bin/env python3
import os
import sys
import django
import json
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

def check_customer_data_quality():
    """Check what data is actually stored for customers"""
    
    print("🔍 Checking Customer Data Quality in Database")
    print("=" * 60)
    
    # Get all customers
    customers = Customer.objects.filter(is_deleted=False)
    print(f"Total customers in DB: {customers.count()}")
    
    # Check first few customers in detail
    print(f"\n📋 Detailed Check of First 5 Customers:")
    print("-" * 50)
    
    for i, customer in enumerate(customers[:5]):
        print(f"\n{i+1}. Customer: {customer.name}")
        print(f"   Network: {customer.network_name}")
        print(f"   Country: {customer.country}")
        print(f"   Node Qty: {customer.node_qty}")
        print(f"   NE Type: {customer.ne_type}")
        print(f"   gTAC: {customer.gtac}")
        print(f"   Total Runs: {customer.total_runs}")
        print(f"   Setup Status: {customer.setup_status}")
        
        # Check monthly_runs field
        print(f"   Monthly Runs Type: {type(customer.monthly_runs)}")
        if customer.monthly_runs:
            print(f"   Monthly Runs Keys: {list(customer.monthly_runs.keys()) if isinstance(customer.monthly_runs, dict) else 'Not a dict'}")
            print(f"   Monthly Runs Sample: {str(customer.monthly_runs)[:200]}...")
        else:
            print(f"   Monthly Runs: NULL/Empty")
    
    # Check distribution of total_runs
    print(f"\n📊 Total Runs Distribution:")
    runs_stats = {}
    for customer in customers:
        runs = customer.total_runs or 0
        runs_stats[runs] = runs_stats.get(runs, 0) + 1
    
    for runs, count in sorted(runs_stats.items()):
        print(f"   {runs} runs: {count} customers")
    
    # Check monthly_runs data quality
    print(f"\n📅 Monthly Runs Data Quality:")
    customers_with_monthly_data = 0
    customers_without_monthly_data = 0
    
    for customer in customers:
        if customer.monthly_runs and isinstance(customer.monthly_runs, dict) and customer.monthly_runs:
            customers_with_monthly_data += 1
        else:
            customers_without_monthly_data += 1
    
    print(f"   Customers WITH monthly data: {customers_with_monthly_data}")
    print(f"   Customers WITHOUT monthly data: {customers_without_monthly_data}")
    
    # Show sample monthly data structure
    customer_with_data = customers.exclude(monthly_runs__isnull=True).first()
    if customer_with_data and customer_with_data.monthly_runs:
        print(f"\n🔍 Sample Monthly Data Structure ({customer_with_data.name}):")
        monthly_data = customer_with_data.monthly_runs
        if isinstance(monthly_data, dict):
            for key, value in list(monthly_data.items())[:5]:  # Show first 5
                print(f"   {key}: {value}")
    
    # Check for October 2025 data specifically
    print(f"\n🗓️ October 2025 Data Check:")
    customers_with_oct_2025 = 0
    
    for customer in customers:
        if customer.monthly_runs and isinstance(customer.monthly_runs, dict):
            # Check for October 2025 in various formats
            oct_keys = [k for k in customer.monthly_runs.keys() if '2025-10' in str(k) or 'Oct' in str(k) or 'October' in str(k)]
            if oct_keys:
                customers_with_oct_2025 += 1
                print(f"   {customer.name}: {oct_keys}")
    
    print(f"   Total customers with October 2025 data: {customers_with_oct_2025}")

if __name__ == "__main__":
    check_customer_data_quality()