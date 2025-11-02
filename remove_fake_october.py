#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(r'C:\Users\surchopr\Hc_Final')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now import Django models
from HealthCheck_app.models import Customer

def remove_fake_october_data():
    """Remove fake October data from customers that shouldn't have it"""
    print("🧹 REMOVING FAKE OCTOBER DATA")
    print("=" * 50)
    
    # Get Tata customer
    try:
        tata_customer = Customer.objects.get(
            name='Tata', 
            network_name='TTML',
            is_deleted=False
        )
        
        print(f"📋 Customer: {tata_customer.name}")
        print(f"   Network: {tata_customer.network_name}")
        print(f"   Current monthly_runs: {tata_customer.monthly_runs}")
        
        # Remove October 2025 data if it exists
        if tata_customer.monthly_runs and '2025-10' in tata_customer.monthly_runs:
            # Remove October data
            del tata_customer.monthly_runs['2025-10']
            
            # Recalculate total_runs
            total_runs = sum(1 for v in tata_customer.monthly_runs.values() 
                           if v and str(v).strip() not in ['-', '', 'None', 'null', 'Not Started', 'Not Run', 'No Report'])
            tata_customer.total_runs = total_runs
            
            # Save the customer
            tata_customer.save()
            
            print(f"   ✅ Removed fake October 2025 data")
            print(f"   📅 Updated monthly_runs: {tata_customer.monthly_runs}")
            print(f"   📊 Updated total_runs: {tata_customer.total_runs}")
        else:
            print(f"   ℹ️ No October 2025 data found")
            
    except Customer.DoesNotExist:
        print("❓ Tata customer not found")

def check_all_customers_october():
    """Check which customers actually have October data and why"""
    print(f"\n📊 CHECKING ALL CUSTOMERS WITH OCTOBER DATA:")
    print("=" * 60)
    
    customers_with_october = Customer.objects.filter(
        monthly_runs__has_key='2025-10',
        is_deleted=False
    ).order_by('name')
    
    print(f"Customers with October 2025 data:")
    
    for customer in customers_with_october:
        october_date = customer.monthly_runs.get('2025-10')
        print(f"📋 {customer.name} - {customer.network_name}: {october_date}")
        
        # Check if this customer had actual sessions today
        from HealthCheck_app.models import HealthCheckSession
        from datetime import datetime
        
        today = datetime.now().date()
        today_sessions = HealthCheckSession.objects.filter(
            customer=customer,
            status='COMPLETED',
            created_at__date=today
        ).count()
        
        if today_sessions > 0:
            print(f"   ✅ Valid - Has {today_sessions} completed session(s) today")
        else:
            print(f"   ⚠️ Suspicious - No completed sessions today")

if __name__ == "__main__":
    remove_fake_october_data()
    check_all_customers_october()
    
    print(f"\n🎯 CLEANED UP!")
    print("✅ Removed fake October data from customers that didn't run health checks")
    print("✅ Only customers with actual completed sessions should have October data")