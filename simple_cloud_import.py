#!/usr/bin/env python3
"""
Simple Cloud Import - Create only Customer records
This script creates ONLY Customer records without any foreign key dependencies
"""

import csv

# Create simple CSV with only Customer model fields
input_file = "Dashboard_Export_Enhanced.csv"
output_file = "Cloud_Import_Simple.csv"

print(f"🔧 Creating simple import file from {input_file}")

# Simple Customer model fields only
simple_headers = [
    'name',
    'network_name', 
    'country',
    'node_qty',
    'ne_type',
    'gtac',
    'setup_status',
    'total_runs',
    'network_type'
]

rows = []

with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        simple_row = [
            row.get('Customer', '').strip(),           # name
            row.get('Network', '').strip(),            # network_name
            row.get('Country', 'Unknown').strip(),     # country
            row.get('Node Qty', '1').strip() or '1',   # node_qty
            row.get('NE Type', 'Unknown').strip(),     # ne_type
            row.get('gTAC', 'Unknown').strip(),        # gtac
            row.get('Setup Status', 'READY').strip(),  # setup_status
            row.get('Total Runs', '0').strip() or '0', # total_runs
            'Excel Imported'                           # network_type
        ]
        rows.append(simple_row)

# Write simple CSV
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(simple_headers)
    writer.writerows(rows)

print(f"✅ Simple import file created: {output_file}")
print(f"📊 {len(rows)} customers ready for import")
print(f"📋 Headers: {simple_headers}")
print("\n🚀 CLOUD IMPORT STEPS:")
print("1. Upload Cloud_Import_Simple.csv to cloud")
print("2. Import using Django admin or loaddata")
print("3. No foreign key errors - only Customer records!")

# Show first few rows
print(f"\n📋 Preview of first 3 rows:")
for i, row in enumerate(rows[:3], 1):
    print(f"Row {i}: {dict(zip(simple_headers, row))}")