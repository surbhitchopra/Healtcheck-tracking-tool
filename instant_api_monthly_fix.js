// INSTANT API MONTHLY_RUNS FIX
// This processes the monthly_runs dictionary from API properly

console.log('🔧 FIXING API MONTHLY_RUNS PROCESSING...');

// Override getNetworkMonthRunDates to properly handle monthly_runs dictionary
window.getNetworkMonthRunDates = function(customer, networkName, year, month) {
    console.log(`🔧 API FIX: Getting dates for network "${networkName}" in month ${month}/${year}`);
    
    if (customer.networks && Array.isArray(customer.networks)) {
        const targetNetwork = customer.networks.find(network => {
            return network.network_name === networkName || 
                   network.name === networkName ||
                   network.name.includes(networkName) ||
                   networkName.includes(network.name);
        });
        
        if (targetNetwork) {
            console.log(`🎯 Found network: ${targetNetwork.name || targetNetwork.network_name}`);
            console.log(`📊 Network data:`, {
                runs: targetNetwork.runs,
                monthly_runs: targetNetwork.monthly_runs,
                last_run_date: targetNetwork.last_run_date
            });
            
            // PRIORITY 1: Check monthly_runs dictionary from API
            if (targetNetwork.monthly_runs && typeof targetNetwork.monthly_runs === 'object') {
                console.log(`📊 Processing monthly_runs for ${networkName}:`, targetNetwork.monthly_runs);
                
                // Convert month number to year-month format
                const monthKey = `${year}-${month.toString().padStart(2, '0')}`;
                console.log(`🔍 Looking for month key: ${monthKey}`);
                
                if (targetNetwork.monthly_runs[monthKey]) {
                    const monthValue = targetNetwork.monthly_runs[monthKey];
                    console.log(`✅ Found monthly data: ${monthKey} = ${monthValue}`);
                    
                    if (monthValue === 'Not Run' || monthValue === 'Not Started') {
                        return { count: 0, date: 'Not Run', fullDate: 'Not Run' };
                    } else if (monthValue && monthValue !== '-') {
                        // Parse date from format like '2025-05-21'
                        try {
                            const apiDate = new Date(monthValue);
                            if (!isNaN(apiDate.getTime())) {
                                const day = apiDate.getDate();
                                const monthName = apiDate.toLocaleDateString('en-US', { month: 'short' });
                                const yearShort = apiDate.getFullYear().toString().slice(-2);
                                const formattedDate = `${day}-${monthName}-${yearShort}`;
                                
                                console.log(`✅ API DATE: ${networkName} ${monthKey} = ${formattedDate}`);
                                return {
                                    count: 1,
                                    date: formattedDate,
                                    fullDate: apiDate.toLocaleDateString('en-US', { 
                                        year: 'numeric', month: 'long', day: 'numeric'
                                    })
                                };
                            }
                        } catch (error) {
                            console.log(`❌ Date parsing error for ${monthValue}: ${error.message}`);
                        }
                    }
                } else {
                    console.log(`⚠️ No data found for month key: ${monthKey}`);
                    console.log(`Available keys:`, Object.keys(targetNetwork.monthly_runs));
                }
            }
            
            // PRIORITY 2: Check last_run_date as fallback
            if (targetNetwork.last_run_date && 
                targetNetwork.last_run_date !== 'Never' && 
                targetNetwork.last_run_date !== '-') {
                
                try {
                    const networkDate = new Date(targetNetwork.last_run_date);
                    if (!isNaN(networkDate.getTime())) {
                        const networkYear = networkDate.getFullYear();
                        const networkMonth = networkDate.getMonth() + 1;
                        
                        if (networkYear === year && networkMonth === month) {
                            const day = networkDate.getDate();
                            const monthName = networkDate.toLocaleDateString('en-US', { month: 'short' });
                            const yearShort = networkDate.getFullYear().toString().slice(-2);
                            const formattedDate = `${day}-${monthName}-${yearShort}`;
                            
                            console.log(`✅ FALLBACK DATE: ${networkName} = ${formattedDate}`);
                            return {
                                count: targetNetwork.runs || 1,
                                date: formattedDate,
                                fullDate: networkDate.toLocaleDateString('en-US', { 
                                    year: 'numeric', month: 'long', day: 'numeric'
                                })
                            };
                        }
                    }
                } catch (error) {
                    console.log(`❌ Fallback date error: ${error.message}`);
                }
            }
        }
    }
    
    console.log(`⚠️ No data found for ${networkName} in month ${month}/${year}`);
    return { count: 0, date: '-', fullDate: 'No data' };
};

// Refresh dashboard
console.log('🔄 Refreshing dashboard with API monthly_runs fix...');
if (typeof updateCustomerGrid === 'function') {
    updateCustomerGrid();
    console.log('✅ API FIX APPLIED! Networks should now show monthly_runs data.');
} else {
    console.log('⚠️ updateCustomerGrid function not found.');
}

// Test with Telekom_Malaysia
console.log('🧪 Testing with Telekom_Malaysia...');
if (window.dashboardData && window.dashboardData.customers) {
    const telekomCustomer = Object.values(window.dashboardData.customers).find(c => 
        c.name && c.name.toLowerCase().includes('telekom')
    );
    
    if (telekomCustomer) {
        console.log('🧪 Found Telekom customer:', telekomCustomer.name);
        if (telekomCustomer.networks && telekomCustomer.networks.length > 0) {
            const network = telekomCustomer.networks[0];
            console.log('🧪 Testing network:', network.name);
            console.log('🧪 Network monthly_runs:', network.monthly_runs);
            
            // Test specific months
            [1, 5, 6, 7, 9].forEach(month => {
                const result = window.getNetworkMonthRunDates(telekomCustomer, network.name, 2025, month);
                console.log(`🧪 Month ${month}: ${result.date} (${result.count} runs)`);
            });
        }
    }
}