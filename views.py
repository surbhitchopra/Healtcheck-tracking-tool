import pandas as pd
import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import path
import os
from urllib.parse import quote

# Quick URL mapping - add this to your main urls.py:
# path('export-dashboard-data/', export_dashboard_data, name='export_dashboard_data'),

# Database imports
from HealthCheck_app.models import Customer, HealthCheckSession

# Helper function to convert DD-MMM format to DD/MM format
def convert_ddmmm_to_ddmm(date_string):
    """
    Convert dates like '5-Mar', '10-Aug', '6-Dec', '9-Oct' to '05/03', '10/08', '06/12', '09/10'
    """
    if not date_string:
        return date_string
    
    # Convert to string and strip whitespace
    date_str = str(date_string).strip()
    
    # Skip if empty or status messages
    if date_str in ['-', '', 'Not Started', 'Not Run', 'No Report', 'nan', 'NaT', 'None']:
        return date_str
    
    try:
        # Check if it contains '-' (like 9-Oct, 14-Mar, 14-10)
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts) == 2:
                day_part = parts[0].strip()
                month_part = parts[1].strip()
                
                # Month name to number mapping
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                
                # Case 1: Month name format (9-Oct, 14-Mar)
                if month_part in month_map:
                    try:
                        day_num = int(day_part)
                        day_formatted = f"{day_num:02d}"
                        month_formatted = month_map[month_part]
                        converted = f"{day_formatted}/{month_formatted}"
                        print(f"✅ DATE CONVERTED (MMM): '{date_str}' -> '{converted}'")
                        return converted
                    except ValueError:
                        print(f"⚠️ Failed to parse day '{day_part}' in '{date_str}'")
                        pass
                
                # Case 2: Numeric format (14-10, 21-10) 
                elif month_part.isdigit() and day_part.isdigit():
                    try:
                        day_num = int(day_part)
                        month_num = int(month_part)
                        if 1 <= day_num <= 31 and 1 <= month_num <= 12:
                            day_formatted = f"{day_num:02d}"
                            month_formatted = f"{month_num:02d}"
                            converted = f"{day_formatted}/{month_formatted}"
                            print(f"✅ DATE CONVERTED (NUM): '{date_str}' -> '{converted}'")
                            return converted
                    except ValueError:
                        print(f"⚠️ Failed to parse numeric date '{date_str}'")
                        pass
    except Exception as e:
        print(f"⚠️ Error converting date '{date_str}': {e}")
        pass
    
    return date_str

