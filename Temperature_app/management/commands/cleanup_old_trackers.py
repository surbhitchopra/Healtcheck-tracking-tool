from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from pathlib import Path
import os

from Temperature_app.models import Customer, UploadLog

class Command(BaseCommand):
    help = 'Clean up duplicate old tracker records - keep only one tracker in tracker_generated per customer'

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        OLD_TRACKER_DIR = BASE_DIR / "generated_trackers" / "old_tracker"
        SCRIPT_DIR = BASE_DIR / "Script"
        
        self.stdout.write(self.style.SUCCESS('Cleaning up old tracker records...'))
        
        for customer in Customer.objects.filter(is_deleted=False):
            self.stdout.write(f'Processing customer: {customer.name}')
            
            # Get all non-deleted trackers for this customer (excluding OLD_TRACKER type)
            active_trackers = UploadLog.objects.filter(
                customer=customer,
                generated_file__isnull=False,
                is_deleted=False
            ).exclude(generated_file='').exclude(upload_type='OLD_TRACKER').order_by('-timestamp')
            
            if active_trackers.count() > 1:
                # Keep only the most recent tracker, move others to old_tracker
                most_recent = active_trackers.first()
                duplicates = active_trackers[1:]
                
                self.stdout.write(f'Found {len(duplicates)} duplicate trackers for {customer.name}')
                
                for duplicate in duplicates:
                    if duplicate.generated_file:
                        # Move the duplicate tracker file to old_tracker directory
                        try:
                            timestamp_suffix = datetime.now().strftime("_%Y%m%d_%H%M%S")
                            old_tracker_filename = duplicate.generated_file.replace('.xlsx', f'{timestamp_suffix}.xlsx')
                            old_path = OLD_TRACKER_DIR / old_tracker_filename
                            script_path = SCRIPT_DIR / duplicate.generated_file
                            
                            if script_path.exists():
                                # Move file from Script to old_tracker
                                os.rename(str(script_path), str(old_path))
                                self.stdout.write(f'Moved duplicate tracker {duplicate.generated_file} to old_tracker as {old_tracker_filename}')
                                
                                # Create old tracker record
                                UploadLog.objects.create(
                                    filename=duplicate.generated_file,
                                    upload_type='OLD_TRACKER',
                                    status='Success',
                                    customer=customer,
                                    threshold=duplicate.threshold,
                                    generated_file=old_tracker_filename
                                )
                                
                                # Soft delete the duplicate from tracker_generated
                                duplicate.soft_delete(reason="Moved to old_tracker during cleanup")
                                self.stdout.write(f'Soft deleted duplicate tracker record: {duplicate.id}')
                            else:
                                # If file doesn't exist, just soft delete the record
                                duplicate.soft_delete(reason="Duplicate tracker record cleanup")
                                self.stdout.write(f'Soft deleted duplicate tracker record (no file): {duplicate.id}')
                                
                        except Exception as e:
                            self.stdout.write(f'Error processing duplicate tracker {duplicate.id}: {e}')
            
            # Clean up duplicate OLD_TRACKER records that point to the same file
            old_tracker_records = UploadLog.objects.filter(
                customer=customer,
                upload_type='OLD_TRACKER',
                is_deleted=False
            ).order_by('-timestamp')
            
            seen_files = set()
            for old_record in old_tracker_records:
                if old_record.generated_file in seen_files:
                    # This is a duplicate OLD_TRACKER record
                    old_record.soft_delete(reason="Duplicate OLD_TRACKER record cleanup")
                    self.stdout.write(f'Soft deleted duplicate OLD_TRACKER record: {old_record.id}')
                else:
                    seen_files.add(old_record.generated_file)
        
        self.stdout.write(self.style.SUCCESS('Cleanup completed.'))
