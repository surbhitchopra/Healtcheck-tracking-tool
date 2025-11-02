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

from HealthCheck_app.models import Customer
from django.http import HttpResponse

def create_simple_excel_export():
    """Create a simple CSV export that matches dashboard exactly"""
    print("📊 CREATING SIMPLE DASHBOARD EXPORT")
    print("=" * 50)
    
    # Get customers from DATABASE (same as dashboard API)
    db_customers = Customer.objects.filter(is_deleted=False)
    print(f"Processing {db_customers.count()} customers...")
    
    # Create CSV data
    csv_rows = []
    
    # Header row
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    headers = ['Customer', 'Network', 'Country', 'Node Qty', 'NE Type', 'gTAC', 'Total Runs'] + month_names
    csv_rows.append(','.join(headers))
    
    for customer in db_customers:
        # Create months array (same logic as dashboard API)
        months = ["-"] * 12
        total_runs_count = customer.total_runs or 0
        
        # Process monthly runs from database (same logic as views.py)
        if customer.monthly_runs:
            for month_key, date_value in customer.monthly_runs.items():
                try:
                    # Parse month from key like "2025-01" or "2025-10"
                    if '-' in month_key and len(month_key.split('-')) >= 2:
                        month_num = int(month_key.split('-')[1])
                        if 1 <= month_num <= 12:
                            # Format date for display
                            if date_value and str(date_value).strip() not in ['-', '', 'None', 'null']:
                                # Check if it's an actual date or status message
                                date_str = str(date_value).strip()
                                if date_str in ['Not Started', 'Not Run', 'No Report']:
                                    # Show status messages as-is
                                    months[month_num - 1] = date_str
                                else:
                                    try:
                                        # Try to parse as date and format it
                                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                        months[month_num - 1] = date_obj.strftime('%d-%b')
                                    except ValueError:
                                        # If parsing fails, show the raw value
                                        months[month_num - 1] = date_str
                            else:
                                months[month_num - 1] = '-'
                except (ValueError, IndexError) as e:
                    continue
        
        # Create row data (same as dashboard)
        row_data = [
            customer.name,
            customer.network_name or 'Unknown',
            customer.country or '',
            str(customer.node_qty or 0),
            customer.ne_type or '1830 PSS',
            customer.gtac or 'PSS',
            str(total_runs_count)
        ]
        
        # Add monthly data
        row_data.extend(months)
        
        # Clean data for CSV (escape commas)
        clean_row = []
        for item in row_data:
            item_str = str(item)
            if ',' in item_str:
                clean_row.append(f'"{item_str}"')
            else:
                clean_row.append(item_str)
        
        csv_rows.append(','.join(clean_row))
    
    # Write to file
    output_file = 'Dashboard_Export_Fixed.csv'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_rows))
    
    print(f"✅ Export created: {output_file}")
    print(f"📊 Total customers: {len(csv_rows) - 1}")
    
    # Show sample of customers with October data
    october_count = 0
    for customer in db_customers:
        if customer.monthly_runs and '2025-10' in customer.monthly_runs:
            october_count += 1
            oct_date = customer.monthly_runs['2025-10']
            # Format it
            try:
                date_obj = datetime.strptime(oct_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d-%b')
                print(f"✅ {customer.name} - {customer.network_name}: October = {formatted_date}")
            except:
                print(f"✅ {customer.name} - {customer.network_name}: October = {oct_date}")
    
    print(f"\n🎯 EXPORT SUMMARY:")
    print(f"✅ Total customers exported: {len(csv_rows) - 1}")
    print(f"✅ Customers with October data: {october_count}")
    print(f"✅ Format: DD-MMM (like 08-Oct)")
    print(f"✅ File: {output_file}")
    
    return output_file

if __name__ == "__main__":
    create_simple_excel_export()
    print("\n💡 Next steps:")
    print("1. Open Dashboard_Export_Fixed.csv")
    print("2. Check if dates are in DD-MMM format")
    print("3. Compare with dashboard live data")
    print("4. If matches, use this logic in export function")