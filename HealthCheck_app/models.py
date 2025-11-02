from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    User profile for region-based access control
    Maps users to their assigned regions/networks for validation
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_check_profile')
    
    # Region assignments
    assigned_operators = models.TextField(
        blank=True, 
        help_text="Comma-separated list of operators this user can access (e.g., 'BSNL,AIRTEL')"
    )
    assigned_regions = models.TextField(
        blank=True,
        help_text="Comma-separated list of regions this user can access (e.g., 'NORTH,SOUTH')"
    )
    assigned_technologies = models.TextField(
        blank=True,
        help_text="Comma-separated list of technologies this user can access (e.g., 'DWDM,MPLS')"
    )
    assigned_locations = models.TextField(
        blank=True,
        help_text="Comma-separated list of locations this user can access (e.g., 'MUMBAI,DELHI')"
    )
    
    # Access control settings
    is_super_user = models.BooleanField(
        default=False,
        help_text="Super users can access any region/network"
    )
    enforce_strict_validation = models.BooleanField(
        default=True,
        help_text="Enforce strict region-based validation for this user"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def get_assigned_operators_list(self):
        """Get list of assigned operators"""
        if not self.assigned_operators.strip():
            return []
        return [op.strip().upper() for op in self.assigned_operators.split(',') if op.strip()]
    
    def get_assigned_regions_list(self):
        """Get list of assigned regions"""
        if not self.assigned_regions.strip():
            return []
        return [region.strip().upper() for region in self.assigned_regions.split(',') if region.strip()]
    
    def get_assigned_technologies_list(self):
        """Get list of assigned technologies"""
        if not self.assigned_technologies.strip():
            return []
        return [tech.strip().upper() for tech in self.assigned_technologies.split(',') if tech.strip()]
    
    def get_assigned_locations_list(self):
        """Get list of assigned locations"""
        if not self.assigned_locations.strip():
            return []
        return [loc.strip().upper() for loc in self.assigned_locations.split(',') if loc.strip()]
    
    def can_access_customer(self, customer_name):
        """
        Check if user can access a specific customer based on region assignments
        """
        if self.is_super_user or not self.enforce_strict_validation:
            return True, "Super user or strict validation disabled"
        
        customer_upper = customer_name.upper()
        customer_words = set(customer_upper.replace('_', ' ').replace('-', ' ').split())
        
        # Check operator access
        assigned_operators = self.get_assigned_operators_list()
        if assigned_operators:
            user_operators = set(assigned_operators)
            customer_operators = customer_words.intersection({'BSNL', 'AIRTEL', 'JIO', 'VI', 'VODAFONE', 'IDEA', 'RELIANCE', 'TATA', 'BHARTI'})
            
            if customer_operators and not customer_operators.intersection(user_operators):
                return False, f"User assigned to {'/'.join(user_operators)} but customer is {'/'.join(customer_operators)}"
        
        # Check region access
        assigned_regions = self.get_assigned_regions_list()
        if assigned_regions:
            user_regions = set(assigned_regions)
            customer_regions = customer_words.intersection({'NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL', 'NORTHEAST'})
            
            if customer_regions and not customer_regions.intersection(user_regions):
                return False, f"User assigned to {'/'.join(user_regions)} but customer is {'/'.join(customer_regions)}"
        
        # Check technology access
        assigned_technologies = self.get_assigned_technologies_list()
        if assigned_technologies:
            user_technologies = set(assigned_technologies)
            customer_technologies = customer_words.intersection({'DWDM', 'SDH', 'MPLS', 'OTN', 'SONET', 'IP', 'ETHERNET', 'FIBER', 'OPTICAL'})
            
            if customer_technologies and not customer_technologies.intersection(user_technologies):
                return False, f"User assigned to {'/'.join(user_technologies)} but customer uses {'/'.join(customer_technologies)}"
        
        # Check location access
        assigned_locations = self.get_assigned_locations_list()
        if assigned_locations:
            user_locations = set(assigned_locations)
            customer_locations = customer_words.intersection({
                'MUMBAI', 'DELHI', 'KOLKATA', 'CHENNAI', 'BANGALORE', 'HYDERABAD', 'PUNE', 'AHMEDABAD',
                'JAIPUR', 'LUCKNOW', 'KANPUR', 'NAGPUR', 'INDORE', 'THANE', 'BHOPAL', 'VISAKHAPATNAM',
                'PATNA', 'VADODARA', 'GHAZIABAD', 'LUDHIANA', 'RAJKOT', 'KOCHI', 'AURANGABAD', 'COIMBATORE',
                'MAHARASHTRA', 'GUJARAT', 'KARNATAKA', 'TAMILNADU', 'TELANGANA', 'RAJASTHAN', 'PUNJAB',
                'HARYANA', 'UP', 'UTTARPRADESH', 'MP', 'MADHYAPRADESH', 'WB', 'WESTBENGAL'
            })
            
            if customer_locations and not customer_locations.intersection(user_locations):
                return False, f"User assigned to {'/'.join(user_locations)} but customer is in {'/'.join(customer_locations)}"
        
        return True, "Access granted"
    
    def __str__(self):
        return f"{self.user.username} - Profile"


class Customer(models.Model):
    name = models.CharField(max_length=255, help_text="Customer/Organization name (e.g., BSNL)")
    network_name = models.CharField(max_length=100, null=True, blank=True, help_text="Network name (e.g., East, West, North)")
    network_type = models.CharField(max_length=100, default='Unknown', help_text="Type of network")
    setup_status = models.CharField(max_length=20, default='NEW')  # NEW, READY
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    # Extended fields for Excel dashboard data
    country = models.CharField(max_length=100, null=True, blank=True, help_text="Country where network is located")
    node_qty = models.IntegerField(default=0, help_text="Number of nodes in network")
    ne_type = models.CharField(max_length=100, null=True, blank=True, help_text="Network Element type (e.g., 1830 PSS)")
    gtac = models.CharField(max_length=100, null=True, blank=True, help_text="Global Technical Assistance Center")
    
    # Monthly run data (JSON field to store monthly dates)
    monthly_runs = models.JSONField(default=dict, blank=True, help_text="Monthly health check run dates")
    total_runs = models.IntegerField(default=0, help_text="Total number of health check runs")
    
    class Meta:
        verbose_name = 'Customer Network'
        verbose_name_plural = 'Customer Networks'
    
    def get_directory_name(self):
        """Get directory name for this customer"""
        return self.name.replace(' ', '_').replace('-', '_').lower()
    
    
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
    
    @classmethod
    def get_networks_for_customer_by_id(cls, customer_id):
        """Get all networks for a specific customer by ID"""
        try:
            customer = cls.objects.get(id=customer_id, is_deleted=False)
            return cls.objects.filter(
                name=customer.name, 
                is_deleted=False
            ).order_by('network_name')
        except cls.DoesNotExist:
            return cls.objects.none()
    
    def __str__(self):
        return self.display_name


class HealthCheckSession(models.Model):
    SESSION_TYPES = [
        ('NEW_NETWORK_SETUP', 'New Network Setup'),
        ('REGULAR_PROCESSING', 'Regular Processing'),
        ('MAINTENANCE', 'Maintenance Check'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UPLOADING', 'Uploading Files'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hc_sessions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    files_expected = models.IntegerField(default=0)
    files_received = models.IntegerField(default=0)
    progress_percentage = models.IntegerField(default=0)
    current_step = models.CharField(max_length=255, blank=True)
    output_tracker_filename = models.CharField(max_length=255, blank=True)
    output_tracker_path = models.CharField(max_length=500, blank=True)
    status_message = models.TextField(blank=True)
    error_messages = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Health Check Session'
        verbose_name_plural = 'Health Check Sessions'
    
    def update_status(self, status, message=''):
        self.status = status
        self.status_message = message
        if status == 'COMPLETED':
            self.completed_at = timezone.now()
        
        # Save session FIRST to avoid race condition
        self.save()
        
        # Then update customer data AFTER session is saved
        if status == 'COMPLETED':
            self._update_customer_monthly_runs()
    
    def _update_customer_monthly_runs(self):
        """Update customer's monthly_runs field when session completes - RACE CONDITION FIXED"""
        try:
            # Get current date in YYYY-MM-DD format
            completion_date = self.completed_at or timezone.now()
            current_month_key = completion_date.strftime('%Y-%m')  # e.g., '2025-10'
            current_date_value = completion_date.strftime('%Y-%m-%d')  # e.g., '2025-10-08'
            
            # Initialize monthly_runs if it doesn't exist
            if not self.customer.monthly_runs:
                self.customer.monthly_runs = {}
            
            # Update the current month with today's date
            self.customer.monthly_runs[current_month_key] = current_date_value
            
            # FIXED RACE CONDITION: Count completed sessions INCLUDING this current session
            # Since this session is being marked as COMPLETED right now
            actual_completed_sessions = HealthCheckSession.objects.filter(
                customer=self.customer,
                status='COMPLETED'
            ).count()
            
            # Add 1 because this current session is now COMPLETED (race condition fix)
            if self.status == 'COMPLETED':
                actual_completed_sessions = actual_completed_sessions  # Already included in count since save() happens after
            
            # Update total_runs to reflect actual completed sessions
            self.customer.total_runs = actual_completed_sessions
            
            # Save the customer
            self.customer.save()
            
            print(f"Updated {self.customer.name} monthly_runs: {current_month_key} = {current_date_value}")
            print(f"Updated total_runs to {actual_completed_sessions} (including current session)")
            
        except Exception as e:
            print(f"Error updating monthly_runs for {self.customer.name}: {e}")
    
    def get_processing_duration_str(self):
        """Get human-readable processing duration"""
        if not self.completed_at:
            # Still processing, calculate from created_at
            from datetime import datetime
            duration = timezone.now() - self.created_at
        else:
            duration = self.completed_at - self.created_at
        
        # Format duration
        seconds = int(duration.total_seconds())
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minutes"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def __str__(self):
        return f"{self.customer.name} - {self.session_id}"


class HealthCheckFile(models.Model):
    FILE_TYPES = [
        ('CONFIG', 'Configuration File'),
        ('NETWORK_MAP', 'Network Map'),
        ('NODE_LIST', 'Node List'),
        ('SERVICE_CONFIG', 'Service Configuration'),
        ('BASELINE', 'Baseline Data'),
        ('HC_TRACKER', 'HC Issues Tracker'),
        ('TRACKER_GENERATED', 'Generated Tracker'),
        ('GLOBAL_IGNORE_TXT', 'Global Ignore Text'),
        ('SELECTIVE_IGNORE_XLSX', 'Selective Ignore Excel'),
        ('TEC_REPORT', 'TEC Health Check Report'),
        ('INVENTORY_CSV', 'Inventory CSV'),
        ('HOST', 'Host File'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    session = models.ForeignKey(HealthCheckSession, on_delete=models.SET_NULL, null=True, blank=True)
    file_type = models.CharField(max_length=30, choices=FILE_TYPES)
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Health Check File'
        verbose_name_plural = 'Health Check Files'
    
    def __str__(self):
        return f"{self.customer.name} - {self.original_filename}"


class NodeCoverage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    session = models.ForeignKey(HealthCheckSession, on_delete=models.CASCADE)
    node_name = models.CharField(max_length=255)
    node_ip = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default='Unknown')  # Online, Offline, Warning
    ping_status = models.BooleanField(default=False)
    response_time = models.FloatField(null=True, blank=True)  # in milliseconds
    last_checked = models.DateTimeField(auto_now=True)
    services_count = models.IntegerField(default=0)
    services_healthy = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Node Coverage'
        verbose_name_plural = 'Node Coverage'
    
    def __str__(self):
        return f"{self.node_name} - {self.status}"


class ServiceCheck(models.Model):
    node = models.ForeignKey(NodeCoverage, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)  # HTTP, TCP, UDP, etc.
    port = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Unknown')  # Healthy, Unhealthy, Timeout
    response_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Service Check'
        verbose_name_plural = 'Service Checks'
    
    def __str__(self):
        return f"{self.node.node_name} - {self.service_name}"


