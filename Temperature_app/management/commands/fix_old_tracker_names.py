from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from pathlib import Path
import os

from Temperature_app.models import Customer, UploadLog

class Command(BaseCommand):
    help = 'Fix old tracker filenames to show full names'

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        OLD_TRACKER_DIR = BASE_DIR / "generated_trackers" / "old_tracker"
        
        self.stdout.write(self.style.SUCCESS('Fixing old tracker filenames...'))
        
        # Get all OLD_TRACKER records
        old_tracker_records = UploadLog.objects.filter(
            upload_type='OLD_TRACKER',
            is_deleted=False
        )
        
        fixed_count = 0
        
        for record in old_tracker_records:
            if record.generated_file:
                # Extract the base filename from the generated file (removing timestamp)
                if '_202' in record.generated_file:
                    base_name = record.generated_file.split('_202')[0]
                    full_filename = f"{base_name}.xlsx"
                    
                    if record.filename != full_filename:
                        old_filename = record.filename
                        record.filename = full_filename
                        record.save()
                        
                        self.stdout.write(f'Fixed record {record.id}: "{old_filename}" -> "{full_filename}"')
                        fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} old tracker filenames.'))
