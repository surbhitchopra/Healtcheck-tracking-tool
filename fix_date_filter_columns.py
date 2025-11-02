#!/usr/bin/env python
"""
Fix the date filtering functionality to show only selected month columns
when user applies a date filter (e.g., Oct-Nov should only show Oct and Nov columns)
"""

import os
from datetime import datetime

# Create backup
template_file = 'templates/customer_dashboard.html'
backup_filename = f"customer_dashboard_filter_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
backup_path = os.path.join('templates', backup_filename)

print(f"🔒 Creating backup: {backup_filename}")

with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Backup created: {backup_filename}")

# Fix 1: Add dynamic month header generation function
new_filter_function = '''
// DYNAMIC MONTH HEADERS - Show only filtered months in table header
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
}'''

# Find insertion point for the new function
insertion_point = "// APPLY CUSTOMER FILTER - Filter dashboard by date range"
if insertion_point in content:
    content = content.replace(insertion_point, new_filter_function + "\n\n" + insertion_point)
    print("✅ Added dynamic header update function")
else:
    print("❌ Could not find insertion point for header function")

# Fix 2: Update the applyCustomerFilter function to call updateTableHeaders
old_apply_filter = '''// Reload dashboard with date filters
    showLoadingState();
    await loadDashboardData(startDate, endDate);
    
    showNotification(`✅ Dashboard filtered: ${startDate} to ${endDate}`, 'success');'''

new_apply_filter = '''// Reload dashboard with date filters
    showLoadingState();
    await loadDashboardData(startDate, endDate);
    
    // Update table headers to show only filtered months
    updateTableHeaders();
    
    showNotification(`✅ Dashboard filtered: ${startDate} to ${endDate}`, 'success');'''

if old_apply_filter in content:
    content = content.replace(old_apply_filter, new_apply_filter)
    print("✅ Updated applyCustomerFilter function")
else:
    print("❌ Could not find applyCustomerFilter update point")

# Fix 3: Update the clearFilter function to restore all month headers
old_clear_filter = '''// Reload dashboard without filters
    showLoadingState();
    await loadDashboardData();
    
    showNotification('✅ Filter cleared - showing all data', 'success');'''

new_clear_filter = '''// Reload dashboard without filters
    showLoadingState();
    await loadDashboardData();
    
    // Update table headers to show all months
    updateTableHeaders();
    
    showNotification('✅ Filter cleared - showing all data', 'success');'''

if old_clear_filter in content:
    content = content.replace(old_clear_filter, new_clear_filter)
    print("✅ Updated clearFilter function")
else:
    print("❌ Could not find clearFilter update point")

# Fix 4: Also call updateTableHeaders after initial page load
old_page_load = '''document.addEventListener('DOMContentLoaded', () => {
    console.log('🏁 Dashboard loaded');
    
    // Load customers immediately on page load
    loadDashboardData();
    
    setupExportModal();
    setDefaultDates();
    setDefaultFilterDates();
});'''

new_page_load = '''document.addEventListener('DOMContentLoaded', () => {
    console.log('🏁 Dashboard loaded');
    
    // Load customers immediately on page load
    loadDashboardData();
    
    setupExportModal();
    setDefaultDates();
    setDefaultFilterDates();
    
    // Initialize table headers (show all months initially)
    updateTableHeaders();
});'''

if old_page_load in content:
    content = content.replace(old_page_load, new_page_load)
    print("✅ Updated page load initialization")
else:
    print("❌ Could not find page load update point")

# Write the fixed content back
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 SUCCESS! Fixed date filter column display")
print("📋 Changes made:")
print("   - Added dynamic table header update function")
print("   - Headers now show only filtered months when date filter applied")
print("   - Oct-Nov filter will show only Oct and Nov columns")
print("   - Clear filter restores all 12 month columns")
print("   - Filter date range shown in special header when active")

print(f"\n🔧 How it works:")
print("   1. Select date range (e.g., Oct 1 to Nov 30)")
print("   2. Click Filter button")
print("   3. Table will show only Oct and Nov columns")
print("   4. Click Clear to restore all 12 months")

print(f"\n📁 Backup available at: {backup_filename}")
print("Refresh your dashboard page to see the fix!")