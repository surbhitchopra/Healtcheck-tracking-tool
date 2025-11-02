from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Customer(models.Model):
    """Network/Customer for Health Check Analysis"""
    name = models.CharField(max_length=255, help_text="Display name for the customer/organization")
    network_name = models.CharField(max_length=255, null=True, blank=True, help_text="Specific network name (e.g., East, West, North)")
    tec_network_name = models.CharField(max_length=255, default='Unknown', help_text="Network name as appears in TEC HC system")
    
    # Health Check setup status
    is_hc_enabled = models.BooleanField(default=False, help_text="Is Health Check analysis enabled")
    setup_status = models.CharField(max_length=50, choices=[
        ('NEW', 'New Network - Needs 5 files'),
        ('READY', 'Ready - Needs 2 files only'),
        ('INCOMPLETE', 'Setup Incomplete')
    ], default='NEW')
    
    # File tracking for initial setup (5 files for new network)
    has_hc_tracker = models.BooleanField(default=False, help_text="HC Issues Tracker uploaded")
    has_global_ignore_txt = models.BooleanField(default=False, help_text="Global ignore text file uploaded")
    has_selective_ignore_xlsx = models.BooleanField(default=False, help_text="Selective ignore xlsx uploaded")
    has_node_coverage = models.BooleanField(default=False, help_text="Node coverage updated from TEC hosts")
    
    # Last processing info
    last_hc_report_date = models.DateField(null=True, blank=True)
    last_hc_processing_date = models.DateTimeField(null=True, blank=True)
    last_generated_tracker = models.CharField(max_length=255, null=True, blank=True)
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.CharField(max_length=255, null=True, blank=True)
    delete_reason = models.TextField(null=True, blank=True)

    @property
    def display_name(self):
        """Get the display name with network if available"""
        if self.network_name:
            return f"{self.name} - {self.network_name}"
        return self.name
    
    @classmethod
    def get_customers_with_networks(cls):
        """Get customers grouped by name with their networks"""
        from collections import defaultdict
        customers_dict = defaultdict(list)
        
        for customer in cls.objects.filter(is_deleted=False).order_by('name', 'network_name'):
            customers_dict[customer.name].append(customer)
        
        return dict(customers_dict)
    
    @classmethod
    def get_networks_for_customer(cls, customer_name):
        """Get all networks for a specific customer name"""
        return cls.objects.filter(
            name=customer_name, 
            is_deleted=False
        ).order_by('network_name')
    
    def __str__(self):
        return self.display_name
    
    def soft_delete(self, user=None, reason=None):
        """Mark this customer as deleted but keep it in database for history"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user.username
        if reason:
            self.delete_reason = reason
        self.save()
    
    def restore(self):
        """Restore a soft-deleted customer"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.delete_reason = None
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to create customer directory structure"""
        is_new = self.pk is None  # Check if this is a new customer
        super().save(*args, **kwargs)
        
        # Create directory structure for new customers
        if is_new:
            self.create_directory_structure()
    
    def create_directory_structure(self):
        """Create directory structure for this customer in customer_files"""
        from pathlib import Path
        import os
        
        # Get base directory (assuming models.py is in Temperature_app)
        base_dir = Path(__file__).resolve().parent.parent
        customer_files_dir = base_dir / "customer_files"
        
        customer_dir = customer_files_dir / self.name.replace(" ", "_").replace("/", "_")
        
        try:
            customer_dir.mkdir(parents=True, exist_ok=True)
            (customer_dir / "host_files").mkdir(exist_ok=True)
            (customer_dir / "tec_reports").mkdir(exist_ok=True)
            (customer_dir / "generated_trackers").mkdir(exist_ok=True)
            (customer_dir / "old_trackers").mkdir(exist_ok=True)
            print(f"✅ AUTO-CREATED directory structure for customer: {self.name}")
            return True
        except Exception as e:
            print(f"❌ Failed to auto-create directory structure for {self.name}: {e}")
            return False

class UploadLog(models.Model):
    filename = models.CharField(max_length=255, default='unnamed')
    upload_type = models.CharField(max_length=50, default='UNKNOWN')  # 'TEC' or 'HOST'
    status = models.CharField(max_length=100, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='uploads', null=True, blank=True)
    threshold = models.IntegerField(null=True, blank=True)  # Temperature threshold for TEC uploads
    generated_file = models.CharField(max_length=255, null=True, blank=True)  # Generated tracker filename
    
    # Soft delete fields - for maintaining history
    is_deleted = models.BooleanField(default=False)  # Mark as deleted but keep in database
    deleted_at = models.DateTimeField(null=True, blank=True)  # When was it deleted
    deleted_by = models.CharField(max_length=255, null=True, blank=True)  # Who deleted it
    delete_reason = models.TextField(null=True, blank=True)  # Optional reason for deletion
    
    def __str__(self):
        return f"{self.upload_type} - {self.filename}"
    
    def soft_delete(self, user=None, reason=None):
        """Mark this record as deleted but keep it in database for history"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user.username
        if reason:
            self.delete_reason = reason
        self.save()
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.delete_reason = None
        self.save()
    
    class Meta:
        ordering = ['-timestamp']
    
    def get_network_directory_name(self):
        """Get directory name for this network"""
        return self.customer.name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    def is_ready_for_processing(self):
        """Check if network is ready for HC report processing"""
        return (self.customer.is_hc_enabled and 
                self.customer.is_initial_setup_complete and 
                self.customer.has_hc_tracker and 
                self.customer.has_global_ignore_txt and 
                self.customer.has_selective_ignore_xlsx and
                self.customer.node_coverage_updated)


