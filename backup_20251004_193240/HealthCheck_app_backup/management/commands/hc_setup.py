import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from HealthCheck_app.models import Customer

class Command(BaseCommand):
    help = 'Setup 1830PSS Health Check Script integration and manage network configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['setup', 'validate', 'reset', 'list'],
            default='setup',
            help='Action to perform: setup, validate, reset, or list networks'
        )
        parser.add_argument(
            '--network',
            type=str,
            help='Network name for specific operations'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force operation without confirmation'
        )

    def handle(self, *args, **options):
        action = options['action']
        network_name = options.get('network')
        force = options.get('force', False)

        try:
            if action == 'setup':
                self.setup_integration()
            elif action == 'validate':
                self.validate_integration(network_name)
            elif action == 'reset':
                self.reset_integration(network_name, force)
            elif action == 'list':
                self.list_networks()
        except Exception as e:
            raise CommandError(f'Error executing {action}: {str(e)}')

    def setup_integration(self):
        """Setup the integration between Django and Script"""
        self.stdout.write(self.style.SUCCESS('Setting up 1830PSS Health Check Script integration...'))
        
        # Get paths
        base_dir = Path(settings.BASE_DIR)
        script_dir = base_dir / "Script"
        
        if not script_dir.exists():
            raise CommandError(f"Script directory not found at {script_dir}")
        
        # Check for required files
        required_files = [
            "main.py",
            "hcfuncs.py", 
            "requirements.txt",
            "venv"
        ]
        
        for file_name in required_files:
            file_path = script_dir / file_name
            if not file_path.exists():
                self.stdout.write(
                    self.style.WARNING(f"Missing: {file_name}")
                )
        
        # Check template files
        template_files = [
            "Template_HC_Issues_Tracker.xlsx",
            "Template_ignored_test_cases.txt",
            "Template_ignored_test_cases.xlsx"
        ]
        
        self.stdout.write("\nChecking template files:")
        for template_file in template_files:
            template_path = script_dir / template_file
            if template_path.exists():
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Found: {template_file}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Missing: {template_file}")
                )
        
        # Ensure required directories exist
        required_dirs = [
            script_dir / "input-hc-report",
            script_dir / "output"
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stdout.write(
                    self.style.SUCCESS(f"Created directory: {dir_path}")
                )
        
        self.stdout.write(self.style.SUCCESS('\n✓ Integration setup completed!'))

    def validate_integration(self, network_name):
        """Validate integration for a specific network or all networks"""
        if network_name:
            try:
                customer = Customer.objects.get(name=network_name, is_deleted=False)
                self.validate_network_files(customer)
            except Customer.DoesNotExist:
                raise CommandError(f"Network '{network_name}' not found")
        else:
            # Validate all networks
            networks = Customer.objects.filter(is_deleted=False)
            if not networks.exists():
                self.stdout.write(self.style.WARNING("No networks found in database"))
                return
            
            for customer in networks:
                self.validate_network_files(customer)

    def validate_network_files(self, customer):
        """Validate network-specific files per MOP requirements"""
        self.stdout.write(f"\nValidating network: {customer.name}")
        
        base_dir = Path(settings.BASE_DIR)
        script_dir = base_dir / "Script"
        
        # Check network-specific files
        network_files = [
            f"{customer.name}_HC_Issues_Tracker.xlsx",
            f"{customer.name}_ignored_test_cases.txt",
            f"{customer.name}_ignored_test_cases.xlsx"
        ]
        
        all_exist = True
        for file_name in network_files:
            file_path = script_dir / file_name
            if file_path.exists():
                # Check file size
                size_mb = file_path.stat().st_size / (1024 * 1024)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ {file_name} ({size_mb:.1f} MB)")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Missing: {file_name}")
                )
                all_exist = False
        
        if all_exist:
            if customer.setup_status != 'READY':
                customer.setup_status = 'READY'
                customer.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  → Network {customer.name} marked as READY")
                )
        else:
            if customer.setup_status != 'NEW':
                customer.setup_status = 'NEW'
                customer.save()
                self.stdout.write(
                    self.style.WARNING(f"  → Network {customer.name} marked as NEW (files missing)")
                )

    def reset_integration(self, network_name, force):
        """Reset integration files"""
        if not force:
            confirm = input("This will delete network files. Continue? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write("Operation cancelled.")
                return
        
        base_dir = Path(settings.BASE_DIR)
        script_dir = base_dir / "Script"
        
        if network_name:
            # Reset specific network
            try:
                customer = Customer.objects.get(name=network_name, is_deleted=False)
                self.reset_network_files(customer, script_dir)
            except Customer.DoesNotExist:
                raise CommandError(f"Network '{network_name}' not found")
        else:
            # Reset all networks
            networks = Customer.objects.filter(is_deleted=False)
            for customer in networks:
                self.reset_network_files(customer, script_dir)
        
        self.stdout.write(self.style.SUCCESS('Reset completed!'))

    def reset_network_files(self, customer, script_dir):
        """Reset files for a specific network"""
        self.stdout.write(f"Resetting files for network: {customer.name}")
        
        network_files = [
            f"{customer.name}_HC_Issues_Tracker.xlsx",
            f"{customer.name}_ignored_test_cases.txt", 
            f"{customer.name}_ignored_test_cases.xlsx"
        ]
        
        for file_name in network_files:
            file_path = script_dir / file_name
            if file_path.exists():
                file_path.unlink()
                self.stdout.write(f"  Deleted: {file_name}")
        
        # Reset customer status
        customer.setup_status = 'NEW'
        customer.save()
        self.stdout.write(f"  → {customer.name} status reset to NEW")

    def list_networks(self):
        """List all networks and their status"""
        networks = Customer.objects.filter(is_deleted=False).order_by('name')
        
        if not networks.exists():
            self.stdout.write(self.style.WARNING("No networks found in database"))
            return
        
        self.stdout.write("\nConfigured Networks:")
        self.stdout.write("-" * 60)
        
        for customer in networks:
            status_color = (
                self.style.SUCCESS if customer.setup_status == 'READY' 
                else self.style.WARNING
            )
            self.stdout.write(
                f"{customer.name:<30} {status_color(customer.setup_status):<10} {customer.network_type}"
            )
        
        self.stdout.write("-" * 60)
        self.stdout.write(f"Total networks: {networks.count()}")
        
        # Show file system status
        base_dir = Path(settings.BASE_DIR)
        script_dir = base_dir / "Script"
        
        self.stdout.write(f"\nScript directory: {script_dir}")
        self.stdout.write(f"Template files status:")
        
        template_files = [
            "Template_HC_Issues_Tracker.xlsx",
            "Template_ignored_test_cases.txt", 
            "Template_ignored_test_cases.xlsx"
        ]
        
        for template_file in template_files:
            template_path = script_dir / template_file
            status = "✓" if template_path.exists() else "✗"
            self.stdout.write(f"  {status} {template_file}")
