// TEMPLATE VIEW FIX - Network Dates Display Issue
// Run this in browser console

console.log("🔧 TEMPLATE VIEW FIX STARTING...");

// Quick fix for network dates display - DD-MMM format only
window.quickFixNetworkDates = function() {
    console.log("🚀 QUICK FIXING NETWORK DATES...");
    
    if (!window.dashboardData || !window.dashboardData.customers) {
        console.log("❌ No dashboard data");
        return;
    }
    
    let fixedCount = 0;
    
    // Find all table rows
    document.querySelectorAll('tr').forEach(row => {
        const cells = row.querySelectorAll('td');
        
        if (cells.length >= 4) {
            const networkNameCell = cells[1];
            const dateCell = cells[3];
            
            if (!networkNameCell || !dateCell) return;
            
            const networkName = networkNameCell.textContent.trim();
            
            // Skip if not a network row
            if (!networkName || 
                networkName.includes('💾') || 
                networkName.includes('Total') ||
                networkName.length < 3) return;
            
            // Find network data
            window.dashboardData.customers.forEach(customer => {
                if (customer.networks) {
                    customer.networks.forEach(network => {
                        if (network.name === networkName) {
                            console.log(`🔍 Found: ${networkName}`);
                            
                            // Get date from network data
                            let dateToShow = '-';
                            
                            if (network.monthly_runs && Array.isArray(network.monthly_runs) && network.monthly_runs.length > 0) {
                                // Get latest run
                                const latestRun = network.monthly_runs[network.monthly_runs.length - 1];
                                dateToShow = formatDateDDMMM(latestRun);
                                console.log(`📅 Network date: ${dateToShow}`);
                            }
                            else if (network.last_run_date && network.last_run_date !== 'Never') {
                                dateToShow = formatDateDDMMM(network.last_run_date);
                                console.log(`📅 Last run date: ${dateToShow}`);
                            }
                            else if (customer.last_run_date && customer.last_run_date !== 'Never') {
                                dateToShow = formatDateDDMMM(customer.last_run_date);
                                console.log(`📅 Customer fallback: ${dateToShow}`);
                            }
                            
                            // Update cell if we have a valid date
                            if (dateToShow !== '-') {
                                dateCell.textContent = dateToShow;
                                dateCell.style.color = '#28a745';
                                dateCell.style.fontWeight = 'bold';
                                fixedCount++;
                                console.log(`✅ FIXED: ${networkName} → ${dateToShow}`);
                            } else {
                                console.log(`⚠️ No date found for: ${networkName}`);
                            }
                        }
                    });
                }
            });
        }
    });
    
    console.log(`🎉 COMPLETED: Fixed ${fixedCount} network dates`);
    return fixedCount;
};

// Format date to DD-MMM only (no year)
function formatDateDDMMM(dateValue) {
    if (!dateValue || dateValue === 'Never' || dateValue === '-') return '-';
    
    const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    let date;
    
    try {
        // Try to parse as Date
        if (typeof dateValue === 'string' && dateValue.includes('-')) {
            // Handle formats like "2024-10-09" or "09-Oct-24"
            const parts = dateValue.split('-');
            if (parts.length === 3) {
                if (parts[0].length === 4) {
                    // YYYY-MM-DD
                    date = new Date(dateValue);
                } else if (monthNames.includes(parts[1])) {
                    // DD-MMM-YY
                    const day = parseInt(parts[0]);
                    const monthIndex = monthNames.indexOf(parts[1]);
                    return `${day.toString().padStart(2, '0')}-${parts[1]}`; // Just DD-MMM
                } else {
                    // DD-MM-YYYY
                    date = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
                }
            }
        } else {
            date = new Date(dateValue);
        }
        
        if (isNaN(date.getTime())) return '-';
        
        const day = date.getDate();
        const month = monthNames[date.getMonth()];
        
        return `${day.toString().padStart(2, '0')}-${month}`;
        
    } catch (e) {
        console.log(`Date parse error: ${e.message}`);
        return '-';
    }
}

// Auto-run the fix
console.log("🎯 Running automatic fix...");
window.quickFixNetworkDates();

// Provide manual trigger
console.log("💡 Manual trigger available: quickFixNetworkDates()");

console.log("✅ TEMPLATE FIX COMPLETE!");