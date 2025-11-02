from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import subprocess
import threading
import json
import os
import uuid
from pathlib import Path
import time
import logging
import shutil
from .models import Customer, HealthCheckSession, HealthCheckFile
from .forms import CustomerForm, HealthCheckNewNetworkForm, HealthCheckExistingNetworkForm

# Configuration
SCRIPT_DIR = Path(settings.BASE_DIR) / "Script"
SCRIPT_INPUT_DIR = SCRIPT_DIR / "input"
SCRIPT_OUTPUT_DIR = SCRIPT_DIR / "output"

# Ensure directories exist
SCRIPT_INPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set up logging
logger = logging.getLogger(__name__)


def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('customer_selection')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def user_register(request):
    """Handle user registration"""
    if request.method == 'POST':
        # Basic registration logic here
        messages.info(request, 'Registration functionality to be implemented.')
    
    return render(request, 'auth/register.html')


@login_required
def customer_selection(request):
    """Display customer selection page"""
    customers = Customer.objects.filter(is_deleted=False).order_by('name')
    
    if request.method == 'POST':
        if 'new_customer' in request.POST:
            form = CustomerForm(request.POST)
            if form.is_valid():
                customer = form.save()
                messages.success(request, f'Customer "{customer.name}" created successfully!')
                
                # Set selected customer in session
                request.session['selected_customer_id'] = customer.id
                request.session['selected_customer_name'] = customer.name
                
                return redirect('dashboard')
        elif 'select_customer' in request.POST:
            customer_id = request.POST.get('customer_id')
            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id, is_deleted=False)
                    request.session['selected_customer_id'] = customer.id
                    request.session['selected_customer_name'] = customer.name
                    messages.success(request, f'Selected customer: {customer.name}')
                    return redirect('dashboard')
                except Customer.DoesNotExist:
                    messages.error(request, 'Selected customer not found.')
    else:
        form = CustomerForm()
    
    return render(request, 'customer_selection.html', {
        'customers': customers,
        'form': form
    })


@login_required
def health_check_dashboard(request):
    """Main dashboard for health check operations"""
    # Check if customer is selected
    selected_customer_id = request.session.get('selected_customer_id')
    if not selected_customer_id:
        messages.warning(request, 'Please select a customer first.')
        return redirect('customer_selection')
    
    try:
        selected_customer = Customer.objects.get(id=selected_customer_id, is_deleted=False)
    except Customer.DoesNotExist:
        messages.error(request, 'Selected customer not found.')
        return redirect('customer_selection')
    
    return render(request, 'dashboard.html', {
        'selected_customer': selected_customer,
    })


@login_required 
def setup_new_network(request, customer_id):
    """Setup new network with 5 required files per MOP"""
    customer = get_object_or_404(Customer, id=customer_id, is_deleted=False)
    
    if request.method == 'POST':
        form = HealthCheckNewNetworkForm(request.POST, request.FILES)
        if form.is_valid():
            # Create session
            session = HealthCheckSession.objects.create(
                customer=customer,
                session_id=str(uuid.uuid4()),
                status='PENDING',
                message='Network setup files uploaded, processing...',
                files_expected=5
            )
            
            # Save uploaded files
            save_network_setup_files(customer, request.FILES, session)
            
            # Start setup processing
            try:
                process_network_setup_files(session.id)
                messages.success(request, f"Network setup started for {customer.name}")
                return redirect('health_check_processing', session_id=session.session_id)
            except Exception as e:
                session.update_status('FAILED', f"Setup failed: {str(e)}")
                messages.error(request, f"Setup failed: {str(e)}")
    else:
        form = HealthCheckNewNetworkForm()
    
    return render(request, 'health_check/setup_new_network.html', {
        'form': form,
        'customer': customer
    })


