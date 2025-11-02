# BACKUP: Original synchronous views.py (before async background processing)
# This is the working version with 20-minute timeout but synchronous processing
# Can be restored if async version doesn't work properly

# Key function that was changed:
def process_health_check_files_enhanced(session_id):
    """Enhanced processing that fully integrates with Script/main.py - SYNCHRONOUS VERSION"""
    try:
        session = HealthCheckSession.objects.get(id=session_id)
        customer = session.customer
        
        session.update_status('PROCESSING', 'Initializing health check analysis...')
        session.progress_percentage = 5
        session.current_step = "Preparing environment"
        session.save()
        
        # Validate network setup files exist
        network_files_exist = validate_network_setup_files(customer.name)
        if not network_files_exist:
            raise Exception(f"Network setup files missing for {customer.name}. Please run initial network setup.")
        
        # Validate input files are present
        input_files = list(SCRIPT_INPUT_DIR.glob("*"))
        if len(input_files) != 2:
            raise Exception("Expected exactly 2 input files (HC report .xlsx and inventory .csv)")
        
        # Update progress
        session.progress_percentage = 15
        session.current_step = "Validating files"
        session.save()
        
        # Extract network information from filenames (per MOP)
        hc_report_file = None
        csv_file = None
        
        for file_path in input_files:
            if file_path.suffix == '.xlsx':
                hc_report_file = file_path
            elif file_path.suffix == '.csv':
                csv_file = file_path
        
        if not hc_report_file or not csv_file:
            raise Exception("Could not identify HC report (.xlsx) and inventory (.csv) files")
        
        # Parse network info from filename (per MOP format)
        network_info = parse_hc_filename(hc_report_file.name)
        if not network_info:
            raise Exception("HC report filename does not follow expected format")
        
        session.progress_percentage = 25
        session.current_step = "Executing health check script"
        session.save()
        
        print(f"🚀 SYNCHRONOUS: Starting script execution for session {session_id}")
        
        # Execute the actual Script/main.py SYNCHRONOUSLY (user waits)
        script_result = execute_hc_script_direct(session)
        
        if script_result['success']:
            session.progress_percentage = 80
            session.current_step = "Processing outputs"
            session.save()
            
            # Process generated outputs (don't fail on file copying issues)
            try:
                output_info = process_script_outputs_enhanced(session, network_info)
            except Exception as output_error:
                print(f"Warning: Output processing had issues: {output_error}")
                output_info = {'output_files': [], 'network_info': network_info}
            
            session.progress_percentage = 95
            session.current_step = "Finalizing results"
            session.save()
            
            # Create detailed report
            try:
                create_detailed_report(session, output_info)
            except Exception as report_error:
                print(f"Warning: Report creation had issues: {report_error}")
            
            session.progress_percentage = 100
            session.current_step = "Completed"
            
            # Count output files to show in success message
            output_dir = SCRIPT_DIR / "output"
            
            # Add small delay to ensure all files are written
            import time
            time.sleep(2)
            
            # Count files more reliably
            output_count = 0
            if output_dir.exists():
                output_files = [f for f in output_dir.glob("*") if f.is_file()]
                output_count = len(output_files)
                print(f"📊 SYNCHRONOUS: Found {output_count} output files")
                for f in output_files:
                    print(f"  - {f.name}")
            
            success_message = f'Health check analysis completed successfully! Generated {output_count} output files.'
            session.update_status('COMPLETED', success_message)
            print(f"✅ SYNCHRONOUS: Processing completed for session {session_id}")
            
        else:
            raise Exception(f"Script execution failed: {script_result['error']}")
        
    except Exception as e:
        session.update_status('FAILED', f'Processing failed: {str(e)}')
        print(f"❌ SYNCHRONOUS: Processing failed for session {session_id}: {str(e)}")
        raise e

# This backup shows the key difference:
# SYNCHRONOUS = User waits for script completion (20 minutes)  
# ASYNCHRONOUS = Background thread + immediate return

# To revert: Replace the async function with this synchronous version
