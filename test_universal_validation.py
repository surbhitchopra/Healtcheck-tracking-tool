#!/usr/bin/env python3
"""
Simple Test for Universal Region-Based Validation
================================================

Test the validation functions directly without Django setup
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Mock Django models since we're testing standalone
class MockCustomer:
    def __init__(self, name):
        self.name = name

class TestColors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

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

def extract_meaningful_words(text):
    """Extract meaningful words from customer name or filename"""
    import re
    
    # Convert to uppercase and clean
    text_upper = text.upper().strip()
    
    # Replace common separators with spaces
    text_clean = re.sub(r'[_\-\.\\\\/\>]', ' ', text_upper)
    
    # Split into words
    words = text_clean.split()
    
    # Define words to exclude (common but not meaningful for matching)
    excluded_words = {
        # Generic terms
        'NETWORK', 'NETWORKS', 'COMPANY', 'LIMITED', 'LTD', 'PVT', 'PRIVATE',
        'CORPORATION', 'CORP', 'INC', 'TECHNOLOGIES', 'TECH', 'SOLUTIONS',
        'SERVICES', 'SERVICE', 'SYSTEMS', 'SYSTEM', 'GROUP', 'ENTERPRISES',
        # File-related terms
        'REPORT', 'REPORTS', 'FILE', 'FILES', 'DATA', 'EXPORT', 'IMPORT',
        'HEALTH', 'CHECK', 'TRACKER', 'ISSUES', 'TEST', 'CASES', 'IGNORE',
        'IGNORED', 'GLOBAL', 'SELECTIVE', 'HC', 'TEC', 'CSV', 'XLSX', 'TXT',
        # Time-related terms
        'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY',
        'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER',
        'JAN', 'FEB', 'MAR', 'APR', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC',
        '2024', '2025', '2026', '2023', '2022', '2021', '2020',
        # Generic location terms (but NOT regions - we need those for validation)
        'ZONE', 'CIRCLE', 'AREA', 'DIVISION', 'BRANCH', 'OFFICE'
    }
    
    # Filter meaningful words (length >= 2 and not in excluded list)
    meaningful_words = []
    for word in words:
        word_clean = word.strip()
        # Skip if too short, numeric only, or in excluded list
        if (len(word_clean) >= 2 and 
            not word_clean.isdigit() and 
            word_clean not in excluded_words):
            meaningful_words.append(word_clean)
    
    return meaningful_words

def validate_customer_technology_match(customer_name, filename):
    """
    UNIVERSAL validation - Works for ANY customer name and ANY region/network
    Extracts key identifiers from both customer and filename to ensure they match
    Prevents cross-network uploads while supporting any customer configuration
    """
    try:
        # Normalize both strings for comparison
        customer_normalized = customer_name.upper().replace('_', ' ').replace('-', ' ').replace('/', ' ')
        filename_normalized = filename.upper().replace('_', ' ').replace('-', ' ').replace('.', ' ')
        
        # Split into words for analysis
        customer_words = set(customer_normalized.split())
        filename_words = set(filename_normalized.split())
        
        # Define comprehensive lists for flexible matching
        operators = {'BSNL', 'AIRTEL', 'JIO', 'VI', 'VODAFONE', 'IDEA', 'RELIANCE', 'TATA', 'BHARTI'}
        regions = {'NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL', 'NORTHEAST'}
        technologies = {'DWDM', 'SDH', 'MPLS', 'OTN', 'SONET', 'IP', 'ETHERNET', 'FIBER', 'OPTICAL'}
        network_types = {'NETWORK', 'NET', 'CIRCLE', 'ZONE', 'DIVISION', 'SECTOR'}
        
        # Cities and states for granular matching
        locations = {
            'MUMBAI', 'DELHI', 'KOLKATA', 'CHENNAI', 'BANGALORE', 'HYDERABAD', 'PUNE', 'AHMEDABAD',
            'JAIPUR', 'LUCKNOW', 'KANPUR', 'NAGPUR', 'INDORE', 'THANE', 'BHOPAL', 'VISAKHAPATNAM',
            'PATNA', 'VADODARA', 'GHAZIABAD', 'LUDHIANA', 'RAJKOT', 'KOCHI', 'AURANGABAD', 'COIMBATORE',
            'MAHARASHTRA', 'GUJARAT', 'KARNATAKA', 'TAMILNADU', 'TELANGANA', 'RAJASTHAN', 'PUNJAB',
            'HARYANA', 'UP', 'UTTARPRADESH', 'MP', 'MADHYAPRADESH', 'WB', 'WESTBENGAL'
        }
        
        validation_errors = []
        matches_found = 0
        
        # 1. OPERATOR MATCHING - Critical for preventing cross-operator uploads
        customer_operators = customer_words.intersection(operators)
        filename_operators = filename_words.intersection(operators)
        
        if customer_operators and filename_operators:
            if not customer_operators.intersection(filename_operators):
                return {
                    'valid': False,
                    'error': f"❌ Cross-operator upload blocked: Customer is {'/'.join(customer_operators)} but file is for {'/'.join(filename_operators)}"
                }
            matches_found += 1
        elif customer_operators and not filename_operators:
            # Customer has operator but file doesn't - could be generic file
            validation_errors.append(f"⚠️ Customer is {'/'.join(customer_operators)} but file has no operator identifier")
        
        # 2. REGION MATCHING - Prevent cross-region uploads
        customer_regions = customer_words.intersection(regions)
        filename_regions = filename_words.intersection(regions)
        
        if customer_regions and filename_regions:
            if not customer_regions.intersection(filename_regions):
                return {
                    'valid': False,
                    'error': f"❌ Cross-region upload blocked: Customer is {'/'.join(customer_regions)} but file is for {'/'.join(filename_regions)}"
                }
            matches_found += 1
        elif customer_regions and not filename_regions:
            validation_errors.append(f"⚠️ Customer is {'/'.join(customer_regions)} region but file has no region identifier")
        
        # 3. TECHNOLOGY MATCHING - Prevent cross-technology uploads
        customer_techs = customer_words.intersection(technologies)
        filename_techs = filename_words.intersection(technologies)
        
        if customer_techs and filename_techs:
            if not customer_techs.intersection(filename_techs):
                return {
                    'valid': False,
                    'error': f"❌ Cross-technology upload blocked: Customer uses {'/'.join(customer_techs)} but file is for {'/'.join(filename_techs)}"
                }
            matches_found += 1
        elif customer_techs and not filename_techs:
            validation_errors.append(f"⚠️ Customer uses {'/'.join(customer_techs)} but file has no technology identifier")
        
        # 4. LOCATION MATCHING - Prevent cross-location uploads
        customer_locations = customer_words.intersection(locations)
        filename_locations = filename_words.intersection(locations)
        
        if customer_locations and filename_locations:
            if not customer_locations.intersection(filename_locations):
                return {
                    'valid': False,
                    'error': f"❌ Cross-location upload blocked: Customer is in {'/'.join(customer_locations)} but file is for {'/'.join(filename_locations)}"
                }
            matches_found += 1
        elif customer_locations and not filename_locations:
            validation_errors.append(f"⚠️ Customer is in {'/'.join(customer_locations)} but file has no location identifier")
        
        # 5. FLEXIBLE WORD MATCHING - Check for any common significant words (3+ chars)
        customer_significant = {word for word in customer_words if len(word) >= 3 and word not in network_types}
        filename_significant = {word for word in filename_words if len(word) >= 3 and word not in {'REPORT', 'REPORTS', 'TEC', 'TRACKER', 'ISSUES', 'CSV', 'XLSX', 'EXPORT'}}
        
        common_words = customer_significant.intersection(filename_significant)
        if common_words:
            matches_found += len(common_words)
        
        # DECISION LOGIC
        if matches_found >= 1:
            # At least one strong match found - allow upload
            return {'valid': True, 'error': None}
        elif validation_errors:
            # Some validation concerns but no hard blocks
            if len(validation_errors) >= 2:
                # Multiple concerns - be more strict
                return {
                    'valid': False,
                    'error': f"❌ Multiple validation concerns: {'; '.join(validation_errors[:2])}"
                }
            else:
                # Single concern - allow with warning
                return {'valid': True, 'warning': validation_errors[0]}
        else:
            # No specific identifiers found - allow generic uploads
            return {'valid': True, 'error': None}
            
    except Exception as e:
        return {
            'valid': False,
            'error': f"❌ Validation error: {str(e)}"
        }

def test_universal_validation():
    """Test universal validation with various customer and file combinations"""
    print(f"{TestColors.BLUE}{TestColors.BOLD}🔒 UNIVERSAL REGION-BASED VALIDATION SYSTEM TEST{TestColors.RESET}")
    print("=" * 80)
    
    test_cases = [
        # Valid same-operator cases
        ("BSNL South DWDM", "BSNL_South_TEC_Report_20250115.xlsx", True, "Same operator and region - should pass"),
        ("AIRTEL West Network", "AIRTEL_West_Reports_Jan2025.xlsx", True, "Same operator and region - should pass"),
        ("JIO East MPLS", "JIO_East_MPLS_Health_Check_20250115.xlsx", True, "Same operator, region, and technology - should pass"),
        
        # Invalid cross-operator cases
        ("BSNL South DWDM", "AIRTEL_West_Reports_20250115.xlsx", False, "Different operator and region - should fail"),
        ("AIRTEL West Network", "BSNL_East_TEC_Report_20250115.xlsx", False, "Different operator and region - should fail"),
        ("JIO North Network", "VI_South_Health_Check_20250115.xlsx", False, "Different operator and region - should fail"),
        
        # Invalid cross-region cases (same operator)
        ("BSNL South DWDM", "BSNL_North_Reports_20250115.xlsx", False, "Same operator but different region - should fail"),
        ("AIRTEL East Network", "AIRTEL_West_TEC_Report_20250115.xlsx", False, "Same operator but different region - should fail"),
        ("JIO North MPLS", "JIO_South_Health_Check_20250115.xlsx", False, "Same operator but different region - should fail"),
        
        # Valid generic cases
        ("Generic Customer", "Any_Report_File_20250115.xlsx", True, "Generic customer - should accept any file"),
        ("Test Network", "Network_Health_Check_Report.xlsx", True, "Simple customer - should accept compatible file"),
        
        # Valid partial match cases
        ("BSNL Customer", "BSNL_TEC_Report_20250115.xlsx", True, "Partial match - should pass"),
        ("Mumbai Network", "Mumbai_Reports_Jan2025.xlsx", True, "Location match - should pass"),
        
        # Technology validation
        ("DWDM Network", "DWDM_Health_Check_Report.xlsx", True, "Technology match - should pass"),
        ("BSNL DWDM Network", "BSNL_SDH_Report.xlsx", False, "Same operator but different technology - should fail"),
    ]
    
    passed = 0
    failed = 0
    
    for customer_name, filename, expected_valid, description in test_cases:
        result = validate_customer_technology_match(customer_name, filename)
        actual_valid = result['valid']
        
        if actual_valid == expected_valid:
            passed += 1
            status = f"{TestColors.GREEN}✅ PASS{TestColors.RESET}"
        else:
            failed += 1
            status = f"{TestColors.RED}❌ FAIL{TestColors.RESET}"
        
        print(f"{status} {customer_name} → {filename}")
        print(f"    {TestColors.YELLOW}{description}{TestColors.RESET}")
        if not actual_valid and result.get('error'):
            print(f"    {TestColors.RED}Rejection reason: {result['error']}{TestColors.RESET}")
        if actual_valid != expected_valid:
            print(f"    {TestColors.RED}Expected: {expected_valid}, Got: {actual_valid}{TestColors.RESET}")
        print()
    
    print("=" * 80)
    print(f"{TestColors.BOLD}Test Summary:{TestColors.RESET}")
    print(f"{TestColors.GREEN}✅ Passed: {passed}{TestColors.RESET}")
    print(f"{TestColors.RED}❌ Failed: {failed}{TestColors.RESET}")
    print(f"{TestColors.BLUE}📊 Total: {passed + failed}{TestColors.RESET}")
    
    if failed == 0:
        print(f"\n{TestColors.GREEN}{TestColors.BOLD}🎉 All tests passed! The universal validation system is working correctly!{TestColors.RESET}")
    else:
        print(f"\n{TestColors.RED}{TestColors.BOLD}⚠️ {failed} test(s) failed. Please review the validation logic.{TestColors.RESET}")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = test_universal_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"{TestColors.RED}❌ Error running tests: {e}{TestColors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
