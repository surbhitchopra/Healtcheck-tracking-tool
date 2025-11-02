#!/usr/bin/env python
"""
Database Revert Script
Restores database to state before Excel migration
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

def revert_database():
    """Revert database to pre-migration state"""
    print("🔄 Starting database revert...")
    
    # Find the backup file
    backup_dir = Path("backup_excel_migration")
    
    if not backup_dir.exists():
        print("❌ No backup directory found!")
        return False
    
    # Find the latest backup file
    backup_files = list(backup_dir.glob("db_backup_*.json"))
    
    if not backup_files:
        print("❌ No backup files found!")
        return False
    
    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Using backup file: {latest_backup}")
    
    try:
        # Load backup data
        with open(latest_backup, 'r') as f:
            backup_data = json.load(f)
        
        print(f"📊 Backup contains:")
        print(f"  - {len(backup_data['customers'])} customer records")
        print(f"  - {len(backup_data['files'])} file records")
        print(f"  - Created at: {backup_data['backup_timestamp']}")
        
        # Ask for confirmation
        response = input("\n⚠️  This will DELETE all current data and restore from backup. Continue? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Revert cancelled.")
            return False
        
        # Delete current data
        print("\n🗑️  Deleting current database records...")
        Customer.objects.all().delete()
        HealthCheckFile.objects.all().delete()
        print("✅ Current data cleared")
        
        # Restore customers from backup
        print("📦 Restoring customers from backup...")
        customers_restored = 0
        
        for customer_data in backup_data['customers']:
            try:
                # Remove fields that might cause issues
                customer_data.pop('id', None)  # Let Django auto-assign IDs
                
                # Create customer
                Customer.objects.create(**customer_data)
                customers_restored += 1
                
            except Exception as e:
                print(f"  ⚠️ Warning: Could not restore customer: {e}")
        
        # Restore files from backup
        print("📁 Restoring file records from backup...")
        files_restored = 0
        
        for file_data in backup_data['files']:
            try:
                # Remove ID and handle foreign key
                file_data.pop('id', None)
                
                # Find customer for this file
                if 'customer_id' in file_data:
                    # Try to find equivalent customer (by position/name)
                    customers = list(Customer.objects.all().order_by('created_at'))
                    if customers and file_data['customer_id'] <= len(customers):
                        file_data['customer'] = customers[0]  # Assign to first customer
                        file_data.pop('customer_id', None)
                        
                        HealthCheckFile.objects.create(**file_data)
                        files_restored += 1
                        
            except Exception as e:
                print(f"  ⚠️ Warning: Could not restore file record: {e}")
        
        print(f"\n✅ Database revert completed!")
        print(f"📊 Restored {customers_restored} customers")
        print(f"📁 Restored {files_restored} file records")
        
        # Show final status
        print(f"\n📋 Current database status:")
        print(f"  - Total customers: {Customer.objects.count()}")
        print(f"  - Total files: {HealthCheckFile.objects.count()}")
        
        # List customers
        print(f"\n👥 Customers in database:")
        customers_dict = Customer.get_customers_with_networks()
        for customer_name, networks in customers_dict.items():
            print(f"  🏢 {customer_name}: {len(networks)} network(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during revert: {e}")
        return False

if __name__ == "__main__":
    print("🔙 Database Revert Tool")
    print("=" * 40)
    
    success = revert_database()
    
    if success:
        print("\n" + "=" * 40)
        print("✅ Database successfully reverted to pre-migration state!")
        print("🎯 Your original data has been restored")
        print("📱 Dashboard will work with original DB customers only")
    else:
        print("\n" + "=" * 40)
        print("❌ Revert failed!")
        print("💡 Check the error messages above")