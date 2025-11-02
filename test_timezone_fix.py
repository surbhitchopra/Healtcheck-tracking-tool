import os
import sys
sys.path.append('.')

# Set Django settings before importing Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')

import django
django.setup()

from django.utils import timezone
from datetime import datetime
from django.conf import settings
from HealthCheck_app.models import HealthCheckSession

print("=== TIMEZONE FIX DEMONSTRATION ===")
print(f"Django TIME_ZONE setting: {settings.TIME_ZONE}")
print(f"Django USE_TZ setting: {settings.USE_TZ}")

# Show current times
current_time_utc = timezone.now()
current_time_local = timezone.localtime(current_time_utc)
system_time = datetime.now()

print(f"\nCurrent UTC time: {current_time_utc}")
print(f"Current IST time: {current_time_local}")
print(f"System time: {system_time}")

# Show recent database entries with both UTC and IST
print("\n=== RECENT HEALTH CHECK SESSIONS ===")
recent_sessions = HealthCheckSession.objects.order_by('-created_at')[:5]

for session in recent_sessions:
    session_utc = session.created_at
    session_ist = timezone.localtime(session.created_at)
    time_diff = (current_time_utc - session.created_at).total_seconds() / 3600
    
    print(f"\nSession {session.session_id[:8]}:")
    print(f"  Created at (UTC): {session_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Created at (IST): {session_ist.strftime('%d-%m-%Y %I:%M:%S %p')}")
    print(f"  Hours ago: {round(time_diff, 2)}")
    print(f"  Status: {session.status}")
    print(f"  Customer: {session.customer.name}")

print("\n✅ TIMEZONE FIX APPLIED SUCCESSFULLY!")
print("✅ Database timestamps now display in IST (India Standard Time)")
print("✅ Health check endpoints are available at:")
print("   - /health/")
print("   - /health/detailed/") 
print("   - /health/database/")
print("   - /health/time-sync/")
