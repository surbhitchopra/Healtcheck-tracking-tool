// GRAPH REFRESH FIX
// This fixes the issue where graphs don't update when new trackers are generated
// even though the total cards, statistics, and table update correctly.

console.log('🔧 GRAPH REFRESH FIX: Loading graph update enhancements...');

// ENHANCED GRAPH UPDATE FUNCTION - Forces fresh data reload
function updateTrackingGraphWithFreshData() {
    console.log('📊 ENHANCED GRAPH UPDATE: Starting fresh data reload...');
    
    const graphContainer = document.getElementById('tracking-graph');
    if (!graphContainer) {
        console.log('❌ Graph container not found');
        return;
    }
    
    // Show loading state
    graphContainer.innerHTML = '<div style="display: flex; justify-content: center; align-items: center; height: 45px; color: #6b7280;"><div class="spinner"></div><span style="margin-left: 10px;">Refreshing graph...</span></div>';
    
    // FORCE FRESH DATA LOAD - Don't use cached dashboardData
    console.log('🔄 FORCING fresh data reload for graphs...');
    
    // Get fresh data from API
    loadFreshGraphData().then((freshData) => {
        if (freshData && freshData.customers) {
            console.log('✅ Fresh data loaded for graphs:', Object.keys(freshData.customers).length, 'customers');
            
            // Update the global dashboardData with fresh data
            dashboardData.customers = freshData.customers;
            dashboardData.statistics = freshData.statistics;
            
            // Now update the graphs with fresh data
            updateTrackingGraphInternal();
            updateCustomerMonthChart();
            
            console.log('✅ Graphs updated with fresh data');
        } else {
            console.log('❌ Failed to get fresh data, using existing data');
            updateTrackingGraphInternal();
            updateCustomerMonthChart();
        }
    }).catch((error) => {
        console.error('❌ Error loading fresh graph data:', error);
        updateTrackingGraphInternal();
        updateCustomerMonthChart();
    });
}

// LOAD FRESH DATA FROM API (Same as cards and table)
async function loadFreshGraphData() {
    console.log('📡 Loading fresh data from API for graphs...');
    
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error('❌ No CSRF token found');
        return null;
    }
    
    try {
        // Use the same API endpoint as the dashboard
        const response = await fetch('/api/customer-dashboard/customers/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',  // Force fresh data
                'Pragma': 'no-cache'
            },
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('📡 Fresh API response:', data);
            
            if (data.status === 'success' && data.customers) {
                // Calculate fresh statistics
                const customers = data.customers;
                let totalCustomers = 0;
                let totalRuns = 0;
                let totalTrackers = 0;
                
                // Count only real customers (not fake/unknown ones)
                Object.values(customers).forEach(customer => {
                    if (!customer.name.toLowerCase().includes('unknown') && 
                        !customer.name.toLowerCase().includes('timedotcom') &&
                        !customer.excel_source && !customer.excel_only) {
                        
                        totalCustomers++;
                        totalRuns += parseInt(customer.runs || customer.total_runs || customer.run_count || 0);
                        totalTrackers += parseInt(customer.trackers_generated || customer.total_trackers || customer.trackers || 0);
                    }
                });
                
                const statistics = {
                    total_customers: totalCustomers,
                    total_runs: totalRuns,
                    total_trackers: totalTrackers,
                    current_month_runs: 0,
                    filtered_runs: totalRuns
                };
                
                console.log('📊 Calculated fresh statistics:', statistics);
                
                return {
                    customers: customers,
                    statistics: statistics
                };
            }
        } else {
            console.log('❌ API response not ok:', response.status);
        }
    } catch (error) {
        console.error('❌ Error fetching fresh data:', error);
    }
    
    return null;
}

