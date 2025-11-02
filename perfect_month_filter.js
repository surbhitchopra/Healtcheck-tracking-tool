// PERFECT MONTH FILTER - Maintains exact format like in the image
// Paste this in browser console after dashboard loads

console.log('🎯 Applying perfect month filter that maintains format...');

function applyPerfectMonthFilter() {
    console.log('📅 Checking filter state...');
    
    // Get filter dates - try multiple possible selectors
    let startDate, endDate;
    
    // Try different selectors for date inputs
    const startInputs = [
        document.querySelector('#filter-start-date'),
        document.querySelector('input[name="start_date"]'),
        document.querySelector('input[placeholder*="From"]'),
        document.querySelector('.filter-content input[type="date"]:first-child')
    ];
    
    const endInputs = [
        document.querySelector('#filter-end-date'), 
        document.querySelector('input[name="end_date"]'),
        document.querySelector('input[placeholder*="To"]'),
        document.querySelector('.filter-content input[type="date"]:last-child')
    ];
    
    for (let input of startInputs) {
        if (input && input.value) {
            startDate = input.value;
            break;
        }
    }
    
    for (let input of endInputs) {
        if (input && input.value) {
            endDate = input.value;
            break;
        }
    }
    
    console.log(`📅 Found dates: ${startDate} to ${endDate}`);
    
    if (!startDate || !endDate) {
        console.log('📅 No filter - showing all original data');
        restoreOriginalFormat();
        return;
    }
    
    // Calculate active months
    const startMonth = new Date(startDate).getMonth(); // 0-based
    const endMonth = new Date(endDate).getMonth(); // 0-based
    
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    console.log(`📅 Active months: ${monthNames[startMonth]} to ${monthNames[endMonth]} (${startMonth}-${endMonth})`);
    
    // Apply selective filtering
    applySelectiveDataFilter(startMonth, endMonth);
    highlightActiveHeaders(startMonth, endMonth);
    showFilterBadge(startMonth, endMonth);
}

function applySelectiveDataFilter(startMonth, endMonth) {
    const tableBody = document.querySelector('#customer-table tbody');
    if (!tableBody) {
        console.log('❌ Table body not found');
        return;
    }
    
    const rows = tableBody.querySelectorAll('tr');
    console.log(`Processing ${rows.length} rows...`);
    
    rows.forEach((row, rowIndex) => {
        const cells = row.querySelectorAll('td');
        
        // Find month columns - they start after GTAC column
        let monthStartIndex = -1;
        
        // Look for GTAC column or PSS text to identify where months start
        cells.forEach((cell, index) => {
            const text = cell.textContent.trim().toLowerCase();
            if (text === 'pss' || text === 'classic' || text.includes('gtac')) {
                monthStartIndex = index + 1;
            }
        });
        
        // Fallback: assume months start at column 6
        if (monthStartIndex === -1) {
            monthStartIndex = 6;
        }
        
        if (rowIndex < 2) {
            console.log(`Row ${rowIndex}: Month columns start at index ${monthStartIndex}`);
        }
        
        // Process each of the 12 month columns
        for (let monthIndex = 0; monthIndex < 12; monthIndex++) {
            const cellIndex = monthStartIndex + monthIndex;
            const cell = cells[cellIndex];
            
            if (!cell) continue;
            
            // Save original content if not already saved
            if (!cell.hasAttribute('data-original-content')) {
                cell.setAttribute('data-original-content', cell.textContent.trim());
            }
            
            if (monthIndex >= startMonth && monthIndex <= endMonth) {
                // Active month - show original data with highlight
                const originalContent = cell.getAttribute('data-original-content');
                cell.textContent = originalContent;
                
                // Highlight active months (similar to your image)
                cell.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                cell.style.borderLeft = '3px solid #3b82f6';
                cell.style.fontWeight = '600';
                cell.style.color = '#1e40af';
            } else {
                // Inactive month - show dash (maintaining exact format)
                cell.textContent = '–';  // Using en-dash like in your image
                cell.style.backgroundColor = '#f9fafb';
                cell.style.borderLeft = '1px solid #e5e7eb';
                cell.style.fontWeight = 'normal';
                cell.style.color = '#9ca3af';
                cell.style.textAlign = 'center';
            }
        }
    });
    
    console.log('✅ Applied selective month filtering');
}

