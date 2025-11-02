from django import forms
from .models import Customer

class CustomerSelectionForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_deleted=False),
        empty_label="Select a customer",
        widget=forms.Select(attrs={'class': 'w-full p-3 rounded-lg border border-blue-200 bg-blue-50'})
    )

class CustomerCreationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'tec_network_name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg border border-blue-200 bg-blue-50', 
                'placeholder': 'Enter customer/network display name',
                'required': True
            }),
            'tec_network_name': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg border border-blue-200 bg-blue-50', 
                'placeholder': 'Enter TEC network name (exactly as in HC system)',
                'required': True
            })
        }
        labels = {
            'name': 'Network Display Name',
            'tec_network_name': 'TEC Network Name'
        }
        help_texts = {
            'name': 'Display name for this network in the system',
            'tec_network_name': 'Network name exactly as it appears in TEC Health Check system'
        }
    

class ReportUploadForm(forms.Form):
    report_file = forms.FileField()

class HostUploadForm(forms.Form):
    host_file = forms.FileField()

# Health Check specific forms
class HealthCheckNewNetworkForm(forms.Form):
    """Form for new network setup (5 files)"""
    hc_tracker_file = forms.FileField(
        label="HC Issues Tracker (.xlsx)",
        help_text="Upload Network_name_HC_Issues_Tracker.xlsx file",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-blue-200 bg-blue-50',
            'accept': '.xlsx'
        })
    )
    
    global_ignore_txt = forms.FileField(
        label="Global Ignore (.txt)",
        help_text="Upload Network_name_ignored_test_cases.txt file",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-blue-200 bg-blue-50',
            'accept': '.txt'
        })
    )
    
    selective_ignore_xlsx = forms.FileField(
        label="Selective Ignore (.xlsx)",
        help_text="Upload Network_name_ignored_test_cases.xlsx file",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-blue-200 bg-blue-50',
            'accept': '.xlsx'
        })
    )
    
    tec_report_file = forms.FileField(
        label="TEC Health Check Report (.xlsx)",
        help_text="Upload latest TEC Health Check report",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-green-200 bg-green-50',
            'accept': '.xlsx'
        })
    )
    
    inventory_csv = forms.FileField(
        label="Remote Inventory (.csv)",
        help_text="Upload remote inventory CSV file",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-green-200 bg-green-50',
            'accept': '.csv'
        })
    )

class HealthCheckExistingNetworkForm(forms.Form):
    """Form for existing network processing (2 files)"""
    tec_report_file = forms.FileField(
        label="TEC Health Check Report (.xlsx)",
        help_text="Upload latest TEC Health Check report",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-green-200 bg-green-50',
            'accept': '.xlsx'
        })
    )
    
    inventory_csv = forms.FileField(
        label="Remote Inventory (.csv)",
        help_text="Upload remote inventory CSV file",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-3 rounded-lg border border-green-200 bg-green-50',
            'accept': '.csv'
        })
    )