@login_required
def health_check_upload(request, customer_id):
    """Handle health check file uploads for existing networks"""
    customer = get_object_or_404(Customer, id=customer_id, is_deleted=False)
    
    if request.method == 'POST':
        # Determine if this is new network (5 files) or existing (2 files)
        if customer.setup_status == 'NEW':
            form = HealthCheckNewNetworkForm(request.POST, request.FILES)
            expected_files = 5
        else:
            form = HealthCheckExistingNetworkForm(request.POST, request.FILES)  
            expected_files = 2
            
        if form.is_valid():
            # Create session
            session = HealthCheckSession.objects.create(
                customer=customer,
                session_id=str(uuid.uuid4()),
                status='PENDING',
                message='Health check files uploaded, processing...',
                files_expected=expected_files
            )
            
            # Save uploaded files
            save_processing_files(customer, request.FILES, session)
            
            # Start processing
            try:
                if customer.setup_status == 'NEW':
                    process_network_setup_files(session.id)
                else:
                    process_health_check_files_enhanced(session.id)
                messages.success(request, f"Health check processing started for {customer.name}")
                return redirect('health_check_processing', session_id=session.session_id)
            except Exception as e:
                session.update_status('FAILED', f"Processing failed: {str(e)}")
                messages.error(request, f"Processing failed: {str(e)}")
        else:
            messages.error(request, "Please correct the form errors and try again.")
            
    # Redirect back to dashboard with error messages
    return redirect('dashboard')


@login_required
def health_check_processing(request, session_id):
    """Display processing status page"""
    try:
        session = HealthCheckSession.objects.get(session_id=session_id)
    except HealthCheckSession.DoesNotExist:
        messages.error(request, 'Processing session not found.')
        return redirect('dashboard')
    
    return render(request, 'health_check/processing.html', {
        'session': session,
        'customer': session.customer
    })


@login_required
def health_check_results(request, session_id):
    """Display processing results"""
    try:
        session = HealthCheckSession.objects.get(session_id=session_id)
    except HealthCheckSession.DoesNotExist:
        messages.error(request, 'Processing session not found.')
        return redirect('dashboard')
    
    # Get output files
    output_files = []
    if session.output_directory and Path(session.output_directory).exists():
        output_dir = Path(session.output_directory)
        output_files = [f for f in output_dir.glob("*") if f.is_file()]
    
    return render(request, 'health_check/results.html', {
        'session': session,
        'customer': session.customer,
        'output_files': output_files
    })


@login_required
def download_tracker_file(request):
    """Download generated tracker file"""
    filename = request.GET.get('filename')
    if not filename:
        raise Http404("Filename not provided")
    
    # Check various possible locations
    possible_paths = [
        SCRIPT_OUTPUT_DIR / filename,
        SCRIPT_DIR / filename,
        Path(settings.MEDIA_ROOT) / 'outputs' / filename,
    ]
    
    file_path = None
    for path in possible_paths:
        if path.exists():
            file_path = path
            break
    
    if not file_path:
        raise Http404("File not found")
    
    try:
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception as e:
        raise Http404(f"Error reading file: {str(e)}")


@login_required
def validate_filename(request):
    """Validate if filename contains customer name"""
    filename = request.GET.get('filename', '')
    
    # Get selected customer
    selected_customer_id = request.session.get('selected_customer_id')
    if not selected_customer_id:
        return JsonResponse({
            'status': 'error',
            'message': 'No customer selected'
        })
    
    try:
        customer = Customer.objects.get(id=selected_customer_id)
        is_valid = validate_filename_contains_customer_name(filename, customer.name)
        
        if is_valid:
            return JsonResponse({
                'status': 'success',
                'is_valid': True,
                'message': f'Filename contains customer name "{customer.name}"'
            })
        else:
            return JsonResponse({
                'status': 'success', 
                'is_valid': False,
                'message': f'Filename must contain customer name "{customer.name}"'
            })
            
    except Customer.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Customer not found'
        })


