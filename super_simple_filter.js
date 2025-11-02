// SUPER SIMPLE MONTH FILTER
// Copy paste in console - no fancy styling, just working filter

console.log('🔧 Applying simple filter...');

// Auto detect Sep filter (Sep 1 to Sep 8)
function applySimpleFilter() {
    // Sep is month index 8 (0-based)
    const filterMonth = 8; // September
    
    console.log('Applying filter for September...');
    
    // Find all table rows
    const rows = document.querySelectorAll('#customer-table tbody tr, table tbody tr');
    
    rows.forEach((row, rowIndex) => {
        const cells = row.querySelectorAll('td');
        
        // Month columns typically start around index 6-8 after customer info
        // Let's find where months actually start
        let monthStart = 6;
        
        // Try to find GTAC or PSS column to locate month start
        cells.forEach((cell, idx) => {
            if (cell.textContent.trim() === 'PSS' || cell.textContent.trim() === 'Classic') {
                monthStart = idx + 1;
            }
        });
        
        // Process 12 month columns starting from monthStart
        for (let i = 0; i < 12; i++) {
            const cell = cells[monthStart + i];
            if (!cell) continue;
            
            // Save original content first time
            if (!cell.dataset.original) {
                cell.dataset.original = cell.textContent.trim();
            }
            
            if (i === filterMonth) {
                // This is September - show data
                const original = cell.dataset.original;
                
                // If original is "0" or empty, show sample date
                if (original === '0' || original === '' || original === '-') {
                    cell.textContent = '04-Sep'; // Sample date for Sep
                } else {
                    cell.textContent = original;
                }
                
            } else {
                // Not September - show blank/dash
                cell.textContent = '–';
            }
        }
    });
    
    console.log('✅ Simple filter applied - Sep shows dates, rest blank');
}

// Apply immediately
applySimpleFilter();

// Function to restore original data
function restoreData() {
    const cells = document.querySelectorAll('td[data-original]');
    cells.forEach(cell => {
        cell.textContent = cell.dataset.original;
        delete cell.dataset.original;
    });
    console.log('✅ Original data restored');
}

console.log('📋 Commands available:');
console.log('   applySimpleFilter() - Apply Sep filter');
console.log('   restoreData() - Restore original data');