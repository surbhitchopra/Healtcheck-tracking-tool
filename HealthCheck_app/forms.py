from django import forms
from .models import Customer, HealthCheckSession

# Excel integration removed - using only database customers


class CustomerSelectionForm(forms.Form):
    """Form for selecting existing customers/networks"""
    customer = forms.ChoiceField(
        choices=[],  # Will be populated in the view
        widget=forms.Select(attrs={
            'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-700',
            'id': 'customer-select'
        })
    )
    
    remove_customer = forms.ChoiceField(
        choices=[],  # Will be populated in the view
        required=False,
        widget=forms.Select(attrs={
            'class': 'flex-1 p-2 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-red-400',
            'id': 'remove-customer-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get unique customer names with at least one customer ID for each name
        customer_data = Customer.objects.filter(is_deleted=False).values('id', 'name').order_by('name')
        
        # Group by name and take the first ID for each unique name
        seen_names = set()
        db_choices = [('', 'Select a customer...')]
        remove_choices = [('', 'Remove customer...')]
        
        for customer in customer_data:
            name = customer['name']
            if name not in seen_names:
                db_choices.append((customer['id'], name))
                remove_choices.append((name, name))  # Use name as both value and display
                seen_names.add(name)
        
        # Use only database choices (Excel integration disabled)
        self.fields['customer'].choices = db_choices
        
        self.fields['remove_customer'].choices = remove_choices


class CustomerCreationForm(forms.ModelForm):
    """Form for creating new customers/networks"""
    customer_name = forms.CharField(
        max_length=255,
        label="Customer Name",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-1 focus:ring-blue-400',
            'placeholder': 'Enter customer name...',
            'required': True
        })
    )
    
    network_name = forms.CharField(
        max_length=255,
        label="Network Name",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-1 focus:ring-blue-400',
            'placeholder': 'Enter network name (optional)...'
        })
    )
    
    class Meta:
        model = Customer
        fields = ['network_type']
        widgets = {
            'network_type': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-1 focus:ring-blue-400'
            })
        }
        
    def clean(self):
        cleaned_data = super().clean()
        customer_name = cleaned_data.get('customer_name')
        network_name = cleaned_data.get('network_name')
        
        if customer_name and network_name:
            # Check if this customer-network combination already exists
            if Customer.objects.filter(
                name=customer_name, 
                network_name=network_name, 
                is_deleted=False
            ).exists():
                raise forms.ValidationError(f"Network '{network_name}' already exists for customer '{customer_name}'.")
        
        return cleaned_data


class HealthCheckNewNetworkForm(forms.Form):
    """Form for uploading files for new network setup per MOP requirements"""
    hc_tracker_file = forms.FileField(
        label="HC Issues Tracker Template (.xlsx/.csv)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text="Upload Template_HC_Issues_Tracker.xlsx or .csv (rename after network setup)"
    )
    
    global_ignore_txt = forms.FileField(
        label="Global Ignore Test Cases (.txt)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.txt'
        }),
        help_text="Upload Template_ignored_test_cases.txt (default contains test case 5.2.1)"
    )
    
    selective_ignore_xlsx = forms.FileField(
        label="Selective Ignore Test Cases (.xlsx/.csv)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text="Upload Template_ignored_test_cases.xlsx or .csv for specific HC Id/Test combinations"
    )
    
    def clean_hc_tracker_file(self):
        file = self.cleaned_data['hc_tracker_file']
        if file:
            if not file.name.endswith(('.xlsx', '.xls', '.csv')):
                raise forms.ValidationError("HC Tracker file must be an Excel file (.xlsx or .xls) or CSV file (.csv)")
            
            # ===== STRICT FILE TYPE VALIDATION =====
            # Import validation function
            from .views import validate_file_type_match
            validation_result = validate_file_type_match(file.name, 'TRACKER')
            if not validation_result['valid']:
                raise forms.ValidationError(f"🚫 WRONG FILE TYPE: {validation_result['error']}")
            
            if file.size > 50 * 1024 * 1024:  # 50MB limit
                raise forms.ValidationError("HC Tracker file must be smaller than 50MB")
        return file
    
    def clean_global_ignore_txt(self):
        file = self.cleaned_data['global_ignore_txt']
        if file:
            if not file.name.endswith('.txt'):
                raise forms.ValidationError("Global ignore file must be a text file (.txt)")
            
            # ===== STRICT FILE TYPE VALIDATION =====
            # Import validation function
            from .views import validate_file_type_match
            validation_result = validate_file_type_match(file.name, 'IGNORE')
            if not validation_result['valid']:
                raise forms.ValidationError(f"🚫 WRONG FILE TYPE: {validation_result['error']}")
            
            if file.size > 1 * 1024 * 1024:  # 1MB limit
                raise forms.ValidationError("Global ignore file must be smaller than 1MB")
        return file
    
    def clean_selective_ignore_xlsx(self):
        file = self.cleaned_data['selective_ignore_xlsx']
        if file:
            if not file.name.endswith(('.xlsx', '.xls', '.csv')):
                raise forms.ValidationError("Selective ignore file must be an Excel file (.xlsx or .xls) or CSV file (.csv)")
            
            # ===== STRICT FILE TYPE VALIDATION =====
            # Import validation function
            from .views import validate_file_type_match
            validation_result = validate_file_type_match(file.name, 'IGNORE')
            if not validation_result['valid']:
                raise forms.ValidationError(f"🚫 WRONG FILE TYPE: {validation_result['error']}")
            
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("Selective ignore file must be smaller than 10MB")
        return file


