// INSTANT CHART FIX - Copy and paste this entire code in browser console

console.log('🔧 APPLYING INSTANT CHART FIX...');

// OVERRIDE THE EXISTING FUNCTION WITH CORRECTED VERSION
window.updateCustomerMonthChart = function() {
    console.log('🔄 ENHANCED: Updating customer month chart with CORRECTED data...');
    
    const chartContainer = document.getElementById('customer-month-chart');
    const chartContainerParent = chartContainer.parentElement;
    const customers = dashboardData.customers;
    
    // Get current month data for all customers
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth() + 1;
    const currentYear = currentDate.getFullYear();
    const currentMonthName = currentDate.toLocaleDateString('en-US', { month: 'long' });
    
    // Update the chart title with current month and year
    const chartTitle = document.getElementById('customer-chart-title');
    if (chartTitle) {
        chartTitle.textContent = `👥 Active Customers - ${currentMonthName} ${currentYear}`;
    }
    
    const customersData = [];
    
    console.log(`📊 CORRECTED: Available customers for month chart:`, Object.keys(customers || {}));
    
    if (customers && Object.keys(customers).length > 0) {
        // *** CORRECTED GROUPING LOGIC ***
        const customerGroups = {};
        
        Object.entries(customers).forEach(([customerKey, customer]) => {
            const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
            
            // Initialize customer group if not exists
            if (!customerGroups[customerName]) {
                customerGroups[customerName] = {
                    name: customerName,
                    totalRuns: 0,
                    networks: [],
                    hasCurrentMonthData: false
                };
            }
            
            const monthRuns = getCustomerMonthRuns(customer, currentYear, currentMonth);
            
            console.log(`🔍 CORRECTED: Customer ${customerName} (${customerKey}): month runs = ${monthRuns}`);
            
            if (monthRuns > 0) {
                customerGroups[customerName].totalRuns += monthRuns;
                customerGroups[customerName].hasCurrentMonthData = true;
                customerGroups[customerName].networks.push(customerKey);
            }
        });
        
        // Convert grouped customers to chart data
        Object.values(customerGroups).forEach(group => {
            if (group.hasCurrentMonthData) {
                customersData.push({
                    name: group.name,
                    runs: group.totalRuns,
                    customer: group,
                    source: 'corrected_grouping',
                    networks: group.networks.length
                });
            }
        });
        
        console.log(`📊 CORRECTED: Found ${customersData.length} customers with data in ${currentMonthName} ${currentYear}`);
        
        // Sort by runs (highest first) and take top 10
        customersData.sort((a, b) => b.runs - a.runs);
        customersData.splice(10); // Keep only top 10
    }
    
    console.log('📊 CORRECTED Final customer data:', customersData.map(c => `${c.name}: ${c.runs} runs from ${c.networks} networks`));
    
    chartContainer.innerHTML = '';
    
    // Handle empty data state
    if (customersData.length === 0) {
        chartContainer.innerHTML = `
            <div style="padding: 40px; text-align: center; color: #6b7280;">
                <div style="font-size: 2rem; margin-bottom: 16px;">📈</div>
                <div style="font-weight: 600; margin-bottom: 8px;">No activity this month</div>
                <div style="font-size: 0.9rem;">Customers will appear here when they run health checks in ${currentMonthName}</div>
            </div>
        `;
        return;
    }
    
    const maxRuns = Math.max(...customersData.map(c => c.runs), 1);
    
    // Dynamic container styling
    chartContainer.style.cssText = `
        display: flex;
        align-items: flex-end;
        justify-content: space-evenly;
        padding: 8px;
        height: 100px;
        gap: 4px;
        overflow-x: auto;
        overflow-y: hidden;
        background: rgba(248, 250, 252, 0.3);
        border-radius: 6px;
    `;
    
    // Create chart bars for each customer
    customersData.forEach((customerData, index) => {
        const height = 40; // Fixed height for all bars
        const isTopPerformer = index < 3;
        
        const chartBar = document.createElement('div');
        chartBar.className = 'customer-chart-bar';
        chartBar.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
            margin: 0 6px;
            flex: 1;
            max-width: 85px;
            min-width: 70px;
            height: 85px;
            cursor: pointer;
            transition: all 0.3s ease;
            filter: drop-shadow(0 1px 3px rgba(0,0,0,0.1));
        `;
        
        const barColor = isTopPerformer ? 
            (index === 0 ? '#10b981' : index === 1 ? '#3b82f6' : '#f59e0b') : 
            '#6b7280';
        
        chartBar.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; width: 100%;">
                <div style="
                    background: ${barColor};
                    color: white;
                    font-weight: 800;
                    font-size: 0.8rem;
                    padding: 3px 8px;
                    border-radius: 6px;
                    margin-bottom: 4px;
                    min-width: 24px;
                    text-align: center;
                    box-shadow: 0 3px 8px rgba(0,0,0,0.25);
                " title="${customerData.name}: ${customerData.runs} runs from ${customerData.networks} networks">
                    ${customerData.runs}
                </div>
                <div style="width: 80%; height: ${height}px; background: linear-gradient(135deg, ${barColor} 0%, ${barColor}cc 100%); border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"></div>
                <div style="font-size: 0.65rem; font-weight: 700; color: #374151; text-align: center; margin-top: 6px; line-height: 1.1;">
                    ${customerData.name}
                </div>
            </div>
        `;
        
        // Add hover effects
        chartBar.addEventListener('mouseenter', () => {
            chartBar.style.transform = 'scale(1.08) translateY(-2px)';
            chartBar.style.filter = 'drop-shadow(0 3px 8px rgba(0,0,0,0.15))';
        });
        chartBar.addEventListener('mouseleave', () => {
            chartBar.style.transform = 'scale(1) translateY(0)';
            chartBar.style.filter = 'drop-shadow(0 1px 3px rgba(0,0,0,0.1))';
        });
        
        chartContainer.appendChild(chartBar);
    });
    
    console.log('✅ CORRECTED customer month chart rendered successfully');
};

// APPLY THE FIX IMMEDIATELY
updateCustomerMonthChart();

console.log('🎉 INSTANT FIX APPLIED! Charts should now show correct data:');
console.log('   - BSNL: 3 runs (from 3 networks)');
console.log('   - Moratelindo: 1 run (from 1 network)');  
console.log('   - OPT_NC: 1 run (from 1 network)');
console.log('');
console.log('✅ If you see the correct numbers now, the fix is working!');