from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication
    path('', views.user_login, name='home'), 
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'), 
    path('logout/', views.user_logout, name='logout'),
    
    # Customer Management
    path('customer-selection/', views.customer_selection_view, name='customer_selection'),
    
    # Health Check Dashboard and Workflow
    path('dashboard/', views.health_check_dashboard, name='dashboard'),
    path('health-check/select-customer/', views.select_customer_for_hc, name='select_customer_for_hc'),
    path('health-check/upload/<int:customer_id>/', views.health_check_upload, name='health_check_upload'),
    path('health-check/processing/<str:session_id>/', views.health_check_processing, name='health_check_processing'),
    path('health-check/results/<str:session_id>/', views.health_check_results, name='health_check_results'),
    
    # File Downloads
    path('download/', views.download_tracker_file, name='download_tracker'),
    
    # API Endpoints
    path('validate-filename/', views.validate_filename, name='validate_filename'),
    path('get-previous-threshold/', views.get_previous_threshold, name='get_previous_threshold'),
    path('sticky-notes-data/', views.get_sticky_notes_data, name='sticky_notes_data'),
    
    # Legacy endpoints (keeping for backward compatibility during transition)
    path('upload_report/', views.upload_report_file, name='upload_report'),
    path('upload_host/', views.upload_host_file, name='upload_host'),
    path('tracker-history/', views.tracker_history, name='tracker_history'),
    path('delete-tracker/', views.delete_tracker_file, name='delete_tracker'),
    path('bulk-delete/', views.bulk_delete_files, name='bulk_delete'),
    path('cleanup-database/', views.cleanup_database_state, name='cleanup_database'),
    path('cleanup-duplicates/', views.cleanup_duplicate_records, name='cleanup_duplicates'),
    path('upload-old-tracker/', views.upload_old_tracker, name='upload_old_tracker'),
    path('upload-tracker-generated/', views.upload_tracker_generated, name='upload_tracker_generated'),
    path('batch-process/', views.batch_process_old_trackers_and_reports, name='batch_process'),
    
    # System Health Check Monitoring Endpoints
    path('health/', views.health_check, name='health_check'),
    path('health/detailed/', views.health_detailed, name='health_detailed'),
    path('health/database/', views.health_database, name='health_database'),
    path('health/time-sync/', views.health_time_sync, name='health_time_sync'),
      
]


 
