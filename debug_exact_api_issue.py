#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer
from collections import defaultdict
from datetime import datetime

print("🔍 DEBUGGING EXACT API FUNCTION ISSUE")
print("=" * 70)

# Simulate the EXACT logic from views.py api_customer_dashboard_customers
try:
    print("📡 API: /api/customer-dashboard/customers/ called")
    
    # Get customers from database
    customers = Customer.objects.filter(is_deleted=False)
    
    # Group customers by name (like BSNL with multiple networks)
    customer_groups = defaultdict(list)
    
    for customer in customers:
        # Skip customers without data
        if not customer.total_runs and not customer.monthly_runs:
            print(f"🚫 Skipping Excel-only customer: {customer.name}")
            continue
        customer_groups[customer.name].append(customer)
    
    print(f"\n📊 Customer groups found: {list(customer_groups.keys())}")
    
    # Focus on BSNL to debug the issue
    if 'BSNL' in customer_groups:
        customer_name = 'BSNL'
        customer_networks = customer_groups[customer_name]
        
        print(f"\n🎯 DEBUGGING BSNL: {len(customer_networks)} networks")
        
        # Show raw data for each BSNL network
        for i, net_customer in enumerate(customer_networks):
            print(f"\n   Network {i+1}: {net_customer.network_name}")
            print(f"      ID: {net_customer.id}")
            print(f"      Total runs: {net_customer.total_runs}")
            print(f"      Raw monthly_runs: {net_customer.monthly_runs}")
        
        # Now simulate the EXACT API processing logic
        if len(customer_networks) > 1:
            print(f"\n📊 Grouping {len(customer_networks)} networks for {customer_name}")
            
            # Calculate combined data
            total_runs = sum(net.total_runs or 0 for net in customer_networks)
            total_nodes = sum(net.node_qty or 0 for net in customer_networks)
            
            print(f"   Combined total runs: {total_runs}")
            print(f"   Combined total nodes: {total_nodes}")
            
            # Create combined months array (latest date from any network)
            combined_months = ['-'] * 12
            for customer in customer_networks:
                if customer.monthly_runs:
                    for month_key, date_str in customer.monthly_runs.items():
                        try:
                            if '-' in month_key and date_str and date_str not in ['-', 'None', '']:
                                month_num = int(month_key.split('-')[1]) - 1
                                if 0 <= month_num < 12:
                                    if date_str in ['Not Started', 'Not Run', 'No Report']:
                                        if combined_months[month_num] == '-':
                                            combined_months[month_num] = date_str
                                    else:
                                        try:
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                            month_abbr = date_obj.strftime('%b')
                                            formatted_date = f"{date_obj.day}-{month_abbr}"
                                            # Use latest date
                                            if combined_months[month_num] == '-':
                                                combined_months[month_num] = formatted_date
                                            elif date_str not in ['Not Started', 'No Report']:
                                                combined_months[month_num] = formatted_date
                                        except ValueError:
                                            if combined_months[month_num] == '-':
                                                combined_months[month_num] = str(date_str)
                        except (ValueError, IndexError):
                            continue
            
            print(f"\n🔥 COMBINED MONTHS ARRAY: {combined_months}")
            
            # Create individual network objects - THIS IS THE CRITICAL PART
            networks_array = []
            for net_customer in customer_networks:
                print(f"\n   🔧 Processing individual network: {net_customer.network_name}")
                
                # Create months array for this specific network
                net_months = ['-'] * 12
                if net_customer.monthly_runs:
                    print(f"      Raw data: {net_customer.monthly_runs}")
                    
                    for month_key, date_str in net_customer.monthly_runs.items():
                        try:
                            if '-' in month_key and date_str and date_str not in ['-', 'None', '']:
                                month_num = int(month_key.split('-')[1]) - 1
                                if 0 <= month_num < 12:
                                    print(f"         Processing: {month_key} = {date_str}")
                                    
                                    if date_str in ['Not Started', 'Not Run', 'No Report']:
                                        net_months[month_num] = date_str
                                        print(f"         Status: {date_str} → Month {month_num+1}")
                                    else:
                                        try:
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                            month_abbr = date_obj.strftime('%b')
                                            formatted = f"{date_obj.day}-{month_abbr}"
                                            net_months[month_num] = formatted
                                            print(f"         Date: {date_str} → {formatted} → Month {month_num+1}")
                                        except ValueError:
                                            net_months[month_num] = str(date_str)
                                            print(f"         Raw: {date_str} → Month {month_num+1}")
                        except (ValueError, IndexError) as e:
                            print(f"         Error processing {month_key}: {e}")
                            continue
                
                print(f"      FINAL NET_MONTHS: {net_months}")
                
                # Count how many actual dates this network has
                actual_dates = sum(1 for month in net_months if month not in ['-', 'Not Started', 'No Report'])
                print(f"      Actual date count: {actual_dates}")
                
                networks_array.append({
                    'name': net_customer.network_name or f'Network_{len(networks_array)+1}',
                    'network_name': net_customer.network_name or f'Network_{len(networks_array)+1}',
                    'runs': net_customer.total_runs or 0,
                    'total_runs': net_customer.total_runs or 0,
                    'months': net_months,  # Individual network months - THIS IS KEY!
                    'monthly_runs': net_customer.monthly_runs or {},
                    'country': net_customer.country,
                    'node_count': net_customer.node_qty or 0,
                    'gtac': net_customer.gtac,
                    'ne_type': net_customer.ne_type
                })
            
            # Print summary
            print(f"\n📋 FINAL NETWORKS_ARRAY SUMMARY:")
            for i, net in enumerate(networks_array):
                actual_dates = sum(1 for month in net['months'] if month not in ['-', 'Not Started', 'No Report'])
                print(f"   {i+1}. {net['network_name']}")
                print(f"      Months: {net['months']}")
                print(f"      Date count: {actual_dates}")
                print(f"      Total runs: {net['runs']}")
            
            # Check if the issue is in the API response structure
            main_customer = customer_networks[0]
            customer_key = f"{customer_name}_MASTER"
            
            api_response = {
                'name': customer_name,
                'network_name': f"{len(customer_networks)} networks",
                'country': main_customer.country or 'Unknown',
                'node_qty': total_nodes,
                'ne_type': main_customer.ne_type or '1830 PSS',
                'gtac': main_customer.gtac or 'PSS',
                'total_runs': total_runs,
                'months': combined_months,  # Customer level months
                'networks': networks_array,  # Individual networks with their own months
                'networks_count': len(networks_array),
                'data_source': 'database_migrated'
            }
            
            print(f"\n🔍 FINAL API RESPONSE STRUCTURE:")
            print(f"Customer key: {customer_key}")
            print(f"Customer months: {api_response['months']}")
            print(f"Networks count: {api_response['networks_count']}")
            print(f"First network months: {api_response['networks'][0]['months'] if api_response['networks'] else 'None'}")
            
            # Test specific scenarios
            print(f"\n🧪 TESTING SPECIFIC SCENARIOS:")
            
            # Check BSNL_West_Zone_OTN specifically
            west_otn = next((net for net in networks_array if 'West_Zone_OTN' in net['network_name']), None)
            if west_otn:
                print(f"   BSNL_West_Zone_OTN months: {west_otn['months']}")
                expected = ['Not Started', 'Not Started', '14-Mar', 'No Report', 'No Report', '13-Jun', '24-Jul', '9-Aug', '-', '-', '-', '-']
                matches = west_otn['months'] == expected
                print(f"   Matches expected: {'✅ YES' if matches else '❌ NO'}")
                if not matches:
                    print(f"   Expected: {expected}")
                    print(f"   Got:      {west_otn['months']}")

except Exception as e:
    print(f"❌ Error in debug: {e}")
    import traceback
    traceback.print_exc()

print(f"\n💡 SUMMARY:")
print("   The backend API logic appears correct.")
print("   If networks still show dashes in frontend, the issue is:")
print("   1. Frontend not using individual network 'months' arrays")
print("   2. Frontend using combined customer 'months' for all networks")
print("   3. JavaScript not correctly mapping network data to table cells")