"""
File Routing Fix for Health Check Application
===========================================

This shows the correct way to route files to proper directories:

1. TEC Report (.xlsx) -> Script/input-hc-report/
2. Inventory CSV (.csv) -> Script/input-hc-report/  
3. HC Tracker (.xlsx) -> Script/ (with network name)
4. Ignore files (.txt, .xlsx) -> Script/ (with network name)
"""

# Add this function to your views.py file
def save_uploaded_files_properly(customer, uploaded_files, session):
    """Save uploaded files to correct directories based on file type"""
    import os
    from pathlib import Path
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    SCRIPT_DIR = BASE_DIR / "Script"
    SCRIPT_INPUT_DIR = SCRIPT_DIR / "input-hc-report"
    
    # Ensure directories exist
    os.makedirs(SCRIPT_INPUT_DIR, exist_ok=True)
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    
    files_saved = []
    
    for field_name, file in uploaded_files.items():
        if file:
            # Determine where to save based on file type and content
            if field_name == 'tec_report_file' or 'report' in file.name.lower():
                # TEC Report goes to input-hc-report
                file_path = SCRIPT_INPUT_DIR / file.name
                file_type = 'TEC_REPORT'
                
            elif field_name == 'inventory_csv' or file.name.lower().endswith('.csv'):
                # Inventory CSV goes to input-hc-report
                file_path = SCRIPT_INPUT_DIR / file.name
                file_type = 'INVENTORY_CSV'
                
            elif field_name == 'hc_tracker_file':
                # HC Tracker goes to Script root with network name
                proper_name = f"{customer.name}_HC_Issues_Tracker.xlsx"
                file_path = SCRIPT_DIR / proper_name
                file_type = 'HC_TRACKER'
                
            elif field_name == 'global_ignore_txt':
                # Global ignore goes to Script root with network name
                proper_name = f"{customer.name}_ignored_test_cases.txt"
                file_path = SCRIPT_DIR / proper_name
                file_type = 'GLOBAL_IGNORE_TXT'
                
            elif field_name == 'selective_ignore_xlsx':
                # Selective ignore goes to Script root with network name
                proper_name = f"{customer.name}_ignored_test_cases.xlsx"
                file_path = SCRIPT_DIR / proper_name
                file_type = 'SELECTIVE_IGNORE_XLSX'
                
            else:
                # Default: put in Script root
                file_path = SCRIPT_DIR / file.name
                file_type = 'OTHER'
            
            # Save the file
            try:
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                # Create database record
                from .models import HealthCheckFile
                hc_file = HealthCheckFile.objects.create(
                    customer=customer,
                    session=session,
                    file_type=file_type,
                    original_filename=file.name,
                    stored_filename=file_path.name,
                    file_path=str(file_path),
                    file_size=file.size
                )
                
                files_saved.append({
                    'original_name': file.name,
                    'saved_path': str(file_path),
                    'file_type': file_type,
                    'id': hc_file.id
                })
                
                print(f"✅ Saved {file.name} -> {file_path}")
                
            except Exception as e:
                print(f"❌ Error saving {file.name}: {str(e)}")
                raise e
    
    return files_saved


