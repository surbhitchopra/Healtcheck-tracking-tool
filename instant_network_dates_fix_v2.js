// INSTANT FIX V2: Show ACTUAL Network Dates from Database
// Run this in browser console to show real network-specific dates

console.log('🔧 APPLYING INSTANT NETWORK DATES FIX V2 - REAL DATABASE DATES...');

// Override getNetworkMonthRunDates to use actual network data from API
window.getNetworkMonthRunDates = function(customer, networkName, year, month) {
    console.log(`🔧 V2: Getting dates for network "${networkName}" in month ${month}/${year}`);
    
    // PRIORITY 1: Find the exact network in customer's networks array
    if (customer.networks && Array.isArray(customer.networks)) {
        const targetNetwork = customer.networks.find(network => {
            // Multiple matching strategies for BSNL networks
            return network.network_name === networkName || 
                   network.name === networkName ||
                   network.name === `${customer.name} - ${networkName}` ||
                   network.name.includes(networkName) ||
                   networkName.includes(network.name) ||
                   // For cleaned names like "BSNL_East_Zone_DWDM"
                   (network.name && network.name.split(' - ').slice(-1)[0] === networkName) ||
                   // Direct match
                   network.network_name === networkName;
        });
        
        if (targetNetwork) {
            console.log(`🎯 FOUND: "${networkName}" matched with "${targetNetwork.name}"`);
            console.log(`📊 Network data:`, {
                runs: targetNetwork.runs,
                last_run_date: targetNetwork.last_run_date,
                network_name: targetNetwork.network_name
            });
            
            // If network has 0 runs, return no date
            if (targetNetwork.runs === 0) {
                console.log(`⚪ Zero runs for ${networkName}`);
                return { count: 0, date: '-', fullDate: 'No runs' };
            }
            
            // If network has its own last_run_date, check if it matches the requested month
            if (targetNetwork.last_run_date && 
                targetNetwork.last_run_date !== 'Never' && 
                targetNetwork.last_run_date !== '-') {
                
                try {
                    const networkDate = new Date(targetNetwork.last_run_date);
                    if (!isNaN(networkDate.getTime())) {
                        const networkYear = networkDate.getFullYear();
                        const networkMonth = networkDate.getMonth() + 1;
                        
                        // If this network's last run was in the requested month/year
                        if (networkYear === year && networkMonth === month) {
                            const day = networkDate.getDate();
                            const monthName = networkDate.toLocaleDateString('en-US', { month: 'short' });
                            const yearShort = networkDate.getFullYear().toString().slice(-2);
                            const formattedDate = `${day}-${monthName}-${yearShort}`;
                            
                            console.log(`✅ NETWORK SPECIFIC: ${networkName} - ${targetNetwork.runs} runs on ${formattedDate}`);
                            return {
                                count: targetNetwork.runs,
                                date: formattedDate,
                                fullDate: networkDate.toLocaleDateString('en-US', { 
                                    year: 'numeric', 
                                    month: 'long', 
                                    day: 'numeric'
                                })
                            };
                        } else {
                            console.log(`⏰ DIFFERENT MONTH: ${networkName} last run was ${networkMonth}/${networkYear}, not ${month}/${year}`);
                        }
                    }
                } catch (error) {
                    console.log(`❌ Date parsing error for ${networkName}: ${error.message}`);
                }
            }
        } else {
            console.log(`❌ NETWORK NOT FOUND: "${networkName}"`);
            if (customer.networks.length > 0) {
                console.log(`Available networks:`, customer.networks.map(n => n.name || n.network_name));
            }
        }
    }
    
    // No data found
    console.log(`⚠️ No specific data for ${networkName} in month ${month}`);
    return { count: 0, date: '-', fullDate: 'No data' };
};

// Also override getNetworkMonthRuns to return actual network runs
window.getNetworkMonthRuns = function(customer, networkName, year, month) {
    console.log(`🔧 V2: Getting monthly runs for network "${networkName}" in month ${month}/${year}`);
    
    if (customer.networks && Array.isArray(customer.networks)) {
        const targetNetwork = customer.networks.find(network => {
            return network.network_name === networkName || 
                   network.name === networkName ||
                   network.name.includes(networkName) ||
                   networkName.includes(network.name) ||
                   (network.name && network.name.split(' - ').slice(-1)[0] === networkName);
        });
        
        if (targetNetwork && targetNetwork.last_run_date && targetNetwork.last_run_date !== 'Never') {
            try {
                const networkDate = new Date(targetNetwork.last_run_date);
                if (!isNaN(networkDate.getTime())) {
                    const networkYear = networkDate.getFullYear();
                    const networkMonth = networkDate.getMonth() + 1;
                    
                    if (networkYear === year && networkMonth === month) {
                        console.log(`✅ NETWORK MONTH RUNS: ${networkName} had ${targetNetwork.runs} runs in ${month}/${year}`);
                        return targetNetwork.runs || 1;
                    }
                }
            } catch (error) {
                console.log(`❌ Error checking network runs: ${error.message}`);
            }
        }
    }
    
    return 0;
};

// Refresh the dashboard
console.log('🔄 Refreshing dashboard with real network dates...');
if (typeof updateCustomerGrid === 'function') {
    updateCustomerGrid();
    console.log('✅ V2 Fix applied! Networks should now show their actual database dates.');
} else {
    console.log('⚠️ updateCustomerGrid function not found.');
}

// Test the fix
console.log('🧪 Testing with BSNL networks...');
if (window.dashboardData && window.dashboardData.customers) {
    const bsnlCustomer = Object.values(window.dashboardData.customers).find(c => 
        c.name && c.name.toLowerCase().includes('bsnl')
    );
    if (bsnlCustomer && bsnlCustomer.networks) {
        console.log(`🧪 BSNL Customer found with ${bsnlCustomer.networks.length} networks:`);
        bsnlCustomer.networks.forEach((network, idx) => {
            if (idx < 3) { // Test first 3 networks
                const testResult = window.getNetworkMonthRunDates(bsnlCustomer, network.name, 2024, 10);
                console.log(`🧪 ${network.name}: ${testResult.date} (${testResult.count} runs)`);
            }
        });
    }
}