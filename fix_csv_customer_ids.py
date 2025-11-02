#!/usr/bin/env python3
"""
Fix CSV Data - Add Customer IDs Before Import
This script fixes your CSV files by adding proper customer_id values

Problem: CSV has NULL/empty customer_id values
Solution: Map customer names to actual database customer IDs

Usage: python fix_csv_customer_ids.py <path_to_csv_file>
"""

import csv
import sys
import os
import django
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

def get_customer_mapping():
    """Get mapping of customer names to IDs from database"""
    print("📊 Getting customer mapping from database...")
    
    # First ensure we have some basic customers
    create_basic_customers()
    
    mapping = {}
    customers = Customer.objects.all()
    
    for customer in customers:
        # Add various name variations to mapping
        mapping[customer.name] = customer.id
        mapping[customer.name.upper()] = customer.id
        mapping[customer.name.lower()] = customer.id
        
        if customer.network_name:
            mapping[f"{customer.name} - {customer.network_name}"] = customer.id
            mapping[f"{customer.name}_{customer.network_name}"] = customer.id
            mapping[customer.display_name] = customer.id
    
    print(f"✅ Found {len(customers)} customers in database:")
    for customer in customers:
        print(f"   ID: {customer.id} -> {customer.display_name}")
    
    return mapping

def create_basic_customers():
    """Create basic customers if they don't exist"""
    print("🔧 Creating basic customers...")
    
    basic_customers = [
        ("BSNL", "East DWDM", "India", 50, "1830 PSS", "Classic"),
        ("BSNL", "North DWDM", "India", 45, "1830 PSS", "Classic"),
        ("BSNL", "West DWDM", "India", 40, "1830 PSS", "Classic"),
        ("BSNL", "South DWDM", "India", 35, "1830 PSS", "Classic"),
        ("Moratelindo", "Network1", "Indonesia", 30, "1830 PSS", "PSS"),
        ("Tata", "Network1", "India", 25, "1830 PSS", "PSS"),
        ("LTV", "Network1", "Latvia", 20, "1830 PSS", "PSS"),
        ("OPT_NC", "Network1", "New Caledonia", 15, "1830 PSS", "PSS"),
        ("Telekom Malaysia", "Network1", "Malaysia", 35, "1830 PSS", "PSS"),
        ("Unknown", "Default", "Unknown", 1, "Unknown", "Unknown"),
    ]
    
    created_count = 0
    for name, network_name, country, node_qty, ne_type, gtac in basic_customers:
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
            created_count += 1
            print(f"   ✅ Created: {customer.display_name} (ID: {customer.id})")
    
    print(f"📊 Created {created_count} new customers")

def fix_csv_file(csv_file_path):
    """Fix CSV file by adding proper customer_id values"""
    print(f"🔧 Fixing CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"❌ File not found: {csv_file_path}")
        return False
    
    # Get customer mapping
    customer_mapping = get_customer_mapping()
    default_customer_id = list(customer_mapping.values())[0] if customer_mapping else 1
    
    # Read original CSV
    fixed_rows = []
    customer_id_column = None
    customer_name_column = None
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Find customer-related columns
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'customer_id' in header_lower:
                customer_id_column = i
            elif 'customer' in header_lower and 'name' in header_lower:
                customer_name_column = i
            elif header_lower in ['customer', 'name']:
                customer_name_column = i
        
        print(f"📋 Headers: {headers}")
        print(f"📋 Customer ID column: {customer_id_column}")
        print(f"📋 Customer name column: {customer_name_column}")
        
        fixed_rows.append(headers)
        
        # Fix each row
        rows_fixed = 0
        for row_num, row in enumerate(reader, 2):  # Start at 2 because header is row 1
            try:
                # Ensure row has enough columns
                while len(row) < len(headers):
                    row.append('')
                
                # Fix customer_id if it's empty/null
                if customer_id_column is not None:
                    current_customer_id = row[customer_id_column].strip()
                    
                    if not current_customer_id or current_customer_id.lower() in ['null', 'none', '']:
                        # Try to find customer by name
                        customer_id = default_customer_id
                        
                        if customer_name_column is not None:
                            customer_name = row[customer_name_column].strip()
                            customer_id = customer_mapping.get(customer_name, 
                                          customer_mapping.get(customer_name.upper(), 
                                          customer_mapping.get(customer_name.lower(), default_customer_id)))
                        
                        row[customer_id_column] = str(customer_id)
                        rows_fixed += 1
                        
                        if rows_fixed <= 5:  # Show first 5 fixes
                            print(f"   🔧 Row {row_num}: customer_id set to {customer_id}")
                
                fixed_rows.append(row)
                
            except Exception as e:
                print(f"❌ Error processing row {row_num}: {e}")
                fixed_rows.append(row)  # Keep original row
    
    # Write fixed CSV
    output_file = csv_file_path.replace('.csv', '_fixed.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(fixed_rows)
    
    print(f"✅ Fixed {rows_fixed} rows")
    print(f"💾 Fixed CSV saved as: {output_file}")
    print(f"🚀 Now import {output_file} instead of the original file")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python fix_csv_customer_ids.py <path_to_csv_file>")
        print("📁 Available CSV files in current directory:")
        
        for file in os.listdir('.'):
            if file.endswith('.csv'):
                print(f"   📄 {file}")
        return
    
    csv_file = sys.argv[1]
    
    print("🔧 CSV CUSTOMER ID FIXER")
    print("=" * 50)
    
    success = fix_csv_file(csv_file)
    
    if success:
        print("\n🎉 SUCCESS!")
        print("📋 Next steps:")
        print("   1. Import the *_fixed.csv file instead of the original")
        print("   2. The fixed file has proper customer_id values")
        print("   3. No more 'customer_id cannot be null' errors!")
    else:
        print("\n❌ FAILED to fix CSV file")

if __name__ == "__main__":
    main()