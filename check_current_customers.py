#!/usr/bin/env python3

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

print('🔍 CURRENT DATABASE CUSTOMERS:')
customers = Customer.objects.filter(is_deleted=False).order_by('name')
print(f'Total: {customers.count()} customers')

customer_groups = {}
for customer in customers:
    if customer.name not in customer_groups:
        customer_groups[customer.name] = []
    customer_groups[customer.name].append(customer)

for name, networks in customer_groups.items():
    print(f'\n🏢 {name}: {len(networks)} networks')
    for net in networks:
        network_name = net.network_name or 'Default'
        print(f'  - {network_name} (ID: {net.id})')

print(f'\n📊 SUMMARY:')
print(f'   Unique customers: {len(customer_groups)}')
print(f'   Total networks: {customers.count()}')

# Check specifically for BSNL networks
bsnl_customers = customers.filter(name__icontains='BSNL')
print(f'\n📍 BSNL NETWORKS: {bsnl_customers.count()}')
for bsnl in bsnl_customers:
    print(f'  - {bsnl.name}: {bsnl.network_name or "Default"}')