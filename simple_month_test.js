// SIMPLE MONTH TEST - Copy paste in console to debug

console.log('🔍 SIMPLE MONTH TEST - Checking why previous months show 0');
console.log('='.repeat(60));

const customers = dashboardData.customers;
const testMonths = [
    { key: '2025-05', name: 'May' },
    { key: '2025-06', name: 'June' }, 
    { key: '2025-07', name: 'July' },
    { key: '2025-08', name: 'August' },
    { key: '2025-09', name: 'September' },
    { key: '2025-10', name: 'October' }
];

testMonths.forEach(monthInfo => {
    console.log(`\n📅 Testing ${monthInfo.name} (${monthInfo.key}):`);
    
    let customerCount = 0;
    let foundCustomers = [];
    
    if (customers && Object.keys(customers).length > 0) {
        Object.entries(customers).forEach(([customerKey, customer]) => {
            const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
            
            // Direct check in monthly_runs
            if (customer.monthly_runs && customer.monthly_runs[monthInfo.key]) {
                const monthValue = customer.monthly_runs[monthInfo.key];
                
                // Count as valid if it's not a status message
                if (monthValue && 
                    monthValue !== '-' && 
                    monthValue !== 'Not Started' && 
                    monthValue !== 'No Report' && 
                    monthValue !== 'Not Run') {
                    
                    if (!foundCustomers.includes(customerName)) {
                        foundCustomers.push(customerName);
                        customerCount++;
                    }
                    console.log(`  ✅ ${customerName}: ${monthValue}`);
                }
            }
        });
    }
    
    console.log(`📊 TOTAL: ${customerCount} unique customers in ${monthInfo.name}`);
    console.log(`👥 Customers: ${foundCustomers.join(', ')}`);
});

console.log('\n' + '='.repeat(60));
console.log('🎯 EXPECTED TRACKING GRAPH DATA:');

// Now apply this data to tracking graph
const monthsData = [];
const currentDate = new Date();

testMonths.forEach((monthInfo, index) => {
    const customerGroups = {};
    
    if (customers && Object.keys(customers).length > 0) {
        Object.entries(customers).forEach(([customerKey, customer]) => {
            const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
            
            if (!customerGroups[customerName]) {
                customerGroups[customerName] = { name: customerName, hasData: false };
            }
            
            if (customer.monthly_runs && customer.monthly_runs[monthInfo.key]) {
                const monthValue = customer.monthly_runs[monthInfo.key];
                if (monthValue && 
                    monthValue !== '-' && 
                    monthValue !== 'Not Started' && 
                    monthValue !== 'No Report' && 
                    monthValue !== 'Not Run') {
                    customerGroups[customerName].hasData = true;
                }
            }
        });
    }
    
    const customersWithData = Object.values(customerGroups).filter(g => g.hasData);
    monthsData.push({
        month: monthInfo.name,
        runs: customersWithData.length,
        customers: customersWithData.map(c => c.name)
    });
});

console.log('Graph should show:');
monthsData.forEach(month => {
    console.log(`  ${month.month}: ${month.runs} customers`);
});

// Force update the tracking graph with this correct data
console.log('\n🔄 Forcing tracking graph update with correct data...');

// Override the updateTrackingGraph function temporarily
const originalFunction = window.updateTrackingGraph;

window.updateTrackingGraph = function() {
    console.log('📊 APPLYING CORRECTED DATA TO TRACKING GRAPH');
    
    const graphContainer = document.getElementById('tracking-graph');
    graphContainer.innerHTML = '';
    
    const maxRuns = Math.max(...monthsData.map(m => m.runs), 1);
    
    // Simple SVG chart creation
    graphContainer.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        height: 140px;
        padding: 20px;
        background: linear-gradient(to top, rgba(102, 126, 234, 0.03) 0%, transparent 40%);
        border-radius: 12px;
    `;
    
    const chartWidth = 320;
    const chartHeight = 120;
    const padding = { left: 25, right: 25, top: 25, bottom: 25 };
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', chartHeight);
    svg.setAttribute('viewBox', `0 0 ${chartWidth} ${chartHeight}`);
    
    const innerWidth = chartWidth - padding.left - padding.right;
    const innerHeight = chartHeight - padding.top - padding.bottom;
    
    // Create points
    const points = monthsData.map((month, i) => {
        const x = padding.left + (i / (monthsData.length - 1)) * innerWidth;
        const normalizedValue = month.runs / maxRuns;
        const y = padding.top + innerHeight - (normalizedValue * innerHeight * 0.9);
        return { x, y, runs: month.runs, month: month.month };
    });
    
    // Draw line
    let pathData = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
        pathData += ` L ${points[i].x} ${points[i].y}`;
    }
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathData);
    path.setAttribute('stroke', '#3b82f6');
    path.setAttribute('stroke-width', '3');
    path.setAttribute('fill', 'none');
    svg.appendChild(path);
    
    // Add points
    points.forEach(point => {
        // Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', point.x);
        circle.setAttribute('cy', point.y);
        circle.setAttribute('r', '5');
        circle.setAttribute('fill', '#3b82f6');
        circle.setAttribute('stroke', 'white');
        circle.setAttribute('stroke-width', '2');
        svg.appendChild(circle);
        
        // Value label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', point.x);
        text.setAttribute('y', point.y - 12);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('fill', '#1f2937');
        text.textContent = point.runs;
        svg.appendChild(text);
        
        // Month label
        const monthText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        monthText.setAttribute('x', point.x);
        monthText.setAttribute('y', chartHeight - 8);
        monthText.setAttribute('text-anchor', 'middle');
        monthText.setAttribute('font-size', '12');
        monthText.setAttribute('font-weight', '600');
        monthText.setAttribute('fill', '#4b5563');
        monthText.textContent = point.month;
        svg.appendChild(monthText);
    });
    
    graphContainer.appendChild(svg);
    console.log('✅ Tracking graph updated with correct data!');
};

// Apply the fix
updateTrackingGraph();

console.log('\n🎉 TEST COMPLETE!');
console.log('If the graph still shows 0s, there might be a browser caching issue.');
console.log('Try hard refresh (Ctrl+F5) or clear browser cache.');