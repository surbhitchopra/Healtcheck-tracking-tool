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
    # Get the latest session
    latest_session = HealthCheckSession.objects.latest('created_at')
    print(f"Latest Session ID: {latest_session.id}")
    print(f"Customer: {latest_session.customer.name}")
    print(f"Status: {latest_session.status}")
    print(f"Progress: {latest_session.progress_percentage}%")
    print(f"Current Step: {latest_session.current_step}")
    print(f"Status Message: {latest_session.status_message}")
    print(f"Created At: {latest_session.created_at}")
    print(f"Completed At: {latest_session.completed_at}")
    
    # Check if there are any PROCESSING sessions
    processing_sessions = HealthCheckSession.objects.filter(status='PROCESSING')
    if processing_sessions.exists():
        print(f"\nFound {processing_sessions.count()} PROCESSING sessions:")
        for session in processing_sessions:
            print(f"  Session {session.id}: {session.customer.name} - {session.current_step}")
            
            # Check if this session should be marked as completed
            script_output_dir = Path("Script/output")
            if script_output_dir.exists():
                output_files = list(script_output_dir.glob("*"))
                output_count = len([f for f in output_files if f.is_file()])
                print(f"    Output files found: {output_count}")
                
                if output_count >= 7:  # Expected minimum output files
                    print(f"    Session {session.id} appears to be completed but not updated!")
                    # Update the session
                    session.update_status('COMPLETED', f'Health check analysis completed successfully! Generated {output_count} output files.')
                    session.progress_percentage = 100
                    session.current_step = "Completed"
                    session.save()
                    print(f"    ✅ Updated session {session.id} to COMPLETED")
    else:
        print("\nNo PROCESSING sessions found.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
