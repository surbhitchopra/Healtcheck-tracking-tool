from django.core.management.base import BaseCommand
from django.utils import timezone
import re
from Temperature_app.models import UploadLog

class Command(BaseCommand):
    help = 'Fix old tracker timestamps and extract temperatures from filenames permanently'

    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive old tracker fix...')
        
        # Get all old tracker records
        old_trackers = UploadLog.objects.filter(upload_type='OLD_TRACKER', is_deleted=False)
        updated_count = 0
        
        for old_tracker in old_trackers:
            updated = False
            
            # Always update timestamp to current time for UI consistency
            old_tracker.timestamp = timezone.now()
            updated = True
            
            # Extract temperature if not set
            if not old_tracker.threshold and old_tracker.generated_file:
                temp_patterns = [
                    r'(\d+)C',          # e.g., "35C"
                    r'(\d+)°C',         # e.g., "35°C" 
                    r'temp(\d+)',       # e.g., "temp35"
                    r'threshold(\d+)',  # e.g., "threshold35"
                    r'_(\d+)_',         # e.g., "_35_"
                    r'(\d{2})(?=\D|$)'  # Two digits at end or before non-digit
                ]
                
                for pattern in temp_patterns:
                    temp_match = re.search(pattern, old_tracker.generated_file, re.IGNORECASE)
                    if temp_match:
                        try:
                            temp_value = int(temp_match.group(1))
                            # Validate temperature is reasonable (20-50°C)
                            if 20 <= temp_value <= 50:
                                old_tracker.threshold = temp_value
                                self.stdout.write(f'Extracted temperature {temp_value}°C for tracker {old_tracker.id} from filename {old_tracker.generated_file}')
                                break
                        except (ValueError, IndexError):
                            continue
            
            if updated:
                old_tracker.save()
                updated_count += 1
                self.stdout.write(f'Updated tracker {old_tracker.id}: {old_tracker.filename}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} old tracker records with current timestamps and extracted temperatures')
        )
