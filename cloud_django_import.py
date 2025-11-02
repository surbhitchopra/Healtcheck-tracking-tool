#!/usr/bin/env python3
"""
Cloud Django Import - Direct Django ORM import
Create customers directly in Django admin or shell
"""

print("=== CLOUD DJANGO IMPORT SCRIPT ===")
print()
print("Copy this code and run in Django shell on CLOUD:")
print("python manage.py shell")
print()
print("=" * 50)

# Django import code for cloud
django_code = '''
# Run this in Django shell on CLOUD
from HealthCheck_app.models import Customer
import json

# Customer data from Excel
customers_data = [
    {"name": "Tata", "network_name": "TTML", "country": "India", "node_qty": 27, "ne_type": "1678MCC", "gtac": "Classic"},
    {"name": "Tata", "network_name": "TTSL_BackBone", "country": "India", "node_qty": 40, "ne_type": "1678MCC", "gtac": "Classic"},
    {"name": "Tata", "network_name": "TTSL North", "country": "India", "node_qty": 17, "ne_type": "1678MCC", "gtac": "Classic"},
    {"name": "airtel", "network_name": "Unknown Network", "country": "Unknown", "node_qty": 1, "ne_type": "Unknown", "gtac": "Unknown"},
    {"name": "Timedotcom", "network_name": "Unknown Network", "country": "Unknown", "node_qty": 1, "ne_type": "Unknown", "gtac": "Unknown"},
    {"name": "Barti", "network_name": "Unknown Network", "country": "Unknown", "node_qty": 1, "ne_type": "Unknown", "gtac": "Unknown"}
]

print("🚀 Creating customers...")
created_count = 0

for data in customers_data:
    try:
        customer, created = Customer.objects.get_or_create(
            name=data["name"],
            network_name=data["network_name"],
            defaults={
                'country': data["country"],
                'node_qty': data["node_qty"],
                'ne_type': data["ne_type"],
                'gtac': data["gtac"],
                'network_type': 'Excel Imported',
                'setup_status': 'READY',
                'total_runs': 0,
                'monthly_runs': {}
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: {customer.display_name}")
        else:
            print(f"⚠️  Already exists: {customer.display_name}")
            
    except Exception as e:
        print(f"❌ Error creating {data['name']}: {e}")

print(f"🎉 Successfully created {created_count} customers!")
print("🔍 Checking customers in database:")

for customer in Customer.objects.all():
    print(f"  - {customer.display_name} (ID: {customer.id})")
'''

print(django_code)
print("=" * 50)
print()
print("ALTERNATIVE: Use Django Admin Import")
print("1. Go to Django Admin on cloud")
print("2. Go to Customer Networks section")
print("3. Click 'Add Customer Network' button")
print("4. Add each customer manually")
print()
print("OR create a management command to import CSV directly")