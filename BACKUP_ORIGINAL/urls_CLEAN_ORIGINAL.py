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
    
    # Network Setup URLs (Per MOP for NEW networks)
    path('setup/<int:customer_id>/', views.setup_new_network, name='setup_new_network'),
    
    # Health Check Processing URLs (Enhanced)
    path('upload/<int:customer_id>/', views.health_check_upload, name='health_check_upload'),
    path('process/<int:customer_id>/', views.process_health_check_enhanced, name='process_health_check_enhanced'),
    path('processing/<str:session_id>/', views.health_check_processing, name='health_check_processing'),
    path('results/<str:session_id>/', views.health_check_results, name='health_check_results'),
    
    # File Download URLs
    path('download/tracker/', views.download_tracker_file, name='download_tracker_file'),
    
    # API Endpoints
    path('api/validate-filename/', views.validate_filename, name='validate_filename'),
    path('api/session-status/<str:session_id>/', views.session_status, name='session_status'),
]