// INTERNAL GRAPH UPDATE (Same as original but with logging)
function updateTrackingGraphInternal() {
    console.log('🔄 INTERNAL GRAPH UPDATE: Starting with current data...');
    
    const graphContainer = document.getElementById('tracking-graph');
    const trackingContainer = graphContainer.parentElement;
    
    if (!dashboardData || !dashboardData.customers || Object.keys(dashboardData.customers).length === 0) {
        console.log('⚠️ No dashboard data available for graphs');
        graphContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #6b7280;">No data available</div>';
        return;
    }
    
    const customers = dashboardData.customers;
    
    console.log('📊 UPDATING TRACKING GRAPH WITH FRESH DATA');
    console.log('=' .repeat(60));
    
    // Use current year and month
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;
    
    console.log(`📅 CURRENT YEAR: ${currentYear}, CURRENT MONTH: ${currentMonth}`);
    
    const monthsData = [];
    
    // Generate last 6 months
    for (let i = 5; i >= 0; i--) {
        const monthDate = new Date(currentYear, currentDate.getMonth() - i, 1);
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'short' });
        const monthNumber = monthDate.getMonth() + 1;
        const year = monthDate.getFullYear();
        
        console.log(`\n📅 === PROCESSING ${monthName} ${year} (Month #${monthNumber}) ===`);
        
        // Calculate total runs for this month from FRESH data
        let monthTotal = 0;
        
        Object.values(customers).forEach(customer => {
            // Skip Excel customers from graph calculations
            if (customer.excel_source || customer.excel_only || customer.excel_data) {
                return;
            }
            
            const monthRuns = getCustomerMonthRuns(customer, year, monthNumber);
            if (monthRuns > 0) {
                console.log(`  🏃 ${customer.name}: ${monthRuns} runs`);
                monthTotal += monthRuns;
            }
        });
        
        console.log(`🎯 MONTH TOTAL: ${monthName} ${year} = ${monthTotal} runs`);
        
        monthsData.push({
            month: monthName,
            runs: monthTotal,
            fullDate: monthDate,
            isCurrentMonth: monthNumber === currentMonth && year === currentYear
        });
    }
    
    // Render the graph (same as original)
    renderLineChart(graphContainer, monthsData);
    
    console.log('📊 6-month tracking graph updated with FRESH data:', monthsData);
}

// ENHANCED CUSTOMER MONTH CHART UPDATE
function updateCustomerMonthChart() {
    console.log('📊 UPDATING CUSTOMER MONTH CHART WITH FRESH DATA');
    
    const chartContainer = document.getElementById('customer-month-chart');
    const chartContainerParent = chartContainer.parentElement;
    const customers = dashboardData.customers;
    
    if (!customers || Object.keys(customers).length === 0) {
        chartContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #6b7280;">No data available</div>';
        return;
    }
    
    // Get current month data for all customers
    const currentDate = new Date();
    let currentMonth = currentDate.getMonth() + 1;
    const currentYear = currentDate.getFullYear();
    const currentMonthName = currentDate.toLocaleDateString('en-US', { month: 'long' });
    
    console.log(`📅 ACTIVE CUSTOMERS: Using month ${currentMonth}/${currentYear}`);
    
    // Update the chart title
    const chartTitle = document.getElementById('customer-chart-title');
    if (chartTitle) {
        chartTitle.textContent = `👥 Active Customers - ${currentMonthName} ${currentYear}`;
    }
    
    const customersData = [];
    
    Object.entries(customers).forEach(([customerName, customer]) => {
        // Skip Excel customers - only show Live DB customers
        if (customer.excel_source || customer.excel_only || customer.excel_data) {
            return;
        }
        
        console.log(`\n📈 ACTIVE CHART: Getting runs for ${customerName} in ${currentMonth}/${currentYear}`);
        const monthRuns = getCustomerMonthRuns(customer, currentYear, currentMonth);
        console.log(`📈 ${customerName}: ${monthRuns} runs in active month`);
        
        if (monthRuns > 0) {
            customersData.push({
                name: customerName,
                runs: monthRuns,
                customer: customer
            });
            console.log(`  ✅ ADDED TO ACTIVE CHART: ${customerName} with ${monthRuns} runs`);
        }
    });
    
    // Sort by runs (highest first) and take top 10
    customersData.sort((a, b) => b.runs - a.runs);
    customersData.splice(10);
    
    // Render the customer chart
    renderCustomerChart(chartContainer, customersData, currentMonthName);
    
    console.log(`📈 Customer monthly chart updated with FRESH data for ${currentMonthName}:`, customersData);
}

