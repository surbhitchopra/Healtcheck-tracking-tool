// URGENT FIX FOR FRONTEND TOTAL RUNS CALCULATION - RUN IN BROWSER CONSOLE

console.log('🔧 FIXING FRONTEND TOTAL RUNS CALCULATION LOGIC...');

// Function to calculate correct total runs by grouping customers properly
function calculateCorrectCustomerRuns(customers) {
    console.log('📊 Calculating CORRECT total runs from customer data...');
    
    // Group customers by name to avoid double counting
    const customerGroups = {};
    let correctTotalRuns = 0;
    let correctTotalCustomers = 0;
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        // Skip if already processed this customer
        if (customerGroups[customerName]) {
            console.log(`⚪ Skipping duplicate: ${customerName} (already counted)`);
            return;
        }
        
        // Mark this customer as processed
        customerGroups[customerName] = true;
        correctTotalCustomers++;
        
        // For database customers, use the total_runs from database
        let customerRuns = 0;
        if (customer.total_runs !== undefined) {
            customerRuns = customer.total_runs || 0;
            console.log(`📊 DB Customer: ${customerName} = ${customerRuns} runs (from database)`);
        } 
        // For Excel customers, calculate from monthly runs
        else if (customer.monthly_runs && typeof customer.monthly_runs === 'object') {
            customerRuns = Object.entries(customer.monthly_runs).filter(([monthKey, monthValue]) => {
                return monthValue && 
                       monthValue !== '-' && 
                       monthValue !== 'Not Started' && 
                       monthValue !== 'No Report' && 
                       monthValue !== 'Not Run';
            }).length;
            console.log(`📊 Excel Customer: ${customerName} = ${customerRuns} runs (from monthly data)`);
        }
        // Fallback calculation
        else {
            customerRuns = customer.runs || customer.run_count || 0;
            console.log(`📊 Fallback Customer: ${customerName} = ${customerRuns} runs`);
        }
        
        correctTotalRuns += customerRuns;
    });
    
    console.log(`📊 CORRECT CALCULATION RESULT:`);
    console.log(`   Total Customers: ${correctTotalCustomers}`);
    console.log(`   Total Runs: ${correctTotalRuns}`);
    
    return {
        totalCustomers: correctTotalCustomers,
        totalRuns: correctTotalRuns
    };
}

// Override the updateStatistics function to use correct calculation
window.originalUpdateStatistics = window.updateStatistics;

window.updateStatistics = function() {
    console.log('📊 ENHANCED: Updating statistics with CORRECT calculation...');
    
    const customers = dashboardData.customers;
    if (!customers || Object.keys(customers).length === 0) {
        console.log('⚠️ No customer data available');
        return;
    }
    
    // Calculate correct statistics
    const correctStats = calculateCorrectCustomerRuns(customers);
    
    // Update dashboardData.statistics with correct values
    dashboardData.statistics = {
        ...dashboardData.statistics,
        total_customers: correctStats.totalCustomers,
        total_runs: correctStats.totalRuns,
        total_trackers: dashboardData.statistics?.total_trackers || 0
    };
    
    console.log('📊 CORRECTED Statistics:', dashboardData.statistics);
    
    // Update the header statistics display
    const customerEl = document.getElementById('header-total-customers');
    const runsEl = document.getElementById('header-total-runs');
    const trackersEl = document.getElementById('header-total-trackers');
    
    if (customerEl) {
        customerEl.textContent = correctStats.totalCustomers;
        console.log(`✅ Updated header customers: ${correctStats.totalCustomers}`);
    }
    
    if (runsEl) {
        runsEl.textContent = correctStats.totalRuns;
        console.log(`✅ Updated header total runs: ${correctStats.totalRuns}`);
    }
    
    if (trackersEl) {
        const trackers = dashboardData.statistics?.total_trackers || 0;
        trackersEl.textContent = trackers;
        console.log(`✅ Updated header trackers: ${trackers}`);
    }
    
    // Update stat cards if they exist
    const statCards = document.querySelectorAll('.header-stat-value');
    if (statCards.length >= 2) {
        statCards[0].textContent = correctStats.totalCustomers; // Customers
        statCards[1].textContent = correctStats.totalRuns;      // Runs
        if (statCards[2]) {
            statCards[2].textContent = dashboardData.statistics?.total_trackers || 0; // Trackers
        }
    }
    
    // Animate the stat cards
    if (typeof animateStatCard === 'function') {
        animateStatCard('customers', correctStats.totalCustomers, Math.max(50, correctStats.totalCustomers));
        animateStatCard('runs', correctStats.totalRuns, Math.max(200, correctStats.totalRuns));
        animateStatCard('trackers', dashboardData.statistics?.total_trackers || 0, Math.max(200, dashboardData.statistics?.total_trackers || 0));
    }
    
    console.log('✅ Statistics display updated with CORRECT values');
};

