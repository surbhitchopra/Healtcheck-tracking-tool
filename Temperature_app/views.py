import os
import uuid
import time
import sqlite3
from datetime import datetime
from django.utils import timezone
from pathlib import Path
from django.conf import settings
from django.db import connection

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Customer, HealthCheckFile, HealthCheckSession, NodeCoverage, IgnoredTestCase
from .forms import CustomerSelectionForm, CustomerCreationForm, HealthCheckNewNetworkForm, HealthCheckExistingNetworkForm

# === Directories ===
BASE_DIR = Path(__file__).resolve().parent.parent
HC_FILES_DIR = BASE_DIR / "hc_files"
HC_INPUT_DIR = HC_FILES_DIR / "input"
HC_OUTPUT_DIR = HC_FILES_DIR / "output"
HC_TEMPLATE_DIR = HC_FILES_DIR / "templates"
HC_ARCHIVE_DIR = HC_FILES_DIR / "archive"
SCRIPT_DIR = BASE_DIR / "Script"
CUSTOMER_FILES_DIR = SCRIPT_DIR / "customer_files"

os.makedirs(HC_INPUT_DIR, exist_ok=True)
os.makedirs(HC_OUTPUT_DIR, exist_ok=True)
os.makedirs(HC_TEMPLATE_DIR, exist_ok=True)
os.makedirs(HC_ARCHIVE_DIR, exist_ok=True)
os.makedirs(CUSTOMER_FILES_DIR, exist_ok=True)

def get_customer_directory_structure(customer_name):
    """Get the proper directory structure for a customer"""
    customer_name_clean = customer_name.lower().replace(' ', '').replace('-', '').replace('_', '')
    customer_dir = CUSTOMER_FILES_DIR / customer_name_clean
    
    directories = {
        'base': customer_dir,
        'tec_reports': customer_dir / 'tec_reports',
        'inventory_files': customer_dir / 'inventory_files', 
        'host_files': customer_dir / 'host_files',
        'generated_trackers': customer_dir / 'generated_trackers',
        'old_trackers': customer_dir / 'old_trackers',
        'reports': customer_dir / 'reports',
        'misc': customer_dir / 'misc'
    }
    
    # Create all directories
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return directories

# === Authentication Views ===
def user_login(request):
    if request.user.is_authenticated:
        return redirect('customer_selection')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("customer_selection")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

def user_register(request):
    if request.user.is_authenticated:
        return redirect('customer_selection')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password != password_confirm:
            return render(request, "register.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken."})

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("login")

    return render(request, "register.html")

def user_logout(request):
    logout(request)
    return redirect('login')

# === Customer Management Views ===
@login_required
def customer_selection_view(request):
    if request.method == "POST":
        # Handle customer selection
        if 'select_customer' in request.POST:
            form = CustomerSelectionForm(request.POST)
            if form.is_valid():
                customer = form.cleaned_data['customer']
                request.session['selected_customer_id'] = customer.id
                request.session['selected_customer_name'] = customer.name
                return redirect('dashboard')

        # Handle new customer creation
        elif 'add_customer' in request.POST:
            customer_form = CustomerCreationForm(request.POST)
            if customer_form.is_valid():
                new_customer = customer_form.save()
                request.session['selected_customer_id'] = new_customer.id
                request.session['selected_customer_name'] = new_customer.name
                return redirect('dashboard')
    
    selection_form = CustomerSelectionForm()
    customer_form = CustomerCreationForm()
    return render(request, 'customer_selection.html', {
        'selection_form': selection_form,
        'customer_form': customer_form
    })

# === Health Check Dashboard and Main Views ===
@login_required
def health_check_dashboard(request):
    # Check if customer is selected
    if 'selected_customer_id' not in request.session:
        return redirect('customer_selection')
    
    selected_customer_id = request.session.get('selected_customer_id')
    
    # Verify customer still exists
    try:
        customer = Customer.objects.get(id=selected_customer_id, is_deleted=False)
    except Customer.DoesNotExist:
        # Customer was deleted, redirect to selection
        del request.session['selected_customer_id']
        del request.session['selected_customer_name']
        return redirect('customer_selection')
    
    # Get recent sessions for this customer
    recent_sessions = HealthCheckSession.objects.filter(
        customer=customer
    ).order_by('-created_at')[:5]
    
    return render(request, 'dashboard.html', {
        'selected_customer': customer,
        'recent_sessions': recent_sessions
    })