function highlightActiveHeaders(startMonth, endMonth) {
    const headerRow = document.querySelector('#customer-table thead tr');
    if (!headerRow) return;
    
    const monthHeaders = [];
    const allHeaders = headerRow.querySelectorAll('th');
    
    // Find month headers by text content
    allHeaders.forEach(header => {
        const text = header.textContent.trim().toUpperCase();
        if (['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
             'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'].includes(text)) {
            monthHeaders.push(header);
        }
    });
    
    console.log(`Found ${monthHeaders.length} month headers`);
    
    // Style headers
    monthHeaders.forEach((header, index) => {
        if (index >= startMonth && index <= endMonth) {
            // Active month header
            header.style.backgroundColor = '#3b82f6';
            header.style.color = 'white';
            header.style.fontWeight = 'bold';
            header.style.borderBottom = '3px solid #1e40af';
        } else {
            // Inactive month header
            header.style.backgroundColor = '#f8f9fa';
            header.style.color = '#6c757d';
            header.style.fontWeight = 'normal';
            header.style.borderBottom = '1px solid #dee2e6';
        }
    });
}

function showFilterBadge(startMonth, endMonth) {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Remove existing badge
    const existing = document.querySelector('#filter-badge');
    if (existing) existing.remove();
    
    // Create filter badge
    const badge = document.createElement('div');
    badge.id = 'filter-badge';
    badge.innerHTML = `📊 Data: ${monthNames[startMonth]}–${monthNames[endMonth]}`;
    badge.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        z-index: 1000;
        border: 2px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    `;
    
    document.body.appendChild(badge);
}

function restoreOriginalFormat() {
    console.log('🔄 Restoring original format...');
    
    // Reset all month headers
    const headerRow = document.querySelector('#customer-table thead tr');
    if (headerRow) {
        const allHeaders = headerRow.querySelectorAll('th');
        allHeaders.forEach(header => {
            const text = header.textContent.trim().toUpperCase();
            if (['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'].includes(text)) {
                header.style.backgroundColor = '';
                header.style.color = '';
                header.style.fontWeight = '';
                header.style.borderBottom = '';
            }
        });
    }
    
    // Reset all data cells
    const tableBody = document.querySelector('#customer-table tbody');
    if (tableBody) {
        const allCells = tableBody.querySelectorAll('td[data-original-content]');
        allCells.forEach(cell => {
            const originalContent = cell.getAttribute('data-original-content');
            cell.textContent = originalContent;
            cell.removeAttribute('data-original-content');
            cell.style.backgroundColor = '';
            cell.style.borderLeft = '';
            cell.style.fontWeight = '';
            cell.style.color = '';
            cell.style.textAlign = '';
        });
    }
    
    // Remove filter badge
    const badge = document.querySelector('#filter-badge');
    if (badge) badge.remove();
    
    console.log('✅ Original format restored');
}

// Apply immediately
setTimeout(applyPerfectMonthFilter, 1000);

// Hook into filter button
document.addEventListener('click', function(e) {
    if (e.target.textContent.includes('FILTER') || e.target.id === 'apply-filter' || e.target.onclick && e.target.onclick.toString().includes('applyCustomerFilter')) {
        console.log('🔄 Filter button clicked - applying in 2 seconds...');
        setTimeout(applyPerfectMonthFilter, 2000);
    }
    
    if (e.target.textContent.includes('CLEAR') || e.target.id === 'clear-filter' || e.target.onclick && e.target.onclick.toString().includes('clearFilter')) {
        console.log('🔄 Clear button clicked - restoring format...');
        setTimeout(restoreOriginalFormat, 500);
    }
});

console.log('🎯 Perfect month filter ready!');
console.log('📋 Usage:');
console.log('   1. Set date filter (e.g., Oct 1 to Nov 30)');
console.log('   2. Click FILTER button');  
console.log('   3. Only Oct-Nov will show dates, rest show "–"');
console.log('   4. Click CLEAR to restore all original data');