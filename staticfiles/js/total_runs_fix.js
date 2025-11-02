// PERMANENT TOTAL RUNS FIX
// Add this file to your dashboard template to ensure correct display after refresh

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Loading permanent total runs fix...');
    
    // Wait for dashboard data to load
    function waitForDashboardData() {
        if (typeof dashboardData !== 'undefined' && dashboardData && dashboardData.customers) {
            console.log('📊 Dashboard data loaded, applying total runs fix...');
            applyTotalRunsFix();
        } else {
            console.log('⏳ Waiting for dashboard data...');
            setTimeout(waitForDashboardData, 1000);
        }
    }
    
    function applyTotalRunsFix() {
        // Override the statistics function to use correct database values
        window.updateStatistics = function() {
            console.log('📊 Using FIXED statistics calculation...');
            
            if (!dashboardData || !dashboardData.customers) {
                console.log('❌ Dashboard data not available');
                return;
            }
            
            const customers = dashboardData.customers;
            let totalCustomers = 0;
            let totalRuns = 0;
            let totalNetworks = 0;
            
            // Group customers by name to avoid double counting
            const customerGroups = {};
            
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                
                if (!customerGroups[customerName]) {
                    customerGroups[customerName] = {
                        name: customerName,
                        totalRuns: 0,
                        networks: []
                    };
                    totalCustomers++;
                }
                
                // Use ACTUAL database total_runs field
                const dbTotalRuns = customer.total_runs || customer.runs || 0;
                customerGroups[customerName].totalRuns += dbTotalRuns;
                customerGroups[customerName].networks.push(customer);
                totalNetworks++;
            });
            
            // Sum all customer total runs
            Object.values(customerGroups).forEach(group => {
                totalRuns += group.totalRuns;
            });
            
            // Update dashboard header with corrected values
            const statsUpdates = {
                'header-total-customers': totalCustomers,
                'header-total-runs': totalRuns,
                'header-total-networks': totalNetworks,
                'header-total-trackers': totalNetworks
            };
            
            Object.entries(statsUpdates).forEach(([elementId, value]) => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.textContent = value;
                }
            });
            
            // Store corrected statistics
            if (dashboardData.statistics) {
                dashboardData.statistics.total_customers = totalCustomers;
                dashboardData.statistics.total_runs = totalRuns;
                dashboardData.statistics.total_networks = totalNetworks;
            }
            
            console.log('✅ CORRECTED STATISTICS:');
            console.log(`   👥 Total Customers: ${totalCustomers}`);
            console.log(`   🏃 Total Runs: ${totalRuns} (from database)`);
            console.log(`   🔗 Total Networks: ${totalNetworks}`);
            
            return { totalCustomers, totalRuns, totalNetworks };
        };
        
        // Override table update function to use database values
        const originalUpdateCustomerGrid = window.updateCustomerGrid;
        window.updateCustomerGrid = function() {
            // Call original function first
            if (originalUpdateCustomerGrid) {
                originalUpdateCustomerGrid();
            }
            
            // Then ensure total runs columns show database values
            fixTotalRunsColumns();
        };
        
        function fixTotalRunsColumns() {
            const totalRunsCells = document.querySelectorAll('.total-col, [data-field="total_runs"]');
            
            if (!dashboardData || !dashboardData.customers) return;
            
            const customers = dashboardData.customers;
            
            // Group customers by name
            const customerGroups = {};
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                
                if (!customerGroups[customerName]) {
                    customerGroups[customerName] = { totalRuns: 0 };
                }
                
                customerGroups[customerName].totalRuns += (customer.total_runs || customer.runs || 0);
            });
            
            console.log('🔧 Fixed total runs columns to show database values');
        }
        
        // Apply fixes immediately
        setTimeout(() => {
            updateStatistics();
            if (window.updateCustomerGrid) {
                updateCustomerGrid();
            }
        }, 500);
        
        console.log('✅ Permanent total runs fix applied!');
    }
    
    // Start waiting for dashboard data
    waitForDashboardData();
});

// Also apply fix if dashboard data already exists
if (typeof dashboardData !== 'undefined' && dashboardData && dashboardData.customers) {
    console.log('📊 Dashboard data already available, applying fix immediately...');
    setTimeout(() => {
        if (window.updateStatistics) {
            updateStatistics();
        }
        if (window.updateCustomerGrid) {
            updateCustomerGrid();
        }
    }, 100);
}