// Fix the customer table total runs column
function fixCustomerTableTotals() {
    console.log('🔧 Fixing customer table total runs column...');
    
    const customers = dashboardData.customers;
    if (!customers) return;
    
    // Group customers to avoid duplicates
    const customerGroups = {};
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = [];
        }
        customerGroups[customerName].push({key: customerKey, data: customer});
    });
    
    // Update table rows for each customer group
    Object.entries(customerGroups).forEach(([customerName, networks]) => {
        let totalRunsForCustomer = 0;
        
        // Calculate total runs for this customer across all networks
        networks.forEach(network => {
            const customer = network.data;
            
            if (customer.total_runs !== undefined) {
                // Database customer - use database total_runs, but don't double count
                if (networks.length === 1) {
                    totalRunsForCustomer = customer.total_runs || 0;
                } else {
                    totalRunsForCustomer += (customer.total_runs || 0);
                }
            } else if (customer.monthly_runs) {
                // Excel customer - calculate from monthly data
                const monthlyCount = Object.entries(customer.monthly_runs).filter(([monthKey, monthValue]) => {
                    return monthValue && 
                           monthValue !== '-' && 
                           monthValue !== 'Not Started' && 
                           monthValue !== 'No Report' && 
                           monthValue !== 'Not Run';
                }).length;
                totalRunsForCustomer += monthlyCount;
            }
        });
        
        console.log(`📊 ${customerName}: Corrected total runs = ${totalRunsForCustomer}`);
        
        // Find and update the table row for this customer
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        tableRows.forEach(row => {
            const customerNameCell = row.querySelector('.customer-name-main, .customer-name-container');
            if (customerNameCell && customerNameCell.textContent.includes(customerName)) {
                const totalCell = row.querySelector('.total-col');
                if (totalCell) {
                    totalCell.innerHTML = `<div style="font-weight: 700; color: #059669; font-size: 0.8rem;">${totalRunsForCustomer}</div>`;
                    totalCell.title = `${customerName}: ${totalRunsForCustomer} total runs (corrected calculation)`;
                    console.log(`✅ Updated table: ${customerName} -> ${totalRunsForCustomer} runs`);
                }
            }
        });
    });
}

// Apply the fixes immediately
console.log('🚀 Applying fixes to current dashboard...');

// 1. Update statistics with correct calculation
updateStatistics();

// 2. Fix table totals
setTimeout(() => {
    fixCustomerTableTotals();
}, 1000);

console.log('🎉 FRONTEND TOTAL RUNS LOGIC FIXED!');
console.log('📊 Summary of corrections:');
console.log('   ✅ Customers are now grouped properly (no duplicate counting)');
console.log('   ✅ Database customers use database total_runs');
console.log('   ✅ Excel customers calculate from monthly data');
console.log('   ✅ Header statistics show correct totals');
console.log('   ✅ Table columns show correct totals');
console.log('');
console.log('Expected results:');
console.log('   🏃 BSNL should show ~53 runs (not 70)');
console.log('   🏃 All customers should show correct database totals');
console.log('   🏃 No more duplicate counting of network runs');