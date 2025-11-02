from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from pathlib import Path
import shutil
import os

from Temperature_app.models import Customer, UploadLog

class Command(BaseCommand):
    help = 'Fix database issues with host files and old trackers'

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        TRACKER_DIR = BASE_DIR / "generated_trackers"
        OLD_TRACKER_DIR = TRACKER_DIR / "old_tracker"
        UPLOAD_DIR = BASE_DIR / "uploaded_files"
        SCRIPT_DIR = BASE_DIR / "Script"
        
        self.stdout.write(self.style.SUCCESS('Starting database fix...'))
        
        # Fix 1: Check for OLD_TRACKER records with missing generated_file
        self.stdout.write('Checking OLD_TRACKER records...')
        old_tracker_records = UploadLog.objects.filter(
            upload_type='OLD_TRACKER',
            is_deleted=False
        )
        
        fixed_count = 0
        for record in old_tracker_records:
            if not record.generated_file:
                # Try to find the file in old_tracker directory
                customer_files = list(OLD_TRACKER_DIR.glob(f"*{record.customer.name}*"))
                if customer_files:
                    # Use the most recent file
                    latest_file = max(customer_files, key=os.path.getmtime)
                    record.generated_file = latest_file.name
                    record.save()
                    self.stdout.write(f'Fixed OLD_TRACKER record {record.id}: {latest_file.name}')
                    fixed_count += 1
        
        # Fix 2: Create database records for orphaned files in old_tracker directory
        self.stdout.write('Checking for orphaned files in old_tracker directory...')
        orphaned_files = list(OLD_TRACKER_DIR.glob("*.xlsx"))
        
        for file_path in orphaned_files:
            # Check if this file has a database record
            existing_record = UploadLog.objects.filter(
                upload_type='OLD_TRACKER',
                generated_file=file_path.name
            ).first()
            
            if not existing_record:
                # Try to find the customer based on filename
                for customer in Customer.objects.filter(is_deleted=False):
                    customer_name_clean = ''.join(c for c in customer.name.lower() if c.isalnum())
                    file_name_clean = ''.join(c for c in file_path.name.lower() if c.isalnum())
                    
                    if customer_name_clean in file_name_clean:
                        # Create database record
                        file_stats = file_path.stat()
                        file_time = datetime.fromtimestamp(file_stats.st_mtime)
                        
                        base_filename = file_path.name.split('_202')[0] + '.xlsx' if '_202' in file_path.name else file_path.name
                        
                        new_record = UploadLog.objects.create(
                            filename=base_filename,
                            upload_type='OLD_TRACKER',
                            status='Success',
                            customer=customer,
                            generated_file=file_path.name,
                            timestamp=timezone.make_aware(file_time)
                        )
                        
                        self.stdout.write(f'Created record for orphaned file: {file_path.name}')
                        fixed_count += 1
                        break
        
        # Fix 3: Ensure host files are NOT in Script directory (they should stay in uploaded_files)
        self.stdout.write('Cleaning up host files from Script directory...')
        host_records = UploadLog.objects.filter(
            upload_type='HOST',
            is_deleted=False
        )
        
        for host_record in host_records:
            script_path = SCRIPT_DIR / host_record.filename
            
            # Remove host files from Script directory if they exist there
            if script_path.exists():
                try:
                    script_path.unlink()
                    self.stdout.write(f'Removed host file from Script directory: {host_record.filename}')
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(f'Failed to remove {host_record.filename}: {e}')
        
        # Fix 4: Check for tracker files that exist but don't have proper database records
        self.stdout.write('Checking for tracker files in Script directory...')
        tracker_files = list(SCRIPT_DIR.glob("*.xlsx"))
        
        for tracker_file in tracker_files:
            # Remove host files from Script directory if they exist there
            if 'host' in tracker_file.name.lower():
                try:
                    tracker_file.unlink()
                    self.stdout.write(f'Removed host file from Script directory: {tracker_file.name}')
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(f'Failed to remove host file {tracker_file.name}: {e}')
                continue
                
            # Check if this tracker has a proper database record
            existing_record = UploadLog.objects.filter(
                generated_file=tracker_file.name,
                is_deleted=False
            ).first()
            
            if not existing_record:
                # Try to find the customer based on filename
                for customer in Customer.objects.filter(is_deleted=False):
                    customer_name_clean = ''.join(c for c in customer.name.lower() if c.isalnum())
                    file_name_clean = ''.join(c for c in tracker_file.name.lower() if c.isalnum())
                    
                    if customer_name_clean in file_name_clean:
                        # Create database record
                        file_stats = tracker_file.stat()
                        file_time = datetime.fromtimestamp(file_stats.st_mtime)
                        
                        new_record = UploadLog.objects.create(
                            filename=f"Generated_{tracker_file.name}",
                            upload_type='HOST',
                            status='Success',
                            customer=customer,
                            generated_file=tracker_file.name,
                            timestamp=timezone.make_aware(file_time)
                        )
                        
                        self.stdout.write(f'Created record for tracker file: {tracker_file.name}')
                        fixed_count += 1
                        break
        
        self.stdout.write(self.style.SUCCESS(f'Database fix completed. Fixed {fixed_count} issues.'))
