from django.contrib import admin
from .models import (
    Customer, 
    HealthCheckSession, 
    HealthCheckFile, 
    NodeCoverage, 
    ServiceCheck
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'network_type', 'setup_status', 'created_at', 'is_deleted']
    list_filter = ['network_type', 'setup_status', 'is_deleted']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(HealthCheckSession)
class HealthCheckSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'customer', 'session_type', 'status', 'initiated_by', 'created_at']
    list_filter = ['session_type', 'status', 'created_at']
    search_fields = ['session_id', 'customer__name', 'initiated_by__username']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(HealthCheckFile)
class HealthCheckFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'customer', 'file_type', 'uploaded_at', 'file_size']
    list_filter = ['file_type', 'uploaded_at', 'is_processed']
    search_fields = ['original_filename', 'customer__name']
    readonly_fields = ['uploaded_at']


@admin.register(NodeCoverage)
class NodeCoverageAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'customer', 'status', 'ping_status', 'response_time', 'last_checked']
    list_filter = ['status', 'ping_status', 'last_checked']
    search_fields = ['node_name', 'node_ip', 'customer__name']
    readonly_fields = ['last_checked']


@admin.register(ServiceCheck)
class ServiceCheckAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'node', 'service_type', 'status', 'port', 'checked_at']
    list_filter = ['service_type', 'status', 'checked_at']
    search_fields = ['service_name', 'node__node_name']
    readonly_fields = ['checked_at']


