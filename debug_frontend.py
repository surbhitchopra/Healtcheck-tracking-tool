#!/usr/bin/env python3

import os
import sys
import django
import json

# Add the project directory to the Python path
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

# Now we can import Django models
from HealthCheck_app.models import Customer

def debug_api_response():
    """Debug what API actually returns to frontend"""
    print("=== DEBUGGING API RESPONSE FOR FRONTEND ===\n")
    
    try:
        customer = Customer.objects.filter(name__icontains='bsnl').first()
        if not customer:
            print("❌ No BSNL customer found")
            return
            
        print(f"📋 Customer: {customer.name}")
        print(f"📊 Monthly runs data: {customer.monthly_runs}")
        print(f"🌐 Networks count: {customer.networks.count()}")
        
        networks_data = []
        for network in customer.networks.all():
            network_info = {
                'name': network.name,
                'network_name': network.network_name,
                'monthly_runs': network.monthly_runs,
                'last_run_date': network.last_run_date,
                'runs': network.sessions.count()
            }
            networks_data.append(network_info)
            
            print(f"\n🌐 Network: {network.network_name}")
            print(f"   - Name: {network.name}")
            print(f"   - Monthly runs: {network.monthly_runs}")
            print(f"   - Type: {type(network.monthly_runs)}")
            print(f"   - Length: {len(network.monthly_runs) if network.monthly_runs else 0}")
            print(f"   - Sample data: {network.monthly_runs[:3] if network.monthly_runs else 'None'}")
        
        # Create the exact structure that goes to frontend
        api_structure = {
            'name': customer.name,
            'networks': networks_data,
            'monthly_runs': customer.monthly_runs
        }
        
        print(f"\n📤 API STRUCTURE SENT TO FRONTEND:")
        print(f"   Customer name: {api_structure['name']}")
        print(f"   Networks count: {len(api_structure['networks'])}")
        
        for i, net in enumerate(api_structure['networks']):
            print(f"   Network {i+1}: {net['network_name']}")
            print(f"     - monthly_runs: {net['monthly_runs']}")
            print(f"     - Array length: {len(net['monthly_runs']) if net['monthly_runs'] else 0}")
        
        print(f"\n✅ Debug completed. Frontend should receive network monthly_runs arrays.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    debug_api_response()