#!/usr/bin/env python
"""
Fix the actual API function that the dashboard calls: api_customer_dashboard_customers

The problem: This function creates separate entries for each BSNL network instead of
grouping them under one BSNL customer with multiple networks.

The solution: Modify the function to group networks by customer name.
"""

import os
from datetime import datetime

# Create backup first
backup_filename = f"views_api_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
print(f"🔒 Creating backup: {backup_filename}")

with open('views.py', 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_filename, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Backup created: {backup_filename}")

# The fix: Replace the entire api_customer_dashboard_customers function
old_function = """@require_http_methods(["GET", "POST"])
def api_customer_dashboard_customers(request):
    \"\"\"
    API endpoint for customer dashboard data - returns migrated Excel data from database
    \"\"\"
    try:
        print("📡 API: /api/customer-dashboard/customers/ called")
        
        # Get customers from database (from the migration)
        customers = Customer.objects.filter(is_deleted=False)
        
        # Format for frontend dashboard
        customer_data = {}
        
        for customer in customers:
            # FILTER: Skip customers that are Excel-only (not properly migrated)
            # Only show customers with proper database integration (Live DB)
            if not customer.total_runs and not customer.monthly_runs:
                print(f"🚫 Skipping Excel-only customer: {customer.name} (no runs/monthly data)")
                continue
                
            # Create unique key for each customer-network combination
            customer_key = f"{customer.name}_{customer.network_name}_{customer.id}"
            
            # Format monthly runs for frontend - FIXED to show actual dates and counts
            monthly_runs_dates = ['-'] * 12  # Initialize 12 months with '-'
            monthly_counts = [0] * 12  # Initialize 12 months with 0
            
            if customer.monthly_runs:
                for month_key, date_str in customer.monthly_runs.items():
                    try:
                        # Extract month number from key like "2025-01"
                        if '-' in month_key and date_str and date_str != '-':
                            month_num = int(month_key.split('-')[1]) - 1  # Convert to 0-based index
                            if 0 <= month_num < 12:
                                # Format date for display like "8-Jan"
                                try:
                                    from datetime import datetime
                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                    monthly_runs_dates[month_num] = date_obj.strftime('%d-%b')
                                    monthly_counts[month_num] = 1  # Mark as having data this month
                                except:
                                    monthly_runs_dates[month_num] = str(date_str)
                                    monthly_counts[month_num] = 1
                    except (ValueError, IndexError):
                        continue
            
            # Create customer entry in format expected by frontend
            customer_data[customer_key] = {
                'name': customer.name,
                'customer_name': customer.name,
                'network_name': customer.network_name,
                'country': customer.country or 'Unknown',
                'node_qty': customer.node_qty or 0,
                'node_count': customer.node_qty or 0,
                'ne_type': customer.ne_type or '1830 PSS',
                'network_type': customer.ne_type or '1830 PSS',
                'gtac': customer.gtac or 'PSS',
                'gtac_team': customer.gtac or 'PSS',
                'total_runs': customer.total_runs or 0,
                'runs': customer.total_runs or 0,
                'run_count': customer.total_runs or 0,
                'monthly_runs': monthly_counts,
                'monthly_runs_dates': monthly_runs_dates,  # NEW: Formatted dates for display
                'monthly_sessions': customer.monthly_runs or {},
                'setup_status': customer.setup_status or 'READY',
                'status': customer.setup_status or 'READY',
                'last_run_date': 'Never',  # Will be updated by frontend if needed
                'networks': [{
                    'id': customer.id,
                    'name': customer.network_name or 'Default Network',
                    'network_name': customer.network_name or 'Default Network',
                    'runs': customer.total_runs or 0,
                    'total_runs': customer.total_runs or 0,
                    'monthly_runs': monthly_counts,
                    'monthly_runs_dates': monthly_runs_dates,  # NEW: Also in networks
                    'country': customer.country,
                    'node_count': customer.node_qty or 0,
                    'gtac': customer.gtac
                }],
                'networks_count': 1,
                'data_source': 'database_migrated'
            }
        
        # DEBUG: Print sample customer data to verify formatting
        if customer_data:
            sample_key = list(customer_data.keys())[0]
            sample_customer = customer_data[sample_key]
            print(f"🔍 SAMPLE CUSTOMER DATA:")
            print(f"   Name: {sample_customer['name']}")
            print(f"   Total Runs (DB): {sample_customer['total_runs']}")
            print(f"   Node Qty (DB): {sample_customer['node_qty']}")
            print(f"   Monthly Dates: {sample_customer['monthly_runs_dates'][:6]}")
            print(f"   Monthly Counts: {sample_customer['monthly_runs'][:6]}")
        
        print(f"✅ API: Returning {len(customer_data)} customers from database")
        
        return JsonResponse({
            'success': True,
            'customers': customer_data,
            'total_customers': len(customer_data),
            'data_source': 'database_migrated',
            'message': f'Loaded {len(customer_data)} customers from migrated database data'
        })
        
    except Exception as e:
        print(f"❌ API Error in api_customer_dashboard_customers: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'customers': {},
            'total_customers': 0
        }, status=500)"""

new_function = """@require_http_methods(["GET", "POST"])
def api_customer_dashboard_customers(request):
    \"\"\"
    API endpoint for customer dashboard data - FIXED to group networks by customer name
    \"\"\"
    try:
        print("📡 API: /api/customer-dashboard/customers/ called")
        
        # Get customers from database
        customers = Customer.objects.filter(is_deleted=False)
        
        # Group customers by name (like BSNL with multiple networks)
        from collections import defaultdict
        customer_groups = defaultdict(list)
        
        for customer in customers:
            # Skip customers without data
            if not customer.total_runs and not customer.monthly_runs:
                print(f"🚫 Skipping Excel-only customer: {customer.name}")
                continue
            customer_groups[customer.name].append(customer)
        
        # Format for frontend dashboard
        customer_data = {}
        
        for customer_name, customer_networks in customer_groups.items():
            if len(customer_networks) == 1:
                # Single network customer - treat normally
                customer = customer_networks[0]
                customer_key = f"{customer.name}_{customer.network_name}_{customer.id}"
                
                # Format monthly runs for this customer
                monthly_runs_dates = ['-'] * 12
                if customer.monthly_runs:
                    for month_key, date_str in customer.monthly_runs.items():
                        try:
                            if '-' in month_key and date_str and date_str not in ['-', 'None', '']:
                                month_num = int(month_key.split('-')[1]) - 1
                                if 0 <= month_num < 12:
                                    if date_str in ['Not Started', 'Not Run', 'No Report']:
                                        monthly_runs_dates[month_num] = date_str
                                    else:
                                        try:
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                            month_abbr = date_obj.strftime('%b')
                                            monthly_runs_dates[month_num] = f"{date_obj.day}-{month_abbr}"
                                        except ValueError:
                                            monthly_runs_dates[month_num] = str(date_str)
                        except (ValueError, IndexError):
                            continue
                
                customer_data[customer_key] = {
                    'name': customer.name,
                    'network_name': customer.network_name,
                    'country': customer.country or 'Unknown',
                    'node_qty': customer.node_qty or 0,
                    'ne_type': customer.ne_type or '1830 PSS',
                    'gtac': customer.gtac or 'PSS',
                    'total_runs': customer.total_runs or 0,
                    'months': monthly_runs_dates,  # This is what frontend expects!
                    'networks': [{
                        'name': customer.network_name or 'Default Network',
                        'network_name': customer.network_name or 'Default Network',
                        'runs': customer.total_runs or 0,
                        'total_runs': customer.total_runs or 0,
                        'months': monthly_runs_dates,  # Individual network months
                        'monthly_runs': customer.monthly_runs or {},
                        'country': customer.country,
                        'node_count': customer.node_qty or 0,
                        'gtac': customer.gtac
                    }],
                    'networks_count': 1,
                    'data_source': 'database_migrated'
                }
            else:
                # Multiple networks (like BSNL) - group them properly
                print(f"📊 Grouping {len(customer_networks)} networks for {customer_name}")
                
                # Calculate combined data
                total_runs = sum(net.total_runs or 0 for net in customer_networks)
                total_nodes = sum(net.node_qty or 0 for net in customer_networks)
                
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
                
                # Create individual network objects
                networks_array = []
                for net_customer in customer_networks:
                    # Create months array for this specific network
                    net_months = ['-'] * 12
                    if net_customer.monthly_runs:
                        for month_key, date_str in net_customer.monthly_runs.items():
                            try:
                                if '-' in month_key and date_str and date_str not in ['-', 'None', '']:
                                    month_num = int(month_key.split('-')[1]) - 1
                                    if 0 <= month_num < 12:
                                        if date_str in ['Not Started', 'Not Run', 'No Report']:
                                            net_months[month_num] = date_str
                                        else:
                                            try:
                                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                month_abbr = date_obj.strftime('%b')
                                                net_months[month_num] = f"{date_obj.day}-{month_abbr}"
                                            except ValueError:
                                                net_months[month_num] = str(date_str)
                            except (ValueError, IndexError):
                                continue
                    
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
                
                # Use main customer info from first network
                main_customer = customer_networks[0]
                customer_key = f"{customer_name}_MASTER"
                
                customer_data[customer_key] = {
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
                print(f"✅ Created grouped customer: {customer_name} with {len(networks_array)} networks")
        
        print(f"✅ API: Returning {len(customer_data)} customers from database")
        
        return JsonResponse({
            'success': True,
            'customers': customer_data,
            'total_customers': len(customer_data),
            'data_source': 'database_migrated',
            'message': f'Loaded {len(customer_data)} customers (BSNL networks grouped properly)'
        })
        
    except Exception as e:
        print(f"❌ API Error in api_customer_dashboard_customers: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'customers': {},
            'total_customers': 0
        }, status=500)"""

# Apply the fix
if old_function in content:
    content = content.replace(old_function, new_function)
    print("✅ Replaced api_customer_dashboard_customers function")
    fixes_applied = 1
else:
    print("❌ Function not found - trying partial match")
    # Try to find the function start
    func_start = content.find("def api_customer_dashboard_customers(request):")
    if func_start != -1:
        # Find the end of the function (next function definition)
        next_func = content.find("@require_http_methods", func_start + 1)
        if next_func != -1:
            # Replace the entire function
            old_func_content = content[func_start:next_func].rstrip()
            # Find the preceding decorator
            decorator_start = content.rfind("@require_http_methods", 0, func_start)
            if decorator_start != -1:
                old_func_with_decorator = content[decorator_start:next_func].rstrip()
                content = content.replace(old_func_with_decorator, new_function)
                print("✅ Replaced function with partial match")
                fixes_applied = 1
            else:
                print("❌ Could not find function decorator")
                fixes_applied = 0
        else:
            print("❌ Could not find end of function")
            fixes_applied = 0
    else:
        print("❌ Function not found at all")
        fixes_applied = 0

if fixes_applied > 0:
    # Write the fixed content back
    with open('views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎉 SUCCESS! Fixed the API function")
    print("📋 Changes made:")
    print("   - Groups BSNL networks under one customer entry")
    print("   - Each network gets its own 'months' array with dates")
    print("   - Fixed 'Not Started' formatting issue")
    print("   - Customer level shows combined data")
    print("   - Individual networks show their specific monthly dates")
    
    print(f"\n🔧 Next steps:")
    print("   1. Restart Django server")
    print("   2. Refresh dashboard page")
    print("   3. BSNL networks should now show individual dates!")
else:
    print(f"\n❌ FAILED to apply fix")
    print("   Manual intervention may be required")

print(f"\n📁 Backup available at: {backup_filename}")