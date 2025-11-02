# 🔒 SUPER STRICT VALIDATION SYSTEM

## Overview
The Health Check Tracking Tool now implements **SUPER STRICT** validation to prevent cross-customer file uploads and ensure data integrity. This system enforces multiple layers of validation to guarantee that files uploaded in any section belong to the exact selected customer.

## Validation Layers

### 1. 🏢 Operator Validation
**Rule:** Files must match the customer's telecom operator exactly.

**Supported Operators:**
- BSNL, RELIANCE, AIRTEL, VI, VODAFONE, IDEA, JIO, TATA, RAILTEL, POWERGRID, BHARTI

**Examples:**
- ✅ Customer: "BSNL East DWDM" → File: "BSNL_East_Reports_20250115.xlsx" 
- ❌ Customer: "BSNL East DWDM" → File: "AIRTEL_West_Reports_20250115.xlsx" 
- ❌ Customer: "BSNL East DWDM" → File: "Network_Reports_20250115.xlsx" (missing operator)

### 2. 🌍 Region Validation  
**Rule:** Files must match the customer's region if both customer and file specify regions.

**Supported Regions:**
- NORTH, SOUTH, EAST, WEST, CENTRAL, NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST

**Examples:**
- ✅ Customer: "BSNL East DWDM" → File: "BSNL_East_Reports_20250115.xlsx"
- ❌ Customer: "BSNL East DWDM" → File: "BSNL_West_Reports_20250115.xlsx"
- ✅ Customer: "BSNL DWDM" (no region) → File: "BSNL_East_Reports_20250115.xlsx" (allowed)

### 3. 🔧 Technology Validation
**Rule:** Files must match the customer's technology if both specify technologies.

**Supported Technologies:**
- DWDM, OTN, SDH, MPLS, IP, ETHERNET, OPTICAL, TRANSPORT, ACCESS

**Examples:**
- ✅ Customer: "BSNL East DWDM" → File: "BSNL_East_DWDM_Reports_20250115.xlsx"
- ❌ Customer: "BSNL East DWDM" → File: "BSNL_East_SDH_Reports_20250115.xlsx"

### 4. 🏷️ Customer Identifier Validation
**Rule:** Files must contain at least 50% of significant customer-specific identifiers.

**Process:**
1. Extract significant words from customer name (≥3 characters)
2. Exclude common words (LIMITED, LTD, ZONE, CIRCLE, NETWORK, etc.)
3. Exclude already-validated operators, regions, and technologies
4. Check that filename contains at least 50% of remaining identifiers

**Examples:**
- ✅ Customer: "BSNL East DWDM Network" → Identifiers: none (all excluded) → Always passes
- ✅ Customer: "BSNL East Mumbai DWDM" → Identifiers: [MUMBAI] → File: "BSNL_East_Mumbai_Reports.xlsx"
- ❌ Customer: "BSNL East Mumbai DWDM" → Identifiers: [MUMBAI] → File: "BSNL_East_Delhi_Reports.xlsx"

### 5. 📂 Section-Specific Validation
**Rule:** Each upload section only accepts files of the correct type.

#### Report Upload Section
- **Required patterns:** REPORT, REPORTS, TEC, HEALTH_CHECK
- **Forbidden patterns:** TRACKER, INVENTORY, IGNORE, HOST
- **Allowed extensions:** .xlsx
- **Examples:**
  - ✅ `BSNL_East_TEC_Report_20250115.xlsx`
  - ✅ `Customer_Health_Check_Reports_Jan2025.xlsx`
  - ❌ `BSNL_East_HC_Issues_Tracker.xlsx` (tracker, not report)
  - ❌ `Remote_Inventory_Export.csv` (inventory, not report)

#### Inventory Upload Section
- **Required patterns:** INVENTORY, REMOTE_INVENTORY, CSV
- **Forbidden patterns:** TRACKER, REPORT, REPORTS, IGNORE, HOST
- **Allowed extensions:** .csv
- **Examples:**
  - ✅ `BSNL_Remote_Inventory_20250115.csv`
  - ✅ `Customer_Node_Inventory_Export.csv`
  - ❌ `BSNL_TEC_Reports_20250115.xlsx` (report, not inventory)

#### Tracker Upload Section
- **Required patterns:** TRACKER, HC_ISSUES, ISSUES_TRACKER, HC_TRACKER
- **Forbidden patterns:** REPORT, REPORTS, INVENTORY, IGNORE, HOST
- **Allowed extensions:** .xlsx
- **Examples:**
  - ✅ `BSNL_HC_Issues_Tracker_20250115.xlsx`
  - ✅ `Customer_Health_Check_Tracker.xlsx`
  - ❌ `BSNL_TEC_Report_20250115.xlsx` (report, not tracker)

