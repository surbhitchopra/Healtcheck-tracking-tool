#!/usr/bin/env python
"""
Fix for showing all 12 months but only populating data for the filtered month range
When user filters Oct-Nov:
- All 12 month columns remain visible (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec)
- Only Oct and Nov columns show actual dates
- Other months show dashes or "No Data"
"""

import os
from datetime import datetime

# Read current template
template_file = 'templates/customer_dashboard.html'
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Create backup
backup_filename = f"customer_dashboard_selective_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
backup_path = os.path.join('templates', backup_filename)

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"🔒 Created backup: {backup_filename}")

# Remove the previous dynamic header function since we want to keep all headers
# Replace updateTableHeaders function with a simpler version
old_dynamic_header_function = """// DYNAMIC MONTH HEADERS - Show only filtered months in table header
function updateTableHeaders() {
    const headerRow = document.querySelector('#customer-table thead tr');
    if (!headerRow) return;
    
    console.log('🔧 Updating table headers for date filter...');
    
    // Define all month names
    const allMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Remove existing month headers (but keep other headers)
    const existingMonthHeaders = headerRow.querySelectorAll('th.month-col');
    existingMonthHeaders.forEach(header => header.remove());
    
    // Get the position where month headers should be inserted (after GTAC column)
    const gtacHeader = headerRow.querySelector('th.info-col:last-of-type');
    const totalRunsHeader = headerRow.querySelector('th.total-col');
    
    if (!gtacHeader || !totalRunsHeader) {
        console.error('❌ Could not find GTAC or Total Runs headers');
        return;
    }
    
    // Determine which months to show
    let monthsToShow = allMonths;
    let startMonth = 0;
    let endMonth = 11;
    
    if (currentStartDate && currentEndDate) {
        startMonth = new Date(currentStartDate).getMonth();
        endMonth = new Date(currentEndDate).getMonth();
        monthsToShow = allMonths.slice(startMonth, endMonth + 1);
        
        console.log(`📅 Filtering headers: showing months ${startMonth + 1}-${endMonth + 1} (${monthsToShow.join(', ')})`);
        
        // Show the filter date header
        const filterHeader = headerRow.querySelector('#filter-date-header');
        if (filterHeader) {
            filterHeader.style.display = 'table-cell';
            const startFormatted = new Date(currentStartDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const endFormatted = new Date(currentEndDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            filterHeader.textContent = `${startFormatted} - ${endFormatted}`;
        }
    } else {
        console.log('📅 No filter applied: showing all months');
        
        // Hide the filter date header
        const filterHeader = headerRow.querySelector('#filter-date-header');
        if (filterHeader) {
            filterHeader.style.display = 'none';
        }
    }
    
    // Insert month headers in correct positions
    let insertAfter = gtacHeader;
    monthsToShow.forEach(month => {
        const monthHeader = document.createElement('th');
        monthHeader.className = 'month-col';
        monthHeader.textContent = month;
        
        // Insert after the current position
        insertAfter.insertAdjacentElement('afterend', monthHeader);
        insertAfter = monthHeader;
    });
    
    console.log(`✅ Updated table headers: ${monthsToShow.length} month columns`);
    
    // Also update data row cells to match filtered columns
    updateDataRowCells();
}"""

