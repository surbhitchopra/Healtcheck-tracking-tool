// FINAL INSTANT FIX: Show Real Network Dates from Database
// Copy-paste this entire script in browser console

console.log('🔧 APPLYING FINAL NETWORK DATES FIX - DIRECT DATABASE ACCESS...');

// Override createNetworkDetailRow to directly access network database dates
const originalCreateNetworkDetailRow = window.createNetworkDetailRow;

window.createNetworkDetailRow = function(customer, network, networkIndex, currentYear, months) {
    console.log(`🔧 FIXED: Creating network row for ${network.name || network.network_name}`);
    
    // Call original function to get the base row
    const row = originalCreateNetworkDetailRow(customer, network, networkIndex, currentYear, months);
    
    // Find all month cells (they should be the last 12 td elements before total)
    const monthCells = Array.from(row.querySelectorAll('td')).slice(-13, -1); // Last 12 cells before total
    
    if (monthCells.length === 12) {
        console.log(`🔧 FIXING: ${monthCells.length} month cells found for ${network.name}`);
        
        // Get the network name for matching
        const networkName = network.network_name || network.name || network;
        const cleanNetworkName = typeof networkName === 'string' && networkName.includes(' - ') ? 
                                 networkName.split(' - ').slice(-1)[0] : networkName;
        
        // Find the actual network object in customer.networks
        let targetNetwork = null;
        if (customer.networks && Array.isArray(customer.networks)) {
            targetNetwork = customer.networks.find(net => {
                return net.network_name === cleanNetworkName || 
                       net.name === cleanNetworkName ||
                       net.name === networkName ||
                       net.name === `${customer.name} - ${cleanNetworkName}` ||
                       net.name.includes(cleanNetworkName) ||
                       cleanNetworkName.includes(net.name);
            });
        }
        
        if (targetNetwork) {
            console.log(`🎯 FOUND: Network "${cleanNetworkName}" matched with database network:`, {
                name: targetNetwork.name,
                runs: targetNetwork.runs,
                last_run_date: targetNetwork.last_run_date
            });
            
            // Update each month cell with actual network date if available
            monthCells.forEach((monthCell, monthIndex) => {
                const monthNum = monthIndex + 1;
                
                // Check if this network had runs in this specific month
                if (targetNetwork.last_run_date && 
                    targetNetwork.last_run_date !== 'Never' && 
                    targetNetwork.last_run_date !== '-' && 
                    targetNetwork.runs > 0) {
                    
                    try {
                        const networkDate = new Date(targetNetwork.last_run_date);
                        if (!isNaN(networkDate.getTime())) {
                            const networkYear = networkDate.getFullYear();
                            const networkMonth = networkDate.getMonth() + 1;
                            
                            // If this network's last run was in this specific month
                            if (networkYear === currentYear && networkMonth === monthNum) {
                                const day = networkDate.getDate();
                                const monthName = networkDate.toLocaleDateString('en-US', { month: 'short' });
                                const yearShort = networkDate.getFullYear().toString().slice(-2);
                                const formattedDate = `${day}-${monthName}-${yearShort}`;
                                
                                monthCell.textContent = formattedDate;
                                monthCell.title = `${targetNetwork.runs} runs from ${cleanNetworkName} on ${formattedDate}`;
                                monthCell.style.color = '#374151';
                                monthCell.style.fontWeight = '600';
                                
                                console.log(`✅ FIXED: ${cleanNetworkName} month ${monthNum} = ${formattedDate}`);
                            } else {
                                // Network has data but not for this month
                                monthCell.textContent = '-';
                                monthCell.title = `No runs from ${cleanNetworkName} in month ${monthNum}`;
                                monthCell.style.color = '#9ca3af';
                            }
                        }
                    } catch (error) {
                        console.log(`❌ Date parsing error: ${error.message}`);
                        monthCell.textContent = '-';
                        monthCell.style.color = '#9ca3af';
                    }
                } else {
                    // Network has no runs or no date
                    monthCell.textContent = '-';
                    monthCell.title = `No runs from ${cleanNetworkName} in month ${monthNum}`;
                    monthCell.style.color = '#9ca3af';
                }
            });
        } else {
            console.log(`❌ NO MATCH: Could not find database network for "${cleanNetworkName}"`);
            if (customer.networks) {
                console.log(`Available networks:`, customer.networks.map(n => n.name || n.network_name));
            }
        }
    }
    
    return row;
};

// Refresh the dashboard
console.log('🔄 Refreshing dashboard with real network dates...');
if (typeof updateCustomerGrid === 'function') {
    updateCustomerGrid();
    console.log('✅ FINAL FIX APPLIED! Networks should now show their actual database dates.');
    console.log('📋 Check BSNL networks - they should now show different dates per network.');
} else {
    console.log('⚠️ updateCustomerGrid function not found. Please refresh the page first.');
}

// Test with BSNL to verify
setTimeout(() => {
    console.log('🧪 TESTING: Looking for BSNL network rows...');
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`🧪 Found ${networkRows.length} network rows`);
    
    if (networkRows.length > 0) {
        networkRows.forEach((row, idx) => {
            if (idx < 5) { // Test first 5 rows
                const networkName = row.querySelector('.network-name-main')?.textContent?.trim();
                const monthCells = Array.from(row.querySelectorAll('.run-count')).slice(0, 12);
                const dates = monthCells.map(cell => cell.textContent.trim());
                console.log(`🧪 ${networkName}: [${dates.join(', ')}]`);
            }
        });
    }
}, 1000);