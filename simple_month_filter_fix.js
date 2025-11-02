// SIMPLE MONTH FILTER FIX
// Copy this code and paste in browser console when dashboard is loaded

console.log('🔧 Applying simple month filter fix...');

// Function to apply selective month data based on current filter
function applySelectiveMonthFilter() {
    console.log('📅 Checking current filter state...');
    
    // Check if filter is active by looking at the date inputs
    const startDateInput = document.querySelector('#filter-start-date');
    const endDateInput = document.querySelector('#filter-end-date');
    
    if (!startDateInput || !endDateInput) {
        console.log('❌ Date inputs not found');
        return;
    }
    
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    console.log(`📅 Filter dates: ${startDate} to ${endDate}`);
    
    if (!startDate || !endDate) {
        console.log('📅 No filter active - showing all data');
        restoreAllMonthData();
        return;
    }
    
    // Calculate which months should show data
    const startMonth = new Date(startDate).getMonth(); // 0-based
    const endMonth = new Date(endDate).getMonth(); // 0-based
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    console.log(`📅 Active months: ${monthNames[startMonth]} (${startMonth}) to ${monthNames[endMonth]} (${endMonth})`);
    
    // Style the headers
    styleMonthHeaders(startMonth, endMonth);
    
    // Update data rows
    updateMonthDataCells(startMonth, endMonth);
    
    // Show filter indicator
    showActiveFilterIndicator(startMonth, endMonth);
}

function styleMonthHeaders(startMonth, endMonth) {
    const headerRow = document.querySelector('#customer-table thead tr');
    if (!headerRow) return;
    
    // Find month headers (JAN, FEB, MAR, etc.)
    const allHeaders = headerRow.querySelectorAll('th');
    const monthHeaders = [];
    
    // Identify month headers by their text content
    allHeaders.forEach(header => {
        const text = header.textContent.trim().toLowerCase();
        if (['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].includes(text)) {
            monthHeaders.push(header);
        }
    });
    
    console.log(`Found ${monthHeaders.length} month headers`);
    
    // Style each month header
    monthHeaders.forEach((header, index) => {
        if (index >= startMonth && index <= endMonth) {
            // Active month
            header.style.backgroundColor = '#3b82f6';
            header.style.color = 'white';
            header.style.fontWeight = 'bold';
            console.log(`✅ Activated header: ${header.textContent}`);
        } else {
            // Inactive month
            header.style.backgroundColor = '#f3f4f6';
            header.style.color = '#9ca3af';
            header.style.fontWeight = 'normal';
            console.log(`⚪ Deactivated header: ${header.textContent}`);
        }
    });
}

function updateMonthDataCells(startMonth, endMonth) {
    const tableBody = document.querySelector('#customer-table tbody');
    if (!tableBody) return;
    
    const allRows = tableBody.querySelectorAll('tr');
    console.log(`Processing ${allRows.length} data rows...`);
    
    allRows.forEach((row, rowIndex) => {
        const cells = row.querySelectorAll('td');
        
        // Find the starting position of month cells
        // They typically start after: Customer, Country, Networks, Node Qty, NE Type, GTAC
        let monthStartIndex = 6; // Adjust this based on your table structure
        
        // Try to find GTAC column to determine month start position
        cells.forEach((cell, cellIndex) => {
            const cellText = cell.textContent.trim().toLowerCase();
            if (cellText === 'pss' || cellText.includes('gtac')) {
                monthStartIndex = cellIndex + 1;
            }
        });
        
        // Process 12 month cells
        for (let monthIndex = 0; monthIndex < 12; monthIndex++) {
            const cellIndex = monthStartIndex + monthIndex;
            const cell = cells[cellIndex];
            
            if (!cell) continue;
            
            if (monthIndex >= startMonth && monthIndex <= endMonth) {
                // Show data for active months
                const originalData = cell.getAttribute('data-original') || cell.textContent;
                if (!cell.getAttribute('data-original')) {
                    cell.setAttribute('data-original', originalData);
                }
                
                cell.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                cell.style.border = '2px solid #3b82f6';
                cell.style.fontWeight = '600';
                cell.style.color = '#1e40af';
            } else {
                // Hide data for inactive months
                const originalData = cell.getAttribute('data-original') || cell.textContent;
                if (!cell.getAttribute('data-original')) {
                    cell.setAttribute('data-original', originalData);
                }
                
                cell.textContent = '—';
                cell.style.backgroundColor = '#f9fafb';
                cell.style.border = '1px solid #e5e7eb';
                cell.style.fontWeight = 'normal';
                cell.style.color = '#9ca3af';
                cell.style.textAlign = 'center';
            }
        }
    });
    
    console.log('✅ Updated all month data cells');
}

function restoreAllMonthData() {
    console.log('🔄 Restoring all month data...');
    
    // Reset headers
    const headerRow = document.querySelector('#customer-table thead tr');
    if (headerRow) {
        const allHeaders = headerRow.querySelectorAll('th');
        allHeaders.forEach(header => {
            const text = header.textContent.trim().toLowerCase();
            if (['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].includes(text)) {
                header.style.backgroundColor = '';
                header.style.color = '';
                header.style.fontWeight = '';
            }
        });
    }
    
    // Restore data cells
    const tableBody = document.querySelector('#customer-table tbody');
    if (tableBody) {
        const allCells = tableBody.querySelectorAll('td[data-original]');
        allCells.forEach(cell => {
            const originalData = cell.getAttribute('data-original');
            cell.textContent = originalData;
            cell.removeAttribute('data-original');
            cell.style.backgroundColor = '';
            cell.style.border = '';
            cell.style.fontWeight = '';
            cell.style.color = '';
            cell.style.textAlign = '';
        });
    }
    
    // Hide filter indicator
    const indicator = document.querySelector('#filter-indicator');
    if (indicator) {
        indicator.remove();
    }
    
    console.log('✅ Restored all original data');
}

function showActiveFilterIndicator(startMonth, endMonth) {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Remove existing indicator
    const existing = document.querySelector('#filter-indicator');
    if (existing) existing.remove();
    
    // Create new indicator
    const indicator = document.createElement('div');
    indicator.id = 'filter-indicator';
    indicator.innerHTML = `📅 Active: ${monthNames[startMonth]} - ${monthNames[endMonth]}`;
    indicator.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: #3b82f6;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        border: 2px solid #1e40af;
    `;
    
    document.body.appendChild(indicator);
}

// Apply the fix immediately
applySelectiveMonthFilter();

// Also apply when filter button is clicked
const filterButton = document.querySelector('button[onclick*="applyCustomerFilter"]');
if (filterButton) {
    filterButton.addEventListener('click', function() {
        setTimeout(applySelectiveMonthFilter, 1000); // Wait for data to load
    });
}

// Apply when clear button is clicked
const clearButton = document.querySelector('button[onclick*="clearFilter"]');
if (clearButton) {
    clearButton.addEventListener('click', function() {
        setTimeout(restoreAllMonthData, 500);
    });
}

console.log('✅ Month filter fix applied! Now test your filter.');