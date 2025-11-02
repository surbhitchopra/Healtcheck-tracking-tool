import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')

django.setup()

from HealthCheck_app.models import Customer

print("🏃 CHECKING TOTAL RUNS FROM DATABASE:")
print("=" * 50)

# Get all active customers
customers = Customer.objects.filter(is_deleted=False)
total_customers = customers.count()
total_runs = 0
customers_with_runs = 0
total_monthly_entries = 0

print(f"📊 Found {total_customers} active customers in database")
print("\nPer Customer Analysis:")
print("-" * 80)

for customer in customers:
    customer_runs = customer.total_runs or 0
    total_runs += customer_runs
    
    if customer_runs > 0:
        customers_with_runs += 1
    
    # Count monthly entries
    monthly_count = 0
    if customer.monthly_runs:
        for month_key, month_value in customer.monthly_runs.items():
            if month_value and str(month_value).strip() not in ['-', '', 'None', 'null', 'Not Started', 'Not Run', 'No Report']:
                monthly_count += 1
    
    total_monthly_entries += monthly_count
    
    network_name = customer.network_name or 'N/A'
    print(f"  {customer.name:<20} | Network: {network_name:<25} | Runs: {customer_runs:>3} | Monthly: {monthly_count:>2}")

print("-" * 80)
print("\n📈 SUMMARY STATISTICS:")
print(f"   🏃 Total Runs (from database): {total_runs}")
print(f"   👥 Total Customers: {total_customers}")
print(f"   ✅ Customers with runs: {customers_with_runs}")
print(f"   📅 Total monthly entries: {total_monthly_entries}")

print(f"\n📱 Expected Dashboard Display:")
print(f"   Header - Total Customers: {total_customers}")
print(f"   Header - Total Runs: {total_runs}")
print(f"   Header - Total Trackers: {total_monthly_entries}")
print(f"   Customer Count: {customers_with_runs} customers with data")