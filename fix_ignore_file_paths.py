#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add project path
project_path = r"C:\Users\surchopr\hc_final"
sys.path.append(project_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import HealthCheckFile, Customer
from HealthCheck_app.views import get_customer_file_path

def fix_ignore_file_paths():
    """Fix database paths for ignore files to point to customer folders"""
    
    # Get all ignore files with incorrect paths
    ignore_files = HealthCheckFile.objects.filter(
        file_type__in=['GLOBAL_IGNORE_TXT', 'SELECTIVE_IGNORE_XLSX']
    )
    
    print(f"Found {ignore_files.count()} ignore files to check...")
    
    fixed_count = 0
    for file_obj in ignore_files:
        customer = file_obj.customer
        current_path = file_obj.file_path
        
        # Generate correct customer folder path
        correct_path = get_customer_file_path(customer, 'OLD_TRACKER', file_obj.stored_filename)
        
        print(f"\n📁 {file_obj.stored_filename}")
        print(f"   Customer: {customer.name}")
        print(f"   Current:  {current_path}")
        print(f"   Correct:  {correct_path}")
        
        # Check if current path is wrong (not pointing to customer folder)
        if 'customer_files' not in str(current_path) or 'old_trackers' not in str(current_path):
            print(f"   🔧 Path needs fixing!")
            
            # Try to find the actual file location
            script_path = Path(r"C:\Users\surchopr\Hc_final\Script") / file_obj.stored_filename
            
            if script_path.exists():
                print(f"   ✅ Found file at Script root: {script_path}")
                
                # Copy file to correct customer folder location
                try:
                    correct_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file to customer folder
                    import shutil
                    shutil.copy2(script_path, correct_path)
                    
                    # Update database record
                    file_obj.file_path = str(correct_path)
                    file_obj.save()
                    
                    print(f"   ✅ Fixed! File copied to customer folder and database updated")
                    fixed_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error fixing: {e}")
            else:
                print(f"   ❌ Source file not found at: {script_path}")
        else:
            print(f"   ✅ Path already correct")
    
    print(f"\n🎯 Summary: Fixed {fixed_count} ignore file paths")
    return fixed_count

if __name__ == "__main__":
    fix_ignore_file_paths()
