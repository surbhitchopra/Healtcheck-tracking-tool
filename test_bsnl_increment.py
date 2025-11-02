#!/usr/bin/env python3
"""
Test BSNL East Zone DWDM total_runs increment
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
sys.path.append('.')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession
from django.contrib.auth.models import User
from datetime import datetime

def test_bsnl_increment():
    """Test BSNL East Zone DWDM total_runs increment"""
    
    # Get BSNL East Zone DWDM customer
    customer = Customer.objects.filter(name='BSNL', network_name='BSNL_East_Zone_DWDM').first()
    
    if not customer:
        print("❌ BSNL East Zone DWDM customer not found!")
        return
    
    print(f"🎯 Testing: {customer.name} - {customer.network_name}")
    
    # Current state
    before_total = customer.total_runs
    before_sessions = HealthCheckSession.objects.filter(customer=customer, status='COMPLETED').count()
    
    print(f"📊 BEFORE TEST:")
    print(f"   total_runs: {before_total}")
    print(f"   completed sessions: {before_sessions}")
    
    # Get or create test user
    test_user, _ = User.objects.get_or_create(
        username='test_user_bsnl',
        defaults={'email': 'test@bsnl.com'}
    )
    
    # Create new session
    session_id = f"TEST_BSNL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session = HealthCheckSession.objects.create(
        customer=customer,
        session_id=session_id,
        session_type='REGULAR_PROCESSING',
        initiated_by=test_user,
        files_expected=1,
        files_received=1
    )
    
    print(f"✅ Created session: {session.session_id}")
    
    # Mark as completed
    print("⚡ Completing session...")
    session.update_status('COMPLETED', 'Test completion')
    
    # Check results
    customer.refresh_from_db()
    after_total = customer.total_runs
    after_sessions = HealthCheckSession.objects.filter(customer=customer, status='COMPLETED').count()
    
    print(f"📊 AFTER TEST:")
    print(f"   total_runs: {after_total}")
    print(f"   completed sessions: {after_sessions}")
    
    # Results
    success = (after_total == before_total + 1) and (after_sessions == before_sessions + 1)
    
    if success:
        print("✅ SUCCESS: total_runs incremented correctly!")
    else:
        print("❌ FAILED: total_runs did not increment properly")
    
    # Clean up
    session.delete()
    print(f"🧹 Cleaned up session: {session_id}")
    
    return success

if __name__ == "__main__":
    test_bsnl_increment()