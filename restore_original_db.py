#!/usr/bin/env python
"""
Restore Original Database Script
Restores the original database data before Excel migration
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckFile

def restore_original_database():
    """Restore original database from backup"""
    print("🔄 Restoring Original Database...")
    
    # Find the first backup (original data)
    backup_dir = Path("backup_excel_migration")
    
    if not backup_dir.exists():
        print("❌ No backup directory found!")
        return False
    
    backup_files = list(backup_dir.glob("db_backup_*.json"))
    
    if not backup_files:
        print("❌ No backup files found!")
        return False
    
    # Use the first backup (original data before any Excel migration)
    original_backup = backup_files[0]
    print(f"📁 Using original backup: {original_backup}")
    
    try:
        with open(original_backup, 'r') as f:
            backup_data = json.load(f)
        
        print(f"📊 Backup contains:")
        print(f"  - {len(backup_data['customers'])} customer records")
        print(f"  - {len(backup_data['files'])} file records")
        
        # Clear current data
        print("🗑️ Clearing current database...")
        Customer.objects.all().delete()
        HealthCheckFile.objects.all().delete()
        
        # Restore original customers
        print("📦 Restoring original customers...")
        restored_count = 0
        
        for customer_data in backup_data['customers']:
            try:
                customer_data.pop('id', None)  # Remove ID to avoid conflicts
                Customer.objects.create(**customer_data)
                restored_count += 1
            except Exception as e:
                print(f"  ⚠️ Warning: Could not restore customer: {e}")
        
        print(f"✅ Restored {restored_count} original customers")
        
        # Restore original files
        print("📁 Restoring original file records...")
        file_count = 0
        
        for file_data in backup_data['files']:
            try:
                file_data.pop('id', None)
                
                # Find customer for this file
                if 'customer_id' in file_data:
                    customers = list(Customer.objects.all().order_by('created_at'))
                    if customers and file_data['customer_id'] <= len(customers):
                        file_data['customer'] = customers[0]
                        file_data.pop('customer_id', None)
                        
                        HealthCheckFile.objects.create(**file_data)
                        file_count += 1
                        
            except Exception as e:
                print(f"  ⚠️ Warning: Could not restore file: {e}")
        
        print(f"✅ Restored {file_count} file records")
        
        # Show final status
        print(f"\n📋 Database Status After Restore:")
        print(f"  👥 Total customers: {Customer.objects.count()}")
        print(f"  📁 Total files: {HealthCheckFile.objects.count()}")
        
        # Show sample customers
        customers_dict = Customer.get_customers_with_networks()
        print(f"  🏢 Unique customer names: {len(customers_dict)}")
        
        print(f"\n👥 Customer List:")
        for customer_name, networks in list(customers_dict.items())[:10]:
            print(f"  🏢 {customer_name}: {len(networks)} network(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False

if __name__ == "__main__":
    print("🔙 Original Database Restore Tool")
    print("=" * 40)
    
    success = restore_original_database()
    
    if success:
        print("\n" + "=" * 40)
        print("✅ Original database successfully restored!")
        print("🎯 Your original customer data is back")
        print("📱 Now ready to ADD Excel data alongside existing data")
    else:
        print("\n" + "=" * 40)
        print("❌ Restore failed!")
        print("💡 Check the error messages above")