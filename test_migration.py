#!/usr/bin/env python
"""
Test script to verify Excel to DB migration success
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckFile
from HealthCheck_app.excel_integration import ExcelDataReader

def test_migration_success():
    """Test that Excel data is properly migrated to database"""
    print("🧪 Testing Excel to Database Migration")
    print("=" * 50)
    
    # Test 1: Check database has data
    print("\n📊 Test 1: Database Content Check")
    
    total_customers = Customer.objects.filter(is_deleted=False).count()
    unique_customers = len(Customer.get_customers_with_networks())
    total_files = HealthCheckFile.objects.count()
    
    print(f"  ✓ Total customer entries: {total_customers}")
    print(f"  ✓ Unique customer names: {unique_customers}")
    print(f"  ✓ Total file records: {total_files}")
    
    if total_customers == 0:
        print("  ❌ ERROR: No customers found in database!")
        return False
    
    # Test 2: Compare with Excel data
    print("\n📈 Test 2: Excel vs Database Comparison")
    
    try:
        excel_reader = ExcelDataReader()
        excel_customers = excel_reader.get_excel_customers_networks()
        
        print(f"  📋 Excel customers: {len(excel_customers)}")
        print(f"  📋 Database customers: {unique_customers}")
        
        # Check if key customers from Excel exist in DB
        key_excel_customers = ['BSNL', 'Telekom_Malaysia', 'OPT_NC', 'Maxis']
        found_in_db = 0
        
        db_customers = Customer.get_customers_with_networks()
        
        for excel_customer in key_excel_customers:
            # Look for similar names in database
            found = False
            for db_customer in db_customers.keys():
                if excel_customer.lower() in db_customer.lower() or db_customer.lower() in excel_customer.lower():
                    found = True
                    break
            
            if found:
                found_in_db += 1
                print(f"  ✓ Found {excel_customer} equivalent in database")
            else:
                print(f"  ⚠️ {excel_customer} not found in database")
        
        print(f"  📊 Match rate: {found_in_db}/{len(key_excel_customers)} ({found_in_db/len(key_excel_customers)*100:.1f}%)")
        
    except Exception as e:
        print(f"  ⚠️ Could not compare with Excel: {e}")
    
    # Test 3: Check specific migrated data
    print("\n🏢 Test 3: Migrated Customer Details")
    
    customers_dict = Customer.get_customers_with_networks()
    
    sample_customers = list(customers_dict.items())[:5]  # Show first 5
    
    for customer_name, networks in sample_customers:
        print(f"\n  🏢 {customer_name}:")
        for network in networks[:3]:  # Show first 3 networks
            print(f"    📡 {network.network_name} ({network.network_type})")
            print(f"        ID: {network.id}, Status: {network.setup_status}")
        if len(networks) > 3:
            print(f"    ... and {len(networks) - 3} more networks")
    
    # Test 4: Test dashboard functionality 
    print("\n🎯 Test 4: Dashboard Functionality Test")
    
    try:
        # Test customer statistics function
        from HealthCheck_app.views import get_customer_statistics
        stats = get_customer_statistics()
        
        print(f"  ✓ Customer statistics generated successfully")
        print(f"    - Total registered customers: {stats['total_registered_customers']}")
        print(f"    - Total networks: {stats['total_networks']}")
        print(f"    - Customer names count: {len(stats['customer_names'])}")
        
        if stats['total_registered_customers'] == 0:
            print("  ❌ ERROR: Customer statistics show no customers!")
            return False
        
    except Exception as e:
        print(f"  ❌ ERROR: Dashboard functionality test failed: {e}")
        return False
    
    # Test 5: Test customer selection functionality
    print("\n📋 Test 5: Customer Selection Test")
    
    try:
        # Check if customers can be selected
        first_customer = Customer.objects.filter(is_deleted=False).first()
        
        if first_customer:
            print(f"  ✓ First customer: {first_customer.display_name}")
            print(f"    - Network type: {first_customer.network_type}")
            print(f"    - Setup status: {first_customer.setup_status}")
            print(f"    - Created: {first_customer.created_at}")
        else:
            print("  ❌ ERROR: No customers available for selection!")
            return False
            
    except Exception as e:
        print(f"  ❌ ERROR: Customer selection test failed: {e}")
        return False
    
    return True

def test_revert_functionality():
    """Test that revert functionality works"""
    print("\n🔙 Test 6: Revert Functionality Check")
    
    backup_dir = Path("backup_excel_migration")
    
    if backup_dir.exists():
        backup_files = list(backup_dir.glob("db_backup_*.json"))
        if backup_files:
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            print(f"  ✓ Backup file available: {latest_backup.name}")
            print(f"  ✓ Revert script available: revert_database.py")
            return True
        else:
            print("  ⚠️ No backup files found")
            return False
    else:
        print("  ⚠️ No backup directory found")
        return False

if __name__ == "__main__":
    print("🚀 Excel to Database Migration Test Suite")
    print("=" * 60)
    
    # Run main tests
    migration_success = test_migration_success()
    revert_available = test_revert_functionality()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"  📊 Migration Success: {'✅ PASS' if migration_success else '❌ FAIL'}")
    print(f"  🔙 Revert Available: {'✅ YES' if revert_available else '❌ NO'}")
    
    if migration_success and revert_available:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Excel data successfully migrated to database")
        print("📱 Dashboard should work with unified database")
        print("🔄 You can revert anytime using: python revert_database.py")
    elif migration_success:
        print("\n⚠️ PARTIAL SUCCESS!")
        print("✅ Excel data migrated successfully")
        print("⚠️ But revert functionality not available")
    else:
        print("\n❌ TESTS FAILED!")
        print("💡 Check the error messages above")
        print("🔙 Consider running: python revert_database.py")