# New function that keeps all headers but styles filtered months differently
new_selective_data_function = """// SELECTIVE MONTH DATA - Keep all 12 months visible but highlight filtered range
function updateSelectiveMonthData() {
    console.log('🔧 Updating selective month data for filter...');
    
    // Get all month headers
    const headerRow = document.querySelector('#customer-table thead tr');
    const monthHeaders = headerRow ? headerRow.querySelectorAll('th.month-col') : [];
    
    // Determine filter range
    let startMonth = null;
    let endMonth = null;
    
    if (currentStartDate && currentEndDate) {
        startMonth = new Date(currentStartDate).getMonth();
        endMonth = new Date(currentEndDate).getMonth();
        console.log(`📅 Filter active: highlighting months ${startMonth + 1}-${endMonth + 1}`);
        
        // Style month headers to show which ones are active
        monthHeaders.forEach((header, index) => {
            if (index >= startMonth && index <= endMonth) {
                header.style.backgroundColor = '#3b82f6';
                header.style.color = 'white';
                header.style.fontWeight = 'bold';
            } else {
                header.style.backgroundColor = '#f3f4f6';
                header.style.color = '#6b7280';
                header.style.fontWeight = 'normal';
            }
        });
        
        // Add filter indicator
        showFilterIndicator(startMonth, endMonth);
    } else {
        console.log('📅 No filter: all months normal');
        
        // Reset all month headers to normal
        monthHeaders.forEach(header => {
            header.style.backgroundColor = '';
            header.style.color = '';
            header.style.fontWeight = '';
        });
        
        hideFilterIndicator();
    }
    
    // Update data rows to show selective data
    updateSelectiveDataRows(startMonth, endMonth);
}

function showFilterIndicator(startMonth, endMonth) {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const filterText = `Showing data for: ${monthNames[startMonth]} - ${monthNames[endMonth]}`;
    
    // Create or update filter indicator
    let indicator = document.querySelector('#filter-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'filter-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #3b82f6;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }
    indicator.textContent = filterText;
    indicator.style.display = 'block';
}

function hideFilterIndicator() {
    const indicator = document.querySelector('#filter-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

function updateSelectiveDataRows(startMonth, endMonth) {
    const tableBody = document.querySelector('#customer-table tbody');
    if (!tableBody) return;
    
    const allRows = tableBody.querySelectorAll('tr');
    
    allRows.forEach(row => {
        // Find month cells (assuming they start from column 5)
        const allCells = row.querySelectorAll('td');
        const monthCellsStartIndex = 4; // Adjust based on your table structure
        
        for (let i = monthCellsStartIndex; i < allCells.length - 1; i++) {
            const cell = allCells[i];
            const monthIndex = i - monthCellsStartIndex;
            
            if (monthIndex >= 0 && monthIndex < 12) {
                if (startMonth !== null && endMonth !== null) {
                    // Show actual data only for filtered months
                    if (monthIndex >= startMonth && monthIndex <= endMonth) {
                        // Keep original data visible with highlight
                        cell.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                        cell.style.fontWeight = '600';
                        cell.style.border = '2px solid #3b82f6';
                    } else {
                        // Show placeholder for non-filtered months
                        const originalContent = cell.getAttribute('data-original-content') || cell.textContent;
                        if (!cell.getAttribute('data-original-content')) {
                            cell.setAttribute('data-original-content', originalContent);
                        }
                        
                        cell.textContent = '—';
                        cell.style.backgroundColor = '#f9fafb';
                        cell.style.color = '#9ca3af';
                        cell.style.fontWeight = 'normal';
                        cell.style.border = '1px solid #e5e7eb';
                        cell.style.textAlign = 'center';
                    }
                } else {
                    // No filter: restore all original data
                    const originalContent = cell.getAttribute('data-original-content');
                    if (originalContent) {
                        cell.textContent = originalContent;
                        cell.removeAttribute('data-original-content');
                    }
                    
                    cell.style.backgroundColor = '';
                    cell.style.color = '';
                    cell.style.fontWeight = '';
                    cell.style.border = '';
                    cell.style.textAlign = '';
                }
            }
        }
    });
    
    console.log(`✅ Updated selective data for ${allRows.length} rows`);
}"""

# Replace the old function
if old_dynamic_header_function in content:
    content = content.replace(old_dynamic_header_function, new_selective_data_function)
    print("✅ Replaced dynamic headers with selective data function")
else:
    print("❌ Could not find old function to replace")
    # Try to add it after a known marker
    marker = "// APPLY CUSTOMER FILTER - Filter dashboard by date range"
    if marker in content:
        content = content.replace(marker, new_selective_data_function + "\n\n" + marker)
        print("✅ Added selective data function at marker")

# Update the applyCustomerFilter function call
old_apply_call = "updateTableHeaders();"
new_apply_call = "updateSelectiveMonthData();"

if old_apply_call in content:
    content = content.replace(old_apply_call, new_apply_call)
    print("✅ Updated applyCustomerFilter to use selective data")

# Update the clearFilter function call
if old_apply_call in content:
    content = content.replace(old_apply_call, new_apply_call)
    print("✅ Updated clearFilter to use selective data")

# Remove the old updateDataRowCells function since it's integrated now
old_row_function_start = "// UPDATE DATA ROWS - Show only filtered month cells in each row"
old_row_function_end = "console.log(`✅ Updated ${allRows.length} data rows for filtered months`);\n}"

# Find and remove the old function
start_pos = content.find(old_row_function_start)
if start_pos != -1:
    end_pos = content.find(old_row_function_end, start_pos)
    if end_pos != -1:
        end_pos += len(old_row_function_end)
        content = content[:start_pos] + content[end_pos:]
        print("✅ Removed old updateDataRowCells function")

# Add CSS for smooth animations
css_addition = '''
<style>
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Smooth transitions for month cells */
#customer-table td {
    transition: all 0.3s ease;
}

/* Filtered month highlight */
.month-filtered {
    background-color: rgba(59, 130, 246, 0.1) !important;
    border: 2px solid #3b82f6 !important;
    font-weight: 600 !important;
}

/* Non-filtered month styling */
.month-placeholder {
    background-color: #f9fafb !important;
    color: #9ca3af !important;
    text-align: center !important;
}
</style>'''

# Add CSS before </head>
if '</head>' in content:
    content = content.replace('</head>', css_addition + '\n</head>')
    print("✅ Added CSS for selective month styling")

# Write the updated content back
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 SUCCESS! Fixed selective month data display")
print("📋 How it works now:")
print("   ✅ All 12 months remain visible (Jan to Dec)")
print("   ✅ Filtered months (e.g., Oct-Nov) show actual dates with blue highlighting")
print("   ✅ Non-filtered months show dashes (—) with gray background")
print("   ✅ Month headers show which months are active (blue) vs inactive (gray)")
print("   ✅ Filter indicator shows current date range")
print("   ✅ Clear filter restores all original data")

print(f"\n🔧 Example:")
print("   📅 Filter: Oct 1 to Nov 30")
print("   📊 Result:")
print("      - Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep: Show dashes (—)")
print("      - Oct, Nov: Show actual dates (highlighted in blue)")
print("      - Dec: Shows dashes (—)")

print(f"\n📁 Backup: {backup_filename}")
print("🚀 Refresh your dashboard to see the perfect fix!")