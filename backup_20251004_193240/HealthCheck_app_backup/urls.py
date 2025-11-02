from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    
    # Customer/Network Management URLs
    path('', views.customer_selection, name='customer_selection'),
    path('dashboard/', views.health_check_dashboard, name='dashboard'),
    path('live-dashboard/', views.comprehensive_dashboard, name='comprehensive_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer-dashboard/excel/', views.customer_dashboard_excel, name='customer_dashboard_excel'),
    path('customer-excel-dashboard/', views.customer_dashboard_excel_page, name='customer_dashboard_excel_page'),
    path('test-excel/', views.test_excel_dashboard, name='test_excel_dashboard'),
    
    # Network Setup URLs (Per MOP for NEW networks)
    path('setup/<int:customer_id>/', views.setup_new_network, name='setup_new_network'),
    
    # Health Check Processing URLs (Enhanced)
    path('upload/<int:customer_id>/', views.health_check_upload, name='health_check_upload'),
    path('process/<int:customer_id>/', views.process_health_check_enhanced, name='process_health_check_enhanced'),
    # Processing page removed - redirect to dashboard instead
    # path('processing/<str:session_id>/', views.health_check_processing, name='health_check_processing'),
    path('results/<str:session_id>/', views.health_check_results, name='health_check_results'),
    
    # File Download URLs
    path('download/tracker/', views.download_tracker_file, name='download_tracker_file'),
    path('download/report/', views.download_report_file, name='download_report_file'),
    path('download/inventory/', views.download_inventory_file, name='download_inventory_file'),
    path('download/host/', views.download_host_file, name='download_host_file'),
    
    # Individual Folder Upload Endpoints
    path('upload-host/', views.upload_host_file, name='upload_host_file'),
    path('upload-inventory/', views.upload_inventory_file, name='upload_inventory_file'),
    path('upload-report/', views.upload_report_file, name='upload_report_file'), 
    path('upload-old-tracker/', views.upload_old_tracker_file, name='upload_old_tracker_file'),
    path('upload-tracker-generated/', views.upload_tracker_generated_file, name='upload_tracker_generated_file'),
    path('upload-ignore-excel/', views.upload_ignore_excel_file, name='upload_ignore_excel_file'),
    path('upload-ignore-text/', views.upload_ignore_text_file, name='upload_ignore_text_file'),
    
    # API Endpoints
    path('api/validate-filename/', views.validate_filename, name='validate_filename'),
    path('api/session-status/<str:session_id>/', views.session_status, name='session_status'),
    path('get-customer-networks/<int:customer_id>/', views.get_customer_networks, name='get_customer_networks'),
    path('api/networks/<str:customer_name>/', views.get_networks_for_customer, name='get_networks_for_customer'),
    path('api/excel-networks/', views.get_excel_networks, name='get_excel_networks'),
    path('api/integrated-excel-data/', views.get_integrated_excel_data, name='get_integrated_excel_data'),
    path('api/tracker-history/', views.tracker_history, name='tracker_history'),
    path('api/sticky-notes-data/', views.get_sticky_notes_data, name='sticky_notes_data'),
    path('api/delete-tracker/', views.delete_tracker_file, name='delete_tracker'),
    
    # Run Statistics API Endpoints
    path('api/run-statistics/', views.api_run_statistics, name='api_run_statistics'),
    # path('api/monthly-run-stats/', views.api_monthly_run_stats, name='api_monthly_run_stats'), # REMOVED
    # path('api/customer-run-stats/<int:customer_id>/', views.api_customer_run_stats, name='api_customer_run_stats'), # MISSING
    
    # Dashboard API Endpoints
    path('api/dashboard/customers/', views.api_dashboard_customers, name='api_dashboard_customers'),
    path('api/dashboard/statistics/', views.api_dashboard_statistics, name='api_dashboard_statistics'),
    
    # Customer Dashboard API Endpoints
    path('api/customer-dashboard/customers/', views.api_customer_dashboard_customers, name='api_customer_dashboard_customers'),
    path('api/customer-dashboard/statistics/', views.api_customer_dashboard_statistics, name='api_customer_dashboard_statistics'),
    path('api/customer-dashboard/export/', views.api_customer_dashboard_export, name='api_customer_dashboard_export'),
    
    # Excel Export API
    path('api/export-excel/', views.api_export_excel, name='api_export_excel'),
    path('api/simple-export-test/', views.simple_export_test, name='simple_export_test'),
    
    # Real Data APIs for Monthly and Network Sessions
    path('api/customer-monthly-sessions/', views.api_customer_monthly_sessions, name='api_customer_monthly_sessions'),
    path('api/network-sessions/', views.api_network_sessions, name='api_network_sessions'),
    
    # Debug endpoints (remove after testing)
    path('api/debug-customer-data/', views.debug_customer_data, name='debug_customer_data'),
    path('api/test-date-filter/', views.test_date_filter_debug, name='test_date_filter_debug'),
    path('api/test-excel-debug/', views.test_excel_debug, name='test_excel_debug'),
]