class HealthCheckFile(models.Model):
    """Track individual Health Check files for each network"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='hc_files')
    
    # File information
    file_type = models.CharField(max_length=50, choices=[
        ('HC_TRACKER', 'HC Issues Tracker'),
        ('GLOBAL_IGNORE_TXT', 'Global Ignore Text File'),
        ('SELECTIVE_IGNORE_XLSX', 'Selective Ignore Excel File'),
        ('TEC_REPORT', 'TEC Health Check Report'),
        ('INVENTORY_CSV', 'Remote Inventory CSV'),
        ('TEMPLATE', 'Template File')
    ])
    
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, help_text="Full path to stored file")
    
    # File metadata
    file_size = models.BigIntegerField(null=True, blank=True)
    file_hash = models.CharField(max_length=64, null=True, blank=True)
    
    # Processing status
    status = models.CharField(max_length=50, choices=[
        ('UPLOADED', 'File Uploaded'),
        ('VALIDATED', 'File Validated'),
        ('PROCESSED', 'File Processed'),
        ('ERROR', 'Processing Error'),
        ('ARCHIVED', 'Archived')
    ], default='UPLOADED')
    
    # Processing information
    processing_notes = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Version tracking (for templates and trackers)
    version = models.CharField(max_length=20, default='1.0')
    is_current_version = models.BooleanField(default=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Health Check File"
        verbose_name_plural = "Health Check Files"
    
    def __str__(self):
        return f"{self.customer.name} - {self.file_type} - {self.original_filename}"


class HealthCheckSession(models.Model):
    """Track Health Check processing sessions"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='hc_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Session type
    session_type = models.CharField(max_length=50, choices=[
        ('NEW_NETWORK_SETUP', 'New Network Setup (5 files)'),
        ('REGULAR_PROCESSING', 'Regular HC Processing (2 files)'),
        ('TEMPLATE_UPDATE', 'Template Files Update')
    ])
    
    # Report identification
    report_date = models.DateField(null=True, blank=True, help_text="Date extracted from TEC report filename")
    
    # Processing status
    status = models.CharField(max_length=50, choices=[
        ('INITIATED', 'Processing Initiated'),
        ('UPLOADING', 'Files Uploading'),
        ('VALIDATING', 'Validating Files'),
        ('PROCESSING', 'Processing HC Report'),
        ('GENERATING', 'Generating Output'),
        ('COMPLETED', 'Processing Completed'),
        ('FAILED', 'Processing Failed'),
        ('CANCELLED', 'Processing Cancelled')
    ], default='INITIATED')
    
    # Files involved
    files_expected = models.IntegerField(help_text="Number of files expected")
    files_received = models.IntegerField(default=0, help_text="Number of files received")
    files_processed = models.IntegerField(default=0, help_text="Number of files processed")
    
    # Progress tracking
    progress_percentage = models.IntegerField(default=0)
    current_step = models.CharField(max_length=255, blank=True)
    
    # Processing results
    total_nodes_processed = models.IntegerField(null=True, blank=True)
    total_test_cases_processed = models.IntegerField(null=True, blank=True)
    issues_found = models.IntegerField(null=True, blank=True)
    issues_ignored = models.IntegerField(null=True, blank=True)
    new_nodes_discovered = models.IntegerField(null=True, blank=True)
    
    # Output files
    output_tracker_filename = models.CharField(max_length=255, null=True, blank=True)
    output_tracker_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Processing timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_duration = models.DurationField(null=True, blank=True)
    
    # Processing logs and messages
    processing_log = models.TextField(blank=True, help_text="Detailed processing log")
    error_messages = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    
    # User information
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Health Check Session"
        verbose_name_plural = "Health Check Sessions"
    
    def __str__(self):
        return f"{self.customer.name} - {self.session_type} ({self.status})"
    
    def get_processing_duration_str(self):
        """Get human-readable processing duration"""
        if self.processing_duration:
            total_seconds = int(self.processing_duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return "N/A"
    
    def update_status(self, new_status, message=None):
        """Update processing status with optional message"""
        self.status = new_status
        if message:
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            self.processing_log += f"\n[{timestamp}] {new_status}: {message}"
        self.save()
    
    def add_log_entry(self, message, level='INFO'):
        """Add entry to session log"""
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.processing_log += log_entry
        self.save(update_fields=['processing_log'])
    
    def update_progress(self, percentage, step=None):
        """Update session progress"""
        self.progress_percentage = percentage
        if step:
            self.current_step = step
        self.save(update_fields=['progress_percentage', 'current_step'])
    
    def get_required_files_for_new_network(self):
        """Get list of required files for new network setup"""
        network_name = self.customer.tec_network_name
        return [
            f"{network_name}_HC_Issues_Tracker.xlsx",
            f"{network_name}_ignored_test_cases.txt", 
            f"{network_name}_ignored_test_cases.xlsx",
            "TEC_Health_Check_Report.xlsx",
            "Remote_Inventory.csv"
        ]
    
    def get_required_files_for_existing_network(self):
        """Get list of required files for existing network processing"""
        return [
            "TEC_Health_Check_Report.xlsx",
            "Remote_Inventory.csv"
        ]


class NodeCoverage(models.Model):
    """Node coverage information from TEC hosts file"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='node_coverage')
    
    # Node identification from TEC hosts file
    hc_id = models.IntegerField(help_text="Health Check ID from TEC system")
    node_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    ne_type = models.CharField(max_length=100, blank=True, help_text="Network Element Type")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Additional information
    region = models.CharField(max_length=100, blank=True)
    site_code = models.CharField(max_length=50, blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    software_version = models.CharField(max_length=100, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_monitored = models.BooleanField(default=True, help_text="Include in HC monitoring")
    
    # Last seen information
    first_discovered = models.DateTimeField(auto_now_add=True)
    last_seen_in_report = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['customer', 'hc_id']
        ordering = ['hc_id']
        verbose_name = "Node Coverage"
        verbose_name_plural = "Node Coverage"
    
    def __str__(self):
        return f"HC{self.hc_id} - {self.node_name or 'Unknown'} ({self.customer.name})"


class IgnoredTestCase(models.Model):
    """Track ignored test cases for each network"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ignored_test_cases')
    
    # Test case identification
    test_case_id = models.CharField(max_length=50, help_text="Test case ID like 5.2.1")
    test_description = models.CharField(max_length=500, blank=True)
    
    # Ignore type
    ignore_type = models.CharField(max_length=50, choices=[
        ('GLOBAL', 'Global - Ignore for entire network'),
        ('SELECTIVE', 'Selective - Ignore for specific HC IDs')
    ])
    
    # For selective ignores
    hc_id = models.IntegerField(null=True, blank=True, help_text="Specific HC ID to ignore (for selective)")
    priority = models.CharField(max_length=20, blank=True, help_text="Test priority")
    findings = models.TextField(blank=True, help_text="Specific findings to ignore")
    
    # Metadata
    reason = models.TextField(blank=True, help_text="Reason for ignoring this test case")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['test_case_id', 'hc_id']
        verbose_name = "Ignored Test Case"
        verbose_name_plural = "Ignored Test Cases"
    
    def __str__(self):
        if self.ignore_type == 'GLOBAL':
            return f"{self.customer.name} - Global Ignore: {self.test_case_id}"
        else:
            return f"{self.customer.name} - HC{self.hc_id}: {self.test_case_id}"
