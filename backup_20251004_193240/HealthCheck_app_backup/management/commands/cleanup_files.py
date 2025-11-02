"""
Django management command for cleaning up customer files
Usage: python manage.py cleanup_files [options]
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from HealthCheck_app.models import Customer
from HealthCheck_app.file_utils import (
    cleanup_old_files,
    find_duplicate_files,
    verify_file_integrity,
    cleanup_empty_directories,
    generate_file_management_report
)
from HealthCheck_app.views import SCRIPT_DIR


class Command(BaseCommand):
    help = 'Clean up customer files and directories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customer-id',
            type=int,
            help='Clean files for specific customer ID'
        )
        
        parser.add_argument(
            '--customer-name',
            type=str,
            help='Clean files for specific customer name'
        )
        
        parser.add_argument(
            '--days-old',
            type=int,
            default=30,
            help='Delete files older than this many days (default: 30)'
        )
        
        parser.add_argument(
            '--file-type',
            type=str,
            choices=['TEC_REPORT', 'INVENTORY_CSV', 'HOST', 'HC_TRACKER', 'TRACKER_GENERATED'],
            help='Only clean files of specific type'
        )
        
        parser.add_argument(
            '--find-duplicates',
            action='store_true',
            help='Find and report duplicate files'
        )
        
        parser.add_argument(
            '--verify-integrity',
            action='store_true',
            help='Verify file integrity (check if database records match physical files)'
        )
        
        parser.add_argument(
            '--cleanup-empty-dirs',
            action='store_true',
            help='Remove empty directories'
        )
        
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate comprehensive file management report'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting file cleanup operations...')
        )

        # Determine which customers to process
        customers = []
        if options['customer_id']:
            try:
                customer = Customer.objects.get(id=options['customer_id'], is_deleted=False)
                customers = [customer]
            except Customer.DoesNotExist:
                raise CommandError(f'Customer with ID {options["customer_id"]} not found')
        
        elif options['customer_name']:
            customers = Customer.objects.filter(
                name__icontains=options['customer_name'], 
                is_deleted=False
            )
            if not customers.exists():
                raise CommandError(f'No customers found matching "{options["customer_name"]}"')
        
        else:
            customers = Customer.objects.filter(is_deleted=False)

        self.stdout.write(f'📊 Processing {customers.count()} customer(s)...')

        # Generate report if requested
        if options['generate_report']:
            self.stdout.write('📋 Generating file management report...')
            report = generate_file_management_report()
            
            self.stdout.write(f'📈 Report Summary:')
            self.stdout.write(f'  • Total Customers: {report["summary"]["total_customers"]}')
            self.stdout.write(f'  • Total Files: {report["summary"]["total_files"]}')
            self.stdout.write(f'  • Total Size: {report["summary"]["total_size_mb"]} MB')
            self.stdout.write(f'  • Active Directories: {report["summary"]["total_directories"]}')
            
            # Save report to file
            report_file = SCRIPT_DIR / f"file_management_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.stdout.write(f'💾 Report saved to: {report_file}')

        # Process each customer
        for customer in customers:
            self.stdout.write(f'\n🏢 Processing customer: {customer.name}')
            
            if customer.network_name:
                self.stdout.write(f'📡 Network: {customer.network_name}')

            # Find duplicates if requested
            if options['find_duplicates']:
                self.stdout.write('🔍 Finding duplicate files...')
                duplicates = find_duplicate_files(customer, options.get('file_type'))
                
                if duplicates:
                    self.stdout.write(f'⚠️  Found {len(duplicates)} sets of duplicate files:')
                    for file_hash, file_list in duplicates.items():
                        self.stdout.write(f'  Hash: {file_hash[:12]}...')
                        for file_obj in file_list:
                            self.stdout.write(f'    - {file_obj.stored_filename} (ID: {file_obj.id})')
                else:
                    self.stdout.write('✅ No duplicate files found')

            # Verify integrity if requested
            if options['verify_integrity']:
                self.stdout.write('🔧 Verifying file integrity...')
                integrity = verify_file_integrity(customer)
                
                if integrity['missing_count'] > 0:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Found {integrity["missing_count"]} missing files:')
                    )
                    for missing in integrity['missing_files']:
                        self.stdout.write(f'  - {missing["filename"]} (Type: {missing["type"]})')
                else:
                    self.stdout.write('✅ All files are present and accounted for')

            # Clean up old files if not just finding duplicates or verifying
            if not (options['find_duplicates'] or options['verify_integrity'] or options['generate_report']):
                if options['dry_run']:
                    self.stdout.write('🧪 DRY RUN - Would clean up old files...')
                else:
                    self.stdout.write(f'🧹 Cleaning up files older than {options["days_old"]} days...')
                    cleaned_files = cleanup_old_files(
                        customer, 
                        options.get('file_type'), 
                        options['days_old']
                    )
                    
                    if cleaned_files:
                        self.stdout.write(f'🗑️  Cleaned up {len(cleaned_files)} files:')
                        for filename in cleaned_files:
                            self.stdout.write(f'  - {filename}')
                    else:
                        self.stdout.write('✅ No old files to clean up')

        # Clean up empty directories if requested
        if options['cleanup_empty_dirs']:
            self.stdout.write('\n🗂️  Cleaning up empty directories...')
            customer_files_dir = SCRIPT_DIR / "customer_files"
            
            if options['dry_run']:
                self.stdout.write('🧪 DRY RUN - Would clean up empty directories...')
            else:
                removed_dirs = cleanup_empty_directories(customer_files_dir)
                
                if removed_dirs:
                    self.stdout.write(f'🗑️  Removed {len(removed_dirs)} empty directories:')
                    for dir_path in removed_dirs:
                        self.stdout.write(f'  - {dir_path}')
                else:
                    self.stdout.write('✅ No empty directories found')

        self.stdout.write(
            self.style.SUCCESS('\n🎉 File cleanup operations completed!')
        )
