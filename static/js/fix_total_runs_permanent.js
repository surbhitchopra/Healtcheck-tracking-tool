// PERMANENT TOTAL RUNS FIX - Auto loads with dashboard
// This file fixes total runs display to use database values

console.log('🔧 Loading permanent total runs fix...');

// Wait for dashboard to load completely
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard DOM loaded, applying total runs fix...');
    
    // Function to apply the fix
    function applyTotalRunsFix() {
        // Override the dashboard data loading
        const originalFetch = window.fetch;
        
        window.fetch = function(...args) {
            const url = args[0];
            
            // Intercept dashboard API calls
            if (typeof url === 'string' && url.includes('/api/customer-dashboard/customers/')) {
                console.log('🔍 Intercepting dashboard API call...');
                
                return originalFetch.apply(this, args)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.customers) {
                            console.log('📊 Processing customer data with database total_runs...');
                            
                            // Force all customers to use database total_runs
                            Object.values(data.customers).forEach(customer => {
                                const dbTotalRuns = customer.total_runs || 0;
                                
                                // Override all run-related fields
                                customer.runs = dbTotalRuns;
                                customer.run_count = dbTotalRuns;
                                customer.total_run_count = dbTotalRuns;
                                
                                // Fix network-level runs too
                                if (customer.networks && customer.networks.length > 0) {
                                    customer.networks.forEach(network => {
                                        network.runs = network.total_runs || 0;
                                        network.run_count = network.total_runs || 0;
                                    });
                                }
                                
                                console.log(`${customer.name}: ${dbTotalRuns} runs (database)`);
                            });
                        }
                        
                        // Return modified data
                        return Promise.resolve({
                            json: () => Promise.resolve(data),
                            text: () => Promise.resolve(JSON.stringify(data)),
                            ok: true,
                            status: 200
                        });
                    });
            }
            
            // For other API calls, use original fetch
            return originalFetch.apply(this, args);
        };
        
        console.log('✅ Total runs fix interceptor installed!');
    }
    
    // Apply the fix immediately
    applyTotalRunsFix();
    
    // Also override statistics function when it becomes available
    function waitForDashboardFunctions() {
        if (typeof window.updateStatistics === 'function') {
            const originalUpdateStats = window.updateStatistics;
            
            window.updateStatistics = function() {
                console.log('📊 Using database total_runs for statistics...');
                
                if (!window.dashboardData || !window.dashboardData.customers) {
                    return originalUpdateStats.apply(this, arguments);
                }
                
                const customers = window.dashboardData.customers;
                let totalCustomers = 0;
                let totalRuns = 0;
                let totalNetworks = 0;
                
                // Group customers by name to avoid double counting
                const customerGroups = {};
                
                Object.entries(customers).forEach(([customerKey, customer]) => {
                    const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                    
                    if (!customerGroups[customerName]) {
                        customerGroups[customerName] = { totalRuns: 0 };
                        totalCustomers++;
                    }
                    
                    // Use database total_runs
                    const dbTotalRuns = customer.total_runs || 0;
                    customerGroups[customerName].totalRuns += dbTotalRuns;
                    totalNetworks++;
                });
                
                // Sum all runs
                Object.values(customerGroups).forEach(group => {
                    totalRuns += group.totalRuns;
                });
                
                // Update header display
                const elements = {
                    'header-total-customers': totalCustomers,
                    'header-total-runs': totalRuns,
                    'header-total-networks': totalNetworks,
                    'header-total-trackers': totalNetworks
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                });
                
                console.log(`✅ Statistics updated: ${totalCustomers} customers, ${totalRuns} total runs`);
                
                return { totalCustomers, totalRuns, totalNetworks };
            };
            
            console.log('✅ Statistics function overridden!');
        } else {
            setTimeout(waitForDashboardFunctions, 500);
        }
    }
    
    // Start waiting for dashboard functions
    waitForDashboardFunctions();
});

// Also apply fix if dashboard already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('📊 Dashboard already loaded, applying fix immediately...');
    
    setTimeout(() => {
        // Force refresh dashboard data if it exists
        if (window.dashboardData && window.updateStatistics) {
            updateStatistics();
        }
        if (window.updateCustomerGrid) {
            updateCustomerGrid();
        }
    }, 1000);
}

console.log('🎯 Permanent total runs fix loaded successfully!');