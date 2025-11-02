from django.contrib import admin
from .models import Customer, UploadLog

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_upload_count', 'get_last_upload']
    search_fields = ['name']
    
    def get_upload_count(self, obj):
        return obj.uploads.count()
    get_upload_count.short_description = 'Upload Count'
    
    def get_last_upload(self, obj):
        last_upload = obj.uploads.first()
        if last_upload:
            return last_upload.timestamp.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    get_last_upload.short_description = 'Last Upload'

@admin.register(UploadLog)
class UploadLogAdmin(admin.ModelAdmin):
    list_display = ['filename', 'customer', 'upload_type', 'status', 'threshold', 'generated_file', 'timestamp']
    list_filter = ['upload_type', 'status', 'customer', 'timestamp']
    search_fields = ['filename', 'customer__name', 'generated_file']
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')


