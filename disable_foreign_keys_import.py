#!/usr/bin/env python3
"""
Quick Fix: Disable Foreign Key Constraints During Import
This temporarily disables MySQL foreign key checks to allow CSV import

WARNING: Only use this for data migration. Re-enable constraints after import.

Usage: Run this before your CSV import
"""

import os
import sys
import django
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

def disable_foreign_key_checks():
    """Disable foreign key constraints in MySQL"""
    print("🔧 DISABLING FOREIGN KEY CONSTRAINTS")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        print("✅ Foreign key constraints DISABLED")
        
        # Show current status
        cursor.execute("SELECT @@FOREIGN_KEY_CHECKS;")
        result = cursor.fetchone()
        print(f"📊 Current FOREIGN_KEY_CHECKS value: {result[0]}")
        
        if result[0] == 0:
            print("✅ SUCCESS: Foreign key constraints are now DISABLED")
            print("⚠️  WARNING: Remember to re-enable after import!")
            print("   Run: enable_foreign_key_checks()")
        
def enable_foreign_key_checks():
    """Re-enable foreign key constraints in MySQL"""
    print("🔧 RE-ENABLING FOREIGN KEY CONSTRAINTS")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("✅ Foreign key constraints RE-ENABLED")
        
        # Show current status
        cursor.execute("SELECT @@FOREIGN_KEY_CHECKS;")
        result = cursor.fetchone()
        print(f"📊 Current FOREIGN_KEY_CHECKS value: {result[0]}")
        
        if result[0] == 1:
            print("✅ SUCCESS: Foreign key constraints are now ENABLED")
            print("🔒 Database integrity protection is active")

def check_foreign_key_status():
    """Check current foreign key constraint status"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT @@FOREIGN_KEY_CHECKS;")
        result = cursor.fetchone()
        status = "ENABLED" if result[0] == 1 else "DISABLED"
        print(f"📊 Foreign key constraints are currently: {status}")
        return result[0]

if __name__ == "__main__":
    print("🔧 FOREIGN KEY CONSTRAINT MANAGER")
    print("=" * 60)
    
    # Check current status
    current_status = check_foreign_key_status()
    
    print("\nChoose action:")
    print("1. Disable foreign key checks (for import)")
    print("2. Enable foreign key checks (after import)")
    print("3. Just check status")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        disable_foreign_key_checks()
        print("\n🚀 NOW RUN YOUR CSV IMPORT")
        print("   After import, run this script again and choose option 2")
        
    elif choice == "2":
        enable_foreign_key_checks()
        print("\n🔒 Database constraints are now active")
        
    elif choice == "3":
        print("\n📊 Current status checked above")
        
    else:
        print("❌ Invalid choice")