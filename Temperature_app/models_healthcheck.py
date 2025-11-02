from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Customer  # Import existing Customer model

class HealthCheckNetwork(models.Model):
    """Health Check Network tracking - complements existing Customer model"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='hc_network')
    
    # Network identification
    tec_network_name = models.CharField(max_length=255, unique=True, help_text="Network name as appears in TEC HC system")
    
    # Status tracking
    is_hc_enabled = models.BooleanField(default=False, help_text="Is Health Check analysis enabled")
    is_initial_setup_complete = models.BooleanField(default=False, help_text="Are all 5 initial files created")
    
    # File tracking for initial setup
    has_hc_tracker = models.BooleanField(default=False)
    has_global_ignore_txt = models.BooleanField(default=False) 
    has_selective_ignore_xlsx = models.BooleanField(default=False)
    
    # Last processing info
    last_hc_report_date = models.DateField(null=True, blank=True)
    last_hc_processing_date = models.DateTimeField(null=True, blank=True)
    last_generated_tracker = models.CharField(max_length=255, null=True, blank=True)
    
    # Configuration
    node_coverage_updated = models.BooleanField(default=False, help_text="NODE COVERAGE sheet filled from TEC hosts file")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Health Check Network"
        verbose_name_plural = "Health Check Networks"
    
    def __str__(self):
        return f"HC Network: {self.tec_network_name}"
    
    def get_network_directory_name(self):
        """Get directory name for this network"""
        return self.tec_network_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    def is_ready_for_processing(self):
        """Check if network is ready for HC report processing"""
        return (self.is_hc_enabled and 
                self.is_initial_setup_complete and 
                self.has_hc_tracker and 
                self.has_global_ignore_txt and 
                self.has_selective_ignore_xlsx and
                self.node_coverage_updated)
    
    def get_required_files_for_new_network(self):
        """Get list of required files for new network setup"""
        network_name = self.tec_network_name
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


class HealthCheckFile(models.Model):
    """Track individual Health Check files for each network"""
    hc_network = models.ForeignKey(HealthCheckNetwork, on_delete=models.CASCADE, related_name='hc_files')
    
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
        return f"{self.hc_network.tec_network_name} - {self.file_type} - {self.original_filename}"


class HealthCheckReport(models.Model):
    """Track Health Check report processing sessions"""
    hc_network = models.ForeignKey(HealthCheckNetwork, on_delete=models.CASCADE, related_name='hc_reports')
    
    # Report identification
    report_date = models.DateField(help_text="Date extracted from TEC report filename")
    session_id = models.CharField(max_length=100, unique=True, help_text="Unique session ID for this processing")
    
    # Input files for this session
    tec_report_file = models.ForeignKey(HealthCheckFile, on_delete=models.CASCADE, 
                                      related_name='tec_reports', null=True, blank=True)
    inventory_file = models.ForeignKey(HealthCheckFile, on_delete=models.CASCADE,
                                     related_name='inventory_reports', null=True, blank=True)
    
    # Processing status
    status = models.CharField(max_length=50, choices=[
        ('INITIATED', 'Processing Initiated'),
        ('VALIDATING', 'Validating Files'),
        ('PROCESSING', 'Processing HC Report'),
        ('GENERATING', 'Generating Output'),
        ('COMPLETED', 'Processing Completed'),
        ('FAILED', 'Processing Failed'),
        ('CANCELLED', 'Processing Cancelled')
    ], default='INITIATED')
    
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
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['hc_network', 'report_date', 'session_id']
        verbose_name = "Health Check Report Session"
        verbose_name_plural = "Health Check Report Sessions"
    
    def __str__(self):
        return f"{self.hc_network.tec_network_name} - {self.report_date} ({self.status})"
    
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


class NodeCoverage(models.Model):
    """Node coverage information from TEC hosts file"""
    hc_network = models.ForeignKey(HealthCheckNetwork, on_delete=models.CASCADE, related_name='node_coverage')
    
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
        unique_together = ['hc_network', 'hc_id']
        ordering = ['hc_id']
        verbose_name = "Node Coverage"
        verbose_name_plural = "Node Coverage"
    
    def __str__(self):
        return f"HC{self.hc_id} - {self.node_name or 'Unknown'} ({self.hc_network.tec_network_name})"


class IgnoredTestCase(models.Model):
    """Track ignored test cases for each network"""
    hc_network = models.ForeignKey(HealthCheckNetwork, on_delete=models.CASCADE, related_name='ignored_test_cases')
    
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
            return f"{self.hc_network.tec_network_name} - Global Ignore: {self.test_case_id}"
        else:
            return f"{self.hc_network.tec_network_name} - HC{self.hc_id}: {self.test_case_id}"


class TemplateFile(models.Model):
    """Track template files used for network setup"""
    
    # Template information
    template_type = models.CharField(max_length=50, choices=[
        ('HC_TRACKER', 'Template_HC_Issues_Tracker.xlsx'),
        ('GLOBAL_IGNORE_TXT', 'Template_ignored_test_cases.txt'),
        ('SELECTIVE_IGNORE_XLSX', 'Template_ignored_test_cases.xlsx')
    ])
    
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    
    # Version information
    version = models.CharField(max_length=20, default='1.0')
    is_current = models.BooleanField(default=True)
    
    # File metadata
    file_size = models.BigIntegerField(null=True, blank=True)
    file_hash = models.CharField(max_length=64, null=True, blank=True)
    
    # Description and notes
    description = models.TextField(blank=True)
    changelog = models.TextField(blank=True, help_text="Changes in this version")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['template_type', '-version']
        unique_together = ['template_type', 'version']
        verbose_name = "Template File"
        verbose_name_plural = "Template Files"
    
    def __str__(self):
        return f"{self.template_type} v{self.version} ({'Current' if self.is_current else 'Old'})"


class ProcessingSession(models.Model):
    """Track overall processing sessions for monitoring and debugging"""
    session_id = models.CharField(max_length=100, unique=True)
    hc_network = models.ForeignKey(HealthCheckNetwork, on_delete=models.CASCADE, related_name='processing_sessions')
    
    # Session type
    session_type = models.CharField(max_length=50, choices=[
        ('NEW_NETWORK_SETUP', 'New Network Setup (5 files)'),
        ('REGULAR_PROCESSING', 'Regular HC Processing (2 files)'),
        ('TEMPLATE_UPDATE', 'Template Files Update'),
        ('NODE_COVERAGE_UPDATE', 'Node Coverage Update')
    ])
    
    # Session status
    status = models.CharField(max_length=50, choices=[
        ('STARTED', 'Session Started'),
        ('UPLOADING', 'Files Uploading'),
        ('VALIDATING', 'Validating Files'),
        ('PROCESSING', 'Processing Data'),
        ('COMPLETED', 'Session Completed'),
        ('FAILED', 'Session Failed'),
        ('CANCELLED', 'Session Cancelled')
    ], default='STARTED')
    
    # Files involved
    files_expected = models.IntegerField(help_text="Number of files expected")
    files_received = models.IntegerField(default=0, help_text="Number of files received")
    files_processed = models.IntegerField(default=0, help_text="Number of files processed")
    
    # Progress tracking
    progress_percentage = models.IntegerField(default=0)
    current_step = models.CharField(max_length=255, blank=True)
    
    # Results
    success = models.BooleanField(default=False)
    output_files_generated = models.JSONField(default=list, blank=True)
    
    # Logs and messages
    session_log = models.TextField(blank=True)
    error_messages = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # User
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Processing Session"
        verbose_name_plural = "Processing Sessions"
    
    def __str__(self):
        return f"{self.hc_network.tec_network_name} - {self.session_type} ({self.status})"
    
    def add_log_entry(self, message, level='INFO'):
        """Add entry to session log"""
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.session_log += log_entry
        self.save(update_fields=['session_log'])
    
    def update_progress(self, percentage, step=None):
        """Update session progress"""
        self.progress_percentage = percentage
        if step:
            self.current_step = step
        self.save(update_fields=['progress_percentage', 'current_step'])