# Replace your health_check_upload view logic with this:
def health_check_upload_fixed(request, customer_id):
    """Fixed health check file upload with proper file routing"""
    customer = get_object_or_404(Customer, id=customer_id, is_deleted=False)
    
    # Determine form type based on customer setup status
    if customer.setup_status == 'NEW':
        form_class = HealthCheckNewNetworkForm
        template_name = 'health_check/upload_new_network.html'
        files_expected = 5
        session_type = 'NEW_NETWORK_SETUP'
    else:
        form_class = HealthCheckExistingNetworkForm
        template_name = 'health_check/upload_existing_network.html'
        files_expected = 2
        session_type = 'REGULAR_PROCESSING'
        
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            # Create health check session
            import uuid
            session = HealthCheckSession.objects.create(
                customer=customer,
                session_id=str(uuid.uuid4()),
                session_type=session_type,
                initiated_by=request.user,
                files_expected=files_expected
            )
            
            # Save files using proper routing
            files_saved = save_uploaded_files_properly(customer, request.FILES, session)
            
            session.files_received = len(files_saved)
            session.update_status('UPLOADING', f"{len(files_saved)} files uploaded successfully.")
            
            # Start processing
            try:
                # Import the fixed processing function
                from .script_helper import execute_health_check_script
                
                # For NEW networks, mark as READY after successful file upload
                if customer.setup_status == 'NEW':
                    customer.setup_status = 'READY'
                    customer.save()
                    session.update_status('COMPLETED', 'Network setup completed successfully')
                    messages.success(request, f"Network {customer.name} has been set up successfully!")
                    return redirect('dashboard')
                else:
                    # For existing networks, start processing
                    process_health_check_files_enhanced(session.id)
                    messages.success(request, f"Health check processing initiated for {customer.name}")
                
            except Exception as e:
                session.update_status('FAILED', f"Processing failed: {str(e)}")
                messages.error(request, f"Processing failed: {str(e)}")
            
            return redirect('health_check_processing', session_id=session.session_id)
    else:
        form = form_class()
        
    return render(request, template_name, {
        'form': form, 
        'customer': customer,
        'files_expected': files_expected
    })


# Also update the process_health_check_files_enhanced function
def process_health_check_files_enhanced_fixed(session_id):
    """Enhanced processing that uses proper file locations"""
    try:
        session = HealthCheckSession.objects.get(id=session_id)
        customer = session.customer
        
        session.update_status('PROCESSING', 'Initializing health check analysis...')
        session.progress_percentage = 5
        session.current_step = "Preparing environment"
        session.save()
        
        # Validate that files are in the right places
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        SCRIPT_DIR = BASE_DIR / "Script"
        SCRIPT_INPUT_DIR = SCRIPT_DIR / "input-hc-report"
        
        # Check input files
        input_files = list(SCRIPT_INPUT_DIR.glob("*"))
        if len(input_files) < 2:
            raise Exception(f"Expected at least 2 files in input directory, found {len(input_files)}")
        
        print(f"📁 Input files found: {[f.name for f in input_files]}")
        
        # Check network files
        network_files = [
            f"{customer.name}_HC_Issues_Tracker.xlsx",
            f"{customer.name}_ignored_test_cases.txt",
            f"{customer.name}_ignored_test_cases.xlsx"
        ]
        
        for filename in network_files:
            file_path = SCRIPT_DIR / filename
            if not file_path.exists():
                raise Exception(f"Network file missing: {filename}")
        
        print(f"📁 Network files validated for: {customer.name}")
        
        # Execute script using improved helper
        session.progress_percentage = 25
        session.current_step = "Executing health check script"
        session.save()
        
        from .script_helper import execute_health_check_script
        script_result = execute_health_check_script(customer.name)
        
        if script_result['success']:
            session.progress_percentage = 80
            session.current_step = "Processing outputs"
            session.save()
            
            # Find generated tracker file
            output_dir = SCRIPT_DIR / "output"
            for output_file in output_dir.glob("*HC_Issues_Tracker*.xlsx"):
                session.output_tracker_filename = output_file.name
                session.output_tracker_path = str(output_file)
                session.save()
                break
            
            session.progress_percentage = 100
            session.current_step = "Completed"
            session.update_status('COMPLETED', 'Health check analysis completed successfully')
            
        else:
            error_msg = script_result.get('error', 'Unknown error occurred')
            session.update_status('FAILED', f"Script execution failed: {error_msg}")
            
    except Exception as e:
        session.update_status('FAILED', f'Processing failed: {str(e)}')
        print(f"❌ Processing error: {str(e)}")
        raise e
