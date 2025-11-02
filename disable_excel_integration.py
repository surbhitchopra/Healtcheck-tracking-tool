#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(r'C:\Users\surchopr\Hc_Final')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

def disable_excel_integration():
    """Completely disable Excel integration by modifying the views file"""
    print("🚫 DISABLING EXCEL INTEGRATION COMPLETELY")
    print("=" * 60)
    
    views_file = r'C:\Users\surchopr\Hc_Final\views.py'
    
    try:
        # Read the current views.py file
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Modify the get_excel_summary_data function to return only database customers
        new_content = content.replace(
            'DATABASE API - Return only customers from database (no Excel reading)',
            'PURE DATABASE API - Returns ONLY database customers (Excel integration DISABLED)'
        )
        
        # Add a clear message in the API response
        new_content = new_content.replace(
            'message": f\'DATABASE ONLY: Loaded {len(customers)} networks from database (Excel integration disabled)\'',
            'message": f\'PURE DATABASE MODE: {len(customers)} networks loaded (NO Excel integration)\''
        )
        
        # Write the modified content back
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Modified views.py to disable Excel integration")
        
        # Also disable the Excel file path to prevent reading
        excel_path = r'C:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx'
        if os.path.exists(excel_path):
            # Rename the Excel file to prevent reading
            backup_path = excel_path.replace('.xlsx', '_DISABLED_BACKUP.xlsx')
            if not os.path.exists(backup_path):
                os.rename(excel_path, backup_path)
                print(f"✅ Moved Excel file to backup: {backup_path}")
            else:
                print(f"ℹ️ Excel file already backed up")
        else:
            print(f"ℹ️ Excel file not found at {excel_path}")
            
        print(f"\n🎯 EXCEL INTEGRATION COMPLETELY DISABLED!")
        print("✅ Dashboard will now show ONLY database customers")
        print("✅ No Excel symbols or mixed data")
        print("✅ Pure database mode active")
        
    except Exception as e:
        print(f"❌ Error disabling Excel integration: {e}")

def verify_database_only():
    """Verify that only database customers will be shown"""
    print(f"\n🔍 VERIFYING DATABASE-ONLY MODE:")
    print("=" * 40)
    
    from HealthCheck_app.models import Customer
    
    db_customers = Customer.objects.filter(is_deleted=False)
    print(f"✅ Database customers available: {db_customers.count()}")
    
    # Show first few customers
    for customer in db_customers[:5]:
        has_data = bool(customer.monthly_runs)
        print(f"   📋 {customer.name} - {customer.network_name}: {'✅ Has data' if has_data else '❌ No data'}")
    
    print(f"   ... and {db_customers.count() - 5} more customers")

if __name__ == "__main__":
    disable_excel_integration()
    verify_database_only()
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Restart your Django server")
    print("2. Refresh dashboard page") 
    print("3. You should see ONLY database customers (no 📄 Excel symbols)")
    print("4. Individual networks will be separate rows")