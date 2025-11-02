import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from HealthCheck_app.models import Customer, HealthCheckSession

class Command(BaseCommand):
    help = 'Monitor and maintain 1830PSS Health Check operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['status', 'cleanup', 'stats', 'failed'],
            default='status',
            help='Action: status, cleanup old files, stats, or show failed sessions'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days for cleanup or stats (default: 30)'
        )
        parser.add_argument(
            '--network',
            type=str,
            help='Filter by specific network'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without deleting'
        )

    def handle(self, *args, **options):
        action = options['action']
        days = options['days']
        network = options.get('network')
        dry_run = options.get('dry_run', False)

        try:
            if action == 'status':
                self.show_status()
            elif action == 'cleanup':
                self.cleanup_old_files(days, dry_run)
            elif action == 'stats':
                self.show_statistics(days, network)
            elif action == 'failed':
                self.show_failed_sessions(network)
        except Exception as e:
            raise CommandError(f'Error executing {action}: {str(e)}')

    def show_status(self):
        """Show overall system status"""
        self.stdout.write(self.style.SUCCESS('1830PSS Health Check System Status'))
        self.stdout.write('=' * 50)

        # Check Script directory and templates
        base_dir = Path(settings.BASE_DIR)
        script_dir = base_dir / "Script"
        
        if script_dir.exists():
            self.stdout.write(f"✓ Script directory: {script_dir}")
        else:
            self.stdout.write(f"✗ Script directory missing: {script_dir}")
            return

        # Check virtual environment
        venv_path = script_dir / "venv"
        if venv_path.exists():
            self.stdout.write("✓ Virtual environment ready")
        else:
            self.stdout.write("✗ Virtual environment missing")

        # Check database stats
        total_networks = Customer.objects.filter(is_deleted=False).count()
        ready_networks = Customer.objects.filter(
            is_deleted=False, 
            setup_status='READY'
        ).count()
        
        self.stdout.write(f"\nNetworks: {total_networks} total, {ready_networks} ready")

        # Check recent activity
        recent_sessions = HealthCheckSession.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        successful_sessions = HealthCheckSession.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7),
            status='COMPLETED'
        ).count()

        self.stdout.write(f"Recent activity (7 days): {recent_sessions} sessions, {successful_sessions} successful")

        # Check disk usage
        input_dir = script_dir / "input-hc-report"
        output_dir = script_dir / "output"
        
        if input_dir.exists():
            input_size = sum(f.stat().st_size for f in input_dir.rglob('*') if f.is_file())
            self.stdout.write(f"Input directory size: {input_size / (1024*1024):.1f} MB")

        if output_dir.exists():
            output_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
            self.stdout.write(f"Output directory size: {output_size / (1024*1024):.1f} MB")

    def cleanup_old_files(self, days, dry_run=False):
        """Clean up old session files"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"{'DRY RUN: ' if dry_run else ''}Cleaning files older than {days} days...")
        
        # Find old sessions
        old_sessions = HealthCheckSession.objects.filter(
            created_at__lt=cutoff_date
        )
        
        total_cleaned = 0
        total_size = 0
        
        base_dir = Path(settings.BASE_DIR)
        script_dir = base_dir / "Script"
        
        for session in old_sessions:
            session_files = []
            
            # Check for input files
            input_dir = script_dir / "input-hc-report"
            for file_path in input_dir.rglob(f"*{session.session_id}*"):
                if file_path.is_file():
                    session_files.append(file_path)
            
            # Check for output files
            output_dir = script_dir / "output"
            for file_path in output_dir.rglob(f"*{session.session_id}*"):
                if file_path.is_file():
                    session_files.append(file_path)
            
            # Clean up files
            for file_path in session_files:
                file_size = file_path.stat().st_size
                total_size += file_size
                
                self.stdout.write(f"  {'Would delete' if dry_run else 'Deleting'}: {file_path.name} ({file_size / (1024*1024):.1f} MB)")
                
                if not dry_run:
                    try:
                        file_path.unlink()
                        total_cleaned += 1
                    except OSError as e:
                        self.stdout.write(f"    Error deleting {file_path}: {e}")
            
            # Mark session as cleaned or delete if no associated files
            if not dry_run and not session_files:
                session.delete()
        
        self.stdout.write(f"\n{'Would clean' if dry_run else 'Cleaned'}: {total_cleaned} files, {total_size / (1024*1024):.1f} MB")

    def show_statistics(self, days, network_filter=None):
        """Show usage statistics"""
        start_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"Health Check Statistics (Last {days} days)")
        self.stdout.write('=' * 50)
        
        # Base queryset
        sessions = HealthCheckSession.objects.filter(created_at__gte=start_date)
        
        if network_filter:
            try:
                customer = Customer.objects.get(name=network_filter, is_deleted=False)
                sessions = sessions.filter(customer=customer)
                self.stdout.write(f"Network: {network_filter}")
            except Customer.DoesNotExist:
                self.stdout.write(f"Warning: Network '{network_filter}' not found")
                return
        
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='COMPLETED').count()
        failed_sessions = sessions.filter(status='FAILED').count()
        in_progress = sessions.filter(status='IN_PROGRESS').count()
        
        self.stdout.write(f"Total sessions: {total_sessions}")
        self.stdout.write(f"Completed: {completed_sessions} ({completed_sessions/total_sessions*100 if total_sessions > 0 else 0:.1f}%)")
        self.stdout.write(f"Failed: {failed_sessions} ({failed_sessions/total_sessions*100 if total_sessions > 0 else 0:.1f}%)")
        self.stdout.write(f"In progress: {in_progress}")
        
        # Network breakdown
        if not network_filter:
            self.stdout.write("\nBy Network:")
            network_stats = {}
            for session in sessions:
                network_name = session.customer.name if session.customer else 'Unknown'
                if network_name not in network_stats:
                    network_stats[network_name] = {'total': 0, 'completed': 0, 'failed': 0}
                
                network_stats[network_name]['total'] += 1
                if session.status == 'COMPLETED':
                    network_stats[network_name]['completed'] += 1
                elif session.status == 'FAILED':
                    network_stats[network_name]['failed'] += 1
            
            for network, stats in sorted(network_stats.items()):
                success_rate = stats['completed'] / stats['total'] * 100 if stats['total'] > 0 else 0
                self.stdout.write(f"  {network:<20} {stats['total']:>3} sessions ({success_rate:>5.1f}% success)")

        # Recent activity
        if completed_sessions > 0:
            recent_session = sessions.filter(status='COMPLETED').order_by('-updated_at').first()
            if recent_session:
                self.stdout.write(f"\nMost recent completion: {recent_session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    def show_failed_sessions(self, network_filter=None):
        """Show details of failed sessions"""
        self.stdout.write("Failed Health Check Sessions")
        self.stdout.write('=' * 40)
        
        failed_sessions = HealthCheckSession.objects.filter(status='FAILED').order_by('-updated_at')
        
        if network_filter:
            try:
                customer = Customer.objects.get(name=network_filter, is_deleted=False)
                failed_sessions = failed_sessions.filter(customer=customer)
            except Customer.DoesNotExist:
                self.stdout.write(f"Network '{network_filter}' not found")
                return
        
        if not failed_sessions.exists():
            self.stdout.write("No failed sessions found.")
            return
        
        for session in failed_sessions[:10]:  # Show last 10 failed sessions
            network_name = session.customer.name if session.customer else 'Unknown'
            self.stdout.write(f"\nSession: {session.session_id}")
            self.stdout.write(f"Network: {network_name}")
            self.stdout.write(f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            self.stdout.write(f"Updated: {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if hasattr(session, 'error_message') and session.error_message:
                self.stdout.write(f"Error: {session.error_message}")
            
            # Try to find log files for more details
            base_dir = Path(settings.BASE_DIR)
            log_pattern = f"*{session.session_id}*.log"
            
            for log_file in (base_dir / "Script" / "output").rglob(log_pattern):
                if log_file.is_file():
                    self.stdout.write(f"Log file: {log_file}")
                    
        if failed_sessions.count() > 10:
            self.stdout.write(f"\n... and {failed_sessions.count() - 10} more failed sessions")
