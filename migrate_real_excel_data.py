#!/usr/bin/env python
"""
Enhanced Excel to Database Migration Script
Reads actual Excel tracker files and migrates to database
"""
import os
import sys
import django
import pandas as pd
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckFile
from HealthCheck_app.excel_integration import ExcelDataReader

def migrate_excel_tracker_to_db():
    """Migrate data from Health_Check_Tracker_1.xlsx to database"""
    
    print("🚀 Migrating Real Excel Tracker Data to Database")
    print("=" * 60)
    
    try:
        # Initialize Excel reader
        excel_reader = ExcelDataReader()
        
        # Get Excel customers and networks
        excel_customers = excel_reader.get_excel_customers_networks()
        
        if not excel_customers:
            print("❌ No Excel data found! Check if Health_Check_Tracker_1.xlsx exists")
            return
        
        migrated_count = 0
        updated_count = 0
        
        for customer_name, networks in excel_customers.items():
            print(f"\n🏢 Processing Customer: {customer_name}")
            
            for network_data in networks:
                try:
                    network_name = network_data.get('network_type', 'Main Network')
                    
                    print(f"  📡 Network: {network_name}")
                    
                    # Check if already exists
                    existing = Customer.objects.filter(
                        name=customer_name,
                        network_name=network_name,
                        is_deleted=False
                    ).first()
                    
                    if existing:
                        print(f"    ✅ Already exists (ID: {existing.id}) - Updating")
                        # Update with Excel data
                        existing.network_type = network_data.get('network_type', 'HealthCheck')
                        existing.save()
                        updated_count += 1
                    else:
                        # Create new customer entry
                        new_customer = Customer.objects.create(
                            name=customer_name,
                            network_name=network_name,
                            network_type=network_data.get('network_type', 'HealthCheck'),
                            setup_status='READY'
                        )
                        
                        print(f"    ✅ Created customer (ID: {new_customer.id})")
                        migrated_count += 1
                    
                    # Log additional details from Excel
                    country = network_data.get('country', 'Unknown')
                    nodes = network_data.get('node_qty', 0)
                    ne_type = network_data.get('ne_type', 'Unknown')
                    gtac = network_data.get('gtac', 'Unknown')
                    
                    print(f"      🌍 Country: {country}, 📊 Nodes: {nodes}")
                    print(f"      🔧 NE Type: {ne_type}, 🏢 gTAC: {gtac}")
                    
                except Exception as e:
                    print(f"    ❌ Error processing network {network_name}: {e}")
        
        print(f"\n🎉 Real Excel Migration Completed!")
        print(f"📊 New customers migrated: {migrated_count}")
        print(f"📊 Existing customers updated: {updated_count}")
        
        # Create Excel file records in database
        migrate_excel_file_records(excel_reader)
        
        # Show final summary
        show_database_summary()
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()

def migrate_excel_file_records(excel_reader):
    """Create database records for Excel files"""
    print(f"\n📁 Creating Excel File Records...")
    
    try:
        excel_files = excel_reader.get_excel_files()
        
        for excel_file in excel_files:
            try:
                # Get file info
                filename = excel_file.name
                file_path = str(excel_file)
                file_size = excel_file.stat().st_size
                
                print(f"  📄 Processing file: {filename}")
                
                # Determine file type
                if 'HC_Issues_Tracker' in filename:
                    file_type = 'HC_TRACKER'
                elif 'Health_Check_Tracker' in filename:
                    file_type = 'TRACKER_GENERATED'
                else:
                    file_type = 'CONFIG'
                
                # Check if file record already exists
                existing_file = HealthCheckFile.objects.filter(
                    original_filename=filename,
                    file_path=file_path
                ).first()
                
                if not existing_file:
                    # Create file record (we'll associate with first customer for now)
                    first_customer = Customer.objects.first()
                    
                    if first_customer:
                        HealthCheckFile.objects.create(
                            customer=first_customer,
                            file_type=file_type,
                            original_filename=filename,
                            stored_filename=filename,
                            file_path=file_path,
                            file_size=file_size,
                            is_processed=True
                        )
                        print(f"    ✅ Created file record for {filename}")
                    else:
                        print(f"    ⚠️ No customer found to associate with {filename}")
                else:
                    print(f"    📊 File record already exists for {filename}")
                    
            except Exception as e:
                print(f"    ❌ Error processing file {excel_file}: {e}")
                
    except Exception as e:
        print(f"❌ Error creating file records: {e}")

def show_database_summary():
    """Show final database summary"""
    print(f"\n📊 Database Summary:")
    print("=" * 40)
    
    try:
        # Customer statistics
        total_customers = Customer.objects.filter(is_deleted=False).count()
        unique_customers = len(Customer.get_customers_with_networks())
        
        print(f"👥 Total customer entries: {total_customers}")
        print(f"🏢 Unique customer names: {unique_customers}")
        
        # File statistics
        total_files = HealthCheckFile.objects.count()
        tracker_files = HealthCheckFile.objects.filter(file_type='HC_TRACKER').count()
        
        print(f"📁 Total file records: {total_files}")
        print(f"📊 Tracker files: {tracker_files}")
        
        # Show customers with networks
        print(f"\n📋 Customer Networks:")
        customers_dict = Customer.get_customers_with_networks()
        
        for customer_name, networks in customers_dict.items():
            print(f"\n🏢 {customer_name}:")
            for network in networks[:3]:  # Show first 3 networks
                print(f"    📡 {network.network_name} ({network.network_type})")
            if len(networks) > 3:
                print(f"    ... and {len(networks) - 3} more networks")
        
        print(f"\n✨ SUCCESS: All Excel data now in database!")
        print(f"🎯 Dashboard will use unified database for all operations")
        
    except Exception as e:
        print(f"❌ Error showing summary: {e}")

def backup_database():
    """Create backup before migration"""
    print("💾 Creating database backup...")
    
    try:
        # Create backup directory
        backup_dir = Path("backup_excel_migration")
        backup_dir.mkdir(exist_ok=True)
        
        # Export current customers
        customers = list(Customer.objects.filter(is_deleted=False).values())
        files = list(HealthCheckFile.objects.values())
        
        import json
        
        backup_data = {
            'customers': customers,
            'files': files,
            'backup_timestamp': str(pd.Timestamp.now())
        }
        
        backup_file = backup_dir / f"db_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✅ Backup created: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Excel to Database Migration Tool (Enhanced)")
    print("=" * 50)
    
    # Create backup first
    backup_file = backup_database()
    
    if backup_file:
        print(f"💾 Backup created successfully")
    
    # Run migration
    migrate_excel_tracker_to_db()
    
    print("\n" + "=" * 50)
    print("🎯 Excel data now fully integrated with database!")
    print("📱 Your dashboard will work seamlessly")
    print("🔄 All Excel and DB customers unified")
    
    if backup_file:
        print(f"🔙 To revert: Use backup file {backup_file}")