@require_http_methods(["GET"])
def get_excel_summary_data(request):
    """
    PURE DATABASE API - Returns ONLY database customers (Excel integration DISABLED)
    """
    # Get date filters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print(f"📅 Database API called with filters: {start_date} to {end_date}")
    
    try:
        # Get customers from DATABASE only (not Excel!)
        db_customers = Customer.objects.filter(is_deleted=False)
        
        customers = {}
        
        # GROUP DATABASE CUSTOMERS BY NAME (like BSNL with multiple networks)
        from collections import defaultdict
        customer_groups = defaultdict(list)
        
        for customer in db_customers:
            customer_groups[customer.name].append(customer)
        
        # Apply date filtering if provided
        filter_start_month = None
        filter_end_month = None
        if start_date and end_date:
            try:
                filter_start_month = datetime.strptime(start_date, '%Y-%m-%d').month
                filter_end_month = datetime.strptime(end_date, '%Y-%m-%d').month
                print(f"📅 Applying filter: months {filter_start_month} to {filter_end_month}")
            except ValueError:
                print(f"⚠️ Invalid date format: {start_date} to {end_date}")
        
        for customer_name, customer_networks in customer_groups.items():
            # If single network, treat as individual
            if len(customer_networks) == 1:
                customer = customer_networks[0]
                # Create months array from database monthly_runs
                months = ["-"] * 12
                total_runs_count = customer.total_runs or 0
                
                # Process monthly runs from database
                if customer.monthly_runs:
                    for month_key, date_value in customer.monthly_runs.items():
                        try:
                            # Parse month from key like "2025-01" or "2025-10"
                            if '-' in month_key and len(month_key.split('-')) >= 2:
                                month_num = int(month_key.split('-')[1])
                                if 1 <= month_num <= 12:
                                    # Format date for display
                                    if date_value and str(date_value).strip() not in ['-', '', 'None', 'null']:
                                        # Check if it's an actual date or status message
                                        date_str = str(date_value).strip()
                                        if date_str in ['Not Started', 'Not Run', 'No Report']:
                                            # Show status messages as-is
                                            months[month_num - 1] = date_str
                                        else:
                                            try:
                                                # Try to parse as date and format it properly
                                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                # Use DD/MM format and put in CORRECT month column based on date
                                                actual_month_idx = date_obj.month - 1  # Use date's actual month
                                                formatted_date = f"{date_obj.day:02d}/{date_obj.month:02d}"
                                                months[actual_month_idx] = formatted_date
                                                print(f"📅 DATABASE DATE: {date_str} -> {formatted_date} placed in month {actual_month_idx+1} (was key {month_key})")
                                            except ValueError:
                                                # If parsing fails, try DD-MMM conversion first  
                                                print(f"🔍 DATABASE PARSE FAILED: {date_str} (key: {month_key}) -> trying DD-MMM conversion")
                                                converted_date = convert_ddmmm_to_ddmm(date_str)
                                                if converted_date != date_str:
                                                    # Successfully converted - figure out correct month placement
                                                    if '/' in converted_date and len(converted_date.split('/')) == 2:
                                                        try:
                                                            day_part, month_part = converted_date.split('/')
                                                            correct_month_idx = int(month_part) - 1
                                                            months[correct_month_idx] = converted_date
                                                            print(f"📅 CONVERTED & PLACED: {date_str} -> {converted_date} in correct month {correct_month_idx+1}")
                                                        except (ValueError, IndexError):
                                                            months[month_num - 1] = converted_date
                                                            print(f"📅 CONVERTED: {date_str} -> {converted_date} in original month {month_num}")
                                                    else:
                                                        months[month_num - 1] = converted_date
                                                        print(f"📅 CONVERTED SIMPLE: {date_str} -> {converted_date} in month {month_num}")
                                                else:
                                                    months[month_num - 1] = converted_date
                                                    print(f"⚠️ NO CONVERSION: {date_str} placed in month {month_num}")
                                    else:
                                        months[month_num - 1] = '-'
                        except (ValueError, IndexError) as e:
                            print(f"⚠️ Error processing month {month_key}: {e}")
                            continue
                
                # Apply date filtering to months array
                if filter_start_month and filter_end_month:
                    # Clear months outside the filter range
                    for i in range(12):
                        month_num = i + 1
                        if not (filter_start_month <= month_num <= filter_end_month):
                            months[i] = '-'
                    
                    # Check if this customer has any data in the filter range
                    has_data_in_range = any(month != '-' for i, month in enumerate(months) 
                                           if filter_start_month <= (i+1) <= filter_end_month)
                    
                    if not has_data_in_range:
                        print(f"🚫 FILTERING OUT: {customer.name} (no data in range {filter_start_month}-{filter_end_month})")
                        continue  # Skip this customer
                    else:
                        print(f"✅ INCLUDING: {customer.name} (has data in range {filter_start_month}-{filter_end_month})")
                
                # Create network entry from DATABASE ONLY (pure database mode)
                network_key = f"{customer.name}_{customer.network_name}_{customer.id}"
            else:
                # Multiple networks - create grouped customer with networks array
                print(f"📊 Grouping {len(customer_networks)} networks for {customer_name}")
                
                # Calculate combined data for master customer
                combined_runs = sum(net.total_runs or 0 for net in customer_networks)
                combined_nodes = sum(net.node_qty or 0 for net in customer_networks)
                
                # Create combined months array (latest date from any network)
                combined_months = ["-"] * 12
                for customer in customer_networks:
                    if customer.monthly_runs:
                        for month_key, date_value in customer.monthly_runs.items():
                            try:
                                if '-' in month_key and len(month_key.split('-')) >= 2:
                                    month_num = int(month_key.split('-')[1])
                                    if 1 <= month_num <= 12:
                                        if date_value and str(date_value).strip() not in ['-', '', 'None', 'null']:
                                            date_str = str(date_value).strip()
                                            if date_str in ['Not Started', 'Not Run', 'No Report']:
                                                if combined_months[month_num - 1] == '-':
                                                    combined_months[month_num - 1] = date_str
                                            else:
                                                try:
                                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                    # Use DD/MM format and put in CORRECT month column
                                                    actual_month_idx = date_obj.month - 1
                                                    formatted_date = f"{date_obj.day:02d}/{date_obj.month:02d}"
                                                    # Use latest date
                                                    if combined_months[actual_month_idx] == '-':
                                                        combined_months[actual_month_idx] = formatted_date
                                                    else:
                                                        try:
                                                            # Parse DD/MM format for comparison
                                                            current_day, current_month = combined_months[actual_month_idx].split('/')
                                                            current_date = datetime(2025, int(current_month), int(current_day))
                                                            if date_obj > current_date:
                                                                combined_months[actual_month_idx] = formatted_date
                                                        except:
                                                            combined_months[actual_month_idx] = formatted_date
                                                except ValueError:
                                                    # Try DD-MMM conversion first
                                                    converted_date = convert_ddmmm_to_ddmm(date_str)
                                                    if combined_months[month_num - 1] == '-':
                                                        combined_months[month_num - 1] = converted_date
                            except (ValueError, IndexError) as e:
                                continue
                
                # Use first network for master customer info
                main_customer = customer_networks[0]
                network_key = f"{customer_name}_MASTER"
                
                # Apply date filtering to combined months
                if filter_start_month and filter_end_month:
                    # Clear months outside the filter range
                    for i in range(12):
                        month_num = i + 1
                        if not (filter_start_month <= month_num <= filter_end_month):
                            combined_months[i] = '-'
                    
                    # Check if this customer group has any data in the filter range
                    has_data_in_range = any(month != '-' for i, month in enumerate(combined_months) 
                                           if filter_start_month <= (i+1) <= filter_end_month)
                    
                    if not has_data_in_range:
                        print(f"🚫 FILTERING OUT GROUP: {customer_name} (no data in range {filter_start_month}-{filter_end_month})")
                        continue  # Skip this customer group
                    else:
                        print(f"✅ INCLUDING GROUP: {customer_name} (has data in range {filter_start_month}-{filter_end_month})")
                
                months = combined_months
                total_runs_count = combined_runs
                customer = main_customer  # For compatibility below
            
            # Create proper networks array based on single/multiple networks
            if len(customer_networks) == 1:
                # Single network - simple structure
                networks_array = [{
                    'name': customer.network_name or 'Unknown Network',
                    'network_name': customer.network_name or 'Unknown Network', 
                    'runs': total_runs_count,
                    'total_runs': total_runs_count,
                    'node_count': customer.node_qty or 0,
                    'months': months,
                    'monthly_runs': customer.monthly_runs or {},  # Pass original monthly_runs dictionary
                    'network_type': customer.network_type or 'Unknown Network',
                    'country': customer.country,
                    'gtac': customer.gtac,
                    'last_run_date': None,  # Database networks don't have individual last_run_date
                    'ne_type': customer.ne_type
                }]
                networks_count = 1
            else:
                # Multiple networks - create individual network objects
                networks_array = []
                for net_customer in customer_networks:
                    # Create months array for this specific network
                    net_months = ["-"] * 12
                    if net_customer.monthly_runs:
                        for month_key, date_value in net_customer.monthly_runs.items():
                            try:
                                if '-' in month_key and len(month_key.split('-')) >= 2:
                                    month_num = int(month_key.split('-')[1])
                                    if 1 <= month_num <= 12:
                                        if date_value and str(date_value).strip() not in ['-', '', 'None', 'null']:
                                            date_str = str(date_value).strip()
                                            if date_str in ['Not Started', 'Not Run', 'No Report']:
                                                net_months[month_num - 1] = date_str
                                            else:
                                                try:
                                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                    # Use DD/MM format and put in CORRECT month column
                                                    actual_month_idx = date_obj.month - 1
                                                    net_months[actual_month_idx] = f"{date_obj.day:02d}/{date_obj.month:02d}"
                                                except ValueError:
                                                    # Try DD-MMM conversion first
                                                    converted_date = convert_ddmmm_to_ddmm(date_str)
                                                    net_months[month_num - 1] = converted_date
                            except (ValueError, IndexError):
                                continue
                    
                    # Apply date filtering to individual network months
                    if filter_start_month and filter_end_month:
                        for i in range(12):
                            month_num = i + 1
                            if not (filter_start_month <= month_num <= filter_end_month):
                                net_months[i] = '-'
                    
                    networks_array.append({
                        'name': net_customer.network_name or f'Network_{len(networks_array)+1}',
                        'network_name': net_customer.network_name or f'Network_{len(networks_array)+1}',
                        'runs': net_customer.total_runs or 0,
                        'total_runs': net_customer.total_runs or 0,
                        'node_count': net_customer.node_qty or 0,
                        'months': net_months,  # Individual network months
                        'monthly_runs': net_customer.monthly_runs or {},  # Individual network monthly_runs
                        'network_type': net_customer.network_type or 'Database Network',
                        'country': net_customer.country,
                        'gtac': net_customer.gtac,
                        'last_run_date': None,
                        'ne_type': net_customer.ne_type
                    })
                networks_count = len(networks_array)
                print(f"✅ Created {networks_count} individual networks for {customer_name}")
            
            customers[network_key] = {
                # Primary fields that dashboard uses
                'Customer': customer.name,
                'Network': customer.network_name or 'Unknown Network', 
                'Country': customer.country or 'Not Specified',
                'Node Qty': combined_nodes if len(customer_networks) > 1 else (customer.node_qty or 0),
                'NE Type': customer.ne_type or '1830 PSS',
                'gTAC': customer.gtac or 'PSS',
                'total_runs': total_runs_count,
                'months': months,
                
                # Dashboard compatibility fields
                'name': customer.name,
                'network_name': customer.network_name,
                'country': customer.country,
                'node_qty': combined_nodes if len(customer_networks) > 1 else (customer.node_qty or 0),
                'node_count': combined_nodes if len(customer_networks) > 1 else (customer.node_qty or 0),
                'ne_type': customer.ne_type,
                'network_type': customer.ne_type,
                'gtac': customer.gtac,
                'gtac_team': customer.gtac,
                'runs': total_runs_count,
                'run_count': total_runs_count,
                'setup_status': customer.setup_status or 'READY',
                'status': customer.setup_status or 'READY',
                
                # Network structure for dashboard (individual networks)
                'networks': networks_array,
                'networks_count': networks_count,
                
                # DATABASE SOURCE ONLY - No Excel integration
                'excel_only': False,
                'excel_data': False,
                'excel_source': False,
                'data_source': 'database_only',
                'is_database_customer': True,
                'show_excel_symbol': False
            }
        
        return JsonResponse({
            'success': True,
            'customers': customers,
            'total_networks': len(customers),
            'message': f'DATABASE ONLY: Loaded {len(customers)} networks from database (Excel integration disabled)'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to load database customer data'
        }, status=500)