#### Ignore Files Upload Section
- **Required patterns:** IGNORE, IGNORED_TEST, TEST_CASES
- **Forbidden patterns:** TRACKER, REPORT, REPORTS, INVENTORY, HOST
- **Allowed extensions:** .xlsx, .txt
- **Examples:**
  - ✅ `BSNL_Ignored_Test_Cases.xlsx`
  - ✅ `Customer_Global_Ignore.txt`
  - ❌ `BSNL_HC_Tracker.xlsx` (tracker, not ignore file)

#### Host Files Upload Section
- **Required patterns:** HOST, HOSTS, NODE_DETAILS
- **Forbidden patterns:** TRACKER, REPORT, REPORTS, INVENTORY, IGNORE
- **Allowed extensions:** .csv
- **Examples:**
  - ✅ `BSNL_Host_Details.csv`
  - ✅ `Customer_Node_Hosts_List.csv`
  - ❌ `BSNL_Inventory_Export.csv` (inventory, not host file)

## Implementation

### Upload Endpoints with SUPER STRICT Validation

All upload endpoints now implement the full validation stack:

1. **Main Upload Endpoint** (`health_check_upload`)
   - Validates TEC reports and inventory files
   - Applies all 5 validation layers

2. **Individual Upload Endpoints**
   - `upload_host_file` - Host files validation
   - `upload_inventory_file` - Inventory files validation  
   - `upload_report_file` - TEC report files validation
   - `upload_old_tracker_file` - Old tracker files validation
   - `upload_tracker_generated_file` - Generated tracker files validation
   - `upload_ignore_excel_file` - Excel ignore files validation
   - `upload_ignore_text_file` - Text ignore files validation

3. **Real-time Validation** (`validate_filename`)
   - AJAX endpoint for real-time validation feedback
   - Shows validation errors before file submission

### Error Messages

Error messages are designed to be helpful and specific:

```
🚫 **WRONG OPERATOR**

Customer 'BSNL East DWDM' is **BSNL** operator.
But file 'AIRTEL_West_Reports.xlsx' is for **AIRTEL** operator.

**🔒 STRICT RULE:** No cross-operator uploads allowed!
**💡 SOLUTION:** Select the correct AIRTEL customer
```

## Benefits

1. **Data Integrity:** Prevents cross-customer data contamination
2. **User Guidance:** Clear error messages help users understand mistakes
3. **Automation:** Automatic validation reduces manual oversight
4. **Compliance:** Ensures proper file organization and customer separation
5. **Error Prevention:** Catches mistakes before processing begins

## Testing Scenarios

To verify the validation system works correctly:

### ✅ Valid Uploads
- BSNL customer → BSNL_East_TEC_Report_20250115.xlsx (correct operator, region, type)
- AIRTEL customer → AIRTEL_Mumbai_Inventory_Export.csv (correct operator, region, type)
- Generic customer → Any_Network_HC_Tracker.xlsx (no specific requirements)

### ❌ Invalid Uploads (Should be Rejected)
- BSNL customer → AIRTEL_Reports.xlsx (wrong operator)
- BSNL East customer → BSNL_West_Reports.xlsx (wrong region)  
- BSNL DWDM customer → BSNL_SDH_Reports.xlsx (wrong technology)
- Mumbai customer → Delhi_Reports.xlsx (wrong location identifier)
- Report section → HC_Issues_Tracker.xlsx (wrong file type for section)
- Inventory section → TEC_Report.xlsx (wrong file type for section)

## Maintenance

The validation system uses configurable lists that can be easily updated:

- **Operators:** Add new telecom operators to `all_operators` list
- **Regions:** Add new regions to `all_regions` list  
- **Technologies:** Add new technologies to `all_technologies` list
- **File Types:** Update section rules in `validate_section_specific_upload`

## Troubleshooting

### Common Issues

1. **File rejected for "missing identifiers"**
   - Solution: Ensure filename contains customer-specific words
   - Check that customer name has meaningful identifiers beyond operators/regions

2. **"Wrong section" errors**
   - Solution: Upload file in the correct section based on file type
   - Check filename patterns match the section requirements

3. **Region/operator conflicts**
   - Solution: Verify customer selection matches the file's origin
   - Check if file belongs to a different customer entirely

### Debug Information

The system logs detailed debug information:
- Customer identifiers extracted
- File patterns detected
- Validation results for each layer
- Specific reasons for rejection

This information helps administrators troubleshoot validation issues.
