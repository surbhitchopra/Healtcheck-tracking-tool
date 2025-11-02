#!/usr/bin/env python3

import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

print('📦 Creating backup before deletion...')

# Create backup
backup_data = []
excel_customers = ['OPT_NC', 'Tata', 'Moratel', 'LTV', 'Maxix', 'Worldlink', 'Timedotcom', 'Telekom_Malaysia', 'KEPCO', 'SKB_LH', 'KT_B2B_KINX', 'LGU_HANA_BANK', 'NongHyup-DCI', 'Kakao', 'Moratelindo', 'BSNL', 'Railtel']

for customer_name in excel_customers:
    customers = Customer.objects.filter(name=customer_name)
    for customer in customers:
        backup_data.append({
            'id': customer.id,
            'name': customer.name,
            'network_name': customer.network_name,
            'country': customer.country,
            'node_qty': customer.node_qty,
            'ne_type': customer.ne_type,
            'gtac': customer.gtac,
            'setup_status': customer.setup_status,
            'total_runs': customer.total_runs,
            'monthly_runs': customer.monthly_runs,
            'created_at': customer.created_at.isoformat() if customer.created_at else None
        })

# Save backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_filename = f'excel_customers_backup_{timestamp}.json'
with open(backup_filename, 'w') as f:
    json.dump(backup_data, f, indent=2, default=str)

print(f'✅ Backup saved: {backup_filename} ({len(backup_data)} records)')

# Now delete
deleted_total = 0
for customer_name in excel_customers:
    count = Customer.objects.filter(name=customer_name).count()
    if count > 0:
        Customer.objects.filter(name=customer_name).delete()
        print(f'🗑️ Deleted {count} records for: {customer_name}')
        deleted_total += count

remaining = Customer.objects.filter(is_deleted=False).count()
print(f'\n📊 SUMMARY:')
print(f'   🗑️ Deleted: {deleted_total} Excel customers')
print(f'   ✅ Remaining: {remaining} pure DB customers')
print(f'   📦 Backup file: {backup_filename}')
print('\n🎯 Dashboard will now show ONLY pure database customers!')
print('🔄 To restore if needed, use the backup file')