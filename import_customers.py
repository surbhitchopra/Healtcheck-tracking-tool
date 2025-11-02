# Save this as: HealthCheck_app/management/commands/import_customers.py on CLOUD

from django.core.management.base import BaseCommand
from HealthCheck_app.models import Customer
import csv

class Command(BaseCommand):
    help = 'Import customers from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            created_count = 0
            
            for row in reader:
                customer, created = Customer.objects.get_or_create(
                    name=row['Customer'],
                    network_name=row.get('Network', ''),
                    defaults={
                        'country': row.get('Country', 'Unknown'),
                        'node_qty': int(row.get('Node Qty', 1)),
                        'ne_type': row.get('NE Type', 'Unknown'),
                        'gtac': row.get('gTAC', 'Unknown'),
                        'setup_status': 'READY',
                        'total_runs': int(row.get('Total Runs', 0)),
                        'network_type': 'Excel Imported'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"✅ Created: {customer.display_name}")
                else:
                    self.stdout.write(f"⚠️  Exists: {customer.display_name}")
            
            self.stdout.write(f"🎉 Import complete! Created {created_count} customers")

# Usage on cloud:
# python manage.py import_customers /path/to/your.csv