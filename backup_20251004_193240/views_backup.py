import pandas as pd
import json
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from urllib.parse import quote

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
                
                # If filters are applied, create filtered Excel file
                if start_date and end_date:
                    try:
                        # Read the Excel file
                        df = pd.read_excel(excel_path, sheet_name='Summary')
                        
                        # Apply date filtering logic here if needed
                        # For now, return the original file
                        
                        # Create a temporary filtered file
                        response = HttpResponse(
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        response['Content-Disposition'] = f'attachment; filename="{filename}"'
                        
                        # Write filtered data to response
                        with pd.ExcelWriter(response, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Summary', index=False)
                        
                        return response
                    except Exception as filter_error:
                        print(f"Error creating filtered Excel: {filter_error}")
                        # Fall back to original file
                        pass
                
                # Return the original Excel file - SIMPLE METHOD
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
                            
                            # Try to parse as date if it looks like a date
                            try:
                                if isinstance(col_value, (datetime, pd.Timestamp)):
                                    total_runs_count += 1
                                    formatted_date = col_value.strftime('%d-%b')
                                    string_value = formatted_date
                                    print(f"📅 Found date: {formatted_date} for month {month_index+1} ({col_name})")
                                elif string_value not in ['Not Started', 'No Report', '-', '', 'nan', 'NaT']:
                                    # Try parsing as date
                                    try:
                                        parsed_date = pd.to_datetime(string_value)
                                        total_runs_count += 1
                                        string_value = parsed_date.strftime('%d-%b')
                                        print(f"📅 Parsed date: {string_value} for month {month_index+1} ({col_name})")
                                    except:
                                        # Not a date, keep as string
                                        if string_value not in ['Not Started', 'No Report']:
                                            total_runs_count += 1
                                        print(f"📝 Found text: {string_value} for month {month_index+1} ({col_name})")
                            except:
                                # Keep as processed string
                                if string_value not in ['Not Started', 'No Report', '-', '', 'nan', 'NaT']:
                                    total_runs_count += 1
                                print(f"📝 Kept text: {string_value} for month {month_index+1} ({col_name})")
                            
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
                
                # If no runs found, set minimum of 1 (since customer exists in sheet)
                if total_runs_count == 0:
                    total_runs_count = 1
                
                print(f"📊 Total runs calculated for {network_name}: {total_runs_count}")
                
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
                    "network": str(network_name).strip() if network_name else '',
                    "country": str(country).strip() if country else '',
                    "node_qty": int(node_qty) if pd.notna(node_qty) else 0,
                    "ne_type": str(nw_type).strip() if nw_type else '',
                    "gtac": str(gtac_team).strip() if gtac_team else '',
                    "months": [month.replace('Not Starte', 'Not Started') if isinstance(month, str) else month for month in months],
                    "total_runs": total_runs_count,
                    
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
