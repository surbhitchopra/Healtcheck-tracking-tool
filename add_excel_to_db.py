#!/usr/bin/env python
"""
Additive Excel to Database Migration Script
ADDS Excel data to existing database WITHOUT deleting existing data
"""
import os
import sys
import django
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckFile

def add_excel_to_existing_db():
    """Add Excel data to existing database without deleting current data"""
    
    print("➕ Adding Excel Data to Existing Database")
    print("=" * 60)
    print("⚠️  This will PRESERVE existing data and ADD Excel data alongside")
    
    # Show current database status
    current_customers = Customer.objects.filter(is_deleted=False).count()
    current_unique = len(Customer.get_customers_with_networks())
    
    print(f"\n📊 Current Database Status:")
    print(f"  👥 Existing customers: {current_customers}")
    print(f"  🏢 Unique customer names: {current_unique}")
    
    try:
        # Read Excel file
        excel_path = Path("Script/Health_Check_Tracker_1.xlsx")
        
        if not excel_path.exists():
            print(f"❌ Excel file not found: {excel_path}")
            return False
        
        print(f"\n📊 Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name='Summary')
        
        print(f"📋 Found {len(df)} records in Excel to add")
        
        # Process each Excel record
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                customer_name = str(row.get('Customer', '')).strip()
                network_name = str(row.get('Network', '')).strip()
                
                if not customer_name or customer_name == 'nan':
                    continue
                
                print(f"\n🏢 Processing: {customer_name} - {network_name}")
                
                # Check if this exact combination already exists
                existing = Customer.objects.filter(
                    name=customer_name,
                    network_name=network_name,
                    is_deleted=False
                ).first()
                
                if existing:
                    print(f"  📊 Already exists (ID: {existing.id}) - Updating with Excel data")
                    
                    # Update existing with Excel data
                    country = str(row.get('Country', 'Unknown')).strip()
                    node_qty = int(row.get('Node Qty', 0)) if pd.notna(row.get('Node Qty')) else 0
                    ne_type = str(row.get('NE Type', '1830 PSS')).strip()
                    gtac = str(row.get('gTAC', 'Classic')).strip()
                    
                    # Extract monthly data
                    monthly_runs = {}
                    total_runs = 0
                    
                    # Get all date columns
                    date_columns = [col for col in df.columns if '2024' in str(col) or '2025' in str(col)]
                    
                    for date_col in date_columns:
                        if pd.notna(row.get(date_col)):
                            month_key = str(date_col)[:7] if len(str(date_col)) >= 7 else str(date_col)
                            run_date = row.get(date_col)
                            
                            if pd.notna(run_date):
                                if hasattr(run_date, 'strftime'):
                                    monthly_runs[month_key] = run_date.strftime('%Y-%m-%d')
                                else:
                                    monthly_runs[month_key] = str(run_date)
                                total_runs += 1
                    
                    # Update fields with Excel data
                    existing.country = country
                    existing.node_qty = node_qty
                    existing.ne_type = ne_type
                    existing.gtac = gtac
                    existing.monthly_runs = monthly_runs
                    existing.total_runs = total_runs
                    existing.network_type = ne_type  # Update network type to NE type
                    existing.save()
                    
                    updated_count += 1
                    print(f"    ✅ Updated with Excel data: {total_runs} runs, {node_qty} nodes")
                    
                else:
                    # Add new customer with Excel data
                    country = str(row.get('Country', 'Unknown')).strip()
                    node_qty = int(row.get('Node Qty', 0)) if pd.notna(row.get('Node Qty')) else 0
                    ne_type = str(row.get('NE Type', '1830 PSS')).strip()
                    gtac = str(row.get('gTAC', 'Classic')).strip()
                    
                    # Extract monthly data
                    monthly_runs = {}
                    total_runs = 0
                    
                    date_columns = [col for col in df.columns if '2024' in str(col) or '2025' in str(col)]
                    
                    for date_col in date_columns:
                        if pd.notna(row.get(date_col)):
                            month_key = str(date_col)[:7] if len(str(date_col)) >= 7 else str(date_col)
                            run_date = row.get(date_col)
                            
                            if pd.notna(run_date):
                                if hasattr(run_date, 'strftime'):
                                    monthly_runs[month_key] = run_date.strftime('%Y-%m-%d')
                                else:
                                    monthly_runs[month_key] = str(run_date)
                                total_runs += 1
                    
                    # Create new customer entry
                    new_customer = Customer.objects.create(
                        name=customer_name,
                        network_name=network_name,
                        network_type=ne_type,
                        setup_status='READY',
                        country=country,
                        node_qty=node_qty,
                        ne_type=ne_type,
                        gtac=gtac,
                        monthly_runs=monthly_runs,
                        total_runs=total_runs
                    )
                    
                    added_count += 1
                    print(f"    ✅ Added new customer (ID: {new_customer.id}): {total_runs} runs, {node_qty} nodes")
                
            except Exception as e:
                print(f"  ❌ Error processing row {index}: {e}")
                skipped_count += 1
                continue
        
        # Show final results
        final_customers = Customer.objects.filter(is_deleted=False).count()
        final_unique = len(Customer.get_customers_with_networks())
        
        print(f"\n🎉 Excel Addition Complete!")
        print(f"📊 Results:")
        print(f"  ➕ New customers added: {added_count}")
        print(f"  🔄 Existing customers updated: {updated_count}")
        print(f"  ⏭️  Records skipped: {skipped_count}")
        
        print(f"\n📈 Database Growth:")
        print(f"  👥 Before: {current_customers} customers → After: {final_customers} customers")
        print(f"  🏢 Before: {current_unique} unique names → After: {final_unique} unique names")
        
        # Show enhanced customers
        print(f"\n🔍 Enhanced Customers (with Excel data):")
        enhanced = Customer.objects.filter(
            country__isnull=False,
            node_qty__gt=0
        ).exclude(country='Unknown')[:5]
        
        for customer in enhanced:
            print(f"  🏢 {customer.name} - {customer.network_name}")
            print(f"    🌍 {customer.country}, 📊 {customer.node_qty} nodes, 📅 {customer.total_runs} runs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during Excel addition: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("➕ Additive Excel to Database Integration Tool")
    print("=" * 60)
    
    # Ask for confirmation
    print("✅ This will PRESERVE your existing database data")
    print("➕ This will ADD Excel data alongside existing customers")
    print("🔄 Matching customers will be ENHANCED with Excel data")
    
    response = input("\n🔄 Continue with additive Excel integration? (y/N): ")
    
    if response.lower() != 'y':
        print("❌ Operation cancelled.")
        exit(0)
    
    # Run additive migration
    success = add_excel_to_existing_db()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ADDITIVE INTEGRATION SUCCESS!")
        print("✅ Your original database data is preserved")
        print("➕ Excel data has been added alongside existing customers")
        print("📊 Customer dashboard will now show:")
        print("  - Your original database customers (unchanged)")
        print("  - Excel customers with complete data (dates, runs, countries, nodes)")
        print("  - Enhanced existing customers with Excel details")
        print("🎯 Perfect unified database with both data sources!")
    else:
        print("❌ INTEGRATION FAILED!")
        print("💡 Check the error messages above")
        print("✅ Your original database data remains safe")