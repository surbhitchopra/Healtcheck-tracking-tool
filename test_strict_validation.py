#!/usr/bin/env python3
"""
Test Script for SUPER STRICT Validation System
==============================================

This script tests all validation layers to ensure cross-customer uploads are blocked
and only correct customer files are accepted.

Usage:
    python test_strict_validation.py
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final.settings')

import django
django.setup()

from HealthCheck_app.views import (
    validate_customer_technology_match,
    validate_section_specific_upload,
    validate_file_type_match
)

class TestColors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_test_header(title):
    """Print a formatted test section header"""
    print(f"\n{TestColors.BLUE}{TestColors.BOLD}{'='*80}{TestColors.RESET}")
    print(f"{TestColors.BLUE}{TestColors.BOLD}{title.center(80)}{TestColors.RESET}")
    print(f"{TestColors.BLUE}{TestColors.BOLD}{'='*80}{TestColors.RESET}\n")

def print_test_result(test_name, expected, actual, details=""):
    """Print formatted test result"""
    if expected == actual:
        status = f"{TestColors.GREEN}✅ PASS{TestColors.RESET}"
    else:
        status = f"{TestColors.RED}❌ FAIL{TestColors.RESET}"
    
    print(f"{status} {test_name}")
    if details:
        print(f"    {TestColors.YELLOW}Details: {details}{TestColors.RESET}")
    if expected != actual:
        print(f"    {TestColors.RED}Expected: {expected}, Got: {actual}{TestColors.RESET}")

def test_operator_validation():
    """Test operator validation layer"""
    print_test_header("OPERATOR VALIDATION TESTS")
    
    test_cases = [
        # Valid cases
        ("BSNL East DWDM", "BSNL_East_TEC_Report_20250115.xlsx", True, "Same operator - should pass"),
        ("AIRTEL West Network", "AIRTEL_Mumbai_Reports_Jan2025.xlsx", True, "Same operator - should pass"),
        ("JIO DWDM South", "JIO_South_Health_Check_20250115.xlsx", True, "Same operator - should pass"),
        
        # Invalid cases - wrong operator
        ("BSNL East DWDM", "AIRTEL_West_Reports_20250115.xlsx", False, "Wrong operator - should fail"),
        ("AIRTEL Mumbai", "BSNL_East_TEC_Report_20250115.xlsx", False, "Wrong operator - should fail"),
        ("JIO Network", "VI_Reports_20250115.xlsx", False, "Wrong operator - should fail"),
        
        # Invalid cases - missing operator
        ("BSNL East DWDM", "Network_TEC_Report_20250115.xlsx", False, "Missing operator - should fail"),
        ("AIRTEL West", "Generic_Health_Check_Reports.xlsx", False, "Missing operator - should fail"),
    ]
    
    for customer_name, filename, expected_valid, description in test_cases:
        result = validate_customer_technology_match(customer_name, filename)
        print_test_result(
            f"Operator Test: {customer_name} → {filename}",
            expected_valid,
            result['valid'],
            description
        )

def test_region_validation():
    """Test region validation layer"""
    print_test_header("REGION VALIDATION TESTS")
    
    test_cases = [
        # Valid cases
        ("BSNL East DWDM", "BSNL_East_TEC_Report_20250115.xlsx", True, "Same region - should pass"),
        ("AIRTEL West Network", "AIRTEL_West_Reports_Jan2025.xlsx", True, "Same region - should pass"),
        ("JIO South Mumbai", "JIO_South_Health_Check_20250115.xlsx", True, "Same region - should pass"),
        ("Generic Network", "BSNL_East_Reports_20250115.xlsx", True, "No customer region - should allow any"),
        
        # Invalid cases - wrong region
        ("BSNL East DWDM", "BSNL_West_Reports_20250115.xlsx", False, "Wrong region - should fail"),
        ("AIRTEL West Network", "AIRTEL_East_TEC_Report_20250115.xlsx", False, "Wrong region - should fail"),
        ("JIO North DWDM", "JIO_South_Health_Check_20250115.xlsx", False, "Wrong region - should fail"),
    ]
    
    for customer_name, filename, expected_valid, description in test_cases:
        result = validate_customer_technology_match(customer_name, filename)
        print_test_result(
            f"Region Test: {customer_name} → {filename}",
            expected_valid,
            result['valid'],
            description
        )

def test_technology_validation():
    """Test technology validation layer"""
    print_test_header("TECHNOLOGY VALIDATION TESTS")
    
    test_cases = [
        # Valid cases
        ("BSNL East DWDM", "BSNL_East_DWDM_Report_20250115.xlsx", True, "Same technology - should pass"),
        ("AIRTEL SDH Network", "AIRTEL_West_SDH_Reports_Jan2025.xlsx", True, "Same technology - should pass"),
        ("JIO MPLS South", "JIO_South_MPLS_Health_Check_20250115.xlsx", True, "Same technology - should pass"),
        ("Generic Network", "BSNL_East_DWDM_Reports_20250115.xlsx", True, "No customer technology - should allow any"),
        
        # Invalid cases - wrong technology
        ("BSNL East DWDM", "BSNL_East_SDH_Reports_20250115.xlsx", False, "Wrong technology - should fail"),
        ("AIRTEL MPLS Network", "AIRTEL_West_DWDM_TEC_Report_20250115.xlsx", False, "Wrong technology - should fail"),
        ("JIO DWDM South", "JIO_South_SDH_Health_Check_20250115.xlsx", False, "Wrong technology - should fail"),
    ]
    
    for customer_name, filename, expected_valid, description in test_cases:
        result = validate_customer_technology_match(customer_name, filename)
        print_test_result(
            f"Technology Test: {customer_name} → {filename}",
            expected_valid,
            result['valid'],
            description
        )

def test_customer_identifier_validation():
    """Test customer identifier validation layer"""
    print_test_header("CUSTOMER IDENTIFIER VALIDATION TESTS")
    
    test_cases = [
        # Valid cases
        ("BSNL East Mumbai DWDM", "BSNL_East_Mumbai_TEC_Report_20250115.xlsx", True, "All identifiers present - should pass"),
        ("AIRTEL West Delhi Network", "AIRTEL_West_Delhi_Reports_Jan2025.xlsx", True, "All identifiers present - should pass"),
        ("JIO Chennai DWDM", "JIO_South_Chennai_Health_Check_20250115.xlsx", True, "Key identifier present - should pass"),
        ("Generic BSNL Network", "BSNL_East_TEC_Reports_20250115.xlsx", True, "No specific identifiers - should pass"),
        
        # Invalid cases - missing customer identifiers
        ("BSNL East Mumbai DWDM", "BSNL_East_Delhi_TEC_Report_20250115.xlsx", False, "Wrong city identifier - should fail"),
        ("AIRTEL West Kolkata Network", "AIRTEL_West_Mumbai_Reports_Jan2025.xlsx", False, "Wrong city identifier - should fail"),
        ("JIO Bangalore DWDM", "JIO_South_Chennai_Health_Check_20250115.xlsx", False, "Wrong city identifier - should fail"),
    ]
    
    for customer_name, filename, expected_valid, description in test_cases:
        result = validate_customer_technology_match(customer_name, filename)
        print_test_result(
            f"Identifier Test: {customer_name} → {filename}",
            expected_valid,
            result['valid'],
            description
        )

def test_section_specific_validation():
    """Test section-specific validation layer"""
    print_test_header("SECTION-SPECIFIC VALIDATION TESTS")
    
    # Test Report Section
    print(f"\n{TestColors.BOLD}Report Section Tests:{TestColors.RESET}")
    report_test_cases = [
        # Valid report files
        ("BSNL_East_TEC_Report_20250115.xlsx", "REPORT", True, "Valid TEC report - should pass"),
        ("AIRTEL_Health_Check_Reports_Jan2025.xlsx", "REPORT", True, "Valid health check report - should pass"),
        ("Customer_TEC_Reports_Monthly.xlsx", "REPORT", True, "Valid reports file - should pass"),
        
        # Invalid report files
        ("BSNL_HC_Issues_Tracker_20250115.xlsx", "REPORT", False, "Tracker file in report section - should fail"),
        ("Remote_Inventory_Export_20250115.csv", "REPORT", False, "Inventory file in report section - should fail"),
        ("Customer_Ignored_Test_Cases.xlsx", "REPORT", False, "Ignore file in report section - should fail"),
    ]
    
    for filename, expected_type, expected_valid, description in report_test_cases:
        result = validate_section_specific_upload("BSNL East", filename, "report_upload", expected_type)
        print_test_result(
            f"Report Section: {filename}",
            expected_valid,
            result['valid'],
            description
        )
    
    # Test Inventory Section
    print(f"\n{TestColors.BOLD}Inventory Section Tests:{TestColors.RESET}")
    inventory_test_cases = [
        # Valid inventory files
        ("BSNL_Remote_Inventory_20250115.csv", "INVENTORY", True, "Valid inventory file - should pass"),
        ("Customer_Node_Inventory_Export.csv", "INVENTORY", True, "Valid node inventory - should pass"),
        ("AIRTEL_Inventory_CSV_Export.csv", "INVENTORY", True, "Valid inventory CSV - should pass"),
        
        # Invalid inventory files
        ("BSNL_TEC_Report_20250115.xlsx", "INVENTORY", False, "Report file in inventory section - should fail"),
        ("Customer_HC_Issues_Tracker.xlsx", "INVENTORY", False, "Tracker file in inventory section - should fail"),
        ("BSNL_Host_Details.csv", "INVENTORY", False, "Host file in inventory section - should fail"),
    ]
    
    for filename, expected_type, expected_valid, description in inventory_test_cases:
        result = validate_section_specific_upload("BSNL East", filename, "inventory_upload", expected_type)
        print_test_result(
            f"Inventory Section: {filename}",
            expected_valid,
            result['valid'],
            description
        )
    
    # Test Tracker Section
    print(f"\n{TestColors.BOLD}Tracker Section Tests:{TestColors.RESET}")
    tracker_test_cases = [
        # Valid tracker files
        ("BSNL_HC_Issues_Tracker_20250115.xlsx", "TRACKER", True, "Valid HC issues tracker - should pass"),
        ("Customer_Health_Check_Tracker.xlsx", "TRACKER", True, "Valid health check tracker - should pass"),
        ("AIRTEL_Issues_Tracker_Updated.xlsx", "TRACKER", True, "Valid issues tracker - should pass"),
        
        # Invalid tracker files
        ("BSNL_TEC_Report_20250115.xlsx", "TRACKER", False, "Report file in tracker section - should fail"),
        ("Remote_Inventory_Export.csv", "TRACKER", False, "Inventory file in tracker section - should fail"),
        ("Customer_Ignored_Test_Cases.xlsx", "TRACKER", False, "Ignore file in tracker section - should fail"),
    ]
    
    for filename, expected_type, expected_valid, description in tracker_test_cases:
        result = validate_section_specific_upload("BSNL East", filename, "tracker_upload", expected_type)
        print_test_result(
            f"Tracker Section: {filename}",
            expected_valid,
            result['valid'],
            description
        )

def test_file_type_matching():
    """Test file type matching validation"""
    print_test_header("FILE TYPE MATCHING TESTS")
    
    test_cases = [
        # Report files
        ("BSNL_TEC_Report_20250115.xlsx", "REPORT", True, "Valid TEC report"),
        ("Customer_Health_Check_Reports.xlsx", "REPORT", True, "Valid health check report"),
        ("BSNL_HC_Issues_Tracker.xlsx", "REPORT", False, "Tracker file - not valid for report"),
        
        # Inventory files  
        ("Remote_Inventory_Export.csv", "INVENTORY", True, "Valid inventory file"),
        ("Customer_Node_List_CSV.csv", "INVENTORY", True, "Valid node list"),
        ("BSNL_TEC_Report.xlsx", "INVENTORY", False, "Report file - not valid for inventory"),
        
        # Tracker files
        ("BSNL_HC_Issues_Tracker.xlsx", "TRACKER", True, "Valid tracker file"),
        ("Customer_Issues_Tracker.xlsx", "TRACKER", True, "Valid issues tracker"),
        ("Remote_Inventory.csv", "TRACKER", False, "Inventory file - not valid for tracker"),
        
        # Ignore files
        ("Customer_Ignored_Test_Cases.xlsx", "IGNORE", True, "Valid ignore file"),
        ("BSNL_Global_Ignore_List.txt", "IGNORE", True, "Valid ignore text file"),
        ("BSNL_HC_Tracker.xlsx", "IGNORE", False, "Tracker file - not valid for ignore"),
        
        # Host files
        ("Customer_Host_Details.csv", "HOST", True, "Valid host file"),
        ("BSNL_Node_Hosts_List.csv", "HOST", True, "Valid hosts list"),
        ("Remote_Inventory.csv", "HOST", False, "Inventory file - not valid for host"),
    ]
    
    for filename, expected_type, expected_valid, description in test_cases:
        result = validate_file_type_match(filename, expected_type)
        print_test_result(
            f"File Type: {filename} as {expected_type}",
            expected_valid,
            result['valid'],
            description
        )

def test_comprehensive_validation():
    """Test comprehensive validation scenarios"""
    print_test_header("COMPREHENSIVE VALIDATION TESTS")
    
    # These test the complete validation pipeline
    test_cases = [
        # Perfect matches - should all pass
        ("BSNL East DWDM Mumbai", "BSNL_East_DWDM_Mumbai_TEC_Report_20250115.xlsx", True, 
         "Perfect match - operator, region, technology, identifier"),
        ("AIRTEL West Network", "AIRTEL_West_Health_Check_Reports_Jan2025.xlsx", True,
         "Good match - operator, region, report type"),
        ("JIO South MPLS", "JIO_South_MPLS_HC_Issues_Tracker.xlsx", True,
         "Good match - operator, region, technology, tracker type"),
        
        # Cross-customer scenarios - should all fail
        ("BSNL East DWDM", "AIRTEL_West_TEC_Report_20250115.xlsx", False,
         "Wrong operator - BSNL customer, AIRTEL file"),
        ("AIRTEL West Network", "BSNL_East_Health_Check_Reports.xlsx", False,
         "Wrong operator - AIRTEL customer, BSNL file"),
        ("BSNL East Mumbai", "BSNL_West_Delhi_TEC_Report.xlsx", False,
         "Wrong region and city - East Mumbai customer, West Delhi file"),
        ("JIO DWDM Network", "JIO_SDH_Health_Check_Report.xlsx", False,
         "Wrong technology - DWDM customer, SDH file"),
        
        # Cross-section scenarios - tested with section validation
        ("BSNL East Network", "BSNL_HC_Issues_Tracker.xlsx", False,
         "Tracker file should not validate as report in report section"),
    ]
    
    for customer_name, filename, expected_valid, description in test_cases:
        result = validate_customer_technology_match(customer_name, filename)
        print_test_result(
            f"Comprehensive: {customer_name} → {filename}",
            expected_valid,
            result['valid'],
            description
        )

def run_all_tests():
    """Run all validation tests"""
    print(f"{TestColors.BOLD}{TestColors.BLUE}")
    print("🔒 SUPER STRICT VALIDATION SYSTEM TEST SUITE")
    print("=" * 80)
    print(f"{TestColors.RESET}")
    
    # Run all test categories
    test_operator_validation()
    test_region_validation()
    test_technology_validation()
    test_customer_identifier_validation()
    test_section_specific_validation()
    test_file_type_matching()
    test_comprehensive_validation()
    
    print_test_header("TEST SUMMARY")
    print(f"{TestColors.GREEN}✅ All tests completed!{TestColors.RESET}")
    print(f"{TestColors.YELLOW}📋 Check results above for any failing tests{TestColors.RESET}")
    print(f"{TestColors.BLUE}💡 Green ✅ = Test Passed, Red ❌ = Test Failed{TestColors.RESET}")
    print(f"\n{TestColors.BOLD}If all tests show ✅ PASS, the SUPER STRICT validation system is working correctly!{TestColors.RESET}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"{TestColors.RED}❌ Error running tests: {e}{TestColors.RESET}")
        import traceback
        traceback.print_exc()
