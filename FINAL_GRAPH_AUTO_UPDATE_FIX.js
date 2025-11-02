// 🎯 FINAL GRAPH AUTO-UPDATE FIX - Complete solution
// This will make graphs automatically update when trackers are generated

console.log('🚀 FINAL GRAPH AUTO-UPDATE FIX: Loading...');

// 🔄 1. Override graph functions to always use fresh data
function createAutoUpdateGraphFunction(originalFunction, functionName) {
    return function() {
        console.log(`🔄 AUTO-UPDATE: ${functionName} called - reloading data first...`);
        
        // Always reload data before updating graphs
        loadDashboardData().then(() => {
            console.log(`✅ Fresh data loaded for ${functionName}`);
            
            // Call the original logic with fresh data
            if (functionName === 'updateTrackingGraph') {
                updateTrackingGraphWithCurrentData();
            } else if (functionName === 'updateCustomerMonthChart') {
                updateCustomerMonthChartWithCurrentData();
            }
            
            console.log(`✅ ${functionName} updated with fresh data`);
        }).catch(error => {
            console.log(`⚠️ Data reload failed for ${functionName}, using cached data:`, error);
            
            // Fallback to cached data
            if (functionName === 'updateTrackingGraph') {
                updateTrackingGraphWithCurrentData();
            } else if (functionName === 'updateCustomerMonthChart') {
                updateCustomerMonthChartWithCurrentData();
            }
        });
    };
}

// Apply the fix to both graph functions
if (typeof updateTrackingGraph === 'function') {
    window.updateTrackingGraph = createAutoUpdateGraphFunction(updateTrackingGraph, 'updateTrackingGraph');
    console.log('✅ updateTrackingGraph fixed for auto-update');
}

if (typeof updateCustomerMonthChart === 'function') {
    window.updateCustomerMonthChart = createAutoUpdateGraphFunction(updateCustomerMonthChart, 'updateCustomerMonthChart');
    console.log('✅ updateCustomerMonthChart fixed for auto-update');
}

// 🎯 2. Create automatic graph refresh function
function autoRefreshGraphs() {
    console.log('🔄 AUTO-REFRESH: Updating both graphs with latest data...');
    
    loadDashboardData().then(() => {
        console.log('✅ Fresh dashboard data loaded');
        
        // Update both graphs with fresh data
        updateTrackingGraph();
        updateCustomerMonthChart();
        
        console.log('🎉 Both graphs updated with latest data!');
        
        // Show success notification
        if (typeof showNotification === 'function') {
            showNotification('📊 Graphs updated with latest data!', 'success');
        }
    }).catch(error => {
        console.error('❌ Auto-refresh failed:', error);
    });
}

// 🎯 3. Monitor for data changes and auto-update graphs
let lastKnownDataHash = '';

function checkForDataChanges() {
    try {
        // Create a simple hash of the current data
        const currentData = JSON.stringify(dashboardData?.customers || {});
        const currentHash = currentData.length + '_' + (currentData.match(/runs/g) || []).length;
        
        if (lastKnownDataHash && lastKnownDataHash !== currentHash) {
            console.log('🔔 Data change detected! Auto-updating graphs...');
            autoRefreshGraphs();
        }
        
        lastKnownDataHash = currentHash;
    } catch (error) {
        // Silent fail for hash calculation
    }
}

// Check for changes every 3 seconds
setInterval(checkForDataChanges, 3000);

// 🎯 4. Manual update function - use this after generating tracker
window.updateGraphsNow = function() {
    console.log('🚀 MANUAL: Forcing immediate graph update...');
    autoRefreshGraphs();
};

// 🎯 5. Hook into existing refresh mechanisms
if (typeof refreshGraphsManually === 'function') {
    const originalRefresh = refreshGraphsManually;
    window.refreshGraphsManually = function() {
        console.log('🔄 Enhanced refreshGraphsManually called...');
        autoRefreshGraphs();
    };
}

// 🎯 6. Create shortcut functions
window.refreshGraphs = autoRefreshGraphs;
window.updateGraphs = autoRefreshGraphs;
window.fixGraphs = autoRefreshGraphs;

console.log('🎉 FINAL GRAPH AUTO-UPDATE FIX APPLIED!');
console.log('📝 Available commands:');
console.log('  updateGraphsNow() - Force immediate update');
console.log('  refreshGraphs() - Auto-refresh with fresh data');
console.log('  fixGraphs() - Fix graphs with latest data');
console.log('');
console.log('✅ Graphs will now auto-update every 3 seconds if data changes');
console.log('✅ Generate a tracker and graphs should update automatically!');