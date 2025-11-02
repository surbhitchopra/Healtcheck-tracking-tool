#!/usr/bin/env python
"""
Advanced Session Recovery Script
===============================

This script provides comprehensive session recovery and monitoring
capabilities to fix stuck sessions and prevent future issues.
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
from django.utils import timezone

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import HealthCheckSession

class SessionRecoveryManager:
    """Manages session recovery and monitoring"""
    
    def __init__(self):
        self.script_output_dir = Path("Script/output")
        self.session_timeout_minutes = 30  # Sessions older than 30 minutes in PROCESSING are considered stuck
        
    def check_output_files_exist(self):
        """Check if output files exist indicating successful processing"""
        if not self.script_output_dir.exists():
            return False, []
        
        output_files = list(self.script_output_dir.glob("*.xlsx"))
        return len(output_files) >= 5, [f.name for f in output_files]  # Expect at least 5 output files
    
    def detect_stuck_sessions(self):
        """Detect sessions that are stuck in PROCESSING state"""
        cutoff_time = timezone.now() - timedelta(minutes=self.session_timeout_minutes)
        
        stuck_sessions = HealthCheckSession.objects.filter(
            status='PROCESSING',
            created_at__lt=cutoff_time
        ).order_by('created_at')
        
        return stuck_sessions
    
    def analyze_session_status(self, session):
        """Analyze if a session should be completed or failed"""
        has_outputs, output_files = self.check_output_files_exist()
        
        analysis = {
            'session_id': session.id,
            'customer': session.customer.name,
            'created_at': session.created_at,
            'duration_minutes': (timezone.now() - session.created_at).total_seconds() / 60,
            'current_step': session.current_step,
            'progress': session.progress_percentage,
            'has_outputs': has_outputs,
            'output_files': output_files,
            'should_complete': False,
            'should_fail': False,
            'reason': ''
        }
        
        # Determine action based on analysis
        if has_outputs and len(output_files) >= 5:
            analysis['should_complete'] = True
            analysis['reason'] = f'Found {len(output_files)} output files - processing appears successful'
        elif analysis['duration_minutes'] > self.session_timeout_minutes:
            analysis['should_fail'] = True
            analysis['reason'] = f'Session timed out after {analysis["duration_minutes"]:.1f} minutes without generating outputs'
        else:
            analysis['reason'] = 'Still within timeout window, monitoring'
            
        return analysis
    
    def fix_session(self, session, action, reason):
        """Fix a session by updating its status"""
        try:
            if action == 'COMPLETE':
                session.update_status('COMPLETED', f'Auto-recovered: {reason}')
                session.progress_percentage = 100
                session.current_step = "Completed (Auto-recovered)"
                
                # Try to set output file info if available
                has_outputs, output_files = self.check_output_files_exist()
                if has_outputs and output_files:
                    # Find the main tracker file
                    tracker_files = [f for f in output_files if 'HC' in f and 'Tracker' in f]
                    if tracker_files:
                        session.output_tracker_filename = tracker_files[0]
                        session.output_tracker_path = str(self.script_output_dir / tracker_files[0])
                
                session.save()
                return True, f"Session {session.id} marked as COMPLETED"
                
            elif action == 'FAIL':
                session.update_status('FAILED', f'Auto-failed: {reason}')
                session.progress_percentage = 0
                session.current_step = "Failed (Timeout)"
                session.save()
                return True, f"Session {session.id} marked as FAILED"
                
        except Exception as e:
            return False, f"Error fixing session {session.id}: {str(e)}"
    
    def run_recovery(self, dry_run=False):
        """Run the complete session recovery process"""
        print("🔍 Starting Session Recovery Analysis...")
        print("=" * 60)
        
        # Get all stuck sessions
        stuck_sessions = self.detect_stuck_sessions()
        
        if not stuck_sessions.exists():
            print("✅ No stuck sessions found!")
            return
        
        print(f"📊 Found {stuck_sessions.count()} potentially stuck session(s)")
        print()
        
        results = []
        for session in stuck_sessions:
            analysis = self.analyze_session_status(session)
            results.append(analysis)
            
            print(f"📋 Session {analysis['session_id']} Analysis:")
            print(f"   Customer: {analysis['customer']}")
            print(f"   Duration: {analysis['duration_minutes']:.1f} minutes")
            print(f"   Current Step: {analysis['current_step']}")
            print(f"   Progress: {analysis['progress']}%")
            print(f"   Has Outputs: {analysis['has_outputs']} ({len(analysis['output_files'])} files)")
            print(f"   Reason: {analysis['reason']}")
            
            if not dry_run:
                if analysis['should_complete']:
                    success, message = self.fix_session(session, 'COMPLETE', analysis['reason'])
                    print(f"   Action: ✅ {message}")
                elif analysis['should_fail']:
                    success, message = self.fix_session(session, 'FAIL', analysis['reason'])
                    print(f"   Action: ❌ {message}")
                else:
                    print(f"   Action: ⏳ Monitoring (within timeout window)")
            else:
                if analysis['should_complete']:
                    print(f"   Suggested Action: ✅ Mark as COMPLETED")
                elif analysis['should_fail']:
                    print(f"   Suggested Action: ❌ Mark as FAILED")
                else:
                    print(f"   Suggested Action: ⏳ Continue monitoring")
            
            print("-" * 40)
        
        # Summary
        if not dry_run:
            completed_count = sum(1 for r in results if r['should_complete'])
            failed_count = sum(1 for r in results if r['should_fail'])
            print(f"\n📈 Recovery Summary:")
            print(f"   Sessions completed: {completed_count}")
            print(f"   Sessions failed: {failed_count}")
            print(f"   Sessions still monitoring: {len(results) - completed_count - failed_count}")
        
        return results
    
    def monitor_current_sessions(self):
        """Monitor all current sessions and their status"""
        print("📊 Current Session Status:")
        print("=" * 60)
        
        recent_sessions = HealthCheckSession.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=2)
        ).order_by('-created_at')
        
        if not recent_sessions.exists():
            print("No sessions in the last 2 hours")
            return
        
        for session in recent_sessions:
            duration = (timezone.now() - session.created_at).total_seconds() / 60
            status_icon = {
                'PENDING': '⏳',
                'UPLOADING': '📤',
                'PROCESSING': '⚡' if duration < 30 else '⚠️',
                'COMPLETED': '✅',
                'FAILED': '❌'
            }.get(session.status, '❓')
            
            print(f"{status_icon} Session {session.id}: {session.customer.name}")
            print(f"   Status: {session.status} ({duration:.1f}m)")
            print(f"   Step: {session.current_step}")
            print(f"   Progress: {session.progress_percentage}%")
            if session.status_message:
                print(f"   Message: {session.status_message}")
            print("-" * 30)


def main():
    """Main function to run session recovery"""
    recovery_manager = SessionRecoveryManager()
    
    # Show current status first
    recovery_manager.monitor_current_sessions()
    print()
    
    # Ask user what to do
    print("🔧 Session Recovery Options:")
    print("1. Run analysis only (dry run)")
    print("2. Fix stuck sessions automatically")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n🔍 Running dry run analysis...")
            recovery_manager.run_recovery(dry_run=True)
        elif choice == '2':
            print("\n🔧 Running automatic session recovery...")
            recovery_manager.run_recovery(dry_run=False)
            print("\n✅ Recovery process completed!")
        elif choice == '3':
            print("👋 Exiting...")
            return
        else:
            print("❌ Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
