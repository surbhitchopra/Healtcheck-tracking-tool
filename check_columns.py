#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')

django.setup()

from HealthCheck_app.models import HealthCheckFile

print("📋 COLUMNS in HealthCheckFile table:")
print("=" * 40)

# Get the first file to see field names
file_obj = HealthCheckFile.objects.first()
if file_obj:
    for field in file_obj._meta.fields:
        print(f"  - {field.name}")

print("\n🔍 Your latest uploaded files with ALL columns:")
print("=" * 60)

for i, file_obj in enumerate(HealthCheckFile.objects.order_by('-id')[:3], 1):
    print(f"\n{i}. File ID: {file_obj.id}")
    print(f"   Original Filename: {file_obj.original_filename}")
    print(f"   Customer: {file_obj.customer.name}")
    print(f"   File Type: {file_obj.file_type}")
    print(f"   Uploaded At: {file_obj.uploaded_at}")
    print(f"   File Path: {file_obj.file_path}")
    print(f"   File Size: {file_obj.file_size}")

print("\n📍 In phpMyAdmin, look for these column names!")