@require_http_methods(["GET"])
def export_dashboard_data(request):
    """
    Export data EXACTLY like dashboard shows - using same API endpoint
    """
    try:
        print(f"📊 Creating export EXACTLY like dashboard live data...")
        
        # Get date filters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(f"📅 Export filters: {start_date} to {end_date}")
        
        # Use SAME data source as dashboard - call the API endpoint directly
        from django.test import RequestFactory
        factory = RequestFactory()
        
        # Create a request object for the dashboard API with exact same parameters
        api_request = factory.get('/api/customer-dashboard/customers/', {
            'start_date': start_date or '',
            'end_date': end_date or ''
        })
        
        # Call the SAME API that dashboard uses
        dashboard_response = api_customer_dashboard_customers(api_request)
        
        if dashboard_response.status_code != 200:
            raise Exception("Failed to get dashboard data")
        
        # Parse the JSON response
        import json
        dashboard_data = json.loads(dashboard_response.content)
        
        if not dashboard_data.get('success') or not dashboard_data.get('customers'):
            raise Exception("No dashboard data available")
        
        customers_data = dashboard_data['customers']
        print(f"📊 Got {len(customers_data)} filtered customers from dashboard API")
        
        # DEBUG: Log first customer's month data to check filter consistency
        if customers_data:
            first_customer = next(iter(customers_data.values()))
            print(f"🔍 DEBUG FIRST CUSTOMER: {first_customer.get('name', 'Unknown')}")
            print(f"🔍 Months: {first_customer.get('months', [])}")
            print(f"🔍 Total runs: {first_customer.get('total_runs', 0)}")
            if first_customer.get('networks'):
                first_network = first_customer['networks'][0]
                print(f"🔍 First network months: {first_network.get('months', [])}")
        
        # DEBUG: Check data sources in dashboard response
        db_customers = [k for k, v in customers_data.items() if v.get('data_source') == 'database_only']
        excel_customers = [k for k, v in customers_data.items() if v.get('excel_source') or v.get('excel_data')]
        print(f"🔍 DEBUG: {len(db_customers)} database customers, {len(excel_customers)} excel customers")
        
        # Create export data in EXACT format as dashboard
        export_rows = []
        
        for customer_key, customer_info in customers_data.items():
            # Handle grouped networks (like BSNL with multiple networks)
            if customer_info.get('networks') and len(customer_info['networks']) > 0:
                # Calculate FILTERED total runs by counting non-empty months in current view
                customer_months = customer_info.get('months', ['-'] * 12)
                filtered_total_runs = sum(1 for month in customer_months if month and month not in ['-', '', 'Not Started', 'Not Run', 'No Report'])
                
                # Customer summary row - EXACT dashboard format with FILTERED total runs
                customer_row = {
                    'Customer': customer_info.get('name', customer_key),
                    'Country': customer_info.get('country', ''),
                    'Networks': f"{len(customer_info['networks'])} NETWORKS" if len(customer_info['networks']) > 1 else "1 NETWORK",
                    'Node Qty': customer_info.get('node_qty', customer_info.get('node_count', 0)),
                    'NE Type': customer_info.get('ne_type', ''),
                    'gTAC': customer_info.get('gtac', ''),
                    'Total Runs': filtered_total_runs  # Use FILTERED count like dashboard
                }
                
                print(f"📊 CUSTOMER {customer_info.get('name', customer_key)}: Filtered Total Runs = {filtered_total_runs} (from months: {customer_months})")
                
                # Add monthly data from customer level - use month numbers and EXACT dashboard dates
                customer_months = customer_info.get('months', ['-'] * 12)
                for i in range(12):
                    month_num = f"{i+1:02d}"  # Use 01, 02, 03... instead of Jan, Feb, Mar...
                    month_value = customer_months[i] if i < len(customer_months) else '-'
                    # Convert DD-MMM format to DD/MM format if needed (like 9-Oct -> 09/10)
                    if month_value and month_value != '-' and month_value not in ['Not Started', 'Not Run', 'No Report']:
                        original_value = month_value
                        converted_value = convert_ddmmm_to_ddmm(month_value)
                        if converted_value != original_value:
                            print(f"📅 CUSTOMER MONTH CONVERTED: {original_value} -> {converted_value} (Customer: {customer_info.get('name', 'Unknown')}, Month: {i+1})")
                        month_value = converted_value
                        
                        # Additional format fix for DD-MM to DD/MM
                        if '-' in month_value and month_value.count('-') == 1:
                            try:
                                day_part, month_part = month_value.split('-')
                                if day_part.isdigit() and month_part.isdigit():
                                    month_value = f"{int(day_part):02d}/{int(month_part):02d}"
                                    print(f"📅 ADDITIONAL FORMAT FIX: {original_value} -> {month_value}")
                            except (ValueError, IndexError):
                                pass
                    customer_row[month_num] = month_value
                
                export_rows.append(customer_row)
                
                # Individual network rows (like dashboard shows)
                for network in customer_info['networks']:
                    # Calculate FILTERED total runs for individual network by counting non-empty months
                    network_months = network.get('months', ['-'] * 12)
                    network_filtered_runs = sum(1 for month in network_months if month and month not in ['-', '', 'Not Started', 'Not Run', 'No Report'])
                    
                    network_row = {
                        'Customer': f"    └─ {network.get('name', 'Unknown Network')}",  # Indented network name
                        'Country': customer_info.get('country', ''),
                        'Networks': f"{network_filtered_runs} runs",  # Use filtered count
                        'Node Qty': network.get('node_count', network.get('node_qty', 0)),
                        'NE Type': network.get('ne_type', ''),
                        'gTAC': network.get('gtac', ''),
                        'Total Runs': network_filtered_runs  # Use FILTERED count like dashboard
                    }
                    
                    print(f"📊 NETWORK {network.get('name', 'Unknown')}: Filtered Runs = {network_filtered_runs} (from months: {network_months})")
                    
                    # Add individual network monthly data - use month numbers and EXACT dashboard dates
                    network_months = network.get('months', ['-'] * 12)
                    for i in range(12):
                        month_num = f"{i+1:02d}"  # Use 01, 02, 03... instead of Jan, Feb, Mar...
                        month_value = network_months[i] if i < len(network_months) else '-'
                        # Convert DD-MMM format to DD/MM format if needed (like 9-Oct -> 09/10)
                        if month_value and month_value != '-' and month_value not in ['Not Started', 'Not Run', 'No Report']:
                            original_value = month_value
                            converted_value = convert_ddmmm_to_ddmm(month_value)
                            if converted_value != original_value:
                                print(f"📅 NETWORK MONTH CONVERTED: {original_value} -> {converted_value} (Network: {network.get('name', 'Unknown')}, Month: {i+1})")
                            month_value = converted_value
                            
                            # Additional format fix for DD-MM to DD/MM  
                            if '-' in month_value and month_value.count('-') == 1:
                                try:
                                    day_part, month_part = month_value.split('-')
                                    if day_part.isdigit() and month_part.isdigit():
                                        month_value = f"{int(day_part):02d}/{int(month_part):02d}"
                                        print(f"📅 NETWORK ADDITIONAL FORMAT FIX: {original_value} -> {month_value}")
                                except (ValueError, IndexError):
                                    pass
                        network_row[month_num] = month_value
                    
                    export_rows.append(network_row)
            
            else:
                # Calculate FILTERED total runs for single customer by counting non-empty months
                customer_months = customer_info.get('months', ['-'] * 12)
                single_filtered_runs = sum(1 for month in customer_months if month and month not in ['-', '', 'Not Started', 'Not Run', 'No Report'])
                
                single_row = {
                    'Customer': customer_info.get('name', customer_key),
                    'Country': customer_info.get('country', ''),
                    'Networks': "1 NETWORK",
                    'Node Qty': customer_info.get('node_qty', customer_info.get('node_count', 0)),
                    'NE Type': customer_info.get('ne_type', ''),
                    'gTAC': customer_info.get('gtac', ''),
                    'Total Runs': single_filtered_runs  # Use FILTERED count like dashboard
                }
                
                print(f"📊 SINGLE {customer_info.get('name', customer_key)}: Filtered Runs = {single_filtered_runs} (from months: {customer_months})")
                
                # Add monthly data - use month numbers and EXACT dashboard dates
                customer_months = customer_info.get('months', ['-'] * 12)
                for i in range(12):
                    month_num = f"{i+1:02d}"  # Use 01, 02, 03... instead of Jan, Feb, Mar...
                    month_value = customer_months[i] if i < len(customer_months) else '-'
                    # Convert DD-MMM format to DD/MM format if needed (like 9-Oct -> 09/10)
                    if month_value and month_value != '-' and month_value not in ['Not Started', 'Not Run', 'No Report']:
                        original_value = month_value
                        converted_value = convert_ddmmm_to_ddmm(month_value)
                        if converted_value != original_value:
                            print(f"📅 SINGLE MONTH CONVERTED: {original_value} -> {converted_value} (Customer: {customer_info.get('name', customer_key)}, Month: {i+1})")
                        month_value = converted_value
                        
                        # Additional format fix for DD-MM to DD/MM
                        if '-' in month_value and month_value.count('-') == 1:
                            try:
                                day_part, month_part = month_value.split('-')
                                if day_part.isdigit() and month_part.isdigit():
                                    month_value = f"{int(day_part):02d}/{int(month_part):02d}"
                                    print(f"📅 SINGLE ADDITIONAL FORMAT FIX: {original_value} -> {month_value}")
                            except (ValueError, IndexError):
                                pass
                    single_row[month_num] = month_value
                
                export_rows.append(single_row)
        
        print(f"✅ Processed {len(export_rows)} rows (matching dashboard exactly)")
        
        # Create Excel export using pandas for better formatting
        import pandas as pd
        from io import BytesIO
        
        # Convert to DataFrame
        df = pd.DataFrame(export_rows)
        
        # Create Excel file in memory
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Dashboard_Data', index=False)
        
        excel_buffer.seek(0)
        
        # Create filename with filter info
        if start_date and end_date:
            filename = f'Dashboard_Data_Filtered_{start_date}_to_{end_date}.xlsx'
            print(f"📅 Creating FILTERED export: {filename}")
        else:
            filename = 'Dashboard_Data_Complete.xlsx'
            print(f"📊 Creating COMPLETE export: {filename}")
        
        # Create Excel response
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        print(f"✅ Dashboard-matching Excel export created: {filename} with {len(export_rows)} rows")
        return response
        
    except Exception as e:
        print(f"❌ Error creating dashboard export: {e}")
        return HttpResponse(f'Error creating export: {str(e)}', status=500)

