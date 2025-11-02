#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import *

def fix_file_paths():
    """Fix incorrect file paths in the database"""
    
    # Get the customer
    customer = Customer.objects.filter(name='timedotcom', is_deleted=False).first()
    if not customer:
        print('❌ Customer timedotcom not found')
        return
    
    print(f'🔧 Fixing file paths for customer: {customer.name}')
    
    # Define the correct base directory  
    BASE_DIR = Path('C:/Users/surchopr/hc_final')
    CUSTOMER_FILES_DIR = BASE_DIR / 'Script' / 'customer_files' / 'timedotcom'
    
    fixes_made = 0
    
    # Fix TEC_REPORT files
    print('\n📊 Fixing TEC_REPORT files...')
    tec_files = HealthCheckFile.objects.filter(customer=customer, file_type='TEC_REPORT')
    for file_obj in tec_files:
        correct_path = CUSTOMER_FILES_DIR / 'tec_reports' / file_obj.stored_filename
        print(f'  Checking: {file_obj.stored_filename}')
        print(f'    Looking for: {correct_path}')
        print(f'    Exists: {correct_path.exists()}')
        
        if correct_path.exists():
            old_path = file_obj.file_path
            file_obj.file_path = str(correct_path)
            file_obj.save()
            print(f'    ✅ FIXED TEC_REPORT: {file_obj.stored_filename}')
            print(f'       Old: {old_path}')
            print(f'       New: {file_obj.file_path}')
            fixes_made += 1
        else:
            print(f'    ❌ File not found at expected location')
    
    # Fix INVENTORY_CSV files  
    print('\n📦 Fixing INVENTORY_CSV files...')
    inventory_files = HealthCheckFile.objects.filter(customer=customer, file_type='INVENTORY_CSV')
    for file_obj in inventory_files:
        correct_path = CUSTOMER_FILES_DIR / 'inventory_files' / file_obj.stored_filename
        print(f'  Checking: {file_obj.stored_filename}')
        print(f'    Looking for: {correct_path}')
        print(f'    Exists: {correct_path.exists()}')
        
        if correct_path.exists():
            old_path = file_obj.file_path
            file_obj.file_path = str(correct_path)
            file_obj.save()
            print(f'    ✅ FIXED INVENTORY_CSV: {file_obj.stored_filename}')
            print(f'       Old: {old_path}')
            print(f'       New: {file_obj.file_path}')
            fixes_made += 1
        else:
            print(f'    ❌ File not found at expected location')
    
    # Fix TRACKER_GENERATED files
    print('\n📈 Fixing TRACKER_GENERATED files...')
    tracker_files = HealthCheckFile.objects.filter(customer=customer, file_type='TRACKER_GENERATED')
    for file_obj in tracker_files:
        correct_path = CUSTOMER_FILES_DIR / 'generated_trackers' / file_obj.stored_filename
        print(f'  Checking: {file_obj.stored_filename}')
        print(f'    Looking for: {correct_path}')
        print(f'    Exists: {correct_path.exists()}')
        
        if correct_path.exists():
            old_path = file_obj.file_path
            file_obj.file_path = str(correct_path)
            file_obj.save()
            print(f'    ✅ FIXED TRACKER_GENERATED: {file_obj.stored_filename}')
            print(f'       Old: {old_path}')
            print(f'       New: {file_obj.file_path}')
            fixes_made += 1
        else:
            print(f'    ❌ File not found at expected location')
    
    # Fix HC_TRACKER files (old trackers)
    print('\n📁 Fixing HC_TRACKER files...')
    hc_tracker_files = HealthCheckFile.objects.filter(customer=customer, file_type='HC_TRACKER')
    for file_obj in hc_tracker_files:
        correct_path = CUSTOMER_FILES_DIR / 'old_trackers' / file_obj.stored_filename
        print(f'  Checking: {file_obj.stored_filename}')
        print(f'    Looking for: {correct_path}')
        print(f'    Exists: {correct_path.exists()}')
        
        if correct_path.exists():
            old_path = file_obj.file_path
            file_obj.file_path = str(correct_path)
            file_obj.save()
            print(f'    ✅ FIXED HC_TRACKER: {file_obj.stored_filename}')
            print(f'       Old: {old_path}')
            print(f'       New: {file_obj.file_path}')
            fixes_made += 1
        else:
            print(f'    ❌ File not found at expected location')
    
    print(f'\n🎯 Summary: {fixes_made} file paths were fixed!')
    
    # Test the download URLs
    print('\n🧪 Testing download URLs:')
    test_files = [
        'TIMEDOTCOM_Reports_20250503.xlsx',
        'TIMEDOTCOM_Inventory.csv'
    ]
    
    for filename in test_files:
        file_obj = HealthCheckFile.objects.filter(customer=customer, stored_filename=filename).first()
        if file_obj:
            print(f'  {filename}:')
            print(f'    DB Path: {file_obj.file_path}')
            print(f'    Exists: {Path(file_obj.file_path).exists() if file_obj.file_path else False}')
            print(f'    Download URL: http://10.131.212.14:3000/download/tracker/?filename={filename}')
        else:
            print(f'  {filename}: ❌ Not found in database')

if __name__ == '__main__':
    fix_file_paths()
