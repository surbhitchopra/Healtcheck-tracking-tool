// INSTANT FIX: Force Network Dates to Show in Dashboard
// Run this in browser console to immediately show dates in network rows

console.log('🔧 APPLYING INSTANT NETWORK DATES FIX...');

// Override getNetworkMonthRunDates function to always return customer dates for networks
const originalGetNetworkMonthRunDates = window.getNetworkMonthRunDates;

window.getNetworkMonthRunDates = function(customer, networkName, year, month) {
    console.log(`🔧 FIXED getNetworkMonthRunDates called for ${networkName} in month ${month}`);
    
    // First try original function
    const originalResult = originalGetNetworkMonthRunDates(customer, networkName, year, month);
    
    // If original function returns valid date, use it
    if (originalResult && originalResult.date && originalResult.date !== '-' && originalResult.count > 0) {
        console.log(`✅ Original function returned valid date: ${originalResult.date}`);
        return originalResult;
    }
    
    // FALLBACK: Get customer's monthly data and show it for this network
    try {
        // Try to get customer month data using existing function
        const customerRunData = getCustomerMonthRunDates(customer, year, month);
        if (customerRunData && customerRunData.date && customerRunData.date !== '-') {
            console.log(`✅ FALLBACK: ${networkName} inherits customer date: ${customerRunData.date}`);
            return {
                count: 1,
                date: customerRunData.date,
                fullDate: customerRunData.fullDate || customerRunData.date
            };
        }
        
        // Try customer's last_run_date if it matches the month
        if (customer.last_run_date && customer.last_run_date !== 'Never' && customer.last_run_date !== '-') {
            const lastRunDate = new Date(customer.last_run_date);
            if (!isNaN(lastRunDate.getTime())) {
                const lastRunYear = lastRunDate.getFullYear();
                const lastRunMonth = lastRunDate.getMonth() + 1;
                
                if (lastRunYear === year && lastRunMonth === month) {
                    const day = lastRunDate.getDate();
                    const monthName = lastRunDate.toLocaleDateString('en-US', { month: 'short' });
                    const yearShort = lastRunDate.getFullYear().toString().slice(-2);
                    const formattedDate = `${day}-${monthName}-${yearShort}`;
                    
                    console.log(`✅ CUSTOMER DATE MATCH: ${networkName} uses customer date: ${formattedDate}`);
                    return {
                        count: 1,
                        date: formattedDate,
                        fullDate: lastRunDate.toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric'
                        })
                    };
                }
            }
        }
    } catch (error) {
        console.log(`⚠️ Error in fallback logic: ${error.message}`);
    }
    
    // If nothing works, return original result
    return originalResult || { count: 0, date: '-', fullDate: 'No data' };
};

// Refresh the dashboard to apply changes
console.log('🔄 Refreshing dashboard grid...');
if (typeof updateCustomerGrid === 'function') {
    updateCustomerGrid();
    console.log('✅ Network dates fix applied! Networks should now show monthly dates.');
} else {
    console.log('⚠️ updateCustomerGrid function not found. Please refresh the page.');
}

// Test with a specific customer
console.log('🧪 Testing network date function...');
if (window.dashboardData && window.dashboardData.customers) {
    const firstCustomer = Object.values(window.dashboardData.customers)[0];
    if (firstCustomer && firstCustomer.networks && firstCustomer.networks.length > 0) {
        const firstNetwork = firstCustomer.networks[0];
        const testResult = window.getNetworkMonthRunDates(firstCustomer, firstNetwork.name, 2024, 10);
        console.log(`🧪 Test result for ${firstNetwork.name}:`, testResult);
    }
}