@require_http_methods(["GET"])
def export_complete_data_with_excel(request):
    """
    Export COMPLETE data including both Database and Excel migrated data
    """
    try:
        print(f"📊 Creating COMPLETE export with DB + Excel migrated data...")
        
        excel_path = r'c:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx'
        
        # Step 1: Get Database data (same as dashboard)
        from django.test import RequestFactory
        factory = RequestFactory()
        
        # Get database data without filters
        db_request = factory.get('/api/customer-dashboard/customers/')
        db_response = api_customer_dashboard_customers(db_request)
        
        if db_response.status_code != 200:
            raise Exception("Failed to get database data")
        
        db_data = json.loads(db_response.content)
        db_customers = db_data.get('customers', {})
        print(f"📊 Got {len(db_customers)} database customers")
        
        # Step 2: Get Excel migrated data
        excel_customers = {}
        if os.path.exists(excel_path):
            try:
                print(f"📁 Reading Excel migrated data from {excel_path}")
                df = pd.read_excel(excel_path, sheet_name='Summary')
                
                # Process column names
                new_columns = []
                for col in df.columns:
                    if isinstance(col, str):
                        new_columns.append(col.strip())
                    else:
                        new_columns.append(col)
                df.columns = new_columns
                
                print(f"📁 Excel data loaded: {len(df)} rows")
                
                # Process Excel data
                for index, row in df.iterrows():
                    customer_name = row.get('Customer', 'Unknown')
                    network_name = row.get('Network', 'Unknown')
                    
                    # Skip if this customer already exists in database (avoid duplicates)
                    if customer_name in db_customers:
                        continue
                    
                    # Create months array from Excel datetime columns
                    months = ["-"] * 12
                    total_runs_count = 0
                    
                    for col_name in df.columns:
                        if isinstance(col_name, datetime):
                            col_value = row[col_name]
                            month_index = col_name.month - 1
                            
                            if pd.notna(col_value):
                                string_value = str(col_value).strip()
                                
                                # Convert DD-MMM format to DD/MM format
                                converted_date = convert_ddmmm_to_ddmm(string_value)
                                
                                if converted_date and converted_date != string_value:
                                    # Successfully converted - place in correct month
                                    if '/' in converted_date:
                                        try:
                                            day_part, month_part = converted_date.split('/')
                                            actual_month_idx = int(month_part) - 1
                                            months[actual_month_idx] = converted_date
                                            total_runs_count += 1
                                            print(f"📅 EXCEL CONVERTED: {string_value} -> {converted_date} for {customer_name}")
                                        except (ValueError, IndexError):
                                            months[month_index] = converted_date
                                            total_runs_count += 1
                                    else:
                                        months[month_index] = converted_date
                                        if converted_date not in ['-', 'Not Started', 'Not Run', 'No Report']:
                                            total_runs_count += 1
                    
                    # Add Excel customer to export data
                    excel_key = f"{customer_name}_{network_name}_EXCEL"
                    excel_customers[excel_key] = {
                        'name': customer_name,
                        'network_name': network_name,
                        'country': row.get('Country', ''),
                        'node_qty': row.get('Node Qty', 0),
                        'ne_type': row.get('NE Type', ''),
                        'gtac': row.get('gTAC', ''),
                        'total_runs': total_runs_count,
                        'months': months,
                        'data_source': 'excel_migrated'
                    }
                
                print(f"📁 Processed {len(excel_customers)} Excel migrated customers")
                
            except Exception as excel_error:
                print(f"⚠️ Error reading Excel data: {excel_error}")
                excel_customers = {}
        
        # Step 3: Combine data and create export
        export_rows = []
        all_customers = {**db_customers, **excel_customers}
        
        print(f"📊 Total customers for export: {len(all_customers)} (DB: {len(db_customers)}, Excel: {len(excel_customers)})")
        
        for customer_key, customer_info in all_customers.items():
            # Determine data source for labeling
            data_source_label = "[Excel]" if customer_info.get('data_source') == 'excel_migrated' else "[DB]"
            
            # Handle grouped networks vs single customers
            if customer_info.get('networks') and len(customer_info['networks']) > 0:
                # Database customer with networks
                customer_row = {
                    'Customer': f"{customer_info.get('name', customer_key)} {data_source_label}",
                    'Country': customer_info.get('country', ''),
                    'Networks': f"{len(customer_info['networks'])} NETWORKS",
                    'Node Qty': customer_info.get('node_qty', 0),
                    'NE Type': customer_info.get('ne_type', ''),
                    'gTAC': customer_info.get('gtac', ''),
                    'Total Runs': customer_info.get('total_runs', 0)
                }
                
                # Add monthly data
                customer_months = customer_info.get('months', ['-'] * 12)
                for i in range(12):
                    month_num = f"{i+1:02d}"
                    month_value = customer_months[i] if i < len(customer_months) else '-'
                    # Apply date conversion
                    if month_value and month_value not in ['-', 'Not Started', 'Not Run', 'No Report']:
                        converted_value = convert_ddmmm_to_ddmm(month_value)
                        month_value = converted_value
                    customer_row[month_num] = month_value
                
                export_rows.append(customer_row)
                
                # Individual network rows
                for network in customer_info['networks']:
                    network_row = {
                        'Customer': f"    └─ {network.get('name', 'Unknown Network')}",
                        'Country': customer_info.get('country', ''),
                        'Networks': f"{network.get('runs', 0)} runs",
                        'Node Qty': network.get('node_count', 0),
                        'NE Type': network.get('ne_type', ''),
                        'gTAC': network.get('gtac', ''),
                        'Total Runs': network.get('total_runs', 0)
                    }
                    
                    # Add network monthly data
                    network_months = network.get('months', ['-'] * 12)
                    for i in range(12):
                        month_num = f"{i+1:02d}"
                        month_value = network_months[i] if i < len(network_months) else '-'
                        if month_value and month_value not in ['-', 'Not Started', 'Not Run', 'No Report']:
                            converted_value = convert_ddmmm_to_ddmm(month_value)
                            month_value = converted_value
                        network_row[month_num] = month_value
                    
                    export_rows.append(network_row)
            
            else:
                # Single customer (Excel migrated or single DB network)
                single_row = {
                    'Customer': f"{customer_info.get('name', customer_key)} {data_source_label}",
                    'Country': customer_info.get('country', ''),
                    'Networks': "1 NETWORK",
                    'Node Qty': customer_info.get('node_qty', 0),
                    'NE Type': customer_info.get('ne_type', ''),
                    'gTAC': customer_info.get('gtac', ''),
                    'Total Runs': customer_info.get('total_runs', 0)
                }
                
                # Add monthly data
                customer_months = customer_info.get('months', ['-'] * 12)
                for i in range(12):
                    month_num = f"{i+1:02d}"
                    month_value = customer_months[i] if i < len(customer_months) else '-'
                    # Apply date conversion
                    if month_value and month_value not in ['-', 'Not Started', 'Not Run', 'No Report']:
                        converted_value = convert_ddmmm_to_ddmm(month_value)
                        month_value = converted_value
                    single_row[month_num] = month_value
                
                export_rows.append(single_row)
        
        print(f"✅ Processed {len(export_rows)} rows for complete export")
        
        # Create Excel export
        import pandas as pd
        from io import BytesIO
        
        df = pd.DataFrame(export_rows)
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Complete_Data', index=False)
        
        excel_buffer.seek(0)
        
        # Create filename
        filename = f'Complete_Data_DB_and_Excel_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        print(f"✅ Complete export created: {filename} with {len(export_rows)} rows")
        return response
        
    except Exception as e:
        print(f"❌ Error creating complete export: {e}")
        return HttpResponse(f'Error creating complete export: {str(e)}', status=500)

