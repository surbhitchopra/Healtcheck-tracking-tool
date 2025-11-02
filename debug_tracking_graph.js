// DEBUG TRACKING GRAPH - Run this in console to see what's happening

console.log('🔍 DEBUGGING TRACKING GRAPH DATA DETECTION');
console.log('='.repeat(60));

// Test last 6 months data detection
const customers = dashboardData.customers;
const currentDate = new Date();

console.log('Available customers:', Object.keys(customers || {}).length);
console.log('Sample customer keys:', Object.keys(customers || {}).slice(0, 5));

// Test each month
for (let i = 5; i >= 0; i--) {
    const monthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
    const monthName = monthDate.toLocaleDateString('en-US', { month: 'short' });
    const monthNumber = monthDate.getMonth() + 1;
    const year = monthDate.getFullYear();
    const monthKey = `${year}-${monthNumber.toString().padStart(2, '0')}`;
    
    console.log(`\n📅 Testing ${monthName} ${year} (${monthKey}):`);
    
    const customerGroups = {};
    let foundCustomers = [];
    
    if (customers && Object.keys(customers).length > 0) {
        Object.entries(customers).forEach(([customerKey, customer]) => {
            const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
            
            // Group by customer name
            if (!customerGroups[customerName]) {
                customerGroups[customerName] = {
                    name: customerName,
                    hasData: false,
                    networks: []
                };
            }
            
            // Method 1: Try getCustomerMonthRuns
            const monthRuns = getCustomerMonthRuns(customer, year, monthNumber);
            
            // Method 2: Direct check
            const hasDirectData = customer.monthly_runs && customer.monthly_runs[monthKey];
            
            if (monthRuns > 0) {
                customerGroups[customerName].hasData = true;
                customerGroups[customerName].networks.push(customerKey);
            } else if (hasDirectData) {
                // Found data but getCustomerMonthRuns didn't detect it
                console.log(`  ⚠️ MISSED: ${customerName} has direct data ${hasDirectData} but getCustomerMonthRuns returned 0`);
                customerGroups[customerName].hasData = true;
                customerGroups[customerName].networks.push(customerKey);
            }
        });
        
        foundCustomers = Object.values(customerGroups).filter(g => g.hasData);
    }
    
    console.log(`  Result: ${foundCustomers.length} customers with data`);
    if (foundCustomers.length > 0) {
        foundCustomers.forEach(customer => {
            console.log(`    ✅ ${customer.name} (${customer.networks.length} networks)`);
        });
    } else {
        console.log(`    ❌ No customers found with data for ${monthName}`);
    }
}

console.log('\n' + '='.repeat(60));
console.log('✅ Debug completed. Check above for any MISSED entries.');

// Force refresh the tracking graph with debug info
console.log('\n🔄 Now refreshing tracking graph...');
updateTrackingGraph();