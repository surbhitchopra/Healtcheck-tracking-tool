#!/usr/bin/env python3
"""
Quick script to check sheet names in tracker files
"""

import openpyxl as opxl
from pathlib import Path

def check_tracker_sheets():
    script_dir = Path("Script")
    
    # Check the most recent tracker files
    tracker_files = [
        "bsnl_west_zone_otn_HC_Issues_Tracker.xlsx",
        "Bsnl_HC_Issues_Tracker.xlsx",
        "Template_HC_Issues_Tracker.xlsx"
    ]
    
    for filename in tracker_files:
        file_path = script_dir / filename
        if file_path.exists():
            print(f"\n=== {filename} ===")
            try:
                wb = opxl.load_workbook(file_path)
                print(f"Sheet names: {wb.sheetnames}")
                wb.close()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"\n❌ {filename} not found")

if __name__ == "__main__":
    check_tracker_sheets()