@require_http_methods(["GET", "POST"])
def customer_dashboard_excel(request):
    """
    Handle both template rendering (GET), API data (POST/AJAX), and Excel file download
    """
    excel_path = r'c:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx'
    
    # PRIORITY: Check if this is a download request FIRST
    print(f"📥 Request parameters: {dict(request.GET)}")
    if 'download' in request.GET or 'format' in request.GET:
        print("📥 DOWNLOAD REQUEST DETECTED - REDIRECTING TO DASHBOARD API!")
        
        # ALWAYS use DASHBOARD API for ALL downloads (filtered or complete)
        print(f"📊 FORCING DASHBOARD API for ALL downloads (no Excel file processing)")
        
        # Call the same export function that dashboard uses
        return export_dashboard_data(request)
    
    try:
        # Read Excel file from Summary sheet (not MAIN sheet)
        df = pd.read_excel(excel_path, sheet_name='Summary')
        print(f"📊 Loaded Summary sheet with columns: {list(df.columns)}")
        
        # Don't strip column names if they are datetime objects
        # Only strip string column names
        new_columns = []
        for col in df.columns:
            if isinstance(col, str):
                new_columns.append(col.strip())
            else:
                new_columns.append(col)  # Keep datetime columns as-is
        df.columns = new_columns
        print(f"📊 Processed columns: {len([c for c in df.columns if isinstance(c, datetime)])} datetime columns found")
        
        # Don't convert to dict yet - work with DataFrame directly to avoid column issues
        
        # Debug: Show DataFrame structure
        if len(df) > 0:
            print(f"📋 DataFrame shape: {df.shape}")
            print(f"📋 Sample column types:")
            datetime_columns = []
            for col in df.columns:
                if isinstance(col, datetime):
                    datetime_columns.append(col.strftime('%Y-%m'))
                print(f"   {repr(col)} ({type(col).__name__})")
            print(f"📅 Found {len(datetime_columns)} datetime columns")
        
        print(f"📊 Processing {len(df)} rows from Summary sheet...")
        
        # Create Excel-based data structure using DataFrame iteration
        excel_customers = {}
        
        # Get date filters for filtering (same as get_excel_summary_data)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(f"📅 Main Excel API called with filters: {start_date} to {end_date}")
        
        for index, row in df.iterrows():
            # Use Summary sheet column names - row is now a pandas Series
            customer_name = row['Customer'] if 'Customer' in row else 'Unknown'
            network_name = row['Network'] if 'Network' in row else 'Unknown'
            node_qty = row['Node Qty'] if 'Node Qty' in row else 0
            gtac_team = row['gTAC'] if 'gTAC' in row else ''
            country = row['Country'] if 'Country' in row else ''
            nw_type = row['NE Type'] if 'NE Type' in row else ''
            
            if network_name and network_name.strip():
                # Create months array by checking Excel date columns
                months = ["-"] * 12  # Initialize all months as "-"
                total_runs_count = 0  # Count actual runs for this customer/network
                
                # Process Excel date columns (2024 and 2025 datetime columns)
                print(f"📊 Processing date columns for {network_name}")
                
                # FIXED: Simple datetime processing
                datetime_cols_found = 0
                
                for col_name in df.columns:
                    if isinstance(col_name, datetime):
                        datetime_cols_found += 1
                        col_value = row[col_name]
                        month_index = col_name.month - 1
                        col_year = col_name.year
                        
                        # Process if there's actual date data
                        if pd.notna(col_value):
                            # Convert everything to string first, then process
                            string_value = str(col_value).strip()
                            
                            # Fix common Excel typos FIRST
                            if string_value == 'Not Starte':
                                string_value = 'Not Started'
                            elif string_value == 'No Repor':
                                string_value = 'No Report'
                            elif 'Not Starte' in string_value:
                                string_value = string_value.replace('Not Starte', 'Not Started')
                            
                            # Additional typo fixes
                            string_value = string_value.replace('Not Starte', 'Not Started')
                            
                            # FIXED: Only count actual runs (dates), not text entries
                            try:
                                if isinstance(col_value, (datetime, pd.Timestamp)):
                                    # Real date = real run
                                    total_runs_count += 1
                                    formatted_date = f"{col_value.day:02d}/{col_value.month:02d}"
                                    string_value = formatted_date
                                    print(f"📅 REAL RUN: {formatted_date} for month {month_index+1} ({col_name})")
                                elif string_value not in ['Not Started', 'No Report', '-', '', 'nan', 'NaT']:
                                    # Try parsing as date
                                    try:
                                        parsed_date = pd.to_datetime(string_value)
                                        # Successfully parsed date = real run
                                        total_runs_count += 1
                                        string_value = f"{parsed_date.day:02d}/{parsed_date.month:02d}"
                                        print(f"📅 REAL RUN: {string_value} for month {month_index+1} ({col_name})")
                                    except:
                                        # Not a parseable date - check if it's a status or actual data
                                        if string_value not in ['Not Started', 'No Report', 'Pending', 'Planned']:
                                            # Only count if it looks like actual run data
                                            if any(char.isdigit() or char in ['-', '/'] for char in string_value):
                                                # Convert DD-MMM format to DD/MM format
                                                converted_value = convert_ddmmm_to_ddmm(string_value)
                                                if converted_value != string_value:
                                                    string_value = converted_value
                                                    print(f"📝 CONVERTED RUN DATA: {string_value} for month {month_index+1} ({col_name})")
                                                else:
                                                    print(f"📝 RUN DATA: {string_value} for month {month_index+1} ({col_name})")
                                                total_runs_count += 1
                                            else:
                                                print(f"⚪ STATUS TEXT (not counted): {string_value} for month {month_index+1} ({col_name})")
                                        else:
                                            print(f"⚪ STATUS (not counted): {string_value} for month {month_index+1} ({col_name})")
                            except:
                                # Keep as processed string but be more selective about counting
                                if string_value not in ['Not Started', 'No Report', '-', '', 'nan', 'NaT', 'Pending', 'Planned']:
                                    # Only count if it looks like actual data
                                    if any(char.isdigit() or char in ['-', '/'] for char in string_value):
                                        # Convert DD-MMM format to DD/MM format
                                        converted_value = convert_ddmmm_to_ddmm(string_value)
                                        if converted_value != string_value:
                                            string_value = converted_value
                                            print(f"📝 CONVERTED RUN DATA: {string_value} for month {month_index+1} ({col_name})")
                                        else:
                                            print(f"📝 RUN DATA: {string_value} for month {month_index+1} ({col_name})")
                                        total_runs_count += 1
                                    else:
                                        print(f"⚪ TEXT (not counted): {string_value} for month {month_index+1} ({col_name})")
                            
                            # Set the value if it's not empty
                            if string_value and string_value not in ['-', '', 'nan', 'NaT']:
                                # For DD/MM format dates, put in correct month column
                                target_month_idx = month_index  # Default to Excel column month
                                
                                # If it's DD/MM format, use the month from the date
                                if '/' in string_value and len(string_value.split('/')) == 2:
                                    try:
                                        day_part, month_part = string_value.split('/')
                                        date_month = int(month_part)
                                        if 1 <= date_month <= 12:
                                            target_month_idx = date_month - 1  # Use actual month from date
                                    except (ValueError, IndexError):
                                        pass  # Keep original month_index
                                
                                # Always prioritize 2024 data, then 2025
                                if col_year == 2024:
                                    months[target_month_idx] = string_value
                                    print(f"✅ Set 2024 value: {string_value} for month {target_month_idx+1}")
                                elif col_year == 2025 and months[target_month_idx] == '-':
                                    months[target_month_idx] = string_value
                                    print(f"✅ Set 2025 value: {string_value} for month {target_month_idx+1}")
                
                print(f"📊 Processed {datetime_cols_found} datetime cols, found {total_runs_count} runs for {network_name}")
                print(f"📅 Sample months: {months[:6]}...")
                
                # FIXED: Keep actual run count - don't force minimum 1
                # Only count actual dates/runs, not customer existence
                # total_runs_count remains as calculated from actual date data
                
                print(f"📊 Total runs calculated for {network_name}: {total_runs_count}")
                
                # Create monthly_runs dictionary for Excel network (needed for frontend)
                network_monthly_runs = {}
                for i, month_value in enumerate(months):
                    if month_value and month_value != '-':
                        # Create keys in format "2024-MM" for each month that has data
                        month_key = f"2024-{str(i + 1).zfill(2)}"
                        network_monthly_runs[month_key] = month_value
                        print(f"📝 Added to network monthly_runs: {month_key} = {month_value}")
                
                # Apply DATE FILTERING (same logic as get_excel_summary_data)
                if start_date and end_date:
                    try:
                        start_month = datetime.strptime(start_date, '%Y-%m-%d').month
                        end_month = datetime.strptime(end_date, '%Y-%m-%d').month
                        
                        # Check if this customer has valid data in date range
                        has_data_in_range = False
                        for i, month_value in enumerate(months):
                            month_num = i + 1
                            if start_month <= month_num <= end_month:
                                if (month_value and month_value not in ['-', 'Not Started', 'Not Run', 'No Report'] and
                                    month_value not in ['', 'nan', 'NaT']):
                                    has_data_in_range = True
                                    print(f"✅ Month {month_num} ({month_value}) is in range {start_month}-{end_month}")
                                    break
                        
                        if not has_data_in_range:
                            print(f"🚫 FILTERING OUT: {customer_name} -> {network_name} (no data in months {start_month}-{end_month})")
                            continue  # Skip this customer - DON'T ADD TO excel_customers
                        else:
                            print(f"✅ INCLUDING: {customer_name} -> {network_name} (has data in months {start_month}-{end_month})")
                    except Exception as date_error:
                        print(f"Error parsing dates for filtering: {date_error}")
                        # If date parsing fails, include the customer
                        pass
                
                # Use network_name as key but store customer_name inside
                excel_customers[network_name] = {
                    # Summary sheet column mappings (exact field names)
                    "Customer": str(customer_name).strip() if customer_name else '',
                    "Network": str(network_name).strip() if network_name else '',
                    "Node Qty": int(node_qty) if pd.notna(node_qty) else 0,
                    "gTAC": str(gtac_team).strip() if gtac_team else '',
                    "Country": str(country).strip() if country else '',
                    "NE Type": str(nw_type).strip() if nw_type else '',
                    
                    # Additional computed fields for UI compatibility
                    "name": str(customer_name).strip() if customer_name else '',
                    "network_name": str(network_name).strip() if network_name else '',
                    "country": str(country).strip() if country else '',
                    "node_qty": int(node_qty) if pd.notna(node_qty) else 0,
                    "ne_type": str(nw_type).strip() if nw_type else '',
                    "gtac": str(gtac_team).strip() if gtac_team else '',
                    "runs": total_runs_count,
                    "run_count": total_runs_count,
                    "months": [month.replace('Not Starte', 'Not Started') if isinstance(month, str) else month for month in months],
                    "total_runs": total_runs_count,
                    
                    # CRITICAL: Add networks structure for dashboard (same as database customers)
                    "networks": [{
                        "name": str(network_name).strip() if network_name else '',
                        "network_name": str(network_name).strip() if network_name else '',
                        "runs": total_runs_count,
                        "total_runs": total_runs_count,
                        "node_count": int(node_qty) if pd.notna(node_qty) else 0,
                        "months": [month.replace('Not Starte', 'Not Started') if isinstance(month, str) else month for month in months],
                        "monthly_runs": network_monthly_runs,  # Use dictionary format for network-specific dates
                        "country": str(country).strip() if country else '',
                        "gtac": str(gtac_team).strip() if gtac_team else '',
                        "ne_type": str(nw_type).strip() if nw_type else '',
                        "network_type": str(nw_type).strip() if nw_type else '',
                        "last_run_date": None  # Excel networks don't have individual last_run_date
                    }],
                    "networks_count": 1,
                    
                    # Excel source markers
                    "excel_only": True,
                    "excel_data": True,
                    "excel_source": True,
                    "migrated_excel_data": True,
                    "data_source": "excel",
                    "is_database_customer": False,
                    "show_excel_symbol": True,
                    
                    # Raw Excel row for complete access
                    "excel_row": row.to_dict()
                }
                
                print(f"✅ Added customer: {customer_name} -> {network_name} with months: {months[:6]}...")
        
        # If this is an AJAX request or POST, return JSON
        if request.headers.get('Content-Type') == 'application/json' or request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'status': 'success',
                'customers': excel_customers,  # Use Excel-based format with exact column names
                'total_customers': len(excel_customers),
                'total_networks': len(excel_customers),
                'excel_columns': list(df.columns.tolist()) if not df.empty else [],  # Available Excel columns
                'raw_data': df.head().to_dict(orient='records') if len(df) > 0 else []  # Sample Excel rows
            })
        
        # Otherwise render template
        return render(request, 'customer_dasboard_excel.html', {
            'customers': list(excel_customers.values()),
            'customer_count': len(excel_customers)
        })
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        
        if request.headers.get('Content-Type') == 'application/json' or request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': str(e),
                'customers': {},
                'total_customers': 0
            })
        
        return render(request, 'customer_dasboard_excel.html', {
            'customers': [],
            'customer_count': 0,
            'error': str(e)
        })

