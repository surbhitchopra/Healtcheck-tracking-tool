#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now we can import Django models
from HealthCheck_app.models import Customer, Network

def test_network_data_structure():
    """Test the data structure that would be sent to frontend"""
    print("=== TESTING NETWORK DATA STRUCTURE FOR FRONTEND ===\n")
    
    # Get a customer with networks (e.g., BSNL)
    try:
        customer = Customer.objects.filter(name__icontains='bsnl').first()
        if not customer:
            print("❌ No BSNL customer found")
            return
            
        print(f"📋 Testing Customer: {customer.name}")
        print(f"   Networks count: {customer.networks.count()}")
        
        # Simulate the data structure that would be sent to frontend
        networks_data = []
        
        for network in customer.networks.all():
            network_data = {
                'name': network.name,
                'network_name': network.network_name,
                'monthly_runs': network.monthly_runs,  # This is the key array
                'runs': network.sessions.count(),
                'last_run_date': network.last_run_date
            }
            networks_data.append(network_data)
            
            print(f"\n🌐 Network: {network.network_name}")
            print(f"   Internal name: {network.name}")
            print(f"   Monthly runs: {network.monthly_runs}")
            print(f"   Total runs: {network.sessions.count()}")
            print(f"   Last run: {network.last_run_date}")
            
            # Test the logic our JavaScript fix would use
            if network.monthly_runs:
                print("   📅 Month-by-month analysis:")
                for month_num in range(1, 13):
                    month_str = f"{month_num:02d}"  # Convert to "01", "02", etc.
                    
                    # Find dates for this month
                    month_dates = [
                        date_str for date_str in network.monthly_runs
                        if isinstance(date_str, str) and '-' in date_str and date_str.split('-')[1] == month_str
                    ]
                    
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    month_name = month_names[month_num - 1]
                    
                    if month_dates:
                        latest = month_dates[-1]  # Get the latest date in that month
                        print(f"      {month_name}: {latest} ({len(month_dates)} runs)")
                    else:
                        print(f"      {month_name}: - (no runs)")
        
        print(f"\n✅ Data structure test completed!")
        print(f"   Frontend should now be able to read monthly_runs arrays correctly")
        print(f"   Each network has individual monthly dates that should display")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data structure: {e}")
        return False

if __name__ == '__main__':
    test_network_data_structure()