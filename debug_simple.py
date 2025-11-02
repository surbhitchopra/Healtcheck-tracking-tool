# Simple script to inspect raw monthly data
from HealthCheck_app.models import Customer

print("🔍 SIMPLE DATABASE INSPECTION FOR MONTHLY RUNS DATA")
print("=" * 60)

# Get all customers that have monthly_runs data
customers_with_monthly_data = Customer.objects.exclude(monthly_runs__isnull=True).exclude(monthly_runs__exact='{}')

print(f"Found {customers_with_monthly_data.count()} customers with monthly_runs data")
print("\n📋 RAW DATA SAMPLE:")
for customer in customers_with_monthly_data[:5]:  # Show first 5
    print(f"\n  CUSTOMER: {customer.name} ({customer.network_name})")
    print(f"    monthly_runs: {repr(customer.monthly_runs)}")
    print(f"    type: {type(customer.monthly_runs)}")
    
    if isinstance(customer.monthly_runs, dict):
        print(f"    Keys/Values:")
        for key, value in customer.monthly_runs.items():
            print(f"      {key} = {repr(value)} (type: {type(value)})")

# Focus on BSNL specifically  
print("\n" + "="*60)
print("🔧 BSNL NETWORKS DETAILED ANALYSIS")
print("="*60)

bsnl_networks = Customer.objects.filter(name='BSNL')
print(f"BSNL Networks found: {bsnl_networks.count()}")

for bsnl in bsnl_networks:
    print(f"\n📡 BSNL Network: {bsnl.network_name}")
    print(f"   Raw monthly_runs: {repr(bsnl.monthly_runs)}")
    print(f"   Type: {type(bsnl.monthly_runs)}")
    print(f"   Bool (has data): {bool(bsnl.monthly_runs)}")
    
    if isinstance(bsnl.monthly_runs, dict):
        print(f"   Dict contents ({len(bsnl.monthly_runs)} items):")
        for key, value in bsnl.monthly_runs.items():
            print(f"     {key} = {repr(value)} (type: {type(value)})")

# Test simple conversion logic
print("\n" + "="*40)
print("🧪 SIMPLE CONVERSION TEST")
print("="*40)

# Create final customer data like the dashboard
bsnl_networks = Customer.objects.filter(name='BSNL')
customer_monthly_array = ['-'] * 12

print(f"Processing {bsnl_networks.count()} BSNL networks...")

for network in bsnl_networks:
    print(f"\nProcessing {network.network_name}:")
    print(f"  monthly_runs: {network.monthly_runs}")
    
    if network.monthly_runs and isinstance(network.monthly_runs, dict):
        for month_key, month_value in network.monthly_runs.items():
            print(f"    Processing {month_key} = {month_value}")
            
            # SIMPLE validation - just check if it has data
            clean_value = str(month_value).strip() if month_value else ''
            
            if clean_value and clean_value not in ['-', '', 'null', 'None', 'Not Started', 'No Report']:
                # Convert date keys - check if it's like '2025-05' (May) or just '5'
                try:
                    if '-' in month_key:
                        # Format: '2025-05' -> extract month number
                        month_num = int(month_key.split('-')[1])
                    else:
                        # Format: '5' -> direct month number
                        month_num = int(month_key)
                    
                    month_index = month_num - 1  # Convert to 0-based index
                    
                    if 0 <= month_index < 12:
                        # Clean the date value (remove year if present)
                        if '-' in clean_value:
                            parts = clean_value.split('-')
                            if len(parts) == 3:  # 2025-01-08
                                clean_value = f"{parts[2]}-{parts[1]}"  # 08-01
                            elif len(parts) == 2:  # Already clean
                                pass
                        
                        customer_monthly_array[month_index] = clean_value
                        print(f"      ✅ Set month {month_num} (index {month_index}) = {clean_value}")
                except (ValueError, IndexError) as e:
                    print(f"      ❌ Error parsing month {month_key}: {e}")

print(f"\n🎯 FINAL BSNL MONTHLY ARRAY:")
print(f"   {customer_monthly_array}")
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for i, val in enumerate(customer_monthly_array):
    print(f"   {months[i]}: {val}")

# Check other customers too
print("\n" + "="*40)
print("🧪 OTHER CUSTOMERS SAMPLE")
print("="*40)

test_customers = ['Tata', 'Moratelindo']
for cust_name in test_customers:
    networks = Customer.objects.filter(name=cust_name)[:1]  # Just first network
    for net in networks:
        print(f"\n{cust_name} sample data:")
        print(f"  monthly_runs: {net.monthly_runs}")
        break