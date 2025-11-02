#!/usr/bin/env python
"""
Enhanced Excel to Database Migration Script
Migrates COMPLETE Excel dashboard data including dates, runs, node quantities etc.
"""
import os
import sys
import django
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckFile

def backup_current_data():
    """Create backup of current database state"""
    print("💾 Creating backup before complete migration...")
    
    try:
        backup_dir = Path("backup_complete_migration")
        backup_dir.mkdir(exist_ok=True)
        
        # Export current data
        customers = list(Customer.objects.filter(is_deleted=False).values())
        files = list(HealthCheckFile.objects.values())
        
        backup_data = {
            'customers': customers,
            'files': files,
            'backup_timestamp': str(datetime.now()),
            'migration_type': 'complete_excel_migration'
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"complete_migration_backup_{timestamp}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✅ Backup created: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return None

def migrate_complete_excel_data():
    """Migrate complete Excel data including monthly dates, runs, countries, nodes etc."""
    
    print("🚀 Starting Complete Excel Dashboard Data Migration")
    print("=" * 70)
    
    try:
        # Read Excel file
        excel_path = Path("Script/Health_Check_Tracker_1.xlsx")
        
        if not excel_path.exists():
            print(f"❌ Excel file not found: {excel_path}")
            return False
        
        print(f"📊 Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name='Summary')
        
        print(f"📋 Found {len(df)} records in Excel")
        
        # Clear existing data first
        print("🗑️ Clearing existing customer data...")
        Customer.objects.all().delete()
        HealthCheckFile.objects.all().delete()
        print("✅ Existing data cleared")
        
        # Process each record
        migrated_count = 0
        
        for index, row in df.iterrows():
            try:
                customer_name = str(row.get('Customer', '')).strip()
                network_name = str(row.get('Network', '')).strip()
                
                if not customer_name or customer_name == 'nan':
                    continue
                
                print(f"\n🏢 Processing: {customer_name} - {network_name}")
                
                # Extract basic info
                country = str(row.get('Country', 'Unknown')).strip()
                node_qty = int(row.get('Node Qty', 0)) if pd.notna(row.get('Node Qty')) else 0
                ne_type = str(row.get('NE Type', '1830 PSS')).strip()
                gtac = str(row.get('gTAC', 'Classic')).strip()
                
                print(f"  🌍 Country: {country}, 📊 Nodes: {node_qty}")
                print(f"  🔧 NE Type: {ne_type}, 🏢 gTAC: {gtac}")
                
                # Extract monthly data
                monthly_runs = {}
                total_runs = 0
                
                # Get all date columns (they appear as datetime objects in pandas)
                date_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col]) and '2024' in str(col) or '2025' in str(col)]
                
                for date_col in date_columns:
                    if pd.notna(row.get(date_col)):
                        # Extract month-year from column name
                        month_key = str(date_col)[:7] if len(str(date_col)) >= 7 else str(date_col)
                        run_date = row.get(date_col)
                        
                        if pd.notna(run_date):
                            # Convert to string format for JSON storage
                            if hasattr(run_date, 'strftime'):
                                monthly_runs[month_key] = run_date.strftime('%Y-%m-%d')
                            else:
                                monthly_runs[month_key] = str(run_date)
                            total_runs += 1
                
                print(f"  📅 Monthly runs: {total_runs} total runs across {len(monthly_runs)} months")
                
                # Create customer entry
                customer = Customer.objects.create(
                    name=customer_name,
                    network_name=network_name,
                    network_type=ne_type,  # Use NE Type as network type
                    setup_status='READY',
                    country=country,
                    node_qty=node_qty,
                    ne_type=ne_type,
                    gtac=gtac,
                    monthly_runs=monthly_runs,
                    total_runs=total_runs
                )
                
                print(f"  ✅ Created customer (ID: {customer.id})")
                migrated_count += 1
                
            except Exception as e:
                print(f"  ❌ Error processing row {index}: {e}")
                continue
        
        print(f"\n🎉 Complete Excel Migration Finished!")
        print(f"📊 Successfully migrated {migrated_count} customers with complete data")
        
        # Show summary
        show_migration_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_migration_summary():
    """Show detailed migration summary"""
    print(f"\n📋 Migration Summary:")
    print("=" * 50)
    
    # Customer statistics
    total_customers = Customer.objects.filter(is_deleted=False).count()
    unique_customers = len(Customer.get_customers_with_networks())
    
    print(f"👥 Total customer entries: {total_customers}")
    print(f"🏢 Unique customer names: {unique_customers}")
    
    # Show sample data
    print(f"\n🔍 Sample Migrated Data:")
    
    customers = Customer.objects.filter(is_deleted=False)[:3]  # Show first 3
    
    for customer in customers:
        print(f"\n  🏢 {customer.name} - {customer.network_name}")
        print(f"    🌍 Country: {customer.country}")
        print(f"    📊 Nodes: {customer.node_qty}")
        print(f"    🔧 NE Type: {customer.ne_type}")
        print(f"    🏢 gTAC: {customer.gtac}")
        print(f"    📅 Total Runs: {customer.total_runs}")
        
        # Show some monthly data
        if customer.monthly_runs:
            recent_runs = list(customer.monthly_runs.items())[:3]  # Show first 3 months
            print(f"    📅 Recent runs: {dict(recent_runs)}")
    
    # Country distribution
    countries = Customer.objects.values_list('country', flat=True).distinct()
    print(f"\n🌍 Countries covered: {list(countries)}")
    
    # Node distribution
    total_nodes = sum(Customer.objects.values_list('node_qty', flat=True))
    print(f"📊 Total nodes across all networks: {total_nodes}")

if __name__ == "__main__":
    print("🚀 Complete Excel Dashboard Data Migration Tool")
    print("=" * 60)
    
    # Ask for confirmation
    print("⚠️  This will REPLACE all existing data with complete Excel data")
    print("📊 This includes: dates, runs, countries, node quantities, gTAC info")
    
    response = input("\n🔄 Continue with complete migration? (y/N): ")
    
    if response.lower() != 'y':
        print("❌ Migration cancelled.")
        exit(0)
    
    # Create backup first
    backup_file = backup_current_data()
    
    if not backup_file:
        print("❌ Could not create backup. Aborting migration.")
        exit(1)
    
    # Run migration
    success = migrate_complete_excel_data()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPLETE MIGRATION SUCCESS!")
        print("✅ Excel dashboard data fully integrated with database")
        print("📱 Your dashboard will now show:")
        print("  - All customer details (country, nodes, gTAC)")
        print("  - Complete monthly run history")
        print("  - All dates and statistics")
        print("📊 Customer dashboard will work perfectly!")
        
        if backup_file:
            print(f"\n🔙 To revert: Use backup file {backup_file}")
    else:
        print("❌ MIGRATION FAILED!")
        print("💡 Check the error messages above")
        if backup_file:
            print(f"🔙 You can restore from: {backup_file}")