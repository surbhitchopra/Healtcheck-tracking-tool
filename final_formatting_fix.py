#!/usr/bin/env python3
"""
Final fix for network.monthly_runs formatting
"""

from pathlib import Path
import shutil
from datetime import datetime
import re

def fix_network_monthly_runs():
    """Fix the remaining network.monthly_runs formatting issue"""
    
    views_file = Path("C:/Users/surchopr/Hc_Final/HealthCheck_app/views.py")
    
    # Create backup
    backup_file = views_file.with_suffix(f'.backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
    shutil.copy2(views_file, backup_file)
    print(f"📦 Backup created: {backup_file}")
    
    # Read content
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix network.monthly_runs assignments that aren't wrapped
    patterns_to_fix = [
        ("'monthly_runs': network.monthly_runs,", "'monthly_runs': format_monthly_runs_to_array(network.monthly_runs),"),
        ("'monthly_runs': network.monthly_runs", "'monthly_runs': format_monthly_runs_to_array(network.monthly_runs)"),
        ("monthly_runs=network.monthly_runs", "monthly_runs=format_monthly_runs_to_array(network.monthly_runs)"),
    ]
    
    fixed_count = 0
    for old_pattern, new_pattern in patterns_to_fix:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"✅ Fixed: {old_pattern}")
            fixed_count += 1
    
    # Also check for any remaining unformatted assignments
    # Look for direct assignments that might have been missed
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        # Check for lines that assign network.monthly_runs without formatting
        if "'monthly_runs':" in line and "network.monthly_runs" in line and "format_monthly_runs_to_array" not in line:
            # Fix this line
            if "network.monthly_runs" in line:
                old_line = line
                new_line = line.replace("network.monthly_runs", "format_monthly_runs_to_array(network.monthly_runs)")
                modified_lines.append(new_line)
                print(f"✅ Fixed line: {old_line.strip()}")
                print(f"   -> {new_line.strip()}")
                fixed_count += 1
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    if fixed_count > 0:
        # Write the fixed content
        content = '\n'.join(modified_lines)
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Applied {fixed_count} additional fixes")
    else:
        print("\n✅ No additional fixes needed")
    
    return fixed_count > 0

def main():
    print("🔧 Final Monthly Runs Formatting Fix")
    print("=" * 40)
    
    if fix_network_monthly_runs():
        print("\n✅ Final fixes applied!")
    else:
        print("\n✅ All formatting appears to be correct!")
    
    print("\n🎯 Ready to test:")
    print("1. Restart Django server: python manage.py runserver")
    print("2. Test API: http://localhost:8000/api/customer-dashboard/customers/")
    print("3. Check dashboard UI for proper date display")

if __name__ == "__main__":
    main()