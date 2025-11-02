#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to the Python path
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now we can import Django models
from HealthCheck_app.models import Customer, HealthCheckSession

def check_actual_sessions():
    """Check for actual BSNL East DWDM sessions from recent days"""
    print("=== CHECKING ACTUAL BSNL EAST DWDM SESSIONS ===\n")
    
    try:
        # Find BSNL East Zone DWDM customer
        bsnl_east = Customer.objects.filter(
            name__icontains='bsnl',
            network_name__icontains='east'
        ).first()
        
        if bsnl_east:
            print(f"✅ Found: {bsnl_east.name} - {bsnl_east.network_name}")
            print(f"Customer ID: {bsnl_east.id}")
            
            # Check recent sessions (last 7 days)
            last_week = datetime.now() - timedelta(days=7)
            recent_sessions = HealthCheckSession.objects.filter(
                customer=bsnl_east,
                created_at__gte=last_week
            ).order_by('-created_at')
            
            print(f"\n📊 Recent Sessions (last 7 days): {recent_sessions.count()}")
            
            for i, session in enumerate(recent_sessions[:10]):  # Show up to 10 recent
                print(f"  {i+1}. {session.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {session.session_type}")
                print(f"     Status: {session.status}")
                if hasattr(session, 'tracker_file') and session.tracker_file:
                    print(f"     Tracker: {session.tracker_file}")
                if hasattr(session, 'report_file') and session.report_file:
                    print(f"     Report: {session.report_file}")
                print()
            
            # Check if there are October sessions specifically
            october_sessions = HealthCheckSession.objects.filter(
                customer=bsnl_east,
                created_at__year=2025,
                created_at__month=10
            ).order_by('-created_at')
            
            print(f"🎯 October 2025 Sessions: {october_sessions.count()}")
            for session in october_sessions:
                print(f"  📅 {session.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {session.session_type}")
                print(f"     Status: {session.status}")
                
        else:
            print("❌ BSNL East network not found")
            
        # Also check all BSNL networks for recent activity
        print("\n" + "="*60)
        print("🔍 CHECKING ALL BSNL NETWORKS FOR RECENT ACTIVITY:")
        
        all_bsnl = Customer.objects.filter(name__icontains='bsnl')
        for customer in all_bsnl:
            recent_count = HealthCheckSession.objects.filter(
                customer=customer,
                created_at__gte=last_week
            ).count()
            
            if recent_count > 0:
                latest_session = HealthCheckSession.objects.filter(
                    customer=customer
                ).order_by('-created_at').first()
                
                print(f"\n📋 {customer.network_name}: {recent_count} recent sessions")
                if latest_session:
                    print(f"   Latest: {latest_session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_all_session_data():
    """Check all session-related data"""
    print("\n" + "="*60)
    print("📊 CHECKING ALL SESSION DATA TABLES:")
    
    try:
        # Check all sessions in October
        october_sessions = HealthCheckSession.objects.filter(
            created_at__year=2025,
            created_at__month=10
        ).order_by('-created_at')
        
        print(f"\n🎯 ALL October 2025 Sessions: {october_sessions.count()}")
        
        for session in october_sessions:
            customer_name = session.customer.name if session.customer else "Unknown"
            network_name = session.customer.network_name if session.customer else "Unknown"
            print(f"  📅 {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Customer: {customer_name} - {network_name}")
            print(f"     Type: {session.session_type}")
            print(f"     Status: {session.status}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking sessions: {e}")
        return False

if __name__ == '__main__':
    check_actual_sessions()
    check_all_session_data()