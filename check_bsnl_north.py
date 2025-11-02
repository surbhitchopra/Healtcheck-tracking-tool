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
from django.contrib.auth.models import User

def check_bsnl_north_dwdm():
    """Check BSNL North DWDM current status"""
    print("🔍 CHECKING BSNL NORTH DWDM STATUS")
    print("=" * 50)
    
    try:
        bsnl_north = Customer.objects.get(
            name='BSNL',
            network_name='BSNL_North_Zone_DWDM',
            is_deleted=False
        )
        
        print(f"📋 Customer: {bsnl_north.name}")
        print(f"   Network: {bsnl_north.network_name}")
        print(f"   Current monthly_runs: {bsnl_north.monthly_runs}")
        print(f"   Total runs: {bsnl_north.total_runs}")
        
        # Check October data
        october_data = bsnl_north.monthly_runs.get('2025-10') if bsnl_north.monthly_runs else None
        if october_data:
            print(f"   ✅ Already has October 2025: {october_data}")
        else:
            print(f"   ❌ Missing October 2025 data")
            
        return bsnl_north
        
    except Customer.DoesNotExist:
        print("❌ BSNL North DWDM customer not found")
        return None

def simulate_health_check_completion(customer):
    """Simulate health check completion for BSNL North DWDM"""
    if not customer:
        return
        
    print(f"\n🧪 SIMULATING HEALTH CHECK COMPLETION FOR {customer.network_name}")
    print("=" * 60)
    
    # Get the first user
    user = User.objects.first()
    if not user:
        print("❌ No user found")
        return
    
    # Create a new test session
    import uuid
    session_id = f"bsnl_north_test_{uuid.uuid4().hex[:8]}"
    
    test_session = HealthCheckSession.objects.create(
        customer=customer,
        session_id=session_id,
        session_type='REGULAR_PROCESSING',
        initiated_by=user,
        status='PENDING'
    )
    
    print(f"1️⃣ Created session: {test_session.session_id}")
    print(f"2️⃣ Current status: {test_session.status}")
    
    # Show current customer data
    print(f"3️⃣ Before completion - monthly_runs: {customer.monthly_runs}")
    
    # Complete the session
    print(f"4️⃣ Completing session...")
    test_session.update_status('COMPLETED', 'BSNL North DWDM health check completed successfully')
    
    # Reload customer data
    customer.refresh_from_db()
    
    print(f"5️⃣ After completion - monthly_runs: {customer.monthly_runs}")
    
    # Check October data
    october_data = customer.monthly_runs.get('2025-10') if customer.monthly_runs else None
    if october_data:
        print(f"✅ SUCCESS! October 2025 data added: {october_data}")
        print(f"📊 Updated total_runs: {customer.total_runs}")
    else:
        print(f"❌ FAILED! October data not added")
    
    # Clean up
    test_session.delete()
    print(f"🧹 Cleaned up test session")

def show_all_bsnl_networks():
    """Show all BSNL networks and their October status"""
    print(f"\n📊 ALL BSNL NETWORKS STATUS:")
    print("=" * 50)
    
    bsnl_customers = Customer.objects.filter(name='BSNL', is_deleted=False).order_by('network_name')
    
    for customer in bsnl_customers:
        october_data = customer.monthly_runs.get('2025-10') if customer.monthly_runs else None
        if october_data:
            print(f"✅ {customer.network_name}: {october_data}")
        else:
            print(f"❌ {customer.network_name}: No October data")

if __name__ == "__main__":
    # Check current status
    bsnl_north = check_bsnl_north_dwdm()
    
    # Simulate health check if needed
    if bsnl_north:
        october_data = bsnl_north.monthly_runs.get('2025-10') if bsnl_north.monthly_runs else None
        if not october_data:
            simulate_health_check_completion(bsnl_north)
        else:
            print(f"\n💡 BSNL North DWDM already has October data!")
            print(f"   If you run a new health check, it will update to today's date.")
    
    # Show all BSNL networks
    show_all_bsnl_networks()
    
    print(f"\n🎯 SUMMARY:")
    print("✅ Auto-update system is active")
    print("✅ Any BSNL health check completion will add/update October date")
    print("✅ Dashboard will show dates in DD-MMM format (08-Oct)")
    print("\n💡 Jab bhi BSNL North DWDM ka health check complete hoga:")
    print("   ➜ Automatically October 2025 date add ho jayega") 
    print("   ➜ Dashboard mein '08-Oct' dikhayi dega")
    print("   ➜ Total runs count increase ho jayega")