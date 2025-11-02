# Simple script to inspect raw monthly data
from HealthCheck_app.models import Customer, Network

print("🔍 SIMPLE DATABASE INSPECTION FOR MONTHLY RUNS DATA")
print("=" * 60)

# Get all customers that have monthly_runs data
customers_with_monthly_data = Customer.objects.exclude(monthly_runs__isnull=True).exclude(monthly_runs__exact='{}')

print(f"Found {customers_with_monthly_data.count()} customers with monthly_runs data")

for customer in customers_with_monthly_data:
    print(f"\n📋 CUSTOMER: {customer.name}")
    print(f"   customer.monthly_runs: {repr(customer.monthly_runs)}")
    print(f"   type: {type(customer.monthly_runs)}")
    
    # Get all networks for this customer
    networks = Network.objects.filter(customer=customer)
    print(f"   Networks: {networks.count()} found")
    
    for i, network in enumerate(networks, 1):
        print(f"   📡 NETWORK {i}: {network.network_name} ({network.name})")
        print(f"      network.monthly_runs: {repr(network.monthly_runs)}")
        print(f"      type: {type(network.monthly_runs)}")
        
        # If it's a dict, show the keys and values
        if isinstance(network.monthly_runs, dict):
            for key, value in network.monthly_runs.items():
                print(f"         Key {key} = {repr(value)} (type: {type(value)})")

# Focus on BSNL specifically  
print("\n" + "="*40)
print("🔧 BSNL SPECIFIC TEST")
print("="*40)

try:
    bsnl_customer = Customer.objects.get(name='BSNL')
    print(f"BSNL Customer found: {bsnl_customer.name}")
    
    networks = Network.objects.filter(customer=bsnl_customer)
    print(f"BSNL Networks: {networks.count()}")
    
    # Initialize result array
    monthly_array = ['-'] * 12
    
    for network in networks:
        print(f"\nProcessing network: {network.network_name}")
        print(f"Raw monthly_runs: {repr(network.monthly_runs)}")
        
        if network.monthly_runs and isinstance(network.monthly_runs, dict):
            for month_key, month_value in network.monthly_runs.items():
                print(f"  Processing: {month_key} = {month_value}")
                
                # Simple validation
                if month_value and str(month_value).strip() not in ['-', '', 'null', 'None']:
                    try:
                        month_index = int(month_key) - 1
                        if 0 <= month_index < 12:
                            clean_value = str(month_value).strip()
                            monthly_array[month_index] = clean_value
                            print(f"    ✅ Set month {month_key} ({month_index}) = {clean_value}")
                    except ValueError:
                        print(f"    ❌ Invalid month key: {month_key}")
    
    print(f"\nFinal BSNL monthly array: {monthly_array}")
    
except Customer.DoesNotExist:
    print("BSNL customer not found")