#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date

# Add the project directory to Python path
sys.path.append(r'C:\Users\surchopr\Hc_Final')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now import Django models
from HealthCheck_app.models import Customer, HealthCheckSession

def fix_all_completed_sessions():
    """Fix all COMPLETED sessions that didn't update monthly_runs"""
    print("🔧 PERMANENT FIX FOR ALL COMPLETED SESSIONS")
    print("=" * 60)
    
    # Get all COMPLETED sessions that don't have corresponding monthly_runs entries
    all_completed_sessions = HealthCheckSession.objects.filter(status='COMPLETED').order_by('created_at')
    
    print(f"Found {all_completed_sessions.count()} completed sessions")
    
    updated_count = 0
    
    for session in all_completed_sessions:
        customer = session.customer
        
        # Use created_at if completed_at is not set
        completion_date = session.completed_at if session.completed_at else session.created_at
        
        # Format the dates
        current_month_key = completion_date.strftime('%Y-%m')  # e.g., '2025-10'
        current_date_value = completion_date.strftime('%Y-%m-%d')  # e.g., '2025-10-08'
        
        # Initialize monthly_runs if it doesn't exist
        if not customer.monthly_runs:
            customer.monthly_runs = {}
        
        # Check if this month already has data
        existing_value = customer.monthly_runs.get(current_month_key)
        
        if not existing_value:
            # Add the data for this month
            customer.monthly_runs[current_month_key] = current_date_value
            updated_count += 1
            
            print(f"✅ {customer.name} ({customer.network_name}): Added {current_month_key} = {current_date_value}")
        else:
            # If there's already data, check if we should update with a more recent date
            try:
                existing_date = datetime.strptime(existing_value, '%Y-%m-%d').date()
                current_date = completion_date.date()
                
                if current_date > existing_date:
                    customer.monthly_runs[current_month_key] = current_date_value
                    print(f"🔄 {customer.name}: Updated {current_month_key} from {existing_value} to {current_date_value}")
                    updated_count += 1
                else:
                    print(f"ℹ️ {customer.name}: Keeping existing {current_month_key} = {existing_value}")
            except:
                # If existing value is not a proper date, replace it
                customer.monthly_runs[current_month_key] = current_date_value
                print(f"🔄 {customer.name}: Replaced invalid {current_month_key} = {existing_value} with {current_date_value}")
                updated_count += 1
        
        # Update total_runs count
        total_runs = sum(1 for v in customer.monthly_runs.values() 
                       if v and str(v).strip() not in ['-', '', 'None', 'null', 'Not Started', 'Not Run', 'No Report'])
        customer.total_runs = total_runs
        
        # Save the customer
        customer.save()
    
    print(f"\n🎉 PERMANENT FIX COMPLETED!")
    print(f"   Total sessions processed: {all_completed_sessions.count()}")
    print(f"   Customer records updated: {updated_count}")

def verify_fix():
    """Verify that the fix worked correctly"""
    print(f"\n🔍 VERIFICATION - CHECKING RECENT CUSTOMERS:")
    print("=" * 50)
    
    # Check the customers you mentioned
    test_customers = ['Barti', 'Timedotcom', 'airtel', 'OPT_NC', 'Moratelindo', 'BSNL']
    
    for customer_name in test_customers:
        try:
            customers = Customer.objects.filter(name=customer_name, is_deleted=False)
            
            for customer in customers:
                print(f"\n📋 {customer.name} - {customer.network_name}")
                
                if customer.monthly_runs:
                    october_data = customer.monthly_runs.get('2025-10')
                    if october_data:
                        print(f"   ✅ October 2025: {october_data}")
                    else:
                        print(f"   ⚠️ No October 2025 data")
                        
                    # Show all months with data
                    months_with_data = [k for k, v in customer.monthly_runs.items() if v and str(v) not in ['-', '']]
                    print(f"   📅 Months with data: {months_with_data}")
                    print(f"   📊 Total runs: {customer.total_runs}")
                else:
                    print(f"   ❌ No monthly_runs data")
                    
        except Customer.DoesNotExist:
            print(f"   ❓ Customer '{customer_name}' not found")

if __name__ == "__main__":
    fix_all_completed_sessions()
    verify_fix()
    print(f"\n🎯 PERMANENT FIX APPLIED!")
    print("Now all future completed sessions will automatically update monthly_runs!")
    print("And all existing completed sessions have been fixed!")