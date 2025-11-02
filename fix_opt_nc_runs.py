#!/usr/bin/env python3
"""
Fix OPT_NC total runs counter specifically
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession

def fix_opt_nc():
    """Fix OPT_NC total runs counter"""
    
    print("🔧 FIXING OPT_NC TOTAL RUNS...")
    print("=" * 50)
    
    # Get OPT_NC customer
    opt_nc = Customer.objects.get(name='OPT_NC', network_name='OPT_NC')
    
    # Count actual completed sessions
    completed_sessions = HealthCheckSession.objects.filter(
        customer=opt_nc,
        status='COMPLETED'
    )
    
    actual_count = completed_sessions.count()
    current_total = opt_nc.total_runs
    
    print(f"📊 OPT_NC Current Status:")
    print(f"   Database total_runs: {current_total}")
    print(f"   Actual completed sessions: {actual_count}")
    
    if current_total != actual_count:
        print(f"   ❌ MISMATCH! Fixing {current_total} → {actual_count}")
        
        # Update total_runs
        opt_nc.total_runs = actual_count
        opt_nc.save()
        
        print(f"   ✅ FIXED! OPT_NC total_runs updated to {actual_count}")
    else:
        print(f"   ✅ Already correct: {actual_count} runs")
    
    # Show recent sessions
    print(f"\n📋 Recent Completed Sessions:")
    recent_sessions = completed_sessions.order_by('-completed_at')[:5]
    for i, session in enumerate(recent_sessions, 1):
        completed_time = session.completed_at.strftime('%Y-%m-%d %H:%M')
        print(f"   {i}. {completed_time} - {session.status}")
    
    return actual_count

def fix_all_customers():
    """Fix total_runs for all customers"""
    
    print("\n🔧 CHECKING ALL CUSTOMERS...")
    print("=" * 60)
    
    customers = Customer.objects.filter(is_deleted=False)
    fixed_count = 0
    
    for customer in customers:
        # Count actual completed sessions
        actual_sessions = HealthCheckSession.objects.filter(
            customer=customer,
            status='COMPLETED'
        ).count()
        
        if customer.total_runs != actual_sessions:
            old_value = customer.total_runs
            customer.total_runs = actual_sessions
            customer.save()
            fixed_count += 1
            
            print(f"🔧 {customer.name} - {customer.network_name}: {old_value} → {actual_sessions}")
        else:
            if actual_sessions > 0:  # Only show active customers
                print(f"✅ {customer.name} - {customer.network_name}: {actual_sessions}")
    
    print("=" * 60)
    print(f"✅ Fixed {fixed_count} customers with incorrect total_runs")
    
    return fixed_count

if __name__ == "__main__":
    # Fix OPT_NC specifically
    opt_nc_count = fix_opt_nc()
    
    # Fix all customers
    fixed_count = fix_all_customers()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   OPT_NC now shows: {opt_nc_count} runs")
    print(f"   Total customers fixed: {fixed_count}")
    print(f"   Dashboard should now show correct values!")
    
    print(f"\n📊 Next time you run OPT_NC health check:")
    print(f"   It will increment from {opt_nc_count} → {opt_nc_count + 1}")
    print(f"   Both database AND dashboard will update correctly!")