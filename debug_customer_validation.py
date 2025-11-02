#!/usr/bin/env python3
"""
DEBUG CUSTOMER VALIDATION - Test karte hain ki naming logic sahi work kar rahi hai ya nahi
"""

import re

def extract_meaningful_words(text):
    """Extract meaningful words from customer name or filename"""
    # Convert to uppercase and clean
    text_upper = text.upper().strip()
    
    # Replace common separators with spaces
    text_clean = re.sub(r'[_\-\.\\\/>]', ' ', text_upper)
    
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
        # Generic location terms
        'ZONE', 'CIRCLE', 'REGION', 'AREA', 'DIVISION', 'BRANCH', 'OFFICE'
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

def check_regions(customer_name, filename):
    """Check region matching logic"""
    regions = [
        'NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL',
        'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
        'NORTHERN', 'SOUTHERN', 'EASTERN', 'WESTERN',
        'DELHI', 'MUMBAI', 'CHENNAI', 'KOLKATA', 'BANGALORE', 'HYDERABAD',
        'UP', 'BIHAR', 'PUNJAB', 'HARYANA', 'RAJASTHAN', 'MP', 'GUJARAT',
        'MAHARASHTRA', 'KARNATAKA', 'TAMILNADU', 'AP', 'TELANGANA'
    ]
    
    customer_upper = customer_name.upper()
    filename_upper = filename.upper()
    
    # Find customer's regions
    customer_regions = [region for region in regions if region in customer_upper]
    
    # Find file's regions  
    file_regions = [region for region in regions if region in filename_upper]
    
    return customer_regions, file_regions

def debug_customer_validation(customer_name, filename):
    """Complete debug of customer validation"""
    print("="*60)
    print(f"🔍 DEBUGGING CUSTOMER VALIDATION")
    print("="*60)
    print(f"Customer Name: '{customer_name}'")
    print(f"Filename: '{filename}'")
    print("-"*60)
    
    # Step 1: Extract meaningful words
    customer_words = extract_meaningful_words(customer_name)
    filename_words = extract_meaningful_words(filename)
    
    print(f"📋 Customer Words: {customer_words}")
    print(f"📋 Filename Words: {filename_words}")
    print("-"*60)
    
    # Step 2: Check regions
    customer_regions, file_regions = check_regions(customer_name, filename)
    
    print(f"🌍 Customer Regions: {customer_regions}")
    print(f"🌍 File Regions: {file_regions}")
    print("-"*60)
    
    # Step 3: Region validation logic
    if customer_regions:
        if file_regions:
            if not any(c_region == f_region for c_region in customer_regions for f_region in file_regions):
                print("❌ REGION MISMATCH - FILE WOULD BE REJECTED")
                print(f"   Reason: Customer has {customer_regions} but file has {file_regions}")
                return False
            else:
                print("✅ REGION MATCH - Region validation passed")
        else:
            print("❌ MISSING REGION - FILE WOULD BE REJECTED")
            print(f"   Reason: Customer has {customer_regions} but file has no region")
            return False
    else:
        print("ℹ️ NO CUSTOMER REGION - Region check skipped")
    
    # Step 4: Word matching logic
    exact_matches = 0
    partial_matches = 0
    matched_words = []
    
    for customer_word in customer_words:
        found_match = False
        
        # Try exact match first
        if customer_word in filename_words:
            exact_matches += 1
            matched_words.append(f"{customer_word}(exact)")
            found_match = True
        else:
            # Try partial matches for words >= 3 characters
            if len(customer_word) >= 3:
                for filename_word in filename_words:
                    if len(filename_word) >= 3:
                        # Check substring matches in both directions
                        if (customer_word in filename_word or 
                            filename_word in customer_word):
                            partial_matches += 1
                            matched_words.append(f"{customer_word}→{filename_word}(partial)")
                            found_match = True
                            break
    
    total_matches = exact_matches + partial_matches
    total_words = len(customer_words)
    match_percentage = total_matches / total_words if total_words > 0 else 0
    
    print(f"🎯 Word Matching Results:")
    print(f"   Exact Matches: {exact_matches}")
    print(f"   Partial Matches: {partial_matches}")
    print(f"   Total Matches: {total_matches}/{total_words} ({match_percentage:.1%})")
    print(f"   Matched Words: {matched_words}")
    print("-"*60)
    
    # Step 5: Final decision
    if total_words == 0:
        print("✅ GENERIC CUSTOMER - Would be accepted")
        return True
    elif total_words == 1:
        required_threshold = 0.7
    elif total_words == 2:
        required_threshold = 0.5
    else:
        required_threshold = 0.4
    
    if exact_matches >= 2:
        print("✅ STRONG MATCH - Would be accepted (2+ exact matches)")
        return True
    elif match_percentage >= required_threshold or total_matches >= 2:
        print(f"✅ SUFFICIENT MATCH - Would be accepted ({match_percentage:.1%} >= {required_threshold:.1%})")
        return True
    else:
        print(f"❌ INSUFFICIENT MATCH - Would be rejected ({match_percentage:.1%} < {required_threshold:.1%})")
        return False

# TEST CASES - अपने real examples add करें
if __name__ == "__main__":
    print("\n🧪 TESTING CUSTOMER VALIDATION LOGIC\n")
    
    # Test Case 1: Same region (should accept)
    debug_customer_validation("BSNL North DWDM", "BSNL_North_DWDM_Report_20250119.xlsx")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case 2: Different region (should reject)
    debug_customer_validation("BSNL North DWDM", "BSNL_East_DWDM_Report_20250119.xlsx")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case 3: No region in file (should reject if customer has region)
    debug_customer_validation("BSNL North DWDM", "BSNL_DWDM_Report_20250119.xlsx")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case 4: Add your real customer name and filename here
    print("\n" + "="*80 + "\n")
    print("🔥 YOUR REAL TEST CASE:")
    debug_customer_validation("YOUR_ACTUAL_CUSTOMER_NAME", "YOUR_ACTUAL_FILENAME.xlsx")
    
    # Uncomment and modify these with your exact names:
    # debug_customer_validation("BSNL North DWDM", "BSNL_East_DWDM_HC_Report.xlsx") 
    # debug_customer_validation("Your Customer Name", "Your_File_Name.xlsx")
