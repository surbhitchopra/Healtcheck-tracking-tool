#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')

django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession, HealthCheckFile
from Temperature_app.models import Customer as TempCustomer
from django.contrib.auth.models import User

print("🔍 LATEST DATA FROM MySQL DATABASE:")
print("=" * 50)

print("\n📊 Database Counts:")
print(f"HealthCheck Customers: {Customer.objects.count()}")
print(f"Temperature Customers: {TempCustomer.objects.count()}")
print(f"Users: {User.objects.count()}")
print(f"Total Sessions: {HealthCheckSession.objects.count()}")
print(f"Total Files: {HealthCheckFile.objects.count()}")

print("\n🕒 Latest 5 HealthCheck Customers:")
for i, customer in enumerate(Customer.objects.order_by('-created_at')[:5], 1):
    print(f"  {i}. {customer.name} | Created: {customer.created_at}")

print("\n🕒 Latest 3 Sessions:")
for i, session in enumerate(HealthCheckSession.objects.order_by('-created_at')[:3], 1):
    print(f"  {i}. {session.session_id} | Customer: {session.customer.name} | {session.created_at}")

print("\n🕒 Latest 3 Uploaded Files:")
for i, file_obj in enumerate(HealthCheckFile.objects.order_by('-uploaded_at')[:3], 1):
    print(f"  {i}. {file_obj.original_filename} | Customer: {file_obj.customer.name} | {file_obj.uploaded_at}")

print("\n✅ All this data is now in MySQL!")
print("📍 View in phpMyAdmin: XAMPP → MySQL Admin → hc_final_db")
