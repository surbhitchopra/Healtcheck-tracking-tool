// TEST SCRIPT: Verify Chart Data Matches Table Data
// Run this in browser console to test the fix

function testChartTableAlignment() {
    console.log('🧪 TESTING CHART-TABLE DATA ALIGNMENT');
    console.log('='.repeat(50));
    
    // Get current dashboard data
    const customers = dashboardData.customers;
    const currentMonth = new Date().getMonth() + 1; // October = 10
    const currentYear = new Date().getFullYear(); // 2025
    
    console.log(`Testing for: ${currentYear}-${currentMonth.toString().padStart(2, '0')} (October 2025)`);
    
    // Group customers by name (same logic as chart)
    const customerGroups = {};
    let totalNetworksWithData = 0;
    
    Object.entries(customers || {}).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        // Initialize customer group if not exists
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = {
                name: customerName,
                totalRuns: 0,
                networks: [],
                networksWithData: []
            };
        }
        
        const monthRuns = getCustomerMonthRuns(customer, currentYear, currentMonth);
        
        customerGroups[customerName].networks.push(customerKey);
        
        if (monthRuns > 0) {
            customerGroups[customerName].totalRuns += monthRuns;
            customerGroups[customerName].networksWithData.push({
                key: customerKey,
                runs: monthRuns,
                monthlyRuns: customer.monthly_runs
            });
            totalNetworksWithData++;
        }
    });
    
    // Show results
    console.log(`📊 SUMMARY:`);
    console.log(`   Total networks with October 2025 data: ${totalNetworksWithData}`);
    console.log(`   Unique customers with data: ${Object.values(customerGroups).filter(g => g.totalRuns > 0).length}`);
    
    console.log(`\n📊 DETAILED BREAKDOWN:`);
    
    Object.values(customerGroups).forEach(group => {
        if (group.totalRuns > 0) {
            console.log(`\n🏢 ${group.name}:`);
            console.log(`   Total runs: ${group.totalRuns}`);
            console.log(`   Networks with October data: ${group.networksWithData.length}/${group.networks.length}`);
            
            group.networksWithData.forEach(network => {
                console.log(`   📡 ${network.key}: ${network.runs} runs`);
                const octData = network.monthlyRuns && network.monthlyRuns['2025-10'];
                if (octData) {
                    console.log(`       October date: ${octData}`);
                }
            });
        }
    });
    
    console.log(`\n✅ Expected Chart Results:`);
    Object.values(customerGroups).forEach(group => {
        if (group.totalRuns > 0) {
            console.log(`   ${group.name}: ${group.totalRuns} runs from ${group.networksWithData.length} networks`);
        }
    });
    
    console.log('='.repeat(50));
}

// Expose to window for manual testing
window.testChartTableAlignment = testChartTableAlignment;

console.log('✅ Test function loaded. Run testChartTableAlignment() to verify data alignment.');