#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthCheck_prj.settings')
django.setup()

from HealthCheck_app.models import Network, HealthCheckSession

print("🔍 Checking BSNL network sessions...")

# Find BSNL networks
networks = Network.objects.filter(name__icontains='BSNL')
print(f"Found {networks.count()} BSNL networks")

for net in networks:
    print(f"\n📊 Network: {net.network_name or net.name} (ID: {net.id})")
    
    # Count sessions
    sessions = HealthCheckSession.objects.filter(customer=net)
    print(f"   Total sessions: {sessions.count()}")
    
    # Check October sessions
    october_sessions = sessions.filter(created_at__month=10, created_at__year=2025)
    print(f"   October 2025 sessions: {october_sessions.count()}")
    
    # Show latest sessions
    latest = sessions.order_by('-created_at')[:3]
    for s in latest:
        print(f"   Latest: {s.created_at} - Status: {s.status}")
    
    print(f"   monthly_runs: {net.monthly_runs}")

print("\n✅ Done!")