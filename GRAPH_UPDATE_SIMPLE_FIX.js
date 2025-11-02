// 🎯 SIMPLE GRAPH UPDATE FIX - No refresh functions, just direct data update
// This fixes the core issue: graphs use cached data that doesn't update after tracker generation

console.log('🔧 SIMPLE GRAPH UPDATE FIX: Loading...');

// 🎯 CORE FIX: Make graphs use LIVE data instead of cached data
// Override the updateTrackingGraphWithCurrentData function to reload data first
if (typeof updateTrackingGraphWithCurrentData === 'function') {
    console.log('✅ Found updateTrackingGraphWithCurrentData - applying fix...');
    
    // Store original function
    const originalUpdateFunction = updateTrackingGraphWithCurrentData;
    
    // Override with live data loading
    window.updateTrackingGraphWithCurrentData = function() {
        console.log('🔄 FIXED: Reloading dashboard data before graph update...');
        
        // Quick data reload and then update graphs
        loadDashboardData().then(() => {
            console.log('✅ Data reloaded - now updating graphs...');
            originalUpdateFunction.call(this);
        }).catch(error => {
            console.log('⚠️ Data reload failed, using cached data:', error);
            originalUpdateFunction.call(this);
        });
    };
    
    console.log('✅ Graph update function fixed to use live data');
}

// 🎯 ALSO FIX: updateCustomerMonthChart to use live data
if (typeof updateCustomerMonthChart === 'function') {
    console.log('✅ Found updateCustomerMonthChart - applying fix...');
    
    // Store original function
    const originalChartFunction = updateCustomerMonthChart;
    
    // Override with live data loading
    window.updateCustomerMonthChart = function() {
        console.log('🔄 FIXED: Reloading dashboard data before chart update...');
        
        // Quick data reload and then update chart
        loadDashboardData().then(() => {
            console.log('✅ Data reloaded - now updating chart...');
            originalChartFunction.call(this);
        }).catch(error => {
            console.log('⚠️ Data reload failed, using cached data:', error);
            originalChartFunction.call(this);
        });
    };
    
    console.log('✅ Chart update function fixed to use live data');
}

// 🎯 MAIN FIX: Override updateTrackingGraph to always reload data first
if (typeof updateTrackingGraph === 'function') {
    console.log('✅ Found updateTrackingGraph - applying main fix...');
    
    // Store original function
    const originalGraphFunction = updateTrackingGraph;
    
    // Override with live data loading
    window.updateTrackingGraph = function() {
        console.log('🔄 MAIN FIX: Always reload data before any graph update...');
        
        // Always reload data first, then update graph
        loadDashboardData().then(() => {
            console.log('✅ Fresh data loaded - now updating tracking graph...');
            
            // Call the actual graph update logic directly
            updateTrackingGraphWithCurrentData();
            
            console.log('✅ Tracking graph updated with fresh data');
        }).catch(error => {
            console.log('⚠️ Data reload failed, using cached data:', error);
            // Still try to update with cached data
            updateTrackingGraphWithCurrentData();
        });
    };
    
    console.log('✅ Main graph function fixed to always use fresh data');
}

// 🎯 EXPOSE SIMPLE UPDATE FUNCTION
window.updateGraphsNow = function() {
    console.log('🚀 MANUAL: Updating graphs with fresh data...');
    updateTrackingGraph(); // This will now reload data first
    updateCustomerMonthChart(); // This will now reload data first
    updateStatistics(); // Update stats too
    console.log('✅ All graphs updated with fresh data!');
};

console.log('🎉 SIMPLE GRAPH UPDATE FIX APPLIED!');
console.log('📝 Usage after tracker generation: updateGraphsNow()');
console.log('📝 Or just call updateTrackingGraph() - it now reloads data automatically');