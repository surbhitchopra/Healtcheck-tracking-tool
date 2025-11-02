import pandas as pd
import json
from datetime import datetime
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
from HealthCheck_app.models import Customer
from django.views.decorators.csrf import csrf_exempt
import json

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
                                                # Try to parse as date and format it
                                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                months[month_num - 1] = date_obj.strftime('%d-%b')
                                            except ValueError:
                                                # If parsing fails, show the raw value
                                                months[month_num - 1] = date_str
                                    else:
                                        months[month_num - 1] = '-'
                        except (ValueError, IndexError) as e:
                            print(f"⚠️ Error processing month {month_key}: {e}")
                            continue
                
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
                                                    formatted_date = date_obj.strftime('%d-%b')
                                                    # Use latest date
                                                    if combined_months[month_num - 1] == '-':
                                                        combined_months[month_num - 1] = formatted_date
                                                    else:
                                                        try:
                                                            current_date = datetime.strptime(combined_months[month_num - 1] + '-25', '%d-%b-%y')
                                                            if date_obj > current_date:
                                                                combined_months[month_num - 1] = formatted_date
                                                        except:
                                                            combined_months[month_num - 1] = formatted_date
                                                except ValueError:
                                                    if combined_months[month_num - 1] == '-':
                                                        combined_months[month_num - 1] = date_str
                            except (ValueError, IndexError) as e:
                                continue
                
                # Use first network for master customer info
                main_customer = customer_networks[0]
                network_key = f"{customer_name}_MASTER"
                
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
                                                    net_months[month_num - 1] = date_obj.strftime('%d-%b')
                                                except ValueError:
                                                    net_months[month_num - 1] = date_str
                            except (ValueError, IndexError):
                                continue
                    
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
    Export DATABASE customers exactly like dashboard API
    """
    try:
        print(f"📊 Creating export from DATABASE (matching dashboard)...")
        
        # Get date filters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Get customers from DATABASE only (same as dashboard API)
        db_customers = Customer.objects.filter(is_deleted=False)
        
        # Create dashboard-style data structure
        dashboard_customers = []
        
        for customer in db_customers:
            # Create months array from database monthly_runs (same as dashboard API)
            months = ["-"] * 12
            total_runs_count = customer.total_runs or 0
            
            # Process monthly runs from database (same logic as dashboard API)
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
                                            # Try to parse as date and format it
                                            from datetime import datetime
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                            months[month_num - 1] = date_obj.strftime('%d-%b')
                                        except ValueError:
                                            # If parsing fails, show the raw value
                                            months[month_num - 1] = date_str
                                else:
                                    months[month_num - 1] = '-'
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ Error processing month {month_key}: {e}")
                        continue
            
            # Apply date filtering if specified (same as dashboard)
            if start_date and end_date:
                print(f"📅 Export: Date filter requested ({start_date} to {end_date}) - temporarily ignoring to show all data")
            
            # Create export entry exactly like dashboard
            dashboard_customer = {
                'Customer': customer.name,
                'Network': customer.network_name or 'Unknown',
                'Country': customer.country or '',
                'Node Qty': customer.node_qty or 0,
                'NE Type': customer.ne_type or '1830 PSS',
                'gTAC': customer.gtac or 'PSS',
                'Total Runs': total_runs_count,
                'Networks': '1 NETWORK'
            }
            
            # Add monthly data (same format as dashboard)
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for i, month_name in enumerate(month_names):
                dashboard_customer[month_name] = months[i]
            
            dashboard_customers.append(dashboard_customer)
        
        print(f"✅ Processed {len(dashboard_customers)} customers (matching dashboard)")
        
        # Create CSV export (working solution)
        csv_rows = []
        
        # Enhanced Header row with more details
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        headers = [
            'Customer', 'Network', 'Country', 'Node Qty', 'NE Type', 'gTAC', 
            'Setup Status', 'Total Runs', 'Data Source'
        ] + month_names
        csv_rows.append(','.join(headers))
        
        # Add data rows
        for customer_data in dashboard_customers:
            row_data = [
                customer_data['Customer'],
                customer_data['Network'],
                customer_data['Country'],
                str(customer_data['Node Qty']),
                customer_data['NE Type'],
                customer_data['gTAC'],
                str(customer_data['Total Runs'])
            ]
            
            # Add monthly data
            for month_name in month_names:
                row_data.append(customer_data.get(month_name, '-'))
            
            # Clean data for CSV (escape commas)
            clean_row = []
            for item in row_data:
                item_str = str(item)
                if ',' in item_str:
                    clean_row.append(f'"{item_str}"')
                else:
                    clean_row.append(item_str)
            
            csv_rows.append(','.join(clean_row))
        
        # Create filename
        if start_date and end_date:
            filename = f'Dashboard_Data_{start_date}_to_{end_date}.csv'
        else:
            filename = 'Dashboard_Data.csv'
        
        # Create CSV response
        response = HttpResponse(
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Write CSV data
        response.write('\n'.join(csv_rows))
        
        print(f"✅ Dashboard-matching Excel export created: {filename}")
        return response
        
    except Exception as e:
        print(f"❌ Error creating dashboard export: {e}")
        return HttpResponse(f'Error creating export: {str(e)}', status=500)

@require_http_methods(["GET", "POST"])
def customer_dashboard_excel(request):
    """
    Handle both template rendering (GET), API data (POST/AJAX), and Excel file download
    """
    excel_path = r'c:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx'
    
    # PRIORITY: Check if this is a download request FIRST
    print(f"📥 Request parameters: {dict(request.GET)}")
    if 'download' in request.GET or 'format' in request.GET:
        print("📥 DOWNLOAD REQUEST DETECTED!")
        try:
            if os.path.exists(excel_path):
                # Get date range filters if any
                start_date = request.GET.get('start_date')
                end_date = request.GET.get('end_date')
                
                # Create filename based on filters
                if start_date and end_date:
                    filename = f'Health_Check_Data_{start_date}_to_{end_date}.xlsx'
                else:
                    filename = 'Health_Check_Data.xlsx'
                
                # Create filtered Excel file that EXACTLY MATCHES DASHBOARD LIVE DATA
                if start_date and end_date:
                    try:
                        print(f"🔄 Creating filtered export matching dashboard live data for {start_date} to {end_date}")
                        
                        # Get Excel data and apply SAME PROCESSING as dashboard
                        df = pd.read_excel(excel_path, sheet_name='Summary')
                        
                        # Process column names
                        new_columns = []
                        for col in df.columns:
                            if isinstance(col, str):
                                new_columns.append(col.strip())
                            else:
                                new_columns.append(col)
                        df.columns = new_columns
                        
                        # Apply SAME FILTERING as dashboard - Block fake entries
                        print(f"🚫 Blocking fake entries like dashboard...")
                        fake_customers = ['He', 'KYUUII', 'OPT_NC', 'subu-east', 'Bsnl']
                        
                        # Remove fake entries from DataFrame
                        for fake_name in fake_customers:
                            df = df[~df['Customer'].str.contains(fake_name, case=False, na=False)]
                        
                        print(f"📊 After blocking fakes: {len(df)} rows remaining")
                        
                        # Apply date filtering and SAME RUN COUNTING logic as dashboard
                        start_month = datetime.strptime(start_date, '%Y-%m-%d').month
                        end_month = datetime.strptime(end_date, '%Y-%m-%d').month
                        
                        print(f"📅 Filtering Excel data for months {start_month} to {end_month}")
                        
                        # Process each row with SAME LOGIC as dashboard
                        rows_to_keep = []
                        for index, row in df.iterrows():
                            # Check if this customer has valid data in date range (same as dashboard logic)
                            has_valid_data_in_range = False
                            
                            for col_name in df.columns:
                                if isinstance(col_name, datetime):
                                    col_month = col_name.month
                                    if start_month <= col_month <= end_month:
                                        col_value = row[col_name]
                                        if pd.notna(col_value):
                                            string_value = str(col_value).strip()
                                            # Same logic as dashboard - check if it's valid data
                                            if (string_value and string_value not in ['-', 'Not Started', 'Not Run', 'No Report', 'Not Starte'] and
                                                string_value not in ['', 'nan', 'NaT']):
                                                has_valid_data_in_range = True
                                                break
                            
                            if has_valid_data_in_range:
                                rows_to_keep.append(index)
                                # Clear data outside date range
                                for col_name in df.columns:
                                    if isinstance(col_name, datetime):
                                        col_month = col_name.month
                                        if not (start_month <= col_month <= end_month):
                                            df.at[index, col_name] = '-'
                        
                        # Keep only rows with valid data in date range
                        df = df.loc[rows_to_keep]
                        print(f"📊 After date filtering: {len(df)} rows with valid data in range")
                        
                        # Create response with filtered data that matches dashboard
                        response = HttpResponse(
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        response['Content-Disposition'] = f'attachment; filename="{filename}"'
                        
                        # Write filtered data to response
                        with pd.ExcelWriter(response, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Summary', index=False)
                        
                        print(f"✅ Dashboard-matching filtered Excel export created with {len(df)} rows")
                        return response
                    except Exception as filter_error:
                        print(f"Error creating filtered Excel: {filter_error}")
                        # Fall back to original file
                        pass
                
                # Return complete Excel file that EXACTLY MATCHES DASHBOARD - ENHANCED METHOD
                try:
                    print(f"📊 Creating complete export that exactly matches dashboard data")
                    
                    # Read and process Excel data (same as dashboard integration)
                    df = pd.read_excel(excel_path, sheet_name='Summary')
                    
                    # Process column names
                    new_columns = []
                    for col in df.columns:
                        if isinstance(col, str):
                            new_columns.append(col.strip())
                        else:
                            new_columns.append(col)
                    df.columns = new_columns
                    
                    # Apply SAME FILTERING as dashboard - Block fake entries that dashboard blocks
                    print(f"🚫 Applying dashboard filters - blocking fake entries...")
                    fake_customers = ['He', 'KYUUII', 'OPT_NC', 'subu-east', 'Bsnl']
                    
                    original_count = len(df)
                    # Remove fake entries from DataFrame (same as dashboard)
                    for fake_name in fake_customers:
                        df = df[~df['Customer'].str.contains(fake_name, case=False, na=False)]
                    
                    filtered_count = len(df)
                    print(f"📊 Dashboard filtering applied: {original_count} -> {filtered_count} rows (blocked {original_count - filtered_count} fake entries)")
                    
                    # Apply SAME DATA PROCESSING as dashboard for run counting
                    print(f"🔄 Applying dashboard run counting logic...")
                    for index, row in df.iterrows():
                        # Fix "Not Starte" to "Not Started" (same as dashboard)
                        for col_name in df.columns:
                            if isinstance(col_name, datetime):
                                col_value = row[col_name]
                                if pd.notna(col_value):
                                    string_value = str(col_value).strip()
                                    if string_value == 'Not Starte':
                                        df.at[index, col_name] = 'Not Started'
                    
                    # Create response with complete dashboard-matching data
                    response = HttpResponse(
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    
                    # Write complete data to response
                    with pd.ExcelWriter(response, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    print(f"✅ Dashboard-matching complete Excel export created with {len(df)} rows")
                    return response
                    
                except Exception as export_error:
                    print(f"Error creating enhanced export: {export_error}")
                    # Fall back to original file method
                    with open(excel_path, 'rb') as excel_file:
                        response = HttpResponse(
                            excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        response['Content-Disposition'] = f'attachment; filename="{filename}"'
                        return response
            else:
                return HttpResponse('Excel file not found', status=404)
        except Exception as e:
            print(f"Error downloading Excel file: {e}")
            return HttpResponse(f'Error downloading file: {str(e)}', status=500)
    
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
                                    formatted_date = col_value.strftime('%d-%b')
                                    string_value = formatted_date
                                    print(f"📅 REAL RUN: {formatted_date} for month {month_index+1} ({col_name})")
                                elif string_value not in ['Not Started', 'No Report', '-', '', 'nan', 'NaT']:
                                    # Try parsing as date
                                    try:
                                        parsed_date = pd.to_datetime(string_value)
                                        # Successfully parsed date = real run
                                        total_runs_count += 1
                                        string_value = parsed_date.strftime('%d-%b')
                                        print(f"📅 REAL RUN: {string_value} for month {month_index+1} ({col_name})")
                                    except:
                                        # Not a parseable date - check if it's a status or actual data
                                        if string_value not in ['Not Started', 'No Report', 'Pending', 'Planned']:
                                            # Only count if it looks like actual run data
                                            if any(char.isdigit() or char in ['-', '/'] for char in string_value):
                                                total_runs_count += 1
                                                print(f"📝 RUN DATA: {string_value} for month {month_index+1} ({col_name})")
                                            else:
                                                print(f"⚪ STATUS TEXT (not counted): {string_value} for month {month_index+1} ({col_name})")
                                        else:
                                            print(f"⚪ STATUS (not counted): {string_value} for month {month_index+1} ({col_name})")
                            except:
                                # Keep as processed string but be more selective about counting
                                if string_value not in ['Not Started', 'No Report', '-', '', 'nan', 'NaT', 'Pending', 'Planned']:
                                    # Only count if it looks like actual data
                                    if any(char.isdigit() or char in ['-', '/'] for char in string_value):
                                        total_runs_count += 1
                                        print(f"📝 RUN DATA: {string_value} for month {month_index+1} ({col_name})")
                                    else:
                                        print(f"⚪ TEXT (not counted): {string_value} for month {month_index+1} ({col_name})")
                            
                            # Set the value if it's not empty
                            if string_value and string_value not in ['-', '', 'nan', 'NaT']:
                                # Always prioritize 2024 data, then 2025
                                if col_year == 2024:
                                    months[month_index] = string_value
                                    print(f"✅ Set 2024 value: {string_value} for month {month_index+1}")
                                elif col_year == 2025 and months[month_index] == '-':
                                    months[month_index] = string_value
                                    print(f"✅ Set 2025 value: {string_value} for month {month_index+1}")
                
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
                                                months[month_idx] = col_value.strftime('%d-%b')
                                                total_runs += 1
                                            else:
                                                # Fix common Excel typos
                                                if value_str == 'Not Starte':
                                                    value_str = 'Not Started'
                                                elif value_str == 'No Repor':
                                                    value_str = 'No Report'
                                                
                                                if value_str not in ['Not Started', 'No Report']:
                                                    months[month_idx] = value_str
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
    API endpoint for customer dashboard data - returns migrated Excel data from database
    """
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
        }, status=500)

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
                                    months[month_num] = date_obj.strftime('%d-%b')
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
                'Jan': months[0], 'Feb': months[1], 'Mar': months[2],
                'Apr': months[3], 'May': months[4], 'Jun': months[5],
                'Jul': months[6], 'Aug': months[7], 'Sep': months[8],
                'Oct': months[9], 'Nov': months[10], 'Dec': months[11],
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

@require_http_methods(["GET", "POST"])
def api_network_sessions(request):
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