// RENDER LINE CHART FUNCTION
function renderLineChart(graphContainer, monthsData) {
    graphContainer.innerHTML = '';
    
    const totalRuns = monthsData.reduce((sum, month) => sum + month.runs, 0);
    
    if (totalRuns === 0) {
        graphContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 45px; color: #6b7280;">
                <div>📈 No activity data</div>
                <div style="font-size: 0.7rem; margin-top: 4px;">Generate trackers to see activity</div>
            </div>
        `;
        return;
    }
    
    // Create professional line chart (simplified version)
    const maxRuns = Math.max(...monthsData.map(m => m.runs), 1);
    
    graphContainer.style.cssText = `
        display: flex;
        align-items: flex-end;
        justify-content: space-evenly;
        padding: 8px;
        height: 45px;
        gap: 4px;
        background: rgba(248, 250, 252, 0.3);
        border-radius: 6px;
    `;
    
    monthsData.forEach(monthData => {
        const height = maxRuns > 0 ? Math.max((monthData.runs / maxRuns) * 30, 4) : 4;
        
        const graphBar = document.createElement('div');
        graphBar.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            min-width: 40px;
        `;
        
        graphBar.innerHTML = `
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                        color: white; font-weight: 600; font-size: 0.7rem; 
                        padding: 2px 4px; border-radius: 4px; margin-bottom: 4px; 
                        min-width: 20px; text-align: center;" 
                 title="${monthData.month}: ${monthData.runs} runs">
                ${monthData.runs}
            </div>
            <div style="width: 60%; height: ${height}px; 
                        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%); 
                        border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>
            <div style="font-size: 0.7rem; font-weight: 600; color: #64748b; 
                        text-align: center; margin-top: 4px;">${monthData.month}</div>
        `;
        
        graphContainer.appendChild(graphBar);
    });
}

// RENDER CUSTOMER CHART FUNCTION
function renderCustomerChart(chartContainer, customersData, currentMonthName) {
    chartContainer.innerHTML = '';
    
    if (customersData.length === 0) {
        chartContainer.innerHTML = `
            <div style="padding: 20px; text-align: center; color: #6b7280;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">📈</div>
                <div style="font-weight: 600;">No activity this month</div>
                <div style="font-size: 0.8rem;">Customers will appear here when they generate trackers in ${currentMonthName}</div>
            </div>
        `;
        return;
    }
    
    chartContainer.style.cssText = `
        display: flex;
        align-items: flex-end;
        justify-content: space-evenly;
        padding: 8px;
        height: 45px;
        gap: 4px;
        background: rgba(248, 250, 252, 0.3);
        border-radius: 6px;
    `;
    
    customersData.forEach((customerData, index) => {
        const isTopPerformer = index < 3;
        const barColor = isTopPerformer ? 
            (index === 0 ? '#10b981' : index === 1 ? '#3b82f6' : '#f59e0b') : 
            '#6b7280';
        
        const chartBar = document.createElement('div');
        chartBar.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            max-width: 80px;
            min-width: 60px;
        `;
        
        chartBar.innerHTML = `
            <div style="background: ${barColor}; color: white; font-weight: 700; 
                        font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; 
                        margin-bottom: 4px; min-width: 20px; text-align: center;" 
                 title="${customerData.name}: ${customerData.runs} runs in ${currentMonthName}">
                ${customerData.runs}
            </div>
            <div style="width: 70%; height: 25px; 
                        background: linear-gradient(135deg, ${barColor} 0%, ${barColor}cc 100%); 
                        border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>
            <div style="font-size: 0.6rem; font-weight: 600; color: #374151; 
                        text-align: center; margin-top: 4px; max-width: 100%; 
                        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" 
                 title="${customerData.name}">
                ${customerData.name.length > 8 ? customerData.name.substring(0, 8) + '...' : customerData.name}
            </div>
        `;
        
        chartContainer.appendChild(chartBar);
    });
}

// OVERRIDE THE ORIGINAL FUNCTIONS
console.log('🔧 Overriding original graph functions...');

// Replace the original updateTrackingGraph function
window.updateTrackingGraph = updateTrackingGraphWithFreshData;

// AUTO-REFRESH GRAPHS WHEN DATA CHANGES
let graphRefreshInterval;

function startGraphAutoRefresh() {
    console.log('🔄 Starting graph auto-refresh...');
    
    // Clear existing interval
    if (graphRefreshInterval) {
        clearInterval(graphRefreshInterval);
    }
    
    // Refresh graphs every 15 seconds
    graphRefreshInterval = setInterval(() => {
        console.log('🔄 Auto-refreshing graphs...');
        updateTrackingGraphWithFreshData();
    }, 15000);
}

// ENHANCED: Also refresh when window gains focus
window.addEventListener('focus', () => {
    console.log('🔄 Window gained focus - refreshing graphs...');
    setTimeout(() => {
        updateTrackingGraphWithFreshData();
    }, 1000);
});

// START AUTO-REFRESH
startGraphAutoRefresh();

console.log('✅ GRAPH REFRESH FIX: Loaded successfully!');
console.log('📊 Graphs will now update automatically when trackers are generated');
console.log('🔄 Auto-refresh: Every 15 seconds + on window focus');