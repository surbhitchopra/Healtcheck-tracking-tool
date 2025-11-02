#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime

# Add the project directory to the Python path
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now we can import Django models
from HealthCheck_app.models import Customer, HealthCheckSession

def update_monthly_runs_from_sessions():
    """Update monthly_runs data based on actual session data"""
    print("=== UPDATING MONTHLY RUNS FROM ACTUAL SESSIONS ===\n")
    
    try:
        # Find all BSNL customers
        bsnl_customers = Customer.objects.filter(name__icontains='bsnl')
        
        for customer in bsnl_customers:
            print(f"📋 Processing: {customer.network_name}")
            
            # Get all sessions for this customer
            sessions = HealthCheckSession.objects.filter(
                customer=customer,
                status='COMPLETED'
            ).order_by('created_at')
            
            if sessions.exists():
                print(f"   Found {sessions.count()} completed sessions")
                
                # Initialize monthly_runs if it doesn't exist
                if not customer.monthly_runs:
                    customer.monthly_runs = {}
                
                # Group sessions by month
                monthly_sessions = {}
                for session in sessions:
                    session_date = session.created_at
                    month_key = session_date.strftime('%Y-%m')
                    
                    if month_key not in monthly_sessions:
                        monthly_sessions[month_key] = []
                    monthly_sessions[month_key].append(session_date)
                
                # Update monthly_runs with actual session dates
                for month_key, session_dates in monthly_sessions.items():
                    # Use the latest session date for that month
                    latest_date = max(session_dates)
                    formatted_date = latest_date.strftime('%Y-%m-%d')
                    
                    customer.monthly_runs[month_key] = formatted_date
                    print(f"   ✅ {month_key}: {formatted_date}")
                
                # Update total runs
                customer.total_runs = sessions.count()
                
                # Save changes
                customer.save()
                print(f"   💾 Saved with {customer.total_runs} total runs\n")
            else:
                print(f"   ⚪ No completed sessions found\n")
        
        print("✅ All BSNL customers updated with actual session data!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_updates():
    """Verify the updates were successful"""
    print("\n" + "="*60)
    print("🔍 VERIFYING UPDATES:")
    
    try:
        bsnl_customers = Customer.objects.filter(name__icontains='bsnl')
        
        for customer in bsnl_customers:
            print(f"\n📋 {customer.network_name}")
            print(f"   Monthly runs: {customer.monthly_runs}")
            print(f"   Total runs: {customer.total_runs}")
            
            # Check for October data specifically
            if customer.monthly_runs and isinstance(customer.monthly_runs, dict):
                october_keys = [key for key in customer.monthly_runs.keys() if '2025-10' in key]
                if october_keys:
                    for key in october_keys:
                        print(f"   🎯 {key}: {customer.monthly_runs[key]} ✅")
                        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

if __name__ == '__main__':
    success1 = update_monthly_runs_from_sessions()
    success2 = verify_updates()
    
    if success1 and success2:
        print("\n🎉 UPDATE COMPLETE!")
        print("Now BSNL East DWDM October data should appear in dashboard!")
        print("Refresh your browser to see the updated data.")
    else:
        print("\n❌ Some updates failed")