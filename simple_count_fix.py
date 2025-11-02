#!/usr/bin/env python3
"""
SIMPLE COUNT FIX - Just make total runs count display correctly
No Excel data changes, just fix the counts
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession

def just_fix_counts():
    """Just fix the total_runs count - no Excel changes"""
    
    print("🔧 SIMPLE COUNT FIX - Only fixing total_runs display")
    print("=" * 60)
    
    # Get active customers with sessions
    customers = Customer.objects.filter(is_deleted=False)
    fixed_count = 0
    
    print("📊 Checking customers with actual sessions:")
    for customer in customers:
        # Count ONLY completed sessions
        actual_sessions = HealthCheckSession.objects.filter(
            customer=customer,
            status='COMPLETED'
        ).count()
        
        # Get current total_runs
        current_runs = customer.total_runs or 0
        
        # Only show customers with actual sessions
        if actual_sessions > 0:
            if current_runs != actual_sessions:
                print(f"🔧 {customer.name} - {customer.network_name}: {current_runs} → {actual_sessions}")
                customer.total_runs = actual_sessions
                customer.save()
                fixed_count += 1
            else:
                print(f"✅ {customer.name} - {customer.network_name}: {actual_sessions} (correct)")
    
    print(f"\n✅ Fixed {fixed_count} customers")
    
    # Show key customers status
    print(f"\n📋 KEY CUSTOMERS STATUS:")
    key_customers = [
        ('OPT_NC', 'OPT_NC'),
        ('BSNL', 'BSNL_East_Zone_DWDM'),
        ('BSNL', 'BSNL_North_Zone_DWDM'),
        ('BSNL', 'BSNL_West_Zone_DWDM'),
        ('Moratelindo', 'Moratelindo_PSS24')
    ]
    
    for name, network in key_customers:
        try:
            customer = Customer.objects.get(name=name, network_name=network)
            sessions = HealthCheckSession.objects.filter(customer=customer, status='COMPLETED').count()
            print(f"   {name}: {customer.total_runs} runs (from {sessions} sessions)")
        except Customer.DoesNotExist:
            pass
    
    return fixed_count

if __name__ == "__main__":
    fixed = just_fix_counts()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Fixed {fixed} customers")
    print(f"   Excel data: UNCHANGED")
    print(f"   Only total_runs count fixed")
    
    print(f"\n🚀 NEXT: Browser console fix for frontend display")
    print(f"   Dashboard will show correct counts")
    print(f"   When you run health checks, counts will increase")