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
    # Get all sessions from today, ordered by most recent
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Get sessions from the last 2 hours
    two_hours_ago = timezone.now() - timedelta(hours=2)
    recent_sessions = HealthCheckSession.objects.filter(
        created_at__gte=two_hours_ago
    ).order_by('-created_at')
    
    print(f"Sessions from the last 2 hours:")
    print("-" * 80)
    
    for session in recent_sessions:
        print(f"Session ID: {session.id}")
        print(f"Customer: {session.customer.name}")
        print(f"Status: {session.status}")
        print(f"Progress: {session.progress_percentage}%")
        print(f"Current Step: {session.current_step}")
        print(f"Status Message: {session.status_message}")
        print(f"Created At: {session.created_at}")
        print("-" * 40)
    
    # Check specifically for any PROCESSING sessions
    processing_sessions = HealthCheckSession.objects.filter(status='PROCESSING')
    if processing_sessions.exists():
        print(f"\nSTILL PROCESSING Sessions:")
        for session in processing_sessions:
            print(f"  Session {session.id}: {session.customer.name} - Created: {session.created_at}")
    else:
        print("\n✅ No sessions are stuck in PROCESSING status")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
