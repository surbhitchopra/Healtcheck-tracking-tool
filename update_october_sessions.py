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
from HealthCheck_app.models import Customer, HealthCheckSession

def update_october_sessions():
    """Update monthly_runs for sessions completed in October 2025"""
    print("🔧 UPDATING OCTOBER 2025 SESSION DATA")
    print("=" * 60)
    
    # Find all COMPLETED sessions from October 2025
    october_sessions = HealthCheckSession.objects.filter(
        status='COMPLETED',
        completed_at__year=2025,
        completed_at__month=10
    ).order_by('-completed_at')
    
    print(f"Found {october_sessions.count()} completed sessions in October 2025:")
    
    updated_customers = set()
    
    for session in october_sessions:
        customer = session.customer
        completion_date = session.completed_at
        
        print(f"\n📋 Session: {session.session_id}")
        print(f"   Customer: {customer.name}")
        print(f"   Network: {customer.network_name}")
        print(f"   Completed: {completion_date}")
        
        # Format the dates
        current_month_key = completion_date.strftime('%Y-%m')  # '2025-10'
        current_date_value = completion_date.strftime('%Y-%m-%d')  # '2025-10-08'
        
        # Check if customer already has October data
        if customer.monthly_runs and '2025-10' in customer.monthly_runs:
            existing_date = customer.monthly_runs['2025-10']
            print(f"   ⚠️ October data already exists: {existing_date}")
        else:
            # Initialize monthly_runs if it doesn't exist
            if not customer.monthly_runs:
                customer.monthly_runs = {}
            
            # Update the current month with session completion date
            customer.monthly_runs[current_month_key] = current_date_value
            
            # Also update total_runs count
            total_runs = sum(1 for v in customer.monthly_runs.values() 
                           if v and str(v).strip() not in ['-', '', 'None', 'null', 'Not Started', 'Not Run', 'No Report'])
            customer.total_runs = total_runs
            
            # Save the customer
            customer.save()
            updated_customers.add(customer.name)
            
            print(f"   ✅ Updated: {current_month_key} = {current_date_value}")
    
    print(f"\n🎉 SUMMARY:")
    print(f"   Total sessions processed: {october_sessions.count()}")
    print(f"   Customers updated: {len(updated_customers)}")
    if updated_customers:
        print(f"   Updated customers: {', '.join(updated_customers)}")

def check_new_customers():
    """Check the new customers created today and see if they need October updates"""
    print(f"\n🆕 CHECKING NEW CUSTOMERS (CREATED TODAY):")
    print("=" * 50)
    
    today = datetime.now().date()
    new_customers = Customer.objects.filter(
        created_at__date=today,
        is_deleted=False
    ).order_by('-created_at')
    
    for customer in new_customers:
        print(f"\n📋 Customer: {customer.name} (ID: {customer.id})")
        print(f"   Network: {customer.network_name}")
        print(f"   Created: {customer.created_at}")
        
        # Check for sessions for this customer today
        today_sessions = HealthCheckSession.objects.filter(
            customer=customer,
            created_at__date=today
        ).order_by('-created_at')
        
        print(f"   Sessions today: {today_sessions.count()}")
        
        for session in today_sessions:
            print(f"      Session {session.session_id}: {session.status}")
            if session.status == 'COMPLETED' and session.completed_at:
                completion_date = session.completed_at
                current_month_key = completion_date.strftime('%Y-%m')
                current_date_value = completion_date.strftime('%Y-%m-%d')
                
                # Update if not already updated
                if not customer.monthly_runs or '2025-10' not in customer.monthly_runs:
                    if not customer.monthly_runs:
                        customer.monthly_runs = {}
                    
                    customer.monthly_runs[current_month_key] = current_date_value
                    customer.total_runs = 1
                    customer.save()
                    
                    print(f"      ✅ Updated monthly_runs: {current_month_key} = {current_date_value}")
                else:
                    print(f"      ℹ️ Already has October data: {customer.monthly_runs.get('2025-10')}")

if __name__ == "__main__":
    update_october_sessions()
    check_new_customers()