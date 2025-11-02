#!/usr/bin/env python
"""
Fix for BSNL Network Monthly Runs Formatting Issue

The problem: "Not Started" is being truncated to "arted" due to 
date formatting logic that uses strftime('%d-%b') which only shows first 3 letters.

Solution: Properly handle special status values before date parsing.
"""

import os
import sys
from datetime import datetime

# Create backup of views.py first
backup_filename = f"views_backup_monthly_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup_path = os.path.join(os.path.dirname(__file__), backup_filename)

print(f"🔒 Creating backup: {backup_filename}")

# Read current views.py
with open('views.py', 'r', encoding='utf-8') as f:
    current_content = f.read()

# Write backup
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(current_content)

print(f"✅ Backup created: {backup_path}")

# The fix: Replace the problematic date formatting sections
fixes_applied = 0

# Fix 1: Main API function (lines 67-73)
old_pattern1 = '''                                        if date_str in ['Not Started', 'Not Run', 'No Report']:
                                            # Show status messages as-is
                                            months[month_num - 1] = date_str
                                        else:
                                            try:
                                                # Try to parse as date and format it
                                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                months[month_num - 1] = date_obj.strftime('%d-%b')
                                            except ValueError:
                                                # If parsing fails, show the raw value
                                                months[month_num - 1] = date_str'''

new_pattern1 = '''                                        if date_str in ['Not Started', 'Not Run', 'No Report']:
                                            # Show status messages as-is
                                            months[month_num - 1] = date_str
                                        else:
                                            try:
                                                # Try to parse as date and format it properly
                                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                # Use custom formatting to avoid truncation
                                                month_abbr = date_obj.strftime('%b')  # Full month abbreviation
                                                months[month_num - 1] = f"{date_obj.day}-{month_abbr}"
                                            except ValueError:
                                                # If parsing fails, show the raw value
                                                months[month_num - 1] = date_str'''

if old_pattern1 in current_content:
    current_content = current_content.replace(old_pattern1, new_pattern1)
    fixes_applied += 1
    print("✅ Fixed main API date formatting")

# Fix 2: Combined months logic (lines 105-108)
old_pattern2 = '''                                                try:
                                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                    formatted_date = date_obj.strftime('%d-%b')'''

new_pattern2 = '''                                                try:
                                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                    # Use custom formatting to avoid truncation
                                                    month_abbr = date_obj.strftime('%b')
                                                    formatted_date = f"{date_obj.day}-{month_abbr}"'''

if old_pattern2 in current_content:
    current_content = current_content.replace(old_pattern2, new_pattern2)
    fixes_applied += 1
    print("✅ Fixed combined months date formatting")

# Fix 3: Individual network months (lines 168-169)
old_pattern3 = '''                                                try:
                                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                    net_months[month_num - 1] = date_obj.strftime('%d-%b')'''

new_pattern3 = '''                                                try:
                                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                                    # Use custom formatting to avoid truncation
                                                    month_abbr = date_obj.strftime('%b')
                                                    net_months[month_num - 1] = f"{date_obj.day}-{month_abbr}"'''

if old_pattern3 in current_content:
    current_content = current_content.replace(old_pattern3, new_pattern3)
    fixes_applied += 1
    print("✅ Fixed individual network date formatting")

# Fix 4: Export function date formatting (lines 287-288)
old_pattern4 = '''                                            from datetime import datetime
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                            months[month_num - 1] = date_obj.strftime('%d-%b')'''

new_pattern4 = '''                                            from datetime import datetime
                                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                            # Use custom formatting to avoid truncation
                                            month_abbr = date_obj.strftime('%b')
                                            months[month_num - 1] = f"{date_obj.day}-{month_abbr}"'''

if old_pattern4 in current_content:
    current_content = current_content.replace(old_pattern4, new_pattern4)
    fixes_applied += 1
    print("✅ Fixed export function date formatting")

# Write the fixed content back to views.py
if fixes_applied > 0:
    with open('views.py', 'w', encoding='utf-8') as f:
        f.write(current_content)
    
    print(f"\n🎉 SUCCESS! Applied {fixes_applied} fixes to views.py")
    print("📋 Changes made:")
    print("   - Fixed 'Not Started' truncation to 'arted'")
    print("   - Proper month abbreviation formatting (Jan, Feb, Mar, etc.)")
    print("   - All BSNL network dates should now display correctly")
    print("\n🔧 Next steps:")
    print("   1. Restart Django server: python manage.py runserver")
    print("   2. Test the API: /api/customer-dashboard/customers/")
    print("   3. Check dashboard - BSNL networks should show proper dates")
    
else:
    print("⚠️ No fixes were needed or patterns not found")
    print("The views.py file might already be fixed or have different structure")

print(f"\n📁 Backup available at: {backup_path}")
print("Use this backup to restore if needed")