# SEPARATE VIEW FOR HTML PAGE (No API logic, just render template)
def customer_dashboard_excel_page(request):
    """
    Simple view to render the Excel dashboard HTML page.
    The actual data loading is handled by JavaScript AJAX calls.
    """
    return render(request, 'customer_dasboard_excel.html', {
        'page_title': 'Excel Customer Dashboard',
        'auto_load_data': True
    })

def test_excel_dashboard(request):
    """
    Test page with clean simple JavaScript
    """
    return render(request, 'customer_test.html')


def unified_customer_dashboard(request):
    """
    Unified customer dashboard showing both Database customers and Excel customers
    """
    try:
        # Get Database customers (dummy data)
        database_customers = []
        try:
            # Import database models
            from HealthCheck_app.models import Customer, HealthCheckSession
            from django.db.models import Count, Max, Q
            from datetime import datetime, timedelta
            
            # Get database customers with their stats
            db_customers = Customer.objects.filter(is_deleted=False)
            
            for customer in db_customers:
                # Get session statistics for this customer
                total_sessions = HealthCheckSession.objects.filter(customer=customer).count()
                completed_sessions = HealthCheckSession.objects.filter(
                    customer=customer, status='COMPLETED'
                ).count()
                last_session = HealthCheckSession.objects.filter(
                    customer=customer
                ).order_by('-created_at').first()
                
                database_customers.append({
                    'name': customer.display_name,
                    'network': customer.network_name or 'Default',
                    'source': 'database',
                    'node_qty': 'N/A',
                    'country': 'N/A',
                    'gtac': 'N/A',
                    'ne_type': 'N/A',
                    'runs': total_sessions,
                    'trackers': completed_sessions,
                    'last_run': last_session.created_at if last_session else None,
                    'status': customer.setup_status,
                    'months': ['-'] * 12  # Default empty months
                })
        except ImportError as e:
            print(f"Database models not available: {e}")
        
        # Get Excel customers (real data)
        excel_customers = []
        try:
            excel_path = r'c:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx'
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path, sheet_name='Summary')
                
                # Clean column names
                new_columns = []
                for col in df.columns:
                    if isinstance(col, str):
                        new_columns.append(col.strip())
                    else:
                        new_columns.append(col)
                df.columns = new_columns
                
                # Process Excel data
                for index, row in df.iterrows():
                    customer_name = row.get('Customer', 'Unknown')
                    network_name = row.get('Network', 'Unknown')
                    
                    if network_name and str(network_name).strip() not in ['nan', '', 'Unknown']:
                        # Process months from datetime columns
                        months = ['-'] * 12
                        total_runs = 0
                        
                        for col_name in df.columns:
                            if isinstance(col_name, datetime):
                                col_value = row[col_name]
                                if pd.notna(col_value):
                                    month_idx = col_name.month - 1
                                    if 0 <= month_idx < 12:
                                        value_str = str(col_value).strip()
                                        
                                        if value_str not in ['nan', '-', '', 'Not Started', 'No Report', 'Not Starte', 'No Repor']:
                                            if isinstance(col_value, (datetime, pd.Timestamp)):
                                                months[month_idx] = f"{col_value.day:02d}/{col_value.month:02d}"
                                                total_runs += 1
                                            else:
                                                # Fix common Excel typos
                                                if value_str == 'Not Starte':
                                                    value_str = 'Not Started'
                                                elif value_str == 'No Repor':
                                                    value_str = 'No Report'
                                                
                                                if value_str not in ['Not Started', 'No Report']:
                                                    # Convert DD-MMM format to DD/MM
                                                    converted_value = convert_ddmmm_to_ddmm(value_str)
                                                    # Place in correct month column
                                                    target_month_idx = month_idx
                                                    if '/' in converted_value and len(converted_value.split('/')) == 2:
                                                        try:
                                                            day_part, month_part = converted_value.split('/')
                                                            date_month = int(month_part)
                                                            if 1 <= date_month <= 12:
                                                                target_month_idx = date_month - 1
                                                        except (ValueError, IndexError):
                                                            pass
                                                    months[target_month_idx] = converted_value
                                                    total_runs += 1
                                                else:
                                                    months[month_idx] = value_str
                        
                        excel_customers.append({
                            'name': str(customer_name).strip(),
                            'network': str(network_name).strip(),
                            'source': 'excel',
                            'node_qty': int(row.get('Node Qty', 0)) if pd.notna(row.get('Node Qty', 0)) else 0,
                            'country': str(row.get('Country', '')).strip(),
                            'gtac': str(row.get('gTAC', '')).strip(),
                            'ne_type': str(row.get('NE Type', '')).strip(),
                            'runs': total_runs,  # Actual runs count, no artificial minimum
                            'trackers': total_runs,
                            'last_run': None,  # Excel doesn't have timestamp info
                            'status': 'Active',
                            'months': months
                        })
        except Exception as excel_error:
            print(f"Excel processing error: {excel_error}")
        
        # Combine both sources
        all_customers = database_customers + excel_customers
        
        context = {
            'all_customers': all_customers,
            'database_customers': database_customers,
            'excel_customers': excel_customers,
            'total_customers': len(all_customers),
            'database_count': len(database_customers),
            'excel_count': len(excel_customers)
        }
        
        return render(request, 'customer_dashboard_unified.html', context)
        
    except Exception as e:
        print(f"Error in unified_customer_dashboard: {e}")
        return render(request, 'customer_dashboard_unified.html', {
            'all_customers': [],
            'error': str(e)
        })

