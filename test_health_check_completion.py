#!/usr/bin/env python3
"""
Test Health Check Completion Logic
Check if total_runs increments when session completes
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession
from django.contrib.auth.models import User
from django.utils import timezone

def test_health_check_completion():
    """Test if health check completion increments total_runs"""
    
    print("🧪 TESTING HEALTH CHECK COMPLETION LOGIC:")
    print("=" * 60)
    
    # Get OPT_NC customer
    try:
        opt_nc = Customer.objects.get(name='OPT_NC', network_name='OPT_NC')
    except Customer.DoesNotExist:
        print("❌ OPT_NC customer not found!")
        return
    
    # Get current status
    current_runs = opt_nc.total_runs or 0
    current_sessions = HealthCheckSession.objects.filter(customer=opt_nc, status='COMPLETED').count()
    
    print(f"📊 CURRENT STATUS:")
    print(f"   Customer: {opt_nc.display_name}")
    print(f"   Database total_runs: {current_runs}")
    print(f"   Actual completed sessions: {current_sessions}")
    print(f"   Monthly runs: {opt_nc.monthly_runs}")
    
    # Get or create a user for the session
    try:
        user = User.objects.get(id=1)
    except User.DoesNotExist:
        user = User.objects.create_user('test_user', 'test@test.com', 'password')
    
    # Create a test session
    print(f"\n🚀 CREATING TEST SESSION...")
    test_session = HealthCheckSession.objects.create(
        customer=opt_nc,
        session_id=f'test_{timezone.now().strftime("%Y%m%d_%H%M%S")}',
        session_type='REGULAR_PROCESSING',
        initiated_by=user,
        status='PENDING'
    )
    
    print(f"✅ Test session created: {test_session.session_id}")
    
    # Complete the session using the update_status method
    print(f"🔄 COMPLETING SESSION...")
    test_session.update_status('COMPLETED', 'Test completion for total_runs increment')
    
    # Refresh customer data from database
    opt_nc.refresh_from_db()
    new_runs = opt_nc.total_runs or 0
    new_sessions = HealthCheckSession.objects.filter(customer=opt_nc, status='COMPLETED').count()
    
    print(f"\n📊 AFTER SESSION COMPLETION:")
    print(f"   Database total_runs: {new_runs}")
    print(f"   Actual completed sessions: {new_sessions}")
    print(f"   Monthly runs: {opt_nc.monthly_runs}")
    
    # Check if increment worked
    if new_runs == current_runs + 1:
        print(f"\n✅ SUCCESS!")
        print(f"   total_runs incremented: {current_runs} → {new_runs}")
        print(f"   Session completion trigger WORKING!")
    else:
        print(f"\n❌ FAILED!")
        print(f"   total_runs should be: {current_runs + 1}")
        print(f"   total_runs actually is: {new_runs}")
        print(f"   Session completion trigger NOT WORKING!")
    
    # Show what should happen in dashboard
    print(f"\n📱 DASHBOARD SHOULD SHOW:")
    print(f"   OPT_NC: {new_runs} runs (after refresh)")
    print(f"   Table total_runs column: {new_runs}")
    print(f"   Static cards: Updated")
    
    # Clean up test session
    print(f"\n🧹 CLEANING UP...")
    test_session.delete()
    print(f"Test session deleted")
    
    # Recalculate after cleanup (should be back to original)
    opt_nc.total_runs = HealthCheckSession.objects.filter(customer=opt_nc, status='COMPLETED').count()
    opt_nc.save()
    
    print(f"✅ Cleanup complete - total_runs back to {opt_nc.total_runs}")
    
    return new_runs > current_runs

if __name__ == "__main__":
    success = test_health_check_completion()
    
    print(f"\n🎯 CONCLUSION:")
    if success:
        print(f"   ✅ Health check completion logic WORKS")
        print(f"   ✅ total_runs increments properly")
        print(f"   🎯 Issue must be in frontend display")
    else:
        print(f"   ❌ Health check completion logic BROKEN")
        print(f"   ❌ total_runs not incrementing")
        print(f"   🔧 Need to fix session completion trigger")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. If backend works: Fix frontend display")
    print(f"   2. If backend broken: Fix session completion")
    print(f"   3. Test with actual health check run")