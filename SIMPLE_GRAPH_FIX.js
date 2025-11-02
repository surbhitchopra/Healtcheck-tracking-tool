// 🚀 SIMPLE GRAPH FIX - Copy this to browser console on dashboard page

console.log("🔧 APPLYING SIMPLE GRAPH FIX...");

// Fix 1: Force graphs to use current year (2025) instead of 2024
function fixGraphsForCurrentYear() {
    console.log("📅 Fixing graphs for current year (2025)...");
    
    // Override the getCustomerMonthRuns function to use 2025
    if (typeof window.getCustomerMonthRuns === 'function') {
        const originalFunction = window.getCustomerMonthRuns;
        
        window.getCustomerMonthRuns = function(customer, year, month) {
            // Force current year
            const currentYear = new Date().getFullYear();
            console.log(`📊 Fixed: Getting runs for ${customer.name} - month ${month}/${currentYear} (was ${year})`);
            
            return originalFunction.call(this, customer, currentYear, month);
        };
        
        console.log("✅ getCustomerMonthRuns function patched for current year");
    }
}

// Fix 2: Update activity graph with current data
function updateGraphsNow() {
    console.log("🔄 Updating graphs with current data...");
    
    // Force refresh the tracking graph
    if (typeof updateTrackingGraph === 'function') {
        updateTrackingGraph();
        console.log("✅ Activity graph updated");
    }
    
    // Force refresh customer month chart  
    if (typeof updateCustomerMonthChart === 'function') {
        updateCustomerMonthChart();
        console.log("✅ Customer chart updated");
    }
}

// Fix 3: Manual refresh function for October data
function forceOctoberUpdate() {
    console.log("🎯 Force updating October data...");
    
    if (window.dashboardData && window.dashboardData.customers) {
        Object.values(window.dashboardData.customers).forEach(customer => {
            if (customer.name && customer.name.includes('OPT')) {
                console.log(`📊 Found OPT customer:`, customer);
                
                // Check if customer has networks with October data
                if (customer.networks) {
                    customer.networks.forEach((network, index) => {
                        if (network.months && network.months[9]) { // October is index 9
                            console.log(`📅 Network ${index} October data: ${network.months[9]}`);
                        }
                    });
                }
            }
        });
    }
    
    updateGraphsNow();
}

// Apply all fixes
fixGraphsForCurrentYear();
setTimeout(() => {
    updateGraphsNow();
    forceOctoberUpdate();
}, 1000);

// Set up automatic refresh every 30 seconds
setInterval(() => {
    console.log("⏰ Auto-refreshing graphs...");
    updateGraphsNow();
}, 30000);

console.log("✅ SIMPLE GRAPH FIX APPLIED!");
console.log("📊 Graphs should now show current year data");
console.log("🔄 Auto-refresh every 30 seconds enabled");

// Expose manual refresh function
window.manualRefreshGraphs = updateGraphsNow;
window.forceOctoberUpdate = forceOctoberUpdate;

console.log("🎮 Manual commands available:");
console.log("   manualRefreshGraphs() - Refresh graphs manually");
console.log("   forceOctoberUpdate() - Force October data update");