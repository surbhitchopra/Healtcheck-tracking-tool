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

def create_enhanced_export():
    """Create enhanced CSV export with proper status messages and network info"""
    print("📊 CREATING ENHANCED DASHBOARD EXPORT")
    print("=" * 60)
    
    # Get customers from DATABASE (same as dashboard API)
    db_customers = Customer.objects.filter(is_deleted=False)
    print(f"Processing {db_customers.count()} customers...")
    
    # Create CSV data
    csv_rows = []
    
    # Enhanced Header row with more details
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    headers = [
        'Customer', 'Network', 'Country', 'Node Qty', 'NE Type', 'gTAC', 
        'Setup Status', 'Total Runs', 'Data Source'
    ] + month_names
    csv_rows.append(','.join(headers))
    
    for customer in db_customers:
        # Create months array (same logic as dashboard API)
        months = ["-"] * 12
        total_runs_count = customer.total_runs or 0
        
        # Process monthly runs from database (enhanced with proper status handling)
        if customer.monthly_runs:
            for month_key, date_value in customer.monthly_runs.items():
                try:
                    # Parse month from key like "2025-01" or "2025-10"
                    if '-' in month_key and len(month_key.split('-')) >= 2:
                        month_num = int(month_key.split('-')[1])
                        if 1 <= month_num <= 12:
                            # Enhanced date/status formatting
                            if date_value and str(date_value).strip() not in ['-', '', 'None', 'null']:
                                date_str = str(date_value).strip()
                                
                                # Handle different status messages properly
                                if date_str in ['Not Started', 'Not Run', 'No Report', 'Not Starte']:
                                    # Clean up typos and standardize status messages
                                    if date_str == 'Not Starte':
                                        months[month_num - 1] = 'Not Started'
                                    else:
                                        months[month_num - 1] = date_str
                                elif date_str.lower() in ['pending', 'processing', 'failed', 'cancelled']:
                                    # Handle session status messages
                                    months[month_num - 1] = date_str.title()
                                else:
                                    try:
                                        # Try to parse as date and format it
                                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                        months[month_num - 1] = date_obj.strftime('%d-%b')
                                    except ValueError:
                                        # If parsing fails, show the raw value (might be custom status)
                                        months[month_num - 1] = date_str
                            else:
                                months[month_num - 1] = '-'
                except (ValueError, IndexError) as e:
                    continue
        
        # Enhanced row data with more information
        row_data = [
            customer.name,
            customer.network_name or 'Unknown Network',
            customer.country or 'Not Specified',
            str(customer.node_qty or 0),
            customer.ne_type or '1830 PSS',
            customer.gtac or 'PSS',
            customer.setup_status or 'READY',
            str(total_runs_count),
            'Database'  # Data source indicator
        ]
        
        # Add monthly data
        row_data.extend(months)
        
        # Clean data for CSV (proper escaping)
        clean_row = []
        for item in row_data:
            item_str = str(item)
            # Escape quotes and commas properly
            if ',' in item_str or '"' in item_str:
                item_str = item_str.replace('"', '""')  # Escape quotes
                clean_row.append(f'"{item_str}"')
            else:
                clean_row.append(item_str)
        
        csv_rows.append(','.join(clean_row))
    
    # Write to enhanced file
    output_file = 'Dashboard_Export_Enhanced.csv'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_rows))
    
    print(f"✅ Enhanced export created: {output_file}")
    print(f"📊 Total customers: {len(csv_rows) - 1}")
    
    # Show detailed analysis
    status_analysis = {}
    october_customers = []
    
    for customer in db_customers:
        if customer.monthly_runs:
            for month_key, date_value in customer.monthly_runs.items():
                if date_value:
                    status = str(date_value).strip()
                    if status not in status_analysis:
                        status_analysis[status] = 0
                    status_analysis[status] += 1
                    
                    # Track October specifically
                    if month_key == '2025-10':
                        october_customers.append((customer.name, customer.network_name, status))
    
    print(f"\n📈 STATUS ANALYSIS:")
    for status, count in sorted(status_analysis.items()):
        if status.startswith('2025-'):
            # It's a date
            try:
                date_obj = datetime.strptime(status, '%Y-%m-%d')
                formatted = date_obj.strftime('%d-%b')
                print(f"   📅 Date {formatted}: {count} entries")
            except:
                print(f"   📅 {status}: {count} entries")
        else:
            # It's a status message
            print(f"   📝 Status '{status}': {count} entries")
    
    print(f"\n🎯 OCTOBER 2025 CUSTOMERS:")
    for name, network, status in october_customers:
        if status.startswith('2025-'):
            try:
                date_obj = datetime.strptime(status, '%Y-%m-%d')
                formatted = date_obj.strftime('%d-%b')
                print(f"   ✅ {name} - {network}: {formatted}")
            except:
                print(f"   ✅ {name} - {network}: {status}")
        else:
            print(f"   ⚠️ {name} - {network}: {status}")
    
    print(f"\n🎯 ENHANCED EXPORT SUMMARY:")
    print(f"✅ Total customers exported: {len(csv_rows) - 1}")
    print(f"✅ Customers with October data: {len(october_customers)}")
    print(f"✅ Enhanced columns: Customer, Network, Country, Node Qty, NE Type, gTAC, Setup Status, Total Runs, Data Source")
    print(f"✅ Proper status messages: Not Started, Not Run, No Report")
    print(f"✅ Dates in DD-MMM format: 08-Oct, 15-May")
    print(f"✅ File: {output_file}")
    
    return output_file

if __name__ == "__main__":
    create_enhanced_export()
    print("\n💡 Enhanced Features:")
    print("✅ Proper status message formatting")
    print("✅ Network information properly displayed")
    print("✅ Additional columns (Setup Status, Data Source)")
    print("✅ Better CSV escaping for special characters")
    print("✅ Status analysis and reporting")