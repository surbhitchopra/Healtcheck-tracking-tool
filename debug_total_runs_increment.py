#!/usr/bin/env python3
"""
Debug Total Runs Increment Issue
Tests exactly what happens when a health check session is completed.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
sys.path.append('.')

try:
    django.setup()
    from HealthCheck_app.models import Customer, HealthCheckSession
    from django.contrib.auth.models import User
    from django.utils import timezone
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    exit(1)

def debug_total_runs_increment():
    """Debug why total_runs is not incrementing properly"""
    
    print("🔍 DEBUGGING TOTAL RUNS INCREMENT ISSUE")
    print("=" * 60)
    
    # Test with a real customer (use BSNL or OPT_NC)
    test_customers = ['BSNL East Zone DWDM', 'OPT_NC', 'BSNL', 'OPT-NC']
    
    customer = None
    for customer_name in test_customers:
        try:
            customer = Customer.objects.filter(name__icontains=customer_name.split()[0]).first()
            if customer:
                print(f"✅ Found customer: {customer.name}")
                break
        except:
            continue
    
    if not customer:
        print("❌ No test customer found. Creating a dummy customer...")
        customer = Customer.objects.create(
            name="TEST_DEBUG_CUSTOMER",
            network_name="DEBUG",
            network_type="TEST"
        )
        print(f"✅ Created test customer: {customer.name}")
    
    # Get current state
    initial_total_runs = customer.total_runs
    initial_completed_sessions = HealthCheckSession.objects.filter(
        customer=customer,
        status='COMPLETED'
    ).count()
    
    print(f"\n📊 INITIAL STATE:")
    print(f"   Customer: {customer.name}")
    print(f"   Current total_runs: {initial_total_runs}")
    print(f"   Actual completed sessions: {initial_completed_sessions}")
    print(f"   Match: {'✅ YES' if initial_total_runs == initial_completed_sessions else '❌ NO'}")
    
    # Create a test user if needed
    test_user, created = User.objects.get_or_create(
        username='test_debug_user',
        defaults={'email': 'test@debug.com'}
    )
    
    # Create a new health check session
    print(f"\n🚀 CREATING NEW HEALTH CHECK SESSION...")
    session_id = f"DEBUG_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    session = HealthCheckSession.objects.create(
        customer=customer,
        session_id=session_id,
        session_type='REGULAR_PROCESSING',
        initiated_by=test_user,
        files_expected=1,
        files_received=1
    )
    
    print(f"✅ Created session: {session.session_id}")
    
    # Check state before completion
    before_completion_runs = customer.total_runs
    before_completion_sessions = HealthCheckSession.objects.filter(
        customer=customer,
        status='COMPLETED'
    ).count()
    
    print(f"\n📊 BEFORE COMPLETION:")
    print(f"   total_runs: {before_completion_runs}")
    print(f"   completed sessions: {before_completion_sessions}")
    
    # Now mark session as COMPLETED - this should trigger total_runs increment
    print(f"\n⚡ MARKING SESSION AS COMPLETED...")
    session.update_status('COMPLETED', 'Debug test completion')
    
    # Refresh customer from database
    customer.refresh_from_db()
    
    # Check state after completion
    after_completion_runs = customer.total_runs
    after_completion_sessions = HealthCheckSession.objects.filter(
        customer=customer,
        status='COMPLETED'
    ).count()
    
    print(f"\n📊 AFTER COMPLETION:")
    print(f"   total_runs: {after_completion_runs}")
    print(f"   completed sessions: {after_completion_sessions}")
    
    # Analyze results
    print(f"\n🔍 ANALYSIS:")
    runs_incremented = after_completion_runs > before_completion_runs
    sessions_incremented = after_completion_sessions > before_completion_sessions
    
    print(f"   total_runs incremented: {'✅ YES' if runs_incremented else '❌ NO'}")
    print(f"   sessions count incremented: {'✅ YES' if sessions_incremented else '❌ NO'}")
    print(f"   Values match: {'✅ YES' if after_completion_runs == after_completion_sessions else '❌ NO'}")
    
    if not runs_incremented:
        print(f"\n🚨 PROBLEM DETECTED:")
        print(f"   total_runs did not increment!")
        print(f"   Expected: {before_completion_runs + 1}")
        print(f"   Got: {after_completion_runs}")
        
        # Check what _update_customer_monthly_runs method did
        print(f"\n🔍 CHECKING MODEL METHOD...")
        try:
            # Manually call the method to see what happens
            session._update_customer_monthly_runs()
            customer.refresh_from_db()
            manual_update_runs = customer.total_runs
            print(f"   After manual _update_customer_monthly_runs: {manual_update_runs}")
        except Exception as e:
            print(f"   Error in _update_customer_monthly_runs: {e}")
    
    # Check monthly_runs update
    print(f"\n📅 MONTHLY RUNS CHECK:")
    print(f"   monthly_runs: {customer.monthly_runs}")
    
    current_month = timezone.now().strftime('%Y-%m')
    if current_month in customer.monthly_runs:
        print(f"   ✅ Current month ({current_month}) updated")
    else:
        print(f"   ❌ Current month ({current_month}) NOT updated")
    
    # Clean up test session
    session.delete()
    print(f"\n🧹 Cleaned up test session: {session_id}")
    
    return runs_incremented and sessions_incremented

def check_all_customers_consistency():
    """Check consistency for all customers"""
    
    print(f"\n\n🔍 CHECKING ALL CUSTOMERS CONSISTENCY")
    print("=" * 60)
    
    customers = Customer.objects.filter(is_deleted=False)
    inconsistent_customers = []
    
    for customer in customers:
        actual_sessions = HealthCheckSession.objects.filter(
            customer=customer,
            status='COMPLETED'
        ).count()
        
        if customer.total_runs != actual_sessions:
            inconsistent_customers.append({
                'name': customer.name,
                'total_runs': customer.total_runs,
                'actual_sessions': actual_sessions,
                'difference': actual_sessions - customer.total_runs
            })
    
    if inconsistent_customers:
        print(f"🚨 FOUND {len(inconsistent_customers)} INCONSISTENT CUSTOMERS:")
        for customer_data in inconsistent_customers:
            print(f"   {customer_data['name']}")
            print(f"     total_runs: {customer_data['total_runs']}")
            print(f"     actual sessions: {customer_data['actual_sessions']}")
            print(f"     difference: {customer_data['difference']:+d}")
            print()
    else:
        print("✅ All customers have consistent total_runs values")
    
    return inconsistent_customers

if __name__ == "__main__":
    # Test increment functionality
    increment_works = debug_total_runs_increment()
    
    # Check overall consistency
    inconsistent = check_all_customers_consistency()
    
    print(f"\n🎯 FINAL DIAGNOSIS:")
    print("=" * 60)
    
    if increment_works:
        print("✅ total_runs increment mechanism is WORKING")
    else:
        print("❌ total_runs increment mechanism is BROKEN")
        print("   The update_status method or _update_customer_monthly_runs has issues")
    
    if inconsistent:
        print(f"⚠️  {len(inconsistent)} customers have inconsistent total_runs values")
        print("   Run the fix script to correct these inconsistencies")
    else:
        print("✅ All customers have consistent total_runs values")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if not increment_works:
        print("1. Check the _update_customer_monthly_runs method in models.py")
        print("2. Check if there's a race condition in the save process")
        print("3. Check database transaction isolation")
    
    if inconsistent:
        print("4. Run COMPLETE_TOTAL_RUNS_FIX.py to fix inconsistent values")
        print("5. Enable the permanent frontend fix to override stale data")