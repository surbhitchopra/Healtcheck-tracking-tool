// FIX TOTAL RUNS AND STATISTICS - Run this in console

console.log('🔧 FIXING TOTAL RUNS AND STATISTICS...');

// Calculate CORRECT statistics from dashboard data
function calculateCorrectStats() {
    const customers = dashboardData.customers;
    
    let totalRuns = 0;
    let totalCustomers = 0;
    let customersWithData = 0;
    let totalMonthlyEntries = 0;
    
    console.log('📊 Calculating correct statistics from dashboard data...');
    
    if (customers && Object.keys(customers).length > 0) {
        const customerGroups = {};
        
        // Group by customer name to avoid double counting
        Object.entries(customers).forEach(([customerKey, customer]) => {
            const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
            
            if (!customerGroups[customerName]) {
                customerGroups[customerName] = {
                    name: customerName,
                    totalRuns: 0,
                    monthlyEntries: 0,
                    networks: []
                };
            }
            
            // Add runs from this network
            const runs = customer.total_runs || customer.runs || 0;
            customerGroups[customerName].totalRuns += runs;
            customerGroups[customerName].networks.push(customerKey);
            
            // Count monthly entries
            if (customer.monthly_runs && typeof customer.monthly_runs === 'object') {
                Object.entries(customer.monthly_runs).forEach(([monthKey, monthValue]) => {
                    if (monthValue && 
                        monthValue !== '-' && 
                        monthValue !== 'Not Started' && 
                        monthValue !== 'No Report' && 
                        monthValue !== 'Not Run') {
                        customerGroups[customerName].monthlyEntries++;
                    }
                });
            }
        });
        
        // Calculate totals from grouped data
        Object.values(customerGroups).forEach(group => {
            totalCustomers++;
            totalRuns += group.totalRuns;
            totalMonthlyEntries += group.monthlyEntries;
            
            if (group.monthlyEntries > 0) {
                customersWithData++;
            }
            
            console.log(`  ${group.name}: ${group.totalRuns} runs, ${group.monthlyEntries} monthly entries, ${group.networks.length} networks`);
        });
    }
    
    console.log('📊 CORRECTED STATISTICS:');
    console.log(`   Total Customers: ${totalCustomers}`);
    console.log(`   Total Runs: ${totalRuns}`);
    console.log(`   Customers with Data: ${customersWithData}`);
    console.log(`   Monthly Entries: ${totalMonthlyEntries}`);
    
    return {
        total_customers: totalCustomers,
        total_runs: totalRuns,
        total_trackers: totalMonthlyEntries,
        customers_with_data: customersWithData
    };
}

// Update the statistics on the page
function updateHeaderStats(stats) {
    console.log('🔄 Updating header statistics...');
    
    // Update header values
    const customerEl = document.getElementById('header-total-customers');
    const runsEl = document.getElementById('header-total-runs');
    const trackersEl = document.getElementById('header-total-trackers');
    
    if (customerEl) {
        customerEl.textContent = stats.total_customers;
        console.log(`✅ Updated customers: ${stats.total_customers}`);
    }
    
    if (runsEl) {
        runsEl.textContent = stats.total_runs;
        console.log(`✅ Updated total runs: ${stats.total_runs}`);
    }
    
    if (trackersEl) {
        trackersEl.textContent = stats.total_trackers;
        console.log(`✅ Updated trackers: ${stats.total_trackers}`);
    }
    
    // Update the customer count text
    const customerCountEl = document.getElementById('customer-count');
    if (customerCountEl) {
        customerCountEl.textContent = `${stats.customers_with_data} customers with data`;
        console.log(`✅ Updated customer count: ${stats.customers_with_data} customers with data`);
    }
}

// Override the updateStatistics function to use correct data
window.updateStatistics = function() {
    console.log('📊 ENHANCED: Updating statistics with CORRECT calculations...');
    
    const correctStats = calculateCorrectStats();
    
    // Update dashboardData.statistics for consistency
    dashboardData.statistics = {
        total_customers: correctStats.total_customers,
        total_runs: correctStats.total_runs,
        total_trackers: correctStats.total_trackers,
        current_month_runs: correctStats.total_trackers,
        filtered_runs: correctStats.total_trackers
    };
    
    // Animate statistics displays
    animateStatCard('customers', correctStats.total_customers, Math.max(50, correctStats.total_customers));
    animateStatCard('runs', correctStats.total_runs, Math.max(200, correctStats.total_runs));
    animateStatCard('trackers', correctStats.total_trackers, Math.max(200, correctStats.total_trackers));
    
    // Update customer count with filter info
    const customerCount = correctStats.customers_with_data;
    let customerCountText = `${customerCount} customers with data`;
    
    // Add filter info if dates are applied
    if (currentStartDate && currentEndDate) {
        const startDate = new Date(currentStartDate).toLocaleDateString();
        const endDate = new Date(currentEndDate).toLocaleDateString();
        customerCountText += ` (${startDate} - ${endDate})`;
    }
    
    document.getElementById('customer-count').textContent = customerCountText;
    
    console.log('📊 CORRECTED Statistics updated:', {
        customers: correctStats.total_customers,
        runs: correctStats.total_runs,
        trackers: correctStats.total_trackers,
        customers_with_data: correctStats.customers_with_data
    });
};

// Apply the fix immediately
const correctedStats = calculateCorrectStats();
updateHeaderStats(correctedStats);

// Also update using the new function
updateStatistics();

console.log('🎉 TOTAL RUNS AND STATISTICS FIXED!');
console.log('📊 Expected header values based on database:');
console.log(`   👥 Customers: ${correctedStats.total_customers}`);
console.log(`   🏃 Total Runs: ${correctedStats.total_runs}`);
console.log(`   📋 Trackers: ${correctedStats.total_trackers}`);
console.log('');
console.log('✅ Header should now show correct totals matching your database data!');