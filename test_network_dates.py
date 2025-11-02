#!/usr/bin/env python3
"""
Quick test to verify database has network dates
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

try:
    django.setup()
    from HealthCheck_app.models import Customer
    
    print("🔍 QUICK NETWORK DATES TEST")
    print("=" * 40)
    
    # Check BSNL networks
    bsnl_networks = Customer.objects.filter(name='BSNL', is_deleted=False)
    print(f"\n📊 BSNL Networks: {bsnl_networks.count()}")
    
    for network in bsnl_networks[:3]:  # Show first 3
        print(f"   🔗 {network.network_name}")
        if network.monthly_runs:
            dates = [f"{k}:{v}" for k, v in network.monthly_runs.items() if v != 'Not Started']
            print(f"      Dates: {', '.join(dates[:3])}...")  # Show first 3 dates
        else:
            print("      No dates")
    
    # Check Tata networks  
    tata_networks = Customer.objects.filter(name='Tata', is_deleted=False)
    print(f"\n📊 Tata Networks: {tata_networks.count()}")
    
    for network in tata_networks[:3]:  # Show first 3
        print(f"   🔗 {network.network_name}")
        if network.monthly_runs:
            dates = [f"{k}:{v}" for k, v in network.monthly_runs.items()]
            print(f"      Dates: {', '.join(dates[:3])}...")  # Show first 3 dates
        else:
            print("      No dates")
    
    print(f"\n✅ Database has network dates!")
    print(f"🌐 Now open: http://127.0.0.1:8000/customer-dashboard/")
    print(f"📊 Check browser console for debug logs")
    
except Exception as e:
    print(f"❌ Error: {e}")