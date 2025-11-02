#!/usr/bin/env python3
"""
FIX TOTAL RUNS COUNTER ISSUE
This script fixes the total_runs field by recalculating based on actual completed sessions.
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

def fix_total_runs_counter():
    """
    Fix the total_runs counter by recalculating based on actual completed sessions
    """
    print("🔧 FIXING TOTAL RUNS COUNTER...")
    print("=" * 60)
    
    # Get all active customers
    customers = Customer.objects.filter(is_deleted=False)
    fixed_count = 0
    
    for customer in customers:
        # Count actual completed sessions for this customer
        actual_sessions_count = HealthCheckSession.objects.filter(
            customer=customer,
            status='COMPLETED'
        ).count()
        
        # Get current total_runs from database
        current_total_runs = customer.total_runs or 0
        
        # If there's a discrepancy, fix it
        if actual_sessions_count != current_total_runs:
            print(f"🔍 {customer.display_name}:")
            print(f"   Current total_runs: {current_total_runs}")
            print(f"   Actual sessions: {actual_sessions_count}")
            print(f"   ➤ Updating to {actual_sessions_count}")
            
            # Update the total_runs field
            customer.total_runs = actual_sessions_count
            customer.save()
            fixed_count += 1
            
            # Also update monthly_runs with latest session dates
            update_monthly_runs_from_sessions(customer)
        else:
            print(f"✅ {customer.display_name}: {current_total_runs} (correct)")
    
    print("=" * 60)
    print(f"🎯 Fixed {fixed_count} customers with incorrect total_runs")
    return fixed_count

def update_monthly_runs_from_sessions(customer):
    """
    Update monthly_runs based on actual completed sessions
    """
    # Get all completed sessions for this customer
    sessions = HealthCheckSession.objects.filter(
        customer=customer,
        status='COMPLETED'
    ).order_by('completed_at')
    
    if not sessions.exists():
        return
    
    # Initialize monthly_runs if needed
    if not customer.monthly_runs:
        customer.monthly_runs = {}
    
    # Group sessions by month and use the latest date for each month
    monthly_sessions = {}
    for session in sessions:
        completion_date = session.completed_at or session.created_at
        month_key = completion_date.strftime('%Y-%m')  # e.g., '2025-10'
        date_value = completion_date.strftime('%Y-%m-%d')  # e.g., '2025-10-14'
        
        # Keep the latest date for each month
        if month_key not in monthly_sessions or date_value > monthly_sessions[month_key]:
            monthly_sessions[month_key] = date_value
    
    # Update customer's monthly_runs with session data
    for month_key, date_value in monthly_sessions.items():
        customer.monthly_runs[month_key] = date_value
        print(f"   📅 {month_key}: {date_value}")
    
    customer.save()

def check_bsnl_east_dwdm_specifically():
    """
    Check BSNL East Zone DWDM specifically to understand the issue
    """
    print("\n🔍 CHECKING BSNL EAST ZONE DWDM SPECIFICALLY:")
    print("=" * 60)
    
    bsnl_east = Customer.objects.filter(
        name='BSNL',
        network_name='BSNL_East_Zone_DWDM',
        is_deleted=False
    ).first()
    
    if not bsnl_east:
        print("❌ BSNL East Zone DWDM not found!")
        return
    
    # Get all sessions for this customer
    sessions = HealthCheckSession.objects.filter(customer=bsnl_east).order_by('-created_at')
    completed_sessions = sessions.filter(status='COMPLETED')
    
    print(f"📊 Customer: {bsnl_east.display_name}")
    print(f"   Current total_runs: {bsnl_east.total_runs}")
    print(f"   Total sessions: {sessions.count()}")
    print(f"   Completed sessions: {completed_sessions.count()}")
    print(f"   Monthly runs data: {bsnl_east.monthly_runs}")
    
    print(f"\n📋 Recent Sessions:")
    for i, session in enumerate(sessions[:10], 1):
        status_icon = "✅" if session.status == 'COMPLETED' else "⏳"
        date_str = (session.completed_at or session.created_at).strftime('%Y-%m-%d %H:%M')
        print(f"   {i}. {status_icon} {date_str} - {session.status} ({session.session_type})")
    
    # Calculate what the total should be
    should_be = completed_sessions.count()
    print(f"\n🎯 SHOULD BE: {should_be} total runs")
    print(f"   CURRENT: {bsnl_east.total_runs} total runs")
    
    if should_be != bsnl_east.total_runs:
        print(f"   ❌ DISCREPANCY: {should_be - bsnl_east.total_runs} missing runs")
        return True  # Needs fixing
    else:
        print(f"   ✅ CORRECT")
        return False  # Already correct

if __name__ == "__main__":
    # Check BSNL East specifically first
    needs_fixing = check_bsnl_east_dwdm_specifically()
    
    if needs_fixing:
        print(f"\n🔧 APPLYING FIX...")
        fixed_count = fix_total_runs_counter()
        print(f"\n✅ FIXED {fixed_count} customers!")
        
        # Check BSNL East again to verify fix
        print(f"\n🔍 VERIFICATION:")
        check_bsnl_east_dwdm_specifically()
    else:
        print(f"\n✅ No fixes needed - all counts are correct!")