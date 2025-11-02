// DEBUG: Compare Database Network Dates vs Display
console.log('🔍 COMPARING DATABASE vs DISPLAY...');

if (window.dashboardData && window.dashboardData.customers) {
    const customers = Object.values(window.dashboardData.customers);
    
    ['BSNL', 'Telekom_Malaysia', 'Moratelindo'].forEach(customerName => {
        const customer = customers.find(c => c.name && c.name.toLowerCase().includes(customerName.toLowerCase()));
        
        if (customer) {
            console.log(`\n🏢 CUSTOMER: ${customer.name}`);
            console.log(`📅 Customer monthly_runs:`, customer.monthly_runs);
            
            if (customer.networks && customer.networks.length > 0) {
                customer.networks.forEach((network, index) => {
                    console.log(`\n  🔗 NETWORK ${index + 1}: ${network.name || network.network_name}`);
                    console.log(`    📊 Database Info:`);
                    console.log(`      - runs: ${network.runs}`);
                    console.log(`      - last_run_date: ${network.last_run_date}`);
                    console.log(`      - monthly_runs:`, network.monthly_runs);
                    
                    // Check what should be displayed for each month
                    console.log(`    📅 Expected Monthly Dates:`);
                    for (let month = 1; month <= 12; month++) {
                        let expectedDate = '-';
                        
                        // Check monthly_runs dictionary
                        if (network.monthly_runs && typeof network.monthly_runs === 'object') {
                            const monthKey = `2024-${month.toString().padStart(2, '0')}`;
                            if (network.monthly_runs[monthKey]) {
                                const monthValue = network.monthly_runs[monthKey];
                                if (monthValue !== 'Not Run' && monthValue !== 'Not Started') {
                                    try {
                                        const date = new Date(monthValue);
                                        const day = date.getDate();
                                        const monthName = date.toLocaleDateString('en-US', { month: 'short' });
                                        const yearShort = date.getFullYear().toString().slice(-2);
                                        expectedDate = `${day}-${monthName}-${yearShort}`;
                                    } catch (error) {
                                        expectedDate = monthValue;
                                    }
                                }
                            }
                        }
                        
                        // Check if network's last_run_date falls in this month
                        if (expectedDate === '-' && network.last_run_date && network.last_run_date !== 'Never') {
                            try {
                                const lastRunDate = new Date(network.last_run_date);
                                if (!isNaN(lastRunDate.getTime())) {
                                    const runYear = lastRunDate.getFullYear();
                                    const runMonth = lastRunDate.getMonth() + 1;
                                    
                                    if (runYear === 2024 && runMonth === month) {
                                        const day = lastRunDate.getDate();
                                        const monthName = lastRunDate.toLocaleDateString('en-US', { month: 'short' });
                                        const yearShort = lastRunDate.getFullYear().toString().slice(-2);
                                        expectedDate = `${day}-${monthName}-${yearShort}`;
                                    }
                                }
                            } catch (error) {
                                console.log(`      ❌ Error parsing date: ${network.last_run_date}`);
                            }
                        }
                        
                        if (expectedDate !== '-') {
                            console.log(`      Month ${month}: ${expectedDate}`);
                        }
                    }
                });
            }
        }
    });
    
    console.log('\n🔍 NOW CHECK THE DASHBOARD - Are network dates showing correctly?');
    console.log('❌ If all networks show same dates as customer = WRONG');
    console.log('✅ If networks show their own specific dates = CORRECT');
    
} else {
    console.log('❌ No dashboard data found');
}

console.log('\n📋 Run this script to see what SHOULD be displayed vs what IS displayed.');