# Fix for Health Check Script Execution Error

## Problem
The error "[WinError 2] The system cannot find the file specified" occurs because the Python executable path is not being constructed correctly for Windows.

## Solution

### Step 1: Copy the script helper file
The file `HealthCheck_app/script_helper.py` has been created with improved path handling.

### Step 2: Update your views.py file

Replace the `execute_hc_script_enhanced` function in your `HealthCheck_app/views.py` file with this improved version:

```python
def execute_hc_script_enhanced(session):
    """Enhanced script execution with better Windows path handling"""
    try:
        from .script_helper import execute_health_check_script, ScriptExecutor
        
        # Get customer name from session
        customer_name = session.customer.name
        
        # Use the improved script executor
        script_result = execute_health_check_script(customer_name)
        
        return {
            'success': script_result['success'],
            'stdout': script_result.get('stdout', ''),
            'stderr': script_result.get('stderr', ''),
            'returncode': script_result.get('returncode', 0),
            'error': script_result.get('error', None)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### Step 3: Replace the process_health_check_files_enhanced function

Replace your existing `process_health_check_files_enhanced` function with:

```python
def process_health_check_files_enhanced(session_id):
    """Enhanced processing that uses the improved script executor"""
    try:
        session = HealthCheckSession.objects.get(id=session_id)
        customer = session.customer
        
        session.update_status('PROCESSING', 'Initializing health check analysis...')
        session.progress_percentage = 5
        session.current_step = "Preparing environment"
        session.save()
        
        # Import our improved script helper
        from .script_helper import execute_health_check_script
        
        # Execute the script using our improved script executor
        session.progress_percentage = 25
        session.current_step = "Executing health check script"
        session.save()
        
        # Execute with network name
        script_result = execute_health_check_script(customer.name)
        
        if script_result['success']:
            session.progress_percentage = 80
            session.current_step = "Processing outputs"
            session.save()
            
            # Process generated outputs
            tracker_file = script_result.get('tracker_file')
            if tracker_file:
                # Save tracker file info to session
                session.output_tracker_filename = tracker_file['name']
                session.output_tracker_path = tracker_file['path']
                session.save()
            
            # Create detailed report
            create_detailed_report(session, script_result)
            
            session.progress_percentage = 100
            session.current_step = "Completed"
            session.update_status('COMPLETED', 'Health check analysis completed successfully')
            
        else:
            error_msg = script_result.get('error', 'Unknown error occurred')
            session.update_status('FAILED', f"Script execution failed: {error_msg}")
            
    except Exception as e:
        session.update_status('FAILED', f'Processing failed: {str(e)}')
        raise e
```

### Step 4: Add import at the top of views.py

Add this import at the top of your `views.py` file:

```python
from .script_helper import execute_health_check_script, ScriptExecutor
```

### Step 5: Test the fix

1. Try uploading files again to see if the script execution works
2. Check the logs to see detailed execution information
3. The script helper provides better error messages and validation

## Key Improvements

1. **Proper path handling**: Uses `pathlib.Path` for cross-platform compatibility
2. **Better error messages**: More detailed error reporting
3. **Environment validation**: Checks all required files before execution
4. **Working directory**: Properly sets the working directory for script execution
5. **Logging**: Better logging for debugging

## Testing the Fix

You can test if the fix works by:

1. Upload the required files (HC report and inventory CSV)
2. Check if processing completes successfully
3. Look for generated files in the Script/output directory

The error should be resolved and you should see proper script execution with detailed progress updates.