@login_required
def select_customer_for_hc(request):
    if request.method == 'POST':
        form = CustomerSelectionForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data['customer']
            return redirect('health_check_upload', customer_id=customer.id)
    else:
        form = CustomerSelectionForm()
    return render(request, 'health_check/select_customer.html', {'form': form})

@login_required
def health_check_upload(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    
    if customer.setup_status == 'NEW':
        form_class = HealthCheckNewNetworkForm
        template_name = 'health_check/upload_new_network.html'
        files_expected = 5
    else:
        form_class = HealthCheckExistingNetworkForm
        template_name = 'health_check/upload_existing_network.html'
        files_expected = 2
        
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            # Create session
            session = HealthCheckSession.objects.create(
                customer=customer,
                session_id=str(uuid.uuid4()),
                session_type='NEW_NETWORK_SETUP' if customer.setup_status == 'NEW' else 'REGULAR_PROCESSING',
                initiated_by=request.user,
                files_expected=files_expected
            )
            
            # Get customer directory structure
            customer_dirs = get_customer_directory_structure(customer.name)
            print(f"📁 UPLOAD: Setting up directories for customer: {customer.name}")
            print(f"📁 Customer directories: {list(customer_dirs.keys())}")
            
            # Process uploaded files with proper directory routing
            files_uploaded = 0
            for field_name, file in request.FILES.items():
                print(f"📤 Processing file: {file.name} (type: {field_name})")
                
                # Determine target directory based on file type - FIXED routing logic for both NEW and EXISTING
                if field_name.lower() in ['tec_report', 'reports', 'report_file', 'tec_report_file']:
                    target_dir = customer_dirs['tec_reports']
                    stored_filename = file.name  # Keep original name for TEC reports
                    print(f"🎯 Routing TEC report to: {target_dir}")
                elif field_name.lower() in ['inventory_csv', 'inventory', 'csv_file', 'inventory_file']:
                    target_dir = customer_dirs['inventory_files']
                    stored_filename = file.name  # Keep original name for inventory
                    print(f"🎯 Routing inventory to: {target_dir}")
                elif field_name.lower() in ['host_file', 'hosts', 'host_files']:
                    target_dir = customer_dirs['host_files']
                    stored_filename = file.name  # Keep original name for host files
                    print(f"🎯 Routing host file to: {target_dir}")
                elif field_name.lower() in ['template_tracker', 'old_tracker', 'hc_tracker']:
                    target_dir = customer_dirs['old_trackers']
                    stored_filename = file.name  # Keep original name for templates/old trackers
                    print(f"🎯 Routing tracker to: {target_dir}")
                elif field_name.lower() in ['ignored_test_cases', 'ignore_file', 'global_ignore', 'selective_ignore']:
                    target_dir = customer_dirs['old_trackers']  # Store ignored test cases with old trackers
                    stored_filename = file.name
                    print(f"🎯 Routing ignore file to: {target_dir}")
                else:
                    # Default to misc directory for unknown file types
                    target_dir = customer_dirs['misc']
                    stored_filename = f"{session.session_id}_{file.name}"
                    print(f"🎯 Routing unknown file type to misc: {target_dir}")
                
                file_path = target_dir / stored_filename
                
                print(f"📁 Target directory: {target_dir}")
                print(f"📄 Stored filename: {stored_filename}")
                print(f"🔗 Full path: {file_path}")
                
                # Save file to appropriate customer directory
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                print(f"✅ File saved successfully: {file_path}")
                
                # Create HealthCheckFile record with proper paths
                hc_file = HealthCheckFile.objects.create(
                    customer=customer,
                    file_type=field_name.upper(),
                    original_filename=file.name,
                    stored_filename=stored_filename,
                    file_path=str(file_path),
                    file_size=file.size,
                    uploaded_by=request.user
                )
                
                files_uploaded += 1
                print(f"📋 Created database record for: {file.name} (ID: {hc_file.id})")
            
            session.update_status('UPLOADING', f"{files_uploaded} files uploaded successfully.")
            
            # Start processing (in a real app, this would be a background task)
            process_health_check_files(session.id)
            
            return redirect('health_check_processing', session_id=session.session_id)
    else:
        form = form_class()
        
    return render(request, template_name, {'form': form, 'customer': customer})

@login_required
def health_check_processing(request, session_id):
    session = HealthCheckSession.objects.get(session_id=session_id)
    return render(request, 'health_check/processing.html', {'session': session})

@login_required
def health_check_results(request, session_id):
    session = HealthCheckSession.objects.get(session_id=session_id)
    return render(request, 'health_check/results.html', {'session': session})

# === Health Check Processing Functions ===
def process_health_check_files(session_id):
    """Process Health Check files - simplified version"""
    session = HealthCheckSession.objects.get(id=session_id)
    session.update_status('PROCESSING', 'Starting health check analysis.')
    
    try:
        # Get all files for this session
        session_files = HealthCheckFile.objects.filter(customer=session.customer)
        
        # Here you would call your actual Health Check processing logic
        # For now, just simulate processing
        import time
        time.sleep(2)  # Simulate processing time
        
        session.update_status('COMPLETED', 'Health check analysis completed successfully.')
        
        # Update customer status if it was a new network
        if session.customer.setup_status == 'NEW':
            session.customer.setup_status = 'READY'
            session.customer.save()
            
    except Exception as e:
        session.error_messages = str(e)
        session.update_status('FAILED', 'An unexpected error occurred during processing.')
    
    session.completed_at = timezone.now()
    session.save()

# === File Download View ===
def download_tracker_file(request):
    filename = request.GET.get("filename")
    if not filename:
        return HttpResponse("No filename provided", status=400)
    
    # First check if we have a selected customer to look in their specific directories
    selected_customer_id = request.session.get('selected_customer_id')
    customer_dirs_to_check = []
    
    if selected_customer_id:
        try:
            customer = Customer.objects.get(id=selected_customer_id)
            customer_dirs = get_customer_directory_structure(customer.name)
            # Priority order for customer directories
            customer_dirs_to_check = [
                customer_dirs['generated_trackers'],  # Most likely location for downloads
                customer_dirs['reports'],
                customer_dirs['old_trackers'],
                customer_dirs['tec_reports'],
                customer_dirs['inventory_files'],
                customer_dirs['host_files'],
                customer_dirs['misc']
            ]
            print(f"🔍 Looking for {filename} in customer {customer.name} directories...")
        except Customer.DoesNotExist:
            print(f"⚠️ Selected customer not found, falling back to global search")
    
    # Add global directories as fallback
    global_directories = [
        HC_OUTPUT_DIR,
        HC_ARCHIVE_DIR,
        HC_INPUT_DIR,
    ]
    
    # Combine customer-specific and global directories
    all_directories = customer_dirs_to_check + global_directories
    
    # Search through all directories
    for directory in all_directories:
        if directory.exists():
            file_path = directory / filename
            print(f"🔍 Checking: {file_path}")
            if file_path.exists():
                print(f"✅ Found file at: {file_path}")
                try:
                    # Determine content type based on file extension
                    if filename.lower().endswith(('.xlsx', '.xls')):
                        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    elif filename.lower().endswith('.csv'):
                        content_type = 'text/csv'
                    elif filename.lower().endswith('.txt'):
                        content_type = 'text/plain'
                    else:
                        content_type = 'application/octet-stream'
                    
                    response = FileResponse(
                        open(file_path, "rb"),
                        as_attachment=True,
                        filename=filename,
                        content_type=content_type
                    )
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    print(f"📥 Serving download: {filename} from {directory}")
                    return response
                except Exception as e:
                    print(f"❌ Error downloading file: {str(e)}")
                    return HttpResponse(f"Error downloading file: {str(e)}", status=500)
    
    print(f"❌ File '{filename}' not found in any directory")
    return HttpResponse(f"File '{filename}' not found", status=404)

# === API Endpoints ===
@login_required
def validate_filename(request):
    """API endpoint to validate if a filename contains the selected customer's name"""
    if 'selected_customer_id' not in request.session:
        return JsonResponse({"status": "error", "message": "No customer selected"})
    
    filename = request.GET.get('filename', '')
    if not filename:
        return JsonResponse({"status": "error", "message": "No filename provided"})
    
    selected_customer_id = request.session.get('selected_customer_id')
    try:
        customer = Customer.objects.get(id=selected_customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Selected customer no longer exists"})
    
    # Simple validation - check if customer name is in filename
    is_valid = customer.name.lower() in filename.lower()
    
    return JsonResponse({
        "status": "success",
        "is_valid": is_valid,
        "customer_name": customer.name,
        "message": "Filename is valid" if is_valid else f"Filename must contain customer name '{customer.name}'"
    })

@login_required
def get_previous_threshold(request):
    """API endpoint - not used in Health Check workflow"""
    return JsonResponse({
        "status": "success",
        "previous_threshold": None,
        "message": "No previous threshold found for Health Check workflow"
    })

@login_required
def get_sticky_notes_data(request):
    """API endpoint to get data for sticky notes panel"""
    try:
        selected_customer_id = request.session.get('selected_customer_id')
        selected_customer_name = request.session.get('selected_customer_name', 'Unknown')
        
        # Get last session for the current customer
        last_session = None
        if selected_customer_id:
            try:
                current_customer = Customer.objects.get(id=selected_customer_id)
                last_session = HealthCheckSession.objects.filter(
                    customer=current_customer
                ).order_by('-created_at').first()
            except Customer.DoesNotExist:
                pass
        
        last_session_data = None
        if last_session:
            last_session_data = {
                "session_id": last_session.session_id,
                "customer": last_session.customer.name,
                "timestamp": timezone.localtime(last_session.created_at).strftime('%d-%m-%Y %I:%M %p'),
                "status": last_session.status
            }
        
        # Get current time for customer selection
        current_time = datetime.now().strftime('%d-%m-%Y %I:%M %p')
        
        return JsonResponse({
            "status": "success",
            "current_customer": {
                "name": selected_customer_name,
                "selected_time": current_time,
                "is_new_customer": True
            },
            "last_session": last_session_data,
            "last_activity": last_session_data
        })
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error getting sticky notes data: {str(e)}"})

# === Legacy Views (for backward compatibility) ===
# These return error messages indicating they're not implemented in Health Check version
@login_required
def upload_report_file(request):
    return JsonResponse({"status": "error", "message": "Temperature workflow not implemented in Health Check version"})

@login_required
def upload_host_file(request):
    return JsonResponse({"status": "error", "message": "Temperature workflow not implemented in Health Check version"})

@login_required
def tracker_history(request):
    return JsonResponse({"status": "error", "message": "Temperature history not available in Health Check version"})

@login_required
def delete_tracker_file(request):
    return JsonResponse({"status": "error", "message": "File deletion not implemented in Health Check version"})

@login_required
def bulk_delete_files(request):
    return JsonResponse({"status": "error", "message": "Bulk deletion not implemented in Health Check version"})

@login_required
def cleanup_database_state(request):
    return JsonResponse({"status": "error", "message": "Database cleanup not implemented in Health Check version"})

@login_required
def cleanup_duplicate_records(request):
    return JsonResponse({"status": "error", "message": "Duplicate cleanup not implemented in Health Check version"})

@login_required
def upload_old_tracker(request):
    return JsonResponse({"status": "error", "message": "Old tracker upload not implemented in Health Check version"})

@login_required
def upload_tracker_generated(request):
    return JsonResponse({"status": "error", "message": "Tracker generated upload not implemented in Health Check version"})

@login_required
def batch_process_old_trackers_and_reports(request):
    return JsonResponse({"status": "error", "message": "Batch processing not implemented in Health Check version"})

# =============================================================================
# SYSTEM HEALTH CHECK ENDPOINTS
# =============================================================================

def health_check(request):
    """
    Basic health check endpoint - returns server status and current time with timezone fix
    """
    try:
        current_time_utc = timezone.now()
        current_time_ist = timezone.localtime(current_time_utc)
        
        return JsonResponse({
            "status": "healthy",
            "message": "Health Check System is running",
            "timestamp_utc": current_time_utc.isoformat(),
            "timestamp_ist": current_time_ist.strftime('%d-%m-%Y %I:%M:%S %p'),
            "timezone": settings.TIME_ZONE,
            "version": "1.0.0",
            "service": "Health Check Backend",
            "system_time": datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "timestamp": timezone.now().isoformat()
        }, status=500)

def health_detailed(request):
    """
    Detailed health check including database, filesystem, and time synchronization
    """
    health_status = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database Health Check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Test model queries
        from .models import Customer, HealthCheckSession, HealthCheckFile
        customer_count = Customer.objects.count()
        session_count = HealthCheckSession.objects.count()
        file_count = HealthCheckFile.objects.count()
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "details": {
                "connection": "ok",
                "customer_count": customer_count,
                "session_count": session_count,
                "file_count": file_count,
                "database_engine": settings.DATABASES['default']['ENGINE']
            }
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Filesystem Health Check
    try:
        directories_status = {}
        
        for dir_name, dir_path in [
            ("BASE_DIR", BASE_DIR),
            ("HC_FILES_DIR", HC_FILES_DIR),
            ("HC_INPUT_DIR", HC_INPUT_DIR),
            ("HC_OUTPUT_DIR", HC_OUTPUT_DIR),
            ("HC_TEMPLATE_DIR", HC_TEMPLATE_DIR),
            ("HC_ARCHIVE_DIR", HC_ARCHIVE_DIR)
        ]:
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*")))
                directories_status[dir_name] = {
                    "exists": True,
                    "writable": os.access(str(dir_path), os.W_OK),
                    "file_count": file_count,
                    "path": str(dir_path)
                }
            else:
                directories_status[dir_name] = {
                    "exists": False,
                    "writable": False,
                    "file_count": 0,
                    "path": str(dir_path)
                }
        
        health_status["checks"]["filesystem"] = {
            "status": "healthy",
            "directories": directories_status
        }
    except Exception as e:
        health_status["checks"]["filesystem"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Time Synchronization Check - THIS IS THE KEY FIX
    try:
        current_time_utc = timezone.now()
        current_time_local = timezone.localtime(current_time_utc)
        system_time = datetime.now()
        
        # Get recent database timestamps to check for consistency
        recent_sessions = HealthCheckSession.objects.order_by('-created_at')[:5]
        timestamp_checks = []
        
        for session in recent_sessions:
            session_local = timezone.localtime(session.created_at)
            time_diff = (current_time_utc - session.created_at).total_seconds() / 3600  # hours
            
            timestamp_checks.append({
                "session_id": session.session_id,
                "created_at_utc": session.created_at.isoformat(),
                "created_at_local": session_local.strftime('%d-%m-%Y %I:%M:%S %p'),
                "hours_ago": round(time_diff, 2),
                "reasonable": 0 <= time_diff < 8760  # Within last year and not future
            })
        
        # Check for time sync issues
        issues = []
        if abs((system_time - current_time_local.replace(tzinfo=None)).total_seconds()) > 300:  # 5 minutes
            issues.append("System time and Django time differ by more than 5 minutes")
        
        unreasonable_timestamps = [check for check in timestamp_checks if not check["reasonable"]]
        if unreasonable_timestamps:
            issues.append(f"{len(unreasonable_timestamps)} recent sessions have unreasonable timestamps")
        
        health_status["checks"]["time_synchronization"] = {
            "status": "healthy" if not issues else "degraded",
            "timezone_setting": settings.TIME_ZONE,
            "use_tz": settings.USE_TZ,
            "current_utc": current_time_utc.isoformat(),
            "current_local": current_time_local.strftime('%d-%m-%Y %I:%M:%S %p %Z'),
            "system_time": system_time.strftime('%d-%m-%Y %I:%M:%S %p'),
            "offset_hours": current_time_local.utcoffset().total_seconds() / 3600 if current_time_local.utcoffset() else 0,
            "recent_timestamps": timestamp_checks,
            "issues": issues
        }
        
        if issues:
            overall_healthy = False
            
    except Exception as e:
        health_status["checks"]["time_synchronization"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status)

def health_database(request):
    """
    Database-specific health check with time analysis
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
        
        # Test model operations
        customer_count = Customer.objects.count()
        active_customers = Customer.objects.filter(is_deleted=False).count()
        session_count = HealthCheckSession.objects.count()
        active_sessions = HealthCheckSession.objects.filter(status__in=['PROCESSING', 'UPLOADING']).count()
        
        # Get recent activity
        recent_session = HealthCheckSession.objects.order_by('-created_at').first()
        last_activity = recent_session.created_at.isoformat() if recent_session else None
        last_activity_local = timezone.localtime(recent_session.created_at).strftime('%d-%m-%Y %I:%M:%S %p') if recent_session else None
        
        return JsonResponse({
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "database": {
                "connection": "ok",
                "migrations_applied": migration_count,
                "total_customers": customer_count,
                "active_customers": active_customers,
                "total_sessions": session_count,
                "active_sessions": active_sessions,
                "last_activity_utc": last_activity,
                "last_activity_local": last_activity_local,
                "database_path": str(settings.DATABASES['default']['NAME'])
            }
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "timestamp": timezone.now().isoformat(),
            "error": str(e),
            "database": {"connection": "failed"}
        }, status=500)

def health_time_sync(request):
    """
    Time synchronization health check - verify time settings and fix timestamp issues
    """
    try:
        # Get current time in different formats
        utc_now = timezone.now()
        local_now = timezone.localtime(utc_now)
        system_time = datetime.now()
        
        # Check timezone configuration
        timezone_info = {
            "django_timezone": settings.TIME_ZONE,
            "django_use_tz": settings.USE_TZ,
            "utc_now": utc_now.isoformat(),
            "local_now": local_now.strftime('%d-%m-%Y %I:%M:%S %p %Z'),
            "system_time": system_time.strftime('%d-%m-%Y %I:%M:%S %p'),
            "timezone_offset_hours": local_now.utcoffset().total_seconds() / 3600 if local_now.utcoffset() else 0
        }
        
        # Check if recent database timestamps are reasonable
        recent_sessions = HealthCheckSession.objects.order_by('-created_at')[:10]
        
        timestamp_checks = []
        for session in recent_sessions:
            session_local = timezone.localtime(session.created_at)
            time_diff = (utc_now - session.created_at).total_seconds() / 3600  # hours
            
            timestamp_checks.append({
                "session_id": session.session_id,
                "customer": session.customer.name,
                "status": session.status,
                "timestamp_utc": session.created_at.isoformat(),
                "timestamp_local": session_local.strftime('%d-%m-%Y %I:%M:%S %p'),
                "hours_ago": round(time_diff, 2),
                "reasonable": 0 <= time_diff < 8760  # Within last year and not future
            })
        
        # Check for time sync issues
        issues = []
        if abs((system_time - local_now.replace(tzinfo=None)).total_seconds()) > 300:  # 5 minutes
            issues.append("System time and Django time differ by more than 5 minutes")
        
        unreasonable_timestamps = [check for check in timestamp_checks if not check["reasonable"]]
        if unreasonable_timestamps:
            issues.append(f"{len(unreasonable_timestamps)} recent sessions have unreasonable timestamps")
        
        status = "healthy" if not issues else "degraded"
        
        response_data = {
            "status": status,
            "timestamp": utc_now.isoformat(),
            "timezone_info": timezone_info,
            "recent_timestamps": timestamp_checks,
            "issues": issues,
            "fix_summary": {
                "timezone_changed_from": "UTC",
                "timezone_changed_to": "Asia/Kolkata",
                "explanation": "Database timestamps are stored in UTC but now displayed in IST (UTC+5:30)"
            }
        }
        
        # Fix timestamp issues if requested
        if request.GET.get('fix_timestamps') == 'true' and issues:
            fixed_count = 0
            for session in recent_sessions:
                if session.created_at > utc_now:  # Future timestamp
                    session.created_at = utc_now
                    session.save()
                    fixed_count += 1
            
            if fixed_count > 0:
                response_data["fix_applied"] = f"Fixed {fixed_count} future timestamps"
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "timestamp": timezone.now().isoformat(),
            "error": str(e)
        }, status=500)
