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
    # Fix Session 149 directly
    session = HealthCheckSession.objects.get(id=149)
    print(f"Found session: {session.id} - {session.customer.name}")
    print(f"Current status: {session.status}")
    print(f"Current step: {session.current_step}")
    print(f"Progress: {session.progress_percentage}%")
    
    # Check if output files exist
    script_output_dir = Path("Script/output")
    if script_output_dir.exists():
        output_files = list(script_output_dir.glob("*.xlsx"))
        print(f"Output files found: {len(output_files)}")
        for file in output_files:
            print(f"  - {file.name}")
        
        if len(output_files) >= 5:
            print(f"\n✅ Found {len(output_files)} output files - marking session as COMPLETED")
            
            # Update session to completed
            session.update_status('COMPLETED', f'Health check analysis completed successfully! Generated {len(output_files)} output files.')
            session.progress_percentage = 100
            session.current_step = "Completed"
            
            # Set output tracker file if found
            tracker_files = [f for f in output_files if 'OPEN' in f.name and 'cases' in f.name]
            if tracker_files:
                session.output_tracker_filename = tracker_files[0].name
                session.output_tracker_path = str(tracker_files[0])
                print(f"Set tracker file: {tracker_files[0].name}")
            
            session.save()
            print(f"✅ Session {session.id} has been marked as COMPLETED")
        else:
            print(f"❌ Only {len(output_files)} output files found, marking as FAILED")
            session.update_status('FAILED', 'Insufficient output files generated')
            session.save()
    else:
        print("❌ No output directory found, marking session as FAILED")
        session.update_status('FAILED', 'No output directory found')
        session.save()
    
except HealthCheckSession.DoesNotExist:
    print("Session 149 not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
