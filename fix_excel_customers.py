#!/usr/bin/env python3

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

print("🔧 FIXING EXCEL MIGRATED CUSTOMERS...")
print("=" * 50)

# Get all customers
all_customers = Customer.objects.filter(is_deleted=False)
print(f"📊 Total active customers: {all_customers.count()}")

# Check current status distribution
new_count = all_customers.filter(setup_status='NEW').count()
ready_count = all_customers.filter(setup_status='READY').count()
other_count = all_customers.exclude(setup_status__in=['NEW', 'READY']).count()

print(f"\n📈 Current Status Distribution:")
print(f"   NEW (5 files): {new_count}")
print(f"   READY (2 files): {ready_count}")
print(f"   Other: {other_count}")

print(f"\n🔍 BEFORE FIX - Sample customers:")
for customer in all_customers[:10]:
    print(f"  {customer.name}: '{customer.setup_status}'")

print(f"\n🚀 APPLYING FIX...")
print("   Setting ALL customers to 'NEW' status (requires 5 files)")
print("   This is correct because Excel migrated customers have no existing files")

# Update ALL customers to NEW status
updated_count = all_customers.update(setup_status='NEW')

print(f"✅ Updated {updated_count} customers to 'NEW' status")

# Verify the fix
customers_after = Customer.objects.filter(is_deleted=False)
new_count_after = customers_after.filter(setup_status='NEW').count()
ready_count_after = customers_after.filter(setup_status='READY').count()

print(f"\n📈 Status Distribution AFTER FIX:")
print(f"   NEW (5 files): {new_count_after}")
print(f"   READY (2 files): {ready_count_after}")

print(f"\n🔍 AFTER FIX - Sample customers:")
for customer in customers_after[:10]:
    customer.refresh_from_db()
    print(f"  {customer.name}: '{customer.setup_status}'")

print(f"\n✅ FIX COMPLETED!")
print("🎯 Now ALL customers will show 5 file upload fields")
print("📝 Both manually created and Excel migrated customers require same files")
print("💡 This is correct because Excel customers have no existing setup files")