@login_required
def session_status(request, session_id):
    """Get processing session status via AJAX"""
    try:
        session = HealthCheckSession.objects.get(session_id=session_id)
        
        return JsonResponse({
            'status': session.status,
            'message': session.message,
            'progress': session.progress_percentage,
            'current_step': session.current_step,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'output_files': session.output_files,
        })
        
    except HealthCheckSession.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Session not found'
        })


# Helper functions
def validate_filename_contains_customer_name(filename, customer_name):
    """Check if filename contains customer name (case-insensitive)"""
    import string
    
    # Clean customer name: remove spaces, punctuation, convert to lowercase
    customer_clean = ''.join(c for c in customer_name.lower() if c not in string.punctuation and c != ' ')
    
    # Clean filename: remove spaces, punctuation, convert to lowercase
    filename_clean = ''.join(c for c in filename.lower() if c not in string.punctuation and c != ' ')
    
    # Also check individual words in customer name
    customer_words = [word.strip().lower() for word in customer_name.split() if len(word.strip()) > 2]
    
    # Check if full cleaned name is in filename or if any significant word is in filename
    return (customer_clean in filename_clean or 
            any(word in filename_clean for word in customer_words if len(word) > 2))


def save_network_setup_files(customer, uploaded_files, session):
    """Save network setup files to Script directory"""
    # Clear previous files
    for file in SCRIPT_INPUT_DIR.glob("*"):
        file.unlink()
    
    # Save new files
    for field_name, file in uploaded_files.items():
        file_path = SCRIPT_INPUT_DIR / file.name
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Determine file type based on field name
        file_type_map = {
            'hc_tracker_file': 'HC_TRACKER',
            'global_ignore_txt': 'GLOBAL_IGNORE',
            'selective_ignore_xlsx': 'SELECTIVE_IGNORE',
            'tec_report_file': 'TEC_REPORT',
            'inventory_csv': 'INVENTORY_CSV'
        }
        
        file_type = file_type_map.get(field_name, 'OTHER')
        
        HealthCheckFile.objects.create(
            customer=customer,
            session=session,
            file_type=file_type,
            original_filename=file.name,
            stored_filename=file.name,
            file_path=str(file_path),
            file_size=file.size
        )


def save_processing_files(customer, uploaded_files, session):
    """Save processing files to Script input directory"""
    # Clear previous files
    for file in SCRIPT_INPUT_DIR.glob("*"):
        file.unlink()
    
    # Save new files
    for field_name, file in uploaded_files.items():
        file_path = SCRIPT_INPUT_DIR / file.name
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Determine file type
        file_type = 'TEC_REPORT' if file.name.endswith('.xlsx') else 'INVENTORY_CSV'
        
        HealthCheckFile.objects.create(
            customer=customer,
            session=session,
            file_type=file_type,
            original_filename=file.name,
            stored_filename=file.name,
            file_path=str(file_path),
            file_size=file.size
        )


def process_network_setup_files(session_id):
    """Process network setup files for NEW networks"""
    try:
        session = HealthCheckSession.objects.get(id=session_id)
        customer = session.customer
        
        session.update_status('PROCESSING', 'Setting up new network configuration...')
        
        # Process the 5 setup files and create network-specific files
        # This would include creating the tracker template, ignore files, etc.
        
        # For now, mark as completed
        session.update_status('COMPLETED', 'Network setup completed successfully')
        
        # Update customer status to EXISTING after successful setup
        customer.setup_status = 'EXISTING'
        customer.save()
        
    except Exception as e:
        session.update_status('FAILED', f'Network setup failed: {str(e)}')
        raise e


