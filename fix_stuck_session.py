#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import HealthCheckSession

try:
    # Fix Session 147 that's stuck in PROCESSING
    stuck_session = HealthCheckSession.objects.get(id=147)
    print(f"Found stuck session: {stuck_session.id} - {stuck_session.customer.name}")
    print(f"Current status: {stuck_session.status}")
    print(f"Current step: {stuck_session.current_step}")
    
    # Mark it as FAILED since it's clearly stuck
    stuck_session.update_status('FAILED', 'Session timed out - processing was interrupted.')
    stuck_session.progress_percentage = 0
    stuck_session.current_step = "Failed"
    stuck_session.save()
    
    print(f"✅ Updated session {stuck_session.id} to FAILED")
    
    # Also clean up other old stuck sessions
    print(f"\nCleaning up other old stuck sessions...")
    old_processing_sessions = HealthCheckSession.objects.filter(
        status='PROCESSING',
        id__lt=147  # Sessions older than 147
    )
    
    for session in old_processing_sessions:
        session.update_status('FAILED', 'Session timed out - old processing session.')
        session.save()
        print(f"✅ Cleaned up stuck session {session.id}")
    
    print(f"\nAfter cleanup, latest session status:")
    latest = HealthCheckSession.objects.latest('created_at')
    print(f"Session {latest.id}: {latest.status} - {latest.progress_percentage}%")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