class HealthCheckExistingNetworkForm(forms.Form):
    """Form for uploading files for existing network processing per MOP"""
    tec_report_file = forms.FileField(
        label="TEC Health Check Report (.xlsx/.csv)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text="Upload the latest TEC Health Check report in xlsx or csv format (Network_name_Reports_YYYYMMDD.xlsx/.csv)"
    )
    
    inventory_csv = forms.FileField(
        label="Remote Inventory (.csv)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text="Upload the remote inventory CSV file associated with the health check report"
    )
    
    
    def clean_tec_report_file(self):
        file = self.cleaned_data['tec_report_file']
        if file:
            # Validate file extension
            if not file.name.endswith(('.xlsx', '.xls', '.csv')):
                raise forms.ValidationError("TEC Health Check report must be an Excel file (.xlsx or .xls) or CSV file (.csv)")
            
            # ===== ENHANCED CUSTOMER-SPECIFIC VALIDATION =====
            try:
                from .views import validate_section_specific_upload
                
                # Get customer name from the current session (if available)
                # Note: This requires access to request which forms don't have by default
                # We'll use a simplified validation here and rely on view-level validation for full checks
                
                # First, basic file type validation
                from .views import validate_file_type_match
                validation_result = validate_file_type_match(file.name, 'REPORT')
                if not validation_result['valid']:
                    raise forms.ValidationError(validation_result['error'])
                
                # Additional forbidden pattern check for reports
                file_name_upper = file.name.upper()
                strict_forbidden_patterns = ['HC_ISSUES_TRACKER', 'ISSUES_TRACKER', 'HC_TRACKER']
                for pattern in strict_forbidden_patterns:
                    if pattern in file_name_upper:
                        raise forms.ValidationError(f"🚫 **WRONG FILE TYPE FOR REPORT SECTION**\n\nFile '{file.name}' contains '{pattern.lower()}' which indicates it's a TRACKER file.\n\n**🎯 CORRECT SECTION:** Please use the 'Upload Old Tracker' section instead.\n\n**❌ This file type is NOT allowed in Report Upload section!**")
                
                inventory_forbidden = ['INVENTORY', 'REMOTE_INVENTORY', 'NODE_LIST']
                for pattern in inventory_forbidden:
                    if pattern in file_name_upper:
                        raise forms.ValidationError(f"🚫 **WRONG FILE TYPE FOR REPORT SECTION**\n\nFile '{file.name}' contains '{pattern.lower()}' which indicates it's an INVENTORY file.\n\n**🎯 CORRECT SECTION:** Please use the Inventory Upload section instead.\n\n**❌ This file type is NOT allowed in Report Upload section!**")
                        
            except ImportError:
                # Fallback validation if import fails
                file_name_upper = file.name.upper()
                forbidden_patterns = ['HC_ISSUES_TRACKER', 'ISSUES_TRACKER', 'HC_TRACKER', 'TRACKER', 'IGNORED_TEST_CASES', 'IGNORE_TEST', 'SELECTIVE_IGNORE', 'GLOBAL_IGNORE', 'IGNORE', 'INVENTORY', 'REMOTE_INVENTORY']
                for pattern in forbidden_patterns:
                    if pattern in file_name_upper:
                        if 'TRACKER' in pattern:
                            section_name = "'Upload Old Tracker' section"
                        elif 'IGNORE' in pattern:
                            section_name = "'Upload Ignore Files' section"
                        elif 'INVENTORY' in pattern:
                            section_name = "Inventory Upload section"
                        else:
                            section_name = "appropriate section"
                        raise forms.ValidationError(f"🚫 WRONG FILE TYPE: File '{file.name}' contains '{pattern}' which is NOT allowed in report upload section. Please upload it in the {section_name}.")
                        
                # Check for required patterns
                required_patterns = ['REPORT', 'REPORTS', 'TEC', 'HEALTH_CHECK']
                if not any(pattern in file_name_upper for pattern in required_patterns):
                    raise forms.ValidationError(f"🚫 NOT A REPORT FILE: File '{file.name}' doesn't appear to be a health check report. Valid report files should contain: REPORT, REPORTS, TEC, or HEALTH_CHECK")
            
            # File size validation (100MB limit for large networks)
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError("TEC Health Check report must be smaller than 100MB")
        return file
    
    def clean_inventory_csv(self):
        file = self.cleaned_data['inventory_csv']
        if file:
            # Validate file extension
            if not file.name.endswith('.csv'):
                raise forms.ValidationError("Remote inventory file must be a CSV file (.csv)")
            
            # ===== ENHANCED CUSTOMER-SPECIFIC VALIDATION =====
            try:
                # First, basic file type validation
                from .views import validate_file_type_match
                validation_result = validate_file_type_match(file.name, 'INVENTORY')
                if not validation_result['valid']:
                    raise forms.ValidationError(validation_result['error'])
                
                # Additional forbidden pattern check for inventory
                file_name_upper = file.name.upper()
                strict_forbidden_patterns = ['HC_ISSUES_TRACKER', 'ISSUES_TRACKER', 'HC_TRACKER']
                for pattern in strict_forbidden_patterns:
                    if pattern in file_name_upper:
                        raise forms.ValidationError(f"🚫 **WRONG FILE TYPE FOR INVENTORY SECTION**\n\nFile '{file.name}' contains '{pattern.lower()}' which indicates it's a TRACKER file.\n\n**🎯 CORRECT SECTION:** Please use the 'Upload Old Tracker' section instead.\n\n**❌ This file type is NOT allowed in Inventory Upload section!**")
                
                report_forbidden = ['REPORT', 'REPORTS', 'TEC_REPORT', 'HEALTH_CHECK']
                for pattern in report_forbidden:
                    if pattern in file_name_upper:
                        raise forms.ValidationError(f"🚫 **WRONG FILE TYPE FOR INVENTORY SECTION**\n\nFile '{file.name}' contains '{pattern.lower()}' which indicates it's a REPORT file.\n\n**🎯 CORRECT SECTION:** Please use the Report Upload section instead.\n\n**❌ This file type is NOT allowed in Inventory Upload section!**")
                        
            except ImportError:
                # Fallback validation if import fails
                file_name_upper = file.name.upper()
                forbidden_patterns = ['HC_ISSUES_TRACKER', 'ISSUES_TRACKER', 'HC_TRACKER', 'TRACKER', 'IGNORED_TEST_CASES', 'IGNORE_TEST', 'SELECTIVE_IGNORE', 'GLOBAL_IGNORE', 'IGNORE', 'REPORT', 'REPORTS', 'TEC_REPORT']
                for pattern in forbidden_patterns:
                    if pattern in file_name_upper:
                        if 'TRACKER' in pattern:
                            section_name = "'Upload Old Tracker' section"
                        elif 'IGNORE' in pattern:
                            section_name = "'Upload Ignore Files' section"
                        elif 'REPORT' in pattern:
                            section_name = "Report Upload section"
                        else:
                            section_name = "appropriate section"
                        raise forms.ValidationError(f"🚫 WRONG FILE TYPE: File '{file.name}' contains '{pattern}' which is NOT allowed in inventory upload section. Please upload it in the {section_name}.")
            
            # File size validation (50MB limit)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("Remote inventory file must be smaller than 50MB")
        return file
    
    def _validate_hc_filename_format(self, filename):
        """Validate HC filename format per MOP requirements"""
        try:
            # Expected format: Network_name_Reports_YYYYMMDD.xlsx
            base_name = filename.replace('.xlsx', '').replace('.xls', '')
            parts = base_name.split('_')
            
            # Should have at least 3 parts: Network, Reports, Date
            if len(parts) < 3:
                return False
            
            # Check if 'Reports' is in the filename
            if 'Reports' not in parts:
                return False
            
            # Check if the last part looks like a date (8 digits)
            date_part = parts[-1]
            if not (len(date_part) == 8 and date_part.isdigit()):
                return False
            
            return True
            
        except Exception:
            return False