# =============================================================================
# API FUNCTIONS FOR CUSTOMER DASHBOARD
# =============================================================================

@require_http_methods(["GET", "POST"])
def api_customer_dashboard_customers(request):
    """
    API endpoint for customer dashboard data - Uses database data with proper filtering
    """
    # Use the database function that already has filtering support
    return get_excel_summary_data(request)

@require_http_methods(["GET", "POST"])
def api_customer_dashboard_statistics(request):
    """
    API endpoint for dashboard statistics
    """
    try:
        customers = Customer.objects.filter(is_deleted=False)
        
        # Calculate statistics
        total_customers = customers.count()
        total_runs = sum(customer.total_runs or 0 for customer in customers)
        total_networks = customers.count()  # Each customer entry is one network
        
        # Calculate monthly breakdown
        monthly_stats = {}
        current_year = datetime.now().year
        
        for month in range(1, 13):
            month_key = f"{current_year}-{month:02d}"
            runs_this_month = 0
            
            for customer in customers:
                if customer.monthly_runs and month_key in customer.monthly_runs:
                    if customer.monthly_runs[month_key] and customer.monthly_runs[month_key] != '-':
                        runs_this_month += 1
            
            monthly_stats[month] = runs_this_month
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_customers': total_customers,
                'total_runs': total_runs,
                'total_networks': total_networks,
                'total_trackers': total_networks,  # Same as networks for this case
                'monthly_breakdown': monthly_stats,
                'active_customers': total_customers,
                'data_source': 'database_migrated'
            }
        })
        
    except Exception as e:
        print(f"❌ API Error in api_customer_dashboard_statistics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_customer_dashboard_export(request):
    """
    API endpoint for dashboard data export
    """
    try:
        customers = Customer.objects.filter(is_deleted=False)
        
        # Convert to export format
        export_data = []
        for customer in customers:
            # Format monthly data
            months = ['-'] * 12
            if customer.monthly_runs:
                for month_key, date_str in customer.monthly_runs.items():
                    try:
                        if '-' in month_key:
                            month_num = int(month_key.split('-')[1]) - 1
                            if 0 <= month_num < 12 and date_str and date_str != '-':
                                # Format date for display
                                try:
                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                    months[month_num] = f"{date_obj.day:02d}/{date_obj.month:02d}"
                                except:
                                    months[month_num] = str(date_str)
                    except (ValueError, IndexError):
                        continue
            
            export_data.append({
                'Customer': customer.name,
                'Network': customer.network_name,
                'Country': customer.country or '',
                'Node Qty': customer.node_qty or 0,
                'NE Type': customer.ne_type or '1830 PSS',
                'gTAC': customer.gtac or 'PSS',
                '01': months[0], '02': months[1], '03': months[2],
                '04': months[3], '05': months[4], '06': months[5],
                '07': months[6], '08': months[7], '09': months[8],
                '10': months[9], '11': months[10], '12': months[11],
                'Total Runs': customer.total_runs or 0
            })
        
        return JsonResponse({
            'success': True,
            'export_data': export_data,
            'total_records': len(export_data)
        })
        
    except Exception as e:
        print(f"❌ API Error in api_customer_dashboard_export: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Additional missing API functions
@require_http_methods(["GET", "POST"])
def api_customer_monthly_sessions(request):
    """
    API endpoint for customer monthly session data
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            customer_name = data.get('customer_name')
            year = data.get('year', datetime.now().year)
        else:
            customer_name = request.GET.get('customer_name')
            year = int(request.GET.get('year', datetime.now().year))
        
        if not customer_name:
            return JsonResponse({'success': False, 'error': 'customer_name required'})
        
        # Find customer in database
        try:
            customer = Customer.objects.filter(name=customer_name, is_deleted=False).first()
            if not customer:
                return JsonResponse({
                    'success': False, 
                    'error': f'Customer {customer_name} not found'
                })
            
            # Build monthly sessions response
            monthly_sessions = {}
            latest_run_date = None
            
            if customer.monthly_runs:
                for month_key, date_str in customer.monthly_runs.items():
                    try:
                        if str(year) in month_key and '-' in month_key:
                            month_num = int(month_key.split('-')[1])
                            if 1 <= month_num <= 12:
                                has_data = date_str and date_str != '-'
                                monthly_sessions[str(month_num)] = {
                                    'count': 1 if has_data else 0,
                                    'date': date_str if has_data else '-',
                                    'hasData': has_data
                                }
                                
                                # Track latest date
                                if has_data:
                                    if not latest_run_date or date_str > latest_run_date:
                                        latest_run_date = date_str
                    except (ValueError, IndexError):
                        continue
            
            return JsonResponse({
                'success': True,
                'customer_name': customer_name,
                'monthly_sessions': monthly_sessions,
                'latest_run_date': latest_run_date or 'Never',
                'total_runs': customer.total_runs or 0
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error processing customer data: {str(e)}'
            })
            
    except Exception as e:
        print(f"❌ API Error in api_customer_monthly_sessions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_customer_dashboard_customers_REALTIME(request):
    """
    🚀 REAL-TIME API: This counts actual sessions instead of static data
    Graphs will now always show current data!
    """
    try:
        print("📡 REAL-TIME API called")
        
        customers = Customer.objects.filter(is_deleted=False)
        customer_data = {}
        
        for customer in customers:
            # Count actual sessions for this customer
            sessions = HealthCheckSession.objects.filter(
                customer_id=customer.id,
                status='COMPLETED'
            )
            
            total_runs = sessions.count()
            
            # Calculate monthly runs for last 6 months
            monthly_runs = ['-'] * 12
            monthly_counts = {}
            
            current_date = datetime.now()
            
            # Get last 6 months data
            for i in range(6):
                target_date = current_date - timedelta(days=30*i)
                month_sessions = sessions.filter(
                    created_at__year=target_date.year,
                    created_at__month=target_date.month
                ).count()
                
                month_key = f"{target_date.year}-{target_date.month:02d}"
                monthly_counts[month_key] = month_sessions
                
                # Format for table display
                month_idx = target_date.month - 1
                if month_sessions > 0:
                    monthly_runs[month_idx] = f"{target_date.day:02d}/{target_date.month:02d}"
            
            customer_key = f"{customer.name}_{customer.network_name}_{customer.id}"
            
            customer_data[customer_key] = {
                'name': customer.name,
                'network_name': customer.network_name,
                'country': getattr(customer, 'country', 'Unknown'),
                'node_qty': getattr(customer, 'node_qty', 0),
                'ne_type': getattr(customer, 'ne_type', '1830 PSS'),
                'gtac': getattr(customer, 'gtac', 'PSS'),
                'total_runs': total_runs,  # REAL COUNT FROM SESSIONS
                'months': monthly_runs,
                'monthly_counts': monthly_counts,  # REAL MONTHLY COUNTS
                'networks': [{
                    'name': customer.network_name,
                    'network_name': customer.network_name,
                    'runs': total_runs,
                    'total_runs': total_runs,
                    'months': monthly_runs,
                    'monthly_counts': monthly_counts,
                    'country': getattr(customer, 'country', 'Unknown'),
                    'node_count': getattr(customer, 'node_qty', 0),
                    'gtac': getattr(customer, 'gtac', 'PSS')
                }],
                'networks_count': 1,
                'data_source': 'real_time_sessions',
                'last_updated': datetime.now().isoformat()
            }
        
        print(f"✅ REAL-TIME API: Returning {len(customer_data)} customers")
        
        return JsonResponse({
            'success': True,
            'customers': customer_data,
            'total_customers': len(customer_data),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'real_time_sessions'
        })
        
    except Exception as e:
        print(f"❌ REAL-TIME API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET", "POST"])
def api_customer_monthly_sessions(request):
    """
    API endpoint for network session data
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            network_id = data.get('network_id')
        else:
            network_id = request.GET.get('network_id')
        
        if not network_id:
            return JsonResponse({'success': False, 'error': 'network_id required'})
        
        # Find customer/network by ID
        try:
            customer = Customer.objects.filter(id=network_id, is_deleted=False).first()
            if not customer:
                return JsonResponse({
                    'success': False,
                    'error': f'Network with ID {network_id} not found'
                })
            
            # Build sessions response
            sessions = []
            monthly_sessions = {}
            latest_session_date = None
            
            if customer.monthly_runs:
                for month_key, date_str in customer.monthly_runs.items():
                    try:
                        if '-' in month_key and date_str and date_str != '-':
                            month_num = int(month_key.split('-')[1])
                            if 1 <= month_num <= 12:
                                sessions.append({
                                    'id': f"{customer.id}_{month_key}",
                                    'network_id': customer.id,
                                    'created_at': date_str,
                                    'date': date_str,
                                    'status': 'COMPLETED'
                                })
                                
                                monthly_sessions[str(month_num)] = {
                                    'count': 1,
                                    'date': date_str
                                }
                                
                                if not latest_session_date or date_str > latest_session_date:
                                    latest_session_date = date_str
                    except (ValueError, IndexError):
                        continue
            
            return JsonResponse({
                'success': True,
                'network_id': network_id,
                'sessions': sessions,
                'monthly_sessions': monthly_sessions,
                'latest_session_date': latest_session_date,
                'total_sessions': len(sessions)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error processing network data: {str(e)}'
            })
            
    except Exception as e:
        print(f"❌ API Error in api_network_sessions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Additional API functions that may be called by frontend
@require_http_methods(["GET"])
def get_networks_for_customer(request, customer_name):
    """
    API endpoint to get networks for a specific customer
    """
    try:
        # Find customers with this name
        customers = Customer.objects.filter(name=customer_name, is_deleted=False)
        
        networks = []
        for customer in customers:
            networks.append({
                'id': customer.id,
                'name': customer.network_name or 'Default Network',
                'network_name': customer.network_name or 'Default Network',
                'customer_name': customer.name,
                'total_runs': customer.total_runs or 0,
                'country': customer.country,
                'node_count': customer.node_qty or 0,
                'gtac': customer.gtac
            })
        
        return JsonResponse({
            'success': True,
            'networks': networks,
            'total_networks': len(networks)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_dashboard_customers(request):
    """
    General dashboard customers API (fallback)
    """
    # Just redirect to customer dashboard API
    return api_customer_dashboard_customers(request)

@require_http_methods(["GET"])
def api_dashboard_statistics(request):
    """
    General dashboard statistics API (fallback)
    """
    # Just redirect to customer dashboard statistics API
    return api_customer_dashboard_statistics(request)

@require_http_methods(["GET"])
def api_export_excel(request):
    """
    API endpoint for Excel export - Uses SAME data as dashboard
    """
    print(f"📥 Export request received with params: {dict(request.GET)}")
    return export_dashboard_data(request)

@require_http_methods(["GET"])
def customer_dashboard(request):
    """
    Render the main customer dashboard page with database data
    """
    try:
        # Get customers from database
        customers = Customer.objects.filter(is_deleted=False)
        
        # Calculate basic statistics for initial page load
        total_customers = customers.count()
        total_runs = sum(customer.total_runs or 0 for customer in customers)
        total_networks = customers.count()
        
        # Get sample customer data for debugging
        sample_customers = []
        for customer in customers[:5]:  # First 5 customers
            # Format monthly data for JavaScript
            monthly_runs_js = []
            if customer.monthly_runs:
                for month in range(1, 13):
                    month_key = f"2025-{month:02d}"
                    if month_key in customer.monthly_runs and customer.monthly_runs[month_key] != '-':
                        monthly_runs_js.append(1)
                    else:
                        monthly_runs_js.append(0)
            else:
                monthly_runs_js = [0] * 12
                
            sample_customers.append({
                'name': customer.name,
                'network_name': customer.network_name,
                'total_runs': customer.total_runs or 0,
                'country': customer.country or 'Unknown',
                'node_qty': customer.node_qty or 0,
                'monthly_runs': monthly_runs_js
            })
        
        print(f"📊 Customer Dashboard: Passing {total_customers} customers to frontend")
        print(f"📈 Total runs in database: {total_runs}")
        
        # Convert sample_customers to JSON for template
        import json
        sample_customers_json = json.dumps(sample_customers)
        
        return render(request, 'customer_dashboard.html', {
            'page_title': 'Customer Health Check Dashboard',
            'dashboard_type': 'database_integrated',
            'initial_stats': {
                'total_customers': total_customers,
                'total_runs': total_runs,
                'total_networks': total_networks
            },
            'sample_customers': sample_customers_json,
            'has_database_data': True,
            'database_loaded': True
        })
        
    except Exception as e:
        print(f"❌ Error in customer_dashboard: {e}")
        return render(request, 'customer_dashboard.html', {
            'page_title': 'Customer Health Check Dashboard',
            'dashboard_type': 'database_integrated',
            'error': str(e),
            'has_database_data': False,
            'database_loaded': False
        })

@csrf_exempt
@require_http_methods(["POST"])
def update_customer_network(request):
    """
    API endpoint to update customer network data from Live DB editor
    Updates both monthly_runs and total_runs in database
    """
    try:
        # Parse JSON request
        import json
        data = json.loads(request.body)
        
        customer_name = data.get('customer_name')
        network_name = data.get('network_name')
        monthly_runs = data.get('monthly_runs', [])
        total_runs = data.get('total_runs', 0)
        
        print(f"💾 API: Update request for {customer_name} - {network_name}: {total_runs} runs")
        
        if not customer_name or not network_name:
            return JsonResponse({
                'success': False,
                'error': 'Missing customer_name or network_name'
            }, status=400)
        
        # Find the customer network in database
        customers = Customer.objects.filter(
            name=customer_name,
            is_deleted=False
        )
        
        if not customers.exists():
            return JsonResponse({
                'success': False,
                'error': f'Customer {customer_name} not found'
            }, status=404)
        
        # Find the specific network
        target_customer = None
        for customer in customers:
            # Check if this customer's network matches
            if (customer.network_name == network_name or 
                network_name in str(customer.network_name or '') or
                customer.network_name in str(network_name)):
                target_customer = customer
                break
        
        if not target_customer:
            # Try to find by partial match
            for customer in customers:
                clean_network_name = network_name.replace(customer_name, '').strip(' -_')
                if (clean_network_name in str(customer.network_name or '') or
                    str(customer.network_name or '') in clean_network_name):
                    target_customer = customer
                    break
        
        if not target_customer:
            return JsonResponse({
                'success': False,
                'error': f'Network {network_name} not found for customer {customer_name}'
            }, status=404)
        
        # Update monthly_runs data
        if not target_customer.monthly_runs:
            target_customer.monthly_runs = {}
        
        # Convert monthly_runs array to database format
        current_year = datetime.now().year
        updated_monthly_runs = target_customer.monthly_runs.copy()
        
        for month_index, month_value in enumerate(monthly_runs):
            if month_value and month_value.strip() not in ['-', '']:
                month_key = f"{current_year}-{month_index + 1:02d}"
                # Store the date value
                if month_value in ['Not Started', 'Not Run', 'No Report']:
                    updated_monthly_runs[month_key] = month_value
                else:
                    # Try to parse and store as proper date
                    try:
                        # If it's a formatted date like "8-Oct", convert to full date
                        if '-' in month_value and len(month_value.split('-')) == 2:
                            day_part, month_part = month_value.split('-')
                            # Convert month abbreviation to number
                            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                            if month_part in month_names:
                                month_num = month_names.index(month_part) + 1
                                formatted_date = f"{current_year}-{month_num:02d}-{int(day_part):02d}"
                                updated_monthly_runs[month_key] = formatted_date
                            else:
                                updated_monthly_runs[month_key] = month_value
                        else:
                            updated_monthly_runs[month_key] = month_value
                    except:
                        updated_monthly_runs[month_key] = month_value
            else:
                # Remove empty months or set to 'Not Started'
                month_key = f"{current_year}-{month_index + 1:02d}"
                if month_key in updated_monthly_runs:
                    updated_monthly_runs[month_key] = 'Not Started'
        
        # Update the customer
        target_customer.monthly_runs = updated_monthly_runs
        target_customer.total_runs = total_runs
        target_customer.save()
        
        print(f"✅ Database updated: {customer_name} - {network_name}: {total_runs} runs")
        print(f"📅 Monthly data: {updated_monthly_runs}")
        
        return JsonResponse({
            'success': True,
            'message': f'Updated {customer_name} - {network_name}',
            'customer_name': customer_name,
            'network_name': network_name,
            'total_runs': total_runs,
            'monthly_runs': updated_monthly_runs
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        print(f"❌ Error updating network: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
