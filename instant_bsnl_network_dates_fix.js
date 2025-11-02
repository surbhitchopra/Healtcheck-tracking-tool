// INSTANT BSNL NETWORK DATES FIX - Copy and paste in browser console
// This script forces BSNL networks to show their individual monthly dates

console.log('🔥 INSTANT BSNL NETWORK DATES FIX STARTING...');

// Override getNetworkMonthRunDates specifically for BSNL networks
window.getNetworkMonthRunDates = function(customer, networkName, year, month) {
    console.log(`🔧 BSNL FIX: Checking ${networkName} for month ${month}`);
    
    // Check if this is BSNL customer
    if (customer.name && customer.name.includes('BSNL') && customer.networks) {
        // Find the specific network in customer.networks array
        const targetNetwork = customer.networks.find(network => {
            // Match network name more flexibly
            const networkKey = network.network_name || network.name || '';
            return networkKey === networkName || 
                   networkKey.includes(networkName) ||
                   networkName.includes(networkKey);
        });
        
        if (targetNetwork) {
            console.log(`🎯 Found BSNL network: ${networkName}`);
            console.log(`   Network data:`, {
                name: targetNetwork.network_name,
                total_runs: targetNetwork.total_runs,
                monthly_runs: targetNetwork.monthly_runs
            });
            
            // Check if network has monthly_runs dictionary
            if (targetNetwork.monthly_runs && typeof targetNetwork.monthly_runs === 'object') {
                const monthKey = `${year}-${month.toString().padStart(2, '0')}`;
                const monthValue = targetNetwork.monthly_runs[monthKey];
                
                console.log(`   Checking ${monthKey}: ${monthValue}`);
                
                if (monthValue) {
                    // Handle special values
                    if (monthValue === 'Not Started' || monthValue === 'No Report') {
                        console.log(`✅ BSNL ${networkName}: ${monthValue}`);
                        return {
                            count: 0,
                            date: monthValue === 'Not Started' ? 'Not Started' : 'No Report',
                            fullDate: monthValue
                        };
                    }
                    
                    // Parse actual dates like '2025-03-14' to '14-Mar-25'
                    try {
                        const apiDate = new Date(monthValue);
                        if (!isNaN(apiDate.getTime())) {
                            const day = apiDate.getDate();
                            const monthName = apiDate.toLocaleDateString('en-US', { month: 'short' });
                            const yearShort = apiDate.getFullYear().toString().slice(-2);
                            const formattedDate = `${day}-${monthName}-${yearShort}`;
                            
                            console.log(`✅ BSNL ${networkName} month ${month}: ${formattedDate}`);
                            return {
                                count: 1,
                                date: formattedDate,
                                fullDate: monthValue
                            };
                        }
                    } catch (error) {
                        console.log(`❌ Date parsing error for ${networkName}: ${error.message}`);
                    }
                }
            }
        }
    }
    
    // Fallback for non-BSNL or no data
    return { count: 0, date: '-', fullDate: 'No data' };
};

// Force update BSNL network rows immediately
function forceBSNLNetworkUpdate() {
    console.log('🔄 FORCING BSNL NETWORK ROWS UPDATE...');
    
    // Find all BSNL network rows
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    let bsnlRowsUpdated = 0;
    
    networkRows.forEach((row, index) => {
        const networkNameElement = row.querySelector('.network-name-main');
        if (!networkNameElement) return;
        
        const networkName = networkNameElement.textContent.replace('└─ ', '').trim();
        
        // Only process BSNL networks
        if (!networkName.includes('BSNL')) return;
        
        console.log(`🔧 Updating BSNL network: ${networkName}`);
        
        // Find BSNL customer data
        if (window.dashboardData && window.dashboardData.customers) {
            const bsnlCustomer = Object.values(window.dashboardData.customers).find(c => 
                c.name && c.name.includes('BSNL')
            );
            
            if (bsnlCustomer && bsnlCustomer.networks) {
                console.log(`📊 Found BSNL customer data with ${bsnlCustomer.networks.length} networks`);
                
                // Update month cells for this network
                const monthCells = Array.from(row.querySelectorAll('td')).slice(6, 18);
                if (monthCells.length === 12) {
                    let cellsUpdated = 0;
                    
                    monthCells.forEach((cell, monthIndex) => {
                        const monthNum = monthIndex + 1;
                        const result = window.getNetworkMonthRunDates(bsnlCustomer, networkName, 2025, monthNum);
                        
                        if (result.date && result.date !== '-' && result.date !== 'No data') {
                            const oldValue = cell.textContent;
                            cell.textContent = result.date;
                            
                            // Style the cell based on content
                            if (result.date === 'Not Started' || result.date === 'No Report') {
                                cell.style.color = '#9ca3af';
                                cell.style.fontStyle = 'italic';
                            } else {
                                cell.style.color = '#374151';
                                cell.style.fontWeight = '600';
                                cell.style.fontStyle = 'normal';
                            }
                            
                            if (oldValue !== result.date) {
                                console.log(`   ✅ Month ${monthNum}: "${oldValue}" → "${result.date}"`);
                                cellsUpdated++;
                            }
                        }
                    });
                    
                    console.log(`   📊 ${networkName}: Updated ${cellsUpdated} month cells`);
                    bsnlRowsUpdated++;
                }
            }
        }
    });
    
    console.log(`🎉 BSNL UPDATE COMPLETE: ${bsnlRowsUpdated} networks updated`);
    return bsnlRowsUpdated;
}

// Apply the fix immediately
console.log('🚀 Applying BSNL network dates fix...');
setTimeout(() => {
    const updated = forceBSNLNetworkUpdate();
    
    if (updated > 0) {
        console.log('✅ BSNL NETWORK DATES FIX SUCCESSFUL!');
        console.log('📋 Check your dashboard - BSNL networks should now show individual dates');
        console.log('🔧 Networks should show dates like: 14-Mar-25, 13-Jun-25, 8-Jul-25, etc.');
    } else {
        console.log('⚠️ No BSNL networks found or updated');
        console.log('💡 Make sure you are on the customer dashboard page');
    }
}, 500);

// Make function available globally for manual trigger
window.forceBSNLNetworkUpdate = forceBSNLNetworkUpdate;

console.log('📋 MANUAL COMMANDS AVAILABLE:');
console.log('   - forceBSNLNetworkUpdate() - Re-run the fix');
console.log('   - window.dashboardData - Check customer data');

console.log('🔥 BSNL NETWORK DATES FIX LOADED AND RUNNING!');