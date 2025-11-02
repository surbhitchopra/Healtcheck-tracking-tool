#!/usr/bin/env python
import os
import sys
import django

# Add project path
project_path = r"C:\Users\surchopr\hc_final"
sys.path.append(project_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import HealthCheckFile, Customer
from django.utils import timezone

# Get the customer 
customer = Customer.objects.filter(name__icontains='timedotcom').first()
if customer:
    print(f'Customer: {customer.name} (ID: {customer.id})')
    
    # Get ignore files for this customer
    ignore_files = HealthCheckFile.objects.filter(
        customer=customer, 
        file_type__in=['GLOBAL_IGNORE_TXT', 'SELECTIVE_IGNORE_XLSX']
    ).order_by('-uploaded_at')[:10]
    
    print(f'Recent ignore files ({ignore_files.count()}):')
    for f in ignore_files:
        print(f'  {f.file_type}: {f.stored_filename}')
        print(f'    Path: {f.file_path}')
        print(f'    Date: {timezone.localtime(f.uploaded_at).strftime("%d-%m-%Y %I:%M %p")}')
        
        # Check if file actually exists
        if f.file_path and os.path.exists(f.file_path):
            print(f'    ✅ File exists on disk')
        else:
            print(f'    ❌ File NOT found on disk')
        print()
        
    print("\n" + "="*50)
    print("TESTING UI LOGIC:")
    print("="*50)
    
    # Test the same logic as tracker_history
    all_files = HealthCheckFile.objects.filter(customer=customer).order_by('-uploaded_at')
    
    file_categories = {
        'host_files': [],
        'reports': [],
        'tracker_generated': [],
        'old_trackers': [],
        'inventory_files': []
    }
    
    for f in all_files:
        file_info = {
            "upload_id": f.id,
            "filename": f.stored_filename,
            "original_filename": f.original_filename,
            "upload_date": timezone.localtime(f.uploaded_at).strftime('%d-%m-%Y %I:%M %p'),
            "file_url": f"/download/tracker/?filename={f.stored_filename}",
            "upload_timestamp": f.uploaded_at,
        }

        if f.file_type == 'INVENTORY_CSV':
            file_categories['inventory_files'].append(file_info)
        elif f.file_type == 'TEC_REPORT':
            file_categories['reports'].append(file_info)
        elif f.file_type == 'TRACKER_GENERATED':
            if "HC_Issues_Tracker" in f.stored_filename:
                file_categories['tracker_generated'].append(file_info)
        elif f.file_type == 'HC_TRACKER':
            if "HC_Issues_Tracker" in f.stored_filename:
                file_categories['old_trackers'].append(file_info)
        elif f.file_type in ['GLOBAL_IGNORE_TXT', 'SELECTIVE_IGNORE_XLSX']:
            file_categories['old_trackers'].append(file_info)
            print(f"🎯 Added ignore file to old_trackers: {f.stored_filename}")
    
    print(f"\nFiles that will show in OLD TRACKERS section: {len(file_categories['old_trackers'])}")
    for item in file_categories['old_trackers']:
        print(f"  - {item['filename']} ({item['upload_date']})")
        
else:
    print('No customer found')
