#!/usr/bin/env python3
"""
Debug script to check customer network data and monthly_runs in database
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession
from django.db import models
import json

def debug_customer_network_data():
    """Debug customer network data to see what's in the database"""
    print("🔍 DEBUGGING CUSTOMER NETWORK DATA")
    print("=" * 60)
    
    # Get all customers
    customers = Customer.objects.filter(is_deleted=False).order_by('name')
    print(f"📊 Found {customers.count()} active customers in database")
    
    customer_groups = {}
    for customer in customers:
        if customer.name not in customer_groups:
            customer_groups[customer.name] = []
        customer_groups[customer.name].append(customer)
    
    print(f"📊 Grouped into {len(customer_groups)} unique customer names")
    
    for customer_name, networks in customer_groups.items():
        print(f"\n🏢 CUSTOMER: {customer_name}")
        print(f"   Networks: {len(networks)}")
        
        for i, network in enumerate(networks):
            print(f"   📡 Network {i+1}: {network.network_name or 'Default'} (ID: {network.id})")
            print(f"      - Country: {network.country}")
            print(f"      - Node Qty: {network.node_qty}")
            print(f"      - Total Runs: {network.total_runs}")
            print(f"      - NE Type: {network.ne_type}")
            print(f"      - gTAC: {network.gtac}")
            print(f"      - Monthly Runs: {network.monthly_runs}")
            print(f"      - Monthly Runs Type: {type(network.monthly_runs)}")
            
            if network.monthly_runs:
                print(f"      - Monthly Runs Detail:")
                if isinstance(network.monthly_runs, dict):
                    for month, date in network.monthly_runs.items():
                        print(f"        {month}: {date}")
                else:
                    print(f"        Raw value: {network.monthly_runs}")
            
            # Check sessions for this network
            sessions = HealthCheckSession.objects.filter(customer=network)
            print(f"      - Sessions: {sessions.count()}")
            
            if sessions.exists():
                recent_sessions = sessions.order_by('-created_at')[:3]
                print(f"      - Recent session dates:")
                for session in recent_sessions:
                    print(f"        {session.created_at.strftime('%Y-%m-%d')}: {session.status}")

def debug_specific_customers():
    """Debug specific customers that should have network data"""
    target_customers = ['BSNL', 'Tata', 'Moratel', 'Railtel']
    
    print(f"\n🎯 DEBUGGING SPECIFIC CUSTOMERS: {target_customers}")
    print("=" * 60)
    
    for customer_name in target_customers:
        customers = Customer.objects.filter(name__icontains=customer_name, is_deleted=False)
        print(f"\n🔍 Searching for customers with '{customer_name}':")
        print(f"   Found: {customers.count()} matches")
        
        for customer in customers:
            print(f"   📊 {customer.name} - {customer.network_name}")
            print(f"      Monthly runs: {customer.monthly_runs}")
            print(f"      Node qty: {customer.node_qty}")
            print(f"      Total runs: {customer.total_runs}")

def check_data_quality():
    """Check data quality issues"""
    print(f"\n⚠️ DATA QUALITY CHECK")
    print("=" * 60)
    
    # Check customers with empty monthly_runs
    empty_monthly = Customer.objects.filter(monthly_runs__isnull=True, is_deleted=False) | \
                   Customer.objects.filter(monthly_runs={}, is_deleted=False)
    print(f"📊 Customers with empty monthly_runs: {empty_monthly.count()}")
    
    # Check customers with populated monthly_runs
    populated_monthly = Customer.objects.exclude(monthly_runs__isnull=True).exclude(monthly_runs={}).filter(is_deleted=False)
    print(f"📊 Customers with populated monthly_runs: {populated_monthly.count()}")
    
    # Show some examples
    if populated_monthly.exists():
        print(f"\n✅ EXAMPLES WITH DATA:")
        for customer in populated_monthly[:5]:
            print(f"   {customer.name} - {customer.network_name}: {len(customer.monthly_runs or {})} months")
            if customer.monthly_runs:
                for month, date in list((customer.monthly_runs or {}).items())[:3]:
                    print(f"     {month}: {date}")

if __name__ == '__main__':
    try:
        debug_customer_network_data()
        debug_specific_customers()
        check_data_quality()
        print("\n✅ Debug completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()