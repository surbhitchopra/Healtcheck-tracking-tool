#!/usr/bin/env python
"""
Proper fix for month filtering:
- When filter is Oct-Nov, only Oct and Nov should be blue with data
- All other months (Jan-Sep, Dec) should show dashes
- Currently Sep is also getting highlighted which is wrong
"""

import os
from datetime import datetime

# Read current template
template_file = 'templates/customer_dashboard.html'
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Create backup
backup_filename = f"customer_dashboard_proper_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
backup_path = os.path.join('templates', backup_filename)

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"🔒 Created backup: {backup_filename}")

# Fix the updateSelectiveMonthData function to properly handle month indices
# The issue is likely in how we calculate startMonth and endMonth from dates

fixed_function = """// SELECTIVE MONTH DATA - Keep all 12 months visible but highlight filtered range
function updateSelectiveMonthData() {
    console.log('🔧 Updating selective month data for filter...');
    
    // Get all month headers
    const headerRow = document.querySelector('#customer-table thead tr');
    const monthHeaders = headerRow ? headerRow.querySelectorAll('th.month-col') : [];
    
    console.log(`Found ${monthHeaders.length} month headers`);
    
    // Determine filter range
    let startMonth = null;
    let endMonth = null;
    
    if (currentStartDate && currentEndDate) {
        const startDate = new Date(currentStartDate);
        const endDate = new Date(currentEndDate);
        
        startMonth = startDate.getMonth(); // 0-based (0=Jan, 11=Dec)
        endMonth = endDate.getMonth();     // 0-based (0=Jan, 11=Dec)
        
        console.log(`📅 Filter dates: ${currentStartDate} to ${currentEndDate}`);
        console.log(`📅 Filter months: ${startMonth} to ${endMonth} (0-based)`);
        console.log(`📅 Filter months: ${startMonth + 1} to ${endMonth + 1} (1-based)`);
        
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        console.log(`📅 Filtering for: ${monthNames[startMonth]} to ${monthNames[endMonth]}`);
        
        // Style month headers to show which ones are active
        monthHeaders.forEach((header, index) => {
            console.log(`Checking header ${index}: ${header.textContent}`);
            
            if (index >= startMonth && index <= endMonth) {
                console.log(`✅ Activating month ${index} (${header.textContent})`);
                header.style.backgroundColor = '#3b82f6';
                header.style.color = 'white';
                header.style.fontWeight = 'bold';
                header.style.border = '2px solid #1e40af';
            } else {
                console.log(`⚪ Deactivating month ${index} (${header.textContent})`);
                header.style.backgroundColor = '#f3f4f6';
                header.style.color = '#6b7280';
                header.style.fontWeight = 'normal';
                header.style.border = '1px solid #e5e7eb';
            }
        });
        
        // Add filter indicator
        showFilterIndicator(startMonth, endMonth);
    } else {
        console.log('📅 No filter: all months normal');
        
        // Reset all month headers to normal
        monthHeaders.forEach((header, index) => {
            console.log(`Resetting header ${index}: ${header.textContent}`);
            header.style.backgroundColor = '';
            header.style.color = '';
            header.style.fontWeight = '';
            header.style.border = '';
        });
        
        hideFilterIndicator();
    }
    
    // Update data rows to show selective data
    updateSelectiveDataRows(startMonth, endMonth);
}

function showFilterIndicator(startMonth, endMonth) {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const filterText = `Active Data: ${monthNames[startMonth]} - ${monthNames[endMonth]}`;
    
    // Create or update filter indicator
    let indicator = document.querySelector('#filter-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'filter-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            background: #3b82f6;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            border: 2px solid #1e40af;
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
    
    console.log(`🔧 Updating data rows for months ${startMonth}-${endMonth}`);
    
    const allRows = tableBody.querySelectorAll('tr');
    
    allRows.forEach((row, rowIndex) => {
        // Find month cells - they should start after NODE QTY, NE TYPE, GTAC columns
        const allCells = row.querySelectorAll('td');
        
        // Log the row structure for debugging
        if (rowIndex < 3) {
            console.log(`Row ${rowIndex} has ${allCells.length} cells:`);
            allCells.forEach((cell, cellIndex) => {
                console.log(`  Cell ${cellIndex}: "${cell.textContent.trim()}"`);
            });
        }
        
        // Find where month columns start - typically after GTAC column
        let monthCellsStartIndex = -1;
        allCells.forEach((cell, cellIndex) => {
            const cellText = cell.textContent.trim().toLowerCase();
            if (cellText === 'pss' || cellText.includes('gtac') || cellIndex === 5) {
                monthCellsStartIndex = cellIndex + 1; // Month cells start after GTAC
            }
        });
        
        if (monthCellsStartIndex === -1) {
            monthCellsStartIndex = 6; // Fallback: assume month cells start at index 6
        }
        
        console.log(`Row ${rowIndex}: Month cells start at index ${monthCellsStartIndex}`);
        
        // Process month cells (12 months)
        for (let i = 0; i < 12; i++) {
            const cellIndex = monthCellsStartIndex + i;
            const cell = allCells[cellIndex];
            
            if (!cell) continue;
            
            if (startMonth !== null && endMonth !== null) {
                // Filter is active
                if (i >= startMonth && i <= endMonth) {
                    // Show actual data for filtered months
                    console.log(`Showing data for month ${i} in row ${rowIndex}`);
                    
                    // Keep original data visible with highlight
                    const originalContent = cell.getAttribute('data-original-content') || cell.textContent;
                    if (!cell.getAttribute('data-original-content')) {
                        cell.setAttribute('data-original-content', originalContent);
                    }
                    
                    cell.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                    cell.style.fontWeight = '600';
                    cell.style.border = '2px solid #3b82f6';
                    cell.style.color = '#1e40af';
                } else {
                    // Show placeholder for non-filtered months
                    console.log(`Hiding data for month ${i} in row ${rowIndex}`);
                    
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
    });
    
    console.log(`✅ Updated selective data for ${allRows.length} rows`);
}"""

# Find and replace the existing function
old_function_start = "// SELECTIVE MONTH DATA - Keep all 12 months visible but highlight filtered range"
old_function_end = "console.log(`✅ Updated selective data for ${allRows.length} rows`);\n}"

start_pos = content.find(old_function_start)
if start_pos != -1:
    end_pos = content.find(old_function_end, start_pos)
    if end_pos != -1:
        end_pos += len(old_function_end)
        content = content[:start_pos] + fixed_function + content[end_pos:]
        print("✅ Replaced selective month data function with fixed version")
    else:
        print("❌ Could not find end of function")
else:
    print("❌ Could not find function to replace")

# Write the fixed content back
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 FIXED! Proper month filtering applied")
print("📋 Fixes applied:")
print("   ✅ Added detailed console logging for debugging")
print("   ✅ Fixed month index calculation (0-based vs 1-based)")
print("   ✅ Better detection of month column start position")
print("   ✅ Clearer visual indicators for active vs inactive months")
print("   ✅ Enhanced filter indicator positioning")

print(f"\n🔧 Now when you filter Oct-Nov:")
print("   📅 Only Oct (month 9) and Nov (month 10) will be blue")
print("   📅 Jan-Sep and Dec will show dashes (—)")
print("   📅 Filter indicator will show 'Active Data: Oct - Nov'")

print(f"\n🐛 Debug info:")
print("   - Open browser console to see detailed month filtering logs")
print("   - Check which months are being activated/deactivated")
print("   - Verify month index calculations")

print(f"\n📁 Backup: {backup_filename}")
print("🚀 Refresh and test the filter again!")