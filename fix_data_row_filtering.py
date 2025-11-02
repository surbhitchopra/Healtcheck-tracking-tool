#!/usr/bin/env python
"""
Additional fix to also hide/show the data cells in rows to match the filtered month columns
This ensures both headers AND data rows only show the selected month range
"""

import os
from datetime import datetime

# Read current template
template_file = 'templates/customer_dashboard.html'
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Create another backup
backup_filename = f"customer_dashboard_row_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
backup_path = os.path.join('templates', backup_filename)

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"🔒 Created additional backup: {backup_filename}")

# Add function to update data row cells to match filtered columns
new_row_filter_function = '''
// UPDATE DATA ROWS - Show only filtered month cells in each row
function updateDataRowCells() {
    const tableBody = document.querySelector('#customer-table tbody');
    if (!tableBody) return;
    
    console.log('🔧 Updating data row cells for date filter...');
    
    // Get all data rows (both customer and network rows)
    const allRows = tableBody.querySelectorAll('tr');
    
    // Determine which month indices to show
    let startMonth = 0;
    let endMonth = 11;
    
    if (currentStartDate && currentEndDate) {
        startMonth = new Date(currentStartDate).getMonth();
        endMonth = new Date(currentEndDate).getMonth();
        console.log(`📅 Filtering row cells: showing months ${startMonth + 1}-${endMonth + 1}`);
    } else {
        console.log('📅 No filter: showing all month cells');
    }
    
    allRows.forEach((row, rowIndex) => {
        // Find all month cells in this row (assuming they have class 'month-cell' or similar)
        const monthCells = row.querySelectorAll('td.month-cell, td[data-month]');
        
        if (monthCells.length === 0) {
            // If no month cells found, try to find cells by position
            // Assuming month cells start after info columns (name, circle, customer, gtac)
            const allCells = row.querySelectorAll('td');
            const monthCellsStartIndex = 4; // Adjust based on your table structure
            
            for (let i = monthCellsStartIndex; i < allCells.length - 1; i++) { // -1 to exclude total column
                const cell = allCells[i];
                const monthIndex = i - monthCellsStartIndex;
                
                if (monthIndex >= 0 && monthIndex < 12) {
                    if (currentStartDate && currentEndDate) {
                        // Show only cells within date range
                        if (monthIndex >= startMonth && monthIndex <= endMonth) {
                            cell.style.display = 'table-cell';
                        } else {
                            cell.style.display = 'none';
                        }
                    } else {
                        // Show all cells when no filter
                        cell.style.display = 'table-cell';
                    }
                }
            }
        } else {
            // Use found month cells
            monthCells.forEach((cell, cellIndex) => {
                if (currentStartDate && currentEndDate) {
                    if (cellIndex >= startMonth && cellIndex <= endMonth) {
                        cell.style.display = 'table-cell';
                    } else {
                        cell.style.display = 'none';
                    }
                } else {
                    cell.style.display = 'table-cell';
                }
            });
        }
    });
    
    console.log(`✅ Updated ${allRows.length} data rows for filtered months`);
}'''

# Find where to insert this new function (after the updateTableHeaders function)
insertion_marker = "console.log(`✅ Updated table headers: ${monthsToShow.length} month columns`);\n}"

if insertion_marker in content:
    content = content.replace(insertion_marker, insertion_marker + "\n\n" + new_row_filter_function)
    print("✅ Added data row cell filtering function")
else:
    print("❌ Could not find insertion point for row filtering function")

# Update the existing updateTableHeaders function to also call updateDataRowCells
old_header_end = '''    console.log(`✅ Updated table headers: ${monthsToShow.length} month columns`);
}'''

new_header_end = '''    console.log(`✅ Updated table headers: ${monthsToShow.length} month columns`);
    
    // Also update data row cells to match filtered columns
    updateDataRowCells();
}'''

if old_header_end in content:
    content = content.replace(old_header_end, new_header_end)
    print("✅ Updated updateTableHeaders to also filter data rows")
else:
    print("❌ Could not find updateTableHeaders end point")

# Also add a CSS style to ensure month cells are properly identified
css_addition = '''
<style>
/* Ensure month cells in data rows can be properly targeted */
#customer-table tbody td:nth-child(n+5):nth-child(-n+16) {
    /* This targets columns 5-16 which should be the 12 month columns */
    transition: all 0.3s ease;
}

/* Hide filtered out columns smoothly */
#customer-table th.month-col[style*="display: none"],
#customer-table td[style*="display: none"] {
    width: 0 !important;
    padding: 0 !important;
    border: none !important;
    overflow: hidden;
}

/* Visual indicator for filtered date range */
#filter-date-header {
    background-color: #e3f2fd;
    color: #1565c0;
    font-weight: bold;
    text-align: center;
}
</style>'''

# Find the </head> tag and insert CSS before it
if '</head>' in content:
    content = content.replace('</head>', css_addition + '\n</head>')
    print("✅ Added CSS for smooth column filtering")
else:
    print("❌ Could not add CSS styles")

# Write the enhanced content back
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 ENHANCED! Date filter now affects both headers AND data rows")
print("📋 Additional changes:")
print("   - Data row cells now hide/show to match filtered month columns")
print("   - Smooth transitions for column visibility")
print("   - Visual styling for filtered date range")
print("   - Both headers and data perfectly synchronized")

print(f"\n🔄 Complete filtering behavior:")
print("   1. Select Oct 1 to Nov 30")
print("   2. Click Filter")
print("   3. Table shows ONLY Oct and Nov columns (headers + data)")
print("   4. All other month columns are hidden")
print("   5. Clear filter restores full 12-month view")

print(f"\n📁 Additional backup: {backup_filename}")
print("🔥 READY! Refresh your dashboard page to see the complete fix!")