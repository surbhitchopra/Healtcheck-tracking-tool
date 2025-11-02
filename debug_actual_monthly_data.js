// DEBUG: Check Actual Monthly Distribution in Database
console.log('🔍 CHECKING ACTUAL DATABASE MONTHLY DATA...');

if (window.dashboardData && window.dashboardData.customers) {
    const customers = Object.values(window.dashboardData.customers);
    
    console.log('\n📊 ANALYZING MONTHLY DATA DISTRIBUTION:');
    
    // Check each month's actual data
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthlyTotals = {};
    const activeCustomersByMonth = {};
    
    // Initialize
    months.forEach((month, index) => {
        monthlyTotals[month] = 0;
        activeCustomersByMonth[month] = [];
    });
    
    customers.forEach(customer => {
        console.log(`\n🏢 ${customer.name}:`);
        console.log(`  Total runs: ${customer.runs || 0}`);
        console.log(`  Monthly runs array:`, customer.monthly_runs);
        console.log(`  Last run date: ${customer.last_run_date}`);
        
        // Check customer monthly_runs array
        if (customer.monthly_runs && Array.isArray(customer.monthly_runs)) {
            customer.monthly_runs.forEach((monthValue, index) => {
                if (monthValue && monthValue !== '-' && monthValue !== 'Not Run') {
                    const monthName = months[index];
                    
                    // Add customer runs to this month's total
                    monthlyTotals[monthName] += customer.runs || 0;
                    
                    // Add customer to active list for this month
                    if (!activeCustomersByMonth[monthName].includes(customer.name)) {
                        activeCustomersByMonth[monthName].push(customer.name);
                    }
                    
                    console.log(`    ✅ ${monthName}: ${monthValue} (${customer.runs || 0} runs)`);
                }
            });
        }
        
        // Also check networks monthly_runs
        if (customer.networks && Array.isArray(customer.networks)) {
            customer.networks.forEach(network => {
                if (network.monthly_runs && typeof network.monthly_runs === 'object') {
                    console.log(`    🔗 Network ${network.name} monthly_runs:`, network.monthly_runs);
                    
                    Object.keys(network.monthly_runs).forEach(monthKey => {
                        const monthValue = network.monthly_runs[monthKey];
                        if (monthValue && monthValue !== 'Not Run') {
                            // Parse month from key like '2025-05'
                            const [year, monthNum] = monthKey.split('-');
                            const monthIndex = parseInt(monthNum) - 1;
                            const monthName = months[monthIndex];
                            
                            if (monthName) {
                                monthlyTotals[monthName] += network.runs || 0;
                                
                                if (!activeCustomersByMonth[monthName].includes(customer.name)) {
                                    activeCustomersByMonth[monthName].push(customer.name);
                                }
                                
                                console.log(`      ✅ Network ${monthName}: ${monthValue} (${network.runs || 0} runs)`);
                            }
                        }
                    });
                }
            });
        }
    });
    
    console.log('\n📈 MONTHLY TOTALS SUMMARY:');
    months.forEach(month => {
        const totalRuns = monthlyTotals[month];
        const activeCount = activeCustomersByMonth[month].length;
        
        if (totalRuns > 0 || activeCount > 0) {
            console.log(`${month}: ${totalRuns} runs, ${activeCount} customers`);
            if (activeCount > 0) {
                console.log(`  Active customers: ${activeCustomersByMonth[month].join(', ')}`);
            }
        }
    });
    
    console.log('\n🎯 CURRENT ISSUES:');
    console.log('📊 Left Graph should show:', monthlyTotals);
    console.log('👥 Right Graph should show October customers:', activeCustomersByMonth['Oct']);
    
    // Check what year the data is actually from
    console.log('\n📅 CHECKING DATA YEARS:');
    customers.forEach(customer => {
        if (customer.last_run_date && customer.last_run_date !== 'Never') {
            try {
                const date = new Date(customer.last_run_date);
                const year = date.getFullYear();
                console.log(`${customer.name}: ${customer.last_run_date} (Year: ${year})`);
            } catch (error) {
                console.log(`${customer.name}: Invalid date format - ${customer.last_run_date}`);
            }
        }
    });
    
} else {
    console.log('❌ No dashboard data found');
}

console.log('\n✅ Analysis complete. Check logs above for actual data distribution.');