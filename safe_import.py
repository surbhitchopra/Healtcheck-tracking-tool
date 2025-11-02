# Cloud server pe save karo as: management/commands/safe_import.py

from django.core.management.base import BaseCommand
from HealthCheck_app.models import Customer

class Command(BaseCommand):
    help = 'Safe import customers only'

    def handle(self, *args, **options):
        customers_data = [
            {"name": "Tata", "network_name": "TTML", "country": "India", "node_qty": 27},
            {"name": "Tata", "network_name": "TTSL_BackBone", "country": "India", "node_qty": 40},
            {"name": "Timedotcom", "network_name": "Malaysia Network", "country": "Malaysia", "node_qty": 15},
            {"name": "airtel", "network_name": "India Network", "country": "India", "node_qty": 25},
        ]
        
        created_count = 0
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=data["name"],
                network_name=data["network_name"],
                defaults={
                    'country': data["country"],
                    'node_qty': data["node_qty"],
                    'ne_type': '1830 PSS',
                    'gtac': 'Classic',
                    'network_type': 'Excel Imported',
                    'setup_status': 'READY',
                    'total_runs': 0,
                    'monthly_runs': {}
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✅ Created: {customer.display_name}")
            else:
                self.stdout.write(f"⚠️  Exists: {customer.display_name}")
        
        self.stdout.write(f"🎉 Import complete! Created {created_count} customers")

# Usage: python manage.py safe_import