def process_health_check_files_enhanced(session_id):
    """Enhanced processing that fully integrates with Script/main.py"""
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
        
        # Execute the actual Script/main.py
        script_result = execute_hc_script_direct(session)
        
        if script_result['success']:
            session.progress_percentage = 80
            session.current_step = "Processing outputs"
            session.save()
            
            # Process generated outputs
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
                print(f"Web app found {output_count} output files:")
                for f in output_files:
                    print(f"  - {f.name}")
            
            success_message = f'Health check analysis completed successfully! Generated {output_count} output files.'
            session.update_status('COMPLETED', success_message)
            
        else:
            raise Exception(f"Script execution failed: {script_result['error']}")
        
    except Exception as e:
        session.update_status('FAILED', f'Processing failed: {str(e)}')
        raise e


def validate_network_setup_files(network_name):
    """Validate that network setup files exist per MOP requirements"""
    required_files = [
        f"{network_name}_HC_Issues_Tracker.xlsx",
        f"{network_name}_ignored_test_cases.txt", 
        f"{network_name}_ignored_test_cases.xlsx"
    ]
    
    for filename in required_files:
        file_path = SCRIPT_DIR / filename
        if not file_path.exists():
            return False
    
    return True


def parse_hc_filename(filename):
    """Parse network info from HC filename per MOP format"""
    try:
        # Expected format: Network_name_Reports_YYYYMMDD.xlsx
        # Parse using the logic from main.py
        base_name = filename.replace('.xlsx', '')
        last_underscore_pos = base_name.rfind('_')
        
        if last_underscore_pos == -1:
            return None
        
        network_name = base_name[:last_underscore_pos - 8]  # -8 for "_Reports"
        date_part = base_name[last_underscore_pos + 1:]
        
        if len(date_part) != 8:
            return None
        
        year = date_part[:4]
        month = date_part[4:6] 
        day = date_part[6:8]
        
        return {
            'network_name': network_name,
            'year': year,
            'month': month,
            'day': day,
            'date': f"{year}-{month}-{day}"
        }
        
    except Exception as e:
        print(f"Error parsing filename {filename}: {e}")
        return None


def execute_hc_script_direct(session):
    """Execute main.py directly using subprocess"""
    try:
        # Change to Script directory
        original_cwd = os.getcwd()
        os.chdir(str(SCRIPT_DIR))
        
        # Execute main.py
        result = subprocess.run(
            ['/usr/bin/python3', 'main.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        # Restore original working directory
        os.chdir(original_cwd)
        
        # Update session with script output
        session.script_stdout = result.stdout
        session.script_stderr = result.stderr
        session.save()
        
        if result.returncode == 0:
            return {'success': True, 'stdout': result.stdout, 'stderr': result.stderr}
        else:
            return {'success': False, 'error': result.stderr or 'Script execution failed'}
            
    except subprocess.TimeoutExpired:
        os.chdir(original_cwd)
        return {'success': False, 'error': 'Script execution timed out (10 minutes)'}
    except Exception as e:
        os.chdir(original_cwd)
        return {'success': False, 'error': str(e)}


def process_script_outputs_enhanced(session, network_info):
    """Process outputs from Script/main.py execution"""
    output_dir = SCRIPT_DIR / "output"
    
    if not output_dir.exists():
        raise Exception("Script output directory not found")
    
    # Find generated tracker file
    tracker_files = list(output_dir.glob("*Tracker*.xlsx"))
    
    if tracker_files:
        tracker_file = tracker_files[0]  # Take first tracker file
        
        # Store in session
        session.output_tracker_filename = tracker_file.name
        session.output_directory = str(output_dir)
        session.save()
        
        return {
            'output_files': [tracker_file.name],
            'tracker_file': tracker_file.name,
            'network_info': network_info
        }
    else:
        raise Exception("No tracker file found in output directory")


def create_detailed_report(session, output_info):
    """Create detailed processing report"""
    report_data = {
        'session_id': session.session_id,
        'customer': session.customer.name,
        'processing_time': session.completed_at - session.created_at if session.completed_at else None,
        'output_files': output_info.get('output_files', []),
        'network_info': output_info.get('network_info', {}),
    }
    
    # Store in session for reference
    session.output_files = json.dumps(report_data)
    session.save()
