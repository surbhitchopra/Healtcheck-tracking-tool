import pandas as pd
import os
import sys

print("🔍 CHECKING EXPECTED CUSTOMER COUNTS:")

# 1. Check Excel customers
excel_path = r'c:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx'
excel_customers = 0
excel_networks = 0

if os.path.exists(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name='Summary')
        excel_networks = len(df)
        excel_customers = df['Customer'].nunique()
        print(f"📊 EXCEL DATA:")
        print(f"   Total networks/rows: {excel_networks}")
        print(f"   Unique customers: {excel_customers}")
        print(f"   Customer names: {list(df['Customer'].unique())}")
    except Exception as e:
        print(f"❌ Excel error: {e}")
else:
    print("❌ Excel file not found")

# 2. Check Database customers
try:
    # Setup Django
    sys.path.append('.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
    
    import django
    django.setup()
    
    from HealthCheck_app.models import Customer
    
    db_customers = Customer.objects.filter(is_deleted=False)
    db_count = db_customers.count()
    db_names = list(db_customers.values_list('name', flat=True).distinct())
    
    print(f"\n💾 DATABASE DATA:")
    print(f"   Total customers: {db_count}")
    print(f"   Customer names: {db_names}")
    
except Exception as e:
    print(f"❌ Database error: {e}")
    db_count = 0

# 3. Calculate total
total_expected = excel_customers + db_count
print(f"\n🎯 EXPECTED TOTAL:")
print(f"   Excel customers: {excel_customers}")
print(f"   Database customers: {db_count}")
print(f"   TOTAL EXPECTED: {total_expected} customers")

print(f"\n📱 Dashboard should show: {total_expected} customers")
print(f"   - {db_count} with 💾 DB badge")
print(f"   - {excel_customers} with 📊 EXCEL badge")