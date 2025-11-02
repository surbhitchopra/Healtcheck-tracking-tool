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

# Now import Django models
from HealthCheck_app.models import Customer

def test_date_processing():
    """Test the new date processing logic"""
    print("🔧 TESTING NEW DATE PROCESSING LOGIC")
    print("=" * 50)
    
    # Get BSNL customers specifically since you mentioned them
    bsnl_customers = Customer.objects.filter(name__icontains='BSNL', is_deleted=False)
    
    print(f"Found {bsnl_customers.count()} BSNL customers")
    
    for customer in bsnl_customers[:3]:  # Test first 3 customers
        print(f"\n📋 Testing Customer: {customer.name}")
        print(f"   Network: {customer.network_name}")
        print(f"   Raw monthly_runs: {customer.monthly_runs}")
        
        # Apply the same logic as the fixed views.py
        months = ["-"] * 12
        total_runs_count = customer.total_runs or 0
        
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
                                        print(f"      ✅ {month_key} ({month_num}): {date_str} -> {months[month_num - 1]}")
                                    except ValueError:
                                        # If parsing fails, show the raw value
                                        months[month_num - 1] = date_str
                                        print(f"      📝 {month_key} ({month_num}): {date_str} (status)")
                            else:
                                months[month_num - 1] = '-'
                except (ValueError, IndexError) as e:
                    print(f"      ❌ Error processing {month_key}: {e}")
                    continue
        
        print(f"   📅 Final months array: {months}")
        print(f"   📊 Months with data: {sum(1 for m in months if m != '-')}")

if __name__ == "__main__":
    test_date_processing()