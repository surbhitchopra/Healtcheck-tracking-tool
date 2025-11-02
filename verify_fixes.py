#!/usr/bin/env python3
"""
Verification script to check if all monthly_runs formatting is fixed
"""

import os
from pathlib import Path
import re

def verify_monthly_runs_fixes():
    """Check that all monthly_runs formatting is properly handled"""
    
    views_file = Path("C:/Users/surchopr/Hc_Final/HealthCheck_app/views.py")
    
    if not views_file.exists():
        print("❌ Views file not found!")
        return False
    
    print("🔍 Verifying monthly_runs formatting fixes...")
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: Formatting function exists
    if "def format_monthly_runs_to_array" in content:
        print("✅ Formatting function exists")
    else:
        print("❌ Formatting function missing")
        return False
    
    # Check 2: Find all places where monthly_runs is assigned
    monthly_runs_assignments = []
    
    # Look for patterns like 'monthly_runs': something
    pattern = r"'monthly_runs':\s*([^,\n}]+)"
    matches = re.findall(pattern, content)
    
    print(f"\n📊 Found {len(matches)} monthly_runs assignments:")
    
    properly_formatted = 0
    needs_fixing = []
    
    for i, match in enumerate(matches):
        assignment = match.strip()
        print(f"  {i+1}. 'monthly_runs': {assignment}")
        
        if "format_monthly_runs_to_array" in assignment:
            print("     ✅ Uses formatting function")
            properly_formatted += 1
        elif assignment in ["monthly_runs", "monthly_data", "network.monthly_runs"]:
            print(f"     ⚠️ May need formatting: {assignment}")
            needs_fixing.append(assignment)
        else:
            print(f"     ✅ Already formatted or hardcoded array")
            properly_formatted += 1
    
    # Check 3: Look for database network processing
    if "network.monthly_runs" in content:
        print("\n📊 Database network processing found")
        # Check if it's properly wrapped with formatting function
        if "format_monthly_runs_to_array(network.monthly_runs)" in content:
            print("✅ Database monthly_runs properly formatted")
        else:
            print("⚠️ Database monthly_runs may need formatting")
            needs_fixing.append("network.monthly_runs")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"   Total assignments: {len(matches)}")
    print(f"   Properly formatted: {properly_formatted}")
    print(f"   May need fixing: {len(needs_fixing)}")
    
    if needs_fixing:
        print(f"\n⚠️ These assignments may need the formatting function:")
        for item in needs_fixing:
            print(f"   - {item}")
        
        # Additional fixes if needed
        apply_additional_fixes(content, views_file, needs_fixing)
    else:
        print("\n✅ All monthly_runs assignments appear to be properly formatted!")
    
    return len(needs_fixing) == 0

def apply_additional_fixes(content, views_file, needs_fixing):
    """Apply additional fixes if needed"""
    
    print("\n🔧 Applying additional fixes...")
    
    modified = False
    
    # Fix any remaining unformatted assignments
    for item in needs_fixing:
        if item == "monthly_runs" and "'monthly_runs': monthly_runs" in content:
            content = content.replace("'monthly_runs': monthly_runs", "'monthly_runs': format_monthly_runs_to_array(monthly_runs)")
            print("   ✅ Fixed: 'monthly_runs': monthly_runs")
            modified = True
        
        elif item == "monthly_data" and "'monthly_runs': monthly_data" in content:
            content = content.replace("'monthly_runs': monthly_data", "'monthly_runs': format_monthly_runs_to_array(monthly_data)")
            print("   ✅ Fixed: 'monthly_runs': monthly_data")
            modified = True
            
        elif item == "network.monthly_runs" and "'monthly_runs': network.monthly_runs" in content:
            content = content.replace("'monthly_runs': network.monthly_runs", "'monthly_runs': format_monthly_runs_to_array(network.monthly_runs)")
            print("   ✅ Fixed: 'monthly_runs': network.monthly_runs")
            modified = True
    
    if modified:
        # Create another backup
        from datetime import datetime
        backup_file = views_file.with_suffix(f'.backup_additional_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
        import shutil
        shutil.copy2(views_file, backup_file)
        
        # Write the fixed content
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Additional fixes applied and backed up to: {backup_file}")
    else:
        print("   ℹ️ No additional fixes needed")

def check_excel_file():
    """Check if the Excel file issue is resolved"""
    
    excel_path = Path("C:/Users/surchopr/Hc_Final/Script/Health_Check_Tracker_1.xlsx")
    
    if excel_path.exists():
        print("✅ Excel file exists")
        
        try:
            import pandas as pd
            df = pd.read_excel(excel_path, sheet_name='Summary')
            print(f"   📊 File is readable: {len(df)} rows")
            return True
        except Exception as e:
            print(f"   ⚠️ Excel file exists but has issues: {e}")
            return False
    else:
        print("❌ Excel file still missing")
        return False

def main():
    print("🔍 Comprehensive Fix Verification")
    print("=" * 40)
    
    # Check Excel file
    print("\n1. Excel File Check:")
    excel_ok = check_excel_file()
    
    # Check monthly_runs formatting
    print("\n2. Monthly Runs Formatting Check:")
    formatting_ok = verify_monthly_runs_fixes()
    
    # Overall status
    print("\n" + "=" * 40)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 40)
    
    if excel_ok and formatting_ok:
        print("✅ ALL CHECKS PASSED!")
        print("\n🎯 Next steps:")
        print("1. Restart your Django server:")
        print("   python manage.py runserver")
        print("\n2. Test the API:")
        print("   http://localhost:8000/api/customer-dashboard/customers/")
        print("\n3. Check the dashboard UI for proper date display")
        
    else:
        print("⚠️ Some issues found:")
        if not excel_ok:
            print("   - Excel file needs attention")
        if not formatting_ok:
            print("   - Monthly runs formatting needs attention")
        
        print("\nPlease address the issues above before testing")

if __name__ == "__main__":
    main()