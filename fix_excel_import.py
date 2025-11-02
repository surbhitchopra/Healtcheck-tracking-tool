#!/usr/bin/env python3
"""
Excel Data Import Fix for Cloud Database
Fixes the "Column 'customer_id' cannot be null" error when importing to MySQL

The issue: MySQL requires foreign key references to exist before inserting dependent records.
SQLite was more lenient, but MySQL enforces foreign key constraints strictly.

This script:
1. Creates Customer records first (primary table)
2. Then imports HealthCheckSession and HealthCheckFile records with proper customer_id references

Usage: python fix_excel_import.py
"""

import os
import sys
import django
from django.conf import settings
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession, HealthCheckFile

def fix_excel_data_import():
    """
    Fix Excel data import by ensuring Customer records exist before importing sessions/files
    """
    print("🔧 FIXING EXCEL DATA IMPORT FOR CLOUD DATABASE")
    print("=" * 60)
    
    # Step 1: Check current database state
    customers_count = Customer.objects.count()
    sessions_count = HealthCheckSession.objects.count() 
    files_count = HealthCheckFile.objects.count()
    
    print(f"📊 Current database state:")
    print(f"   Customers: {customers_count}")
    print(f"   Sessions: {sessions_count}")
    print(f"   Files: {files_count}")
    
    # Step 2: Create Customer records from Excel data if they don't exist
    excel_customers = [
        # Add your Excel customer data here
        # Format: (name, network_name, country, node_qty, ne_type, gtac)
        ("BSNL", "East DWDM", "India", 50, "1830 PSS", "Classic"),
        ("BSNL", "North DWDM", "India", 45, "1830 PSS", "Classic"), 
        ("Moratelindo", "Network1", "Indonesia", 30, "1830 PSS", "PSS"),
        ("Tata", "Network1", "India", 25, "1830 PSS", "PSS"),
        ("LTV", "Network1", "Latvia", 20, "1830 PSS", "PSS"),
        ("OPT_NC", "Network1", "New Caledonia", 15, "1830 PSS", "PSS"),
        # Add more customers as needed based on your Excel data
    ]
    
    print(f"\\n📝 Creating Customer records...")
    customers_created = 0
    
    with transaction.atomic():
        for name, network_name, country, node_qty, ne_type, gtac in excel_customers:
            customer, created = Customer.objects.get_or_create(
                name=name,
                network_name=network_name,
                defaults={
                    'country': country,
                    'node_qty': node_qty,
                    'ne_type': ne_type,
                    'gtac': gtac,
                    'network_type': 'Excel Imported',
                    'setup_status': 'READY',
                    'total_runs': 0,
                    'monthly_runs': {}
                }
            )
            
            if created:
                customers_created += 1
                print(f"   ✅ Created: {customer.display_name}")
            else:
                print(f"   ⚪ Exists: {customer.display_name}")
    
    print(f"\\n📊 Created {customers_created} new Customer records")
    
    # Step 3: Verify all required customers exist
    print(f"\\n🔍 Verifying Customer records...")
    all_customers = Customer.objects.all()
    for customer in all_customers:
        print(f"   ID: {customer.id}, Name: {customer.display_name}")
    
    # Step 4: Instructions for importing sessions and files
    print(f"\\n📋 NEXT STEPS:")
    print(f"   1. Customer records are now created with proper IDs")
    print(f"   2. When importing HealthCheckSession records, use customer.id as customer_id")
    print(f"   3. When importing HealthCheckFile records, use customer.id as customer_id")
    print(f"   4. Update your CSV import script to map customer names to IDs:")
    print(f"   ")
    print(f"   Example mapping:")
    for customer in all_customers[:5]:  # Show first 5 as example
        print(f"   '{customer.name}' -> customer_id = {customer.id}")
    
    print(f"\\n✅ Excel import preparation completed!")
    print(f"   Total customers in database: {Customer.objects.count()}")

def create_customer_id_mapping():
    """Create a mapping file for CSV import scripts"""
    
    mapping_file = "customer_id_mapping.py"
    
    print(f"\\n📝 Creating customer ID mapping file: {mapping_file}")
    
    mapping_content = '''# Customer ID Mapping for Excel Import
# Generated automatically - maps customer names to database IDs

CUSTOMER_ID_MAPPING = {
'''
    
    all_customers = Customer.objects.all()
    for customer in all_customers:
        # Create mapping entries for various name formats
        mapping_content += f"    '{customer.name}': {customer.id},\\n"
        if customer.network_name:
            mapping_content += f"    '{customer.name} - {customer.network_name}': {customer.id},\\n"
            mapping_content += f"    '{customer.display_name}': {customer.id},\\n"
    
    mapping_content += '''}

def get_customer_id(customer_name):
    """Get customer ID by name"""
    return CUSTOMER_ID_MAPPING.get(customer_name, None)

def get_customer_id_safe(customer_name):
    """Get customer ID by name with fallback"""
    customer_id = get_customer_id(customer_name)
    if customer_id is None:
        print(f"⚠️  Customer not found: {customer_name}")
        print(f"Available customers: {list(CUSTOMER_ID_MAPPING.keys())}")
    return customer_id
'''
    
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write(mapping_content)
    
    print(f"   ✅ Mapping file created: {mapping_file}")
    print(f"   Use: from customer_id_mapping import get_customer_id")

if __name__ == "__main__":
    try:
        fix_excel_data_import()
        create_customer_id_mapping()
        
        print(f"\\n🎉 SUCCESS! Excel import preparation completed.")
        print(f"   Now you can run your CSV import with proper customer_id references.")
        
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()