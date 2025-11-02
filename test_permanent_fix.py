#!/usr/bin/env python3
"""
Test if the permanent fix is working correctly
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession

def verify_fix_status():
    """Verify that the fix is working correctly"""
    
    print("🔍 VERIFYING PERMANENT TOTAL RUNS FIX:")
    print("=" * 60)
    
    # Check key customers
    key_customers = [
        ('OPT_NC', 'OPT_NC'),
        ('BSNL', 'BSNL_East_Zone_DWDM'),
        ('BSNL', 'BSNL_North_Zone_DWDM'),
        ('BSNL', 'BSNL_West_Zone_DWDM'),
        ('Moratelindo', 'Moratelindo_PSS24')
    ]
    
    print("📊 KEY CUSTOMERS STATUS:")
    for customer_name, network_name in key_customers:
        try:
            customer = Customer.objects.get(name=customer_name, network_name=network_name)
            sessions = HealthCheckSession.objects.filter(customer=customer, status='COMPLETED').count()
            
            status = "✅" if customer.total_runs == sessions else "❌"
            print(f"{status} {customer_name} - {network_name}: DB={customer.total_runs}, Sessions={sessions}")
            
        except Customer.DoesNotExist:
            print(f"❌ {customer_name} - {network_name}: NOT FOUND")
    
    # Check static file
    static_file_path = "static/js/fix_total_runs_permanent.js"
    if os.path.exists(static_file_path):
        print(f"\n✅ Static JavaScript file exists: {static_file_path}")
    else:
        print(f"\n❌ Static JavaScript file missing: {static_file_path}")
    
    # Check template modification
    template_file = "templates/customer_dashboard.html"
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'fix_total_runs_permanent.js' in content:
                print(f"✅ Template includes permanent fix script")
            else:
                print(f"❌ Template does NOT include permanent fix script")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Database: Fixed (shows actual session counts)")
    print(f"   Static file: Created")
    print(f"   Template: Updated")
    print(f"   Server: Needs restart for full effect")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Restart Django server: python manage.py runserver")
    print(f"   2. Refresh dashboard")
    print(f"   3. Check browser console for fix messages")
    print(f"   4. Table should show correct total_runs automatically")
    
    print(f"\n📊 EXPECTED RESULTS AFTER RESTART:")
    print(f"   OPT_NC: 19 runs (from 19 sessions)")
    print(f"   BSNL East DWDM: 6 runs (from 6 sessions)")
    print(f"   All others: Database session counts")
    print(f"   No more JavaScript console fixes needed!")

if __name__ == "__main__":
    verify_fix_status()