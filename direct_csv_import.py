#!/usr/bin/env python3
"""
Direct CSV Import - Handle Customer Names Properly
Import CSV directly by mapping customer names to database IDs
"""

import csv
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession

def import_csv_direct(csv_file):
    """Import CSV by creating customers first, then sessions"""
    print(f"🚀 Direct CSV Import: {csv_file}")
    
    sessions_created = 0
    customers_created = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Get or create customer
                customer_name = row.get('Customer', '').strip()
                network_name = row.get('Network', '').strip()
                
                if not customer_name:
                    continue
                
                customer, created = Customer.objects.get_or_create(
                    name=customer_name,
                    network_name=network_name,
                    defaults={
                        'country': row.get('Country', ''),
                        'node_qty': int(row.get('Node Qty', 0) or 0),
                        'ne_type': row.get('NE Type', ''),
                        'gtac': row.get('gTAC', ''),
                        'setup_status': row.get('Setup Status', 'READY'),
                        'total_runs': int(row.get('Total Runs', 0) or 0),
                        'network_type': 'Excel Imported'
                    }
                )
                
                if created:
                    customers_created += 1
                    print(f"✅ Created customer: {customer.display_name}")
                
                # Create sessions for each month that has runs
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                for month in months:
                    runs_data = row.get(month, '').strip()
                    if runs_data and runs_data != '-':
                        try:
                            # Extract run count from "08-Jan" format
                            if '-' in runs_data:
                                run_count = int(runs_data.split('-')[0])
                                
                                # Create session
                                session = HealthCheckSession.objects.create(
                                    customer=customer,
                                    session_type='Monthly',
                                    run_count=run_count,
                                    status='COMPLETED',
                                    created_at=datetime.now(),
                                    notes=f"Imported from Excel - {month}"
                                )
                                sessions_created += 1
                        except:
                            pass  # Skip invalid data
                            
            except Exception as e:
                print(f"❌ Error processing row: {e}")
                continue
    
    print(f"🎉 Import completed!")
    print(f"👥 Customers created: {customers_created}")
    print(f"📊 Sessions created: {sessions_created}")

if __name__ == "__main__":
    import_csv_direct("Dashboard_Export_Enhanced.csv")