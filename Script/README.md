# 1830PSS Health Check Script

## Overview
This script automates the analysis of TEC Health Check reports for 1830PSS networks. It helps identify important issues while filtering out benign ones, maintaining a historical record of network health over time.

## Prerequisites
- Windows 10 OS
- Python V3.10.4 or greater
- Internet connection (direct broadband, not Nokia Intranet) for initial setup
- Latest Health Check report in xlsx format
- Remote inventory in CSV format

## Initial Setup (One-time only)

### 1. Python Virtual Environment Setup
The Python virtual environment is already created in the `venv` folder. To activate it:
```powershell
venv\Scripts\activate
```

If you need to recreate the environment:
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Adding a New Network (First time only)

#### Create HC Tracker:
1. Open `Template_HC_Issues_Tracker.xlsx`
2. Save as `Network_name_HC_Issues_Tracker.xlsx` (use exact TEC HC system name)
3. Fill NODE COVERAGE sheet with TEC hosts file details
4. Ensure 'HC Id' column is numeric with no decimal places

#### Create Global Ignore File:
1. Open `Template_ignored_test_cases.txt`
2. Add test cases to ignore (one per line)
3. Save as `Network_name_ignored_test_cases.txt`
4. Default: contains test case 5.2.1

#### Create Specific Ignore File:
1. Open `Template_ignored_test_cases.xlsx`
2. Save as `Network_name_ignored_test_cases.xlsx`
3. Enter combinations of HC Id, Test, Prio, and Findings to ignore

## Script Usage

### Running the Script:
1. Copy latest TEC Health Check report and remote inventory CSV to `input-hc-report` folder
2. Delete any old files from `input-hc-report` folder first
3. Activate Python environment and run:
```powershell
venv\Scripts\activate
python main.py
```
4. Check `output` folder for updated HC tracker: `Network_name_HC_Issues_Tracker_DD-MM-20YY.xlsx`

## File Structure
```
Script/
├── input-hc-report/          # Input folder for HC reports and CSV files
├── output/                   # Output folder for processed results
├── venv/                     # Python virtual environment
├── main.py                   # Main script
├── hcfuncs.py               # Function definitions module
├── requirements.txt          # Python dependencies
├── Template_HC_Issues_Tracker.xlsx
├── Template_ignored_test_cases.txt
├── Template_ignored_test_cases.xlsx
└── README.md                # This file
```

## Template Files
- `Template_HC_Issues_Tracker.xlsx`: Base tracker template for new networks
- `Template_ignored_test_cases.txt`: Global ignore list template (default: 5.2.1)
- `Template_ignored_test_cases.xlsx`: Specific ignore combinations template

## Support
For support, bug reports, or feature requests:
📧 I_INP_APAC_TEAM@internal.nsn.com

---
**Document Version:** 01 | **Date:** 03/02/2025 | **Author:** Shiv Sahu
