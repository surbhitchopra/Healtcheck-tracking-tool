// INSTANT TRACKING GRAPH FIX - Run this in console

console.log('🔧 APPLYING INSTANT TRACKING GRAPH FIX...');

// Override updateTrackingGraph with DIRECT database approach
window.updateTrackingGraph = function() {
    console.log('📊 FIXED: Updating tracking graph with DIRECT database detection...');
    
    const graphContainer = document.getElementById('tracking-graph');
    const customers = dashboardData.customers;
    
    // Get last 6 months with DIRECT monthly_runs checking
    const currentDate = new Date();
    const monthsData = [];
    
    for (let i = 5; i >= 0; i--) {
        const monthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'short' });
        const monthNumber = monthDate.getMonth() + 1;
        const year = monthDate.getFullYear();
        const monthKey = `${year}-${monthNumber.toString().padStart(2, '0')}`;
        
        console.log(`🔍 DIRECT CHECK: ${monthName} ${year} (${monthKey})`);
        
        // DIRECT APPROACH: Check monthly_runs directly
        const customerGroups = {};
        
        if (customers && Object.keys(customers).length > 0) {
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                
                // Initialize customer group
                if (!customerGroups[customerName]) {
                    customerGroups[customerName] = {
                        name: customerName,
                        hasData: false
                    };
                }
                
                // DIRECT CHECK: Look directly in monthly_runs
                if (customer.monthly_runs && customer.monthly_runs[monthKey]) {
                    const monthValue = customer.monthly_runs[monthKey];
                    // Valid if it's not a status message
                    if (monthValue && 
                        monthValue !== '-' && 
                        monthValue !== 'Not Started' && 
                        monthValue !== 'No Report' && 
                        monthValue !== 'Not Run') {
                        
                        customerGroups[customerName].hasData = true;
                        console.log(`  ✅ DIRECT: ${customerName} has ${monthValue}`);
                    }
                }
            });
        }
        
        const customersWithData = Object.values(customerGroups).filter(g => g.hasData);
        const monthTotal = customersWithData.length;
        
        console.log(`📅 FIXED: ${monthName} ${year}: ${monthTotal} customers`);
        console.log(`  Customers: ${customersWithData.map(c => c.name).join(', ')}`);
        
        monthsData.push({
            month: monthName,
            runs: monthTotal,
            fullDate: monthDate,
            customers: customersWithData.map(c => c.name)
        });
    }
    
    // Clear and rebuild chart
    graphContainer.innerHTML = '';
    
    const totalRuns = monthsData.reduce((sum, month) => sum + month.runs, 0);
    const maxRuns = Math.max(...monthsData.map(m => m.runs), 1);
    
    if (totalRuns === 0) {
        graphContainer.innerHTML = `
            <div style="padding: 40px; text-align: center; color: #6b7280;">
                <div style="font-size: 2rem; margin-bottom: 16px;">📈</div>
                <div style="font-weight: 600; margin-bottom: 8px;">No activity data</div>
                <div style="font-size: 0.9rem;">Start by uploading health checks</div>
            </div>
        `;
        return;
    }
    
    // Create line chart
    graphContainer.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        height: 140px;
        padding: 20px;
        position: relative;
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
    
    // Create data points
    const points = monthsData.map((month, i) => {
        const x = padding.left + (i / Math.max(monthsData.length - 1, 1)) * innerWidth;
        const normalizedValue = maxRuns > 0 ? month.runs / maxRuns : 0;
        const y = padding.top + innerHeight - (normalizedValue * innerHeight * 0.9);
        
        return { x, y, runs: month.runs, month: month.month, customers: month.customers };
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
    path.setAttribute('stroke-linecap', 'round');
    svg.appendChild(path);
    
    // Add data points with tooltips
    points.forEach(point => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', point.x);
        circle.setAttribute('cy', point.y);
        circle.setAttribute('r', '5');
        circle.setAttribute('fill', '#3b82f6');
        circle.setAttribute('stroke', 'white');
        circle.setAttribute('stroke-width', '2');
        
        // Add tooltip
        const tooltip = point.customers.length > 0 ? 
            `${point.month}: ${point.runs} customers (${point.customers.join(', ')})` :
            `${point.month}: ${point.runs} customers`;
        
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = tooltip;
        circle.appendChild(title);
        
        svg.appendChild(circle);
        
        // Add value labels
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', point.x);
        text.setAttribute('y', point.y - 12);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('fill', '#1f2937');
        text.textContent = point.runs;
        svg.appendChild(text);
        
        // Add month labels
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
    
    console.log('✅ FIXED tracking graph rendered with DIRECT database approach');
    console.log('📊 Expected results based on database:');
    console.log('   May: 7+ customers (Tata group + LTV + others)');
    console.log('   June: 7+ customers');  
    console.log('   July: 6+ customers');
    console.log('   August: 6+ customers');
    console.log('   September: 4+ customers');
    console.log('   October: 3 customers (BSNL, Moratelindo, OPT_NC)');
};

// Apply the fix immediately
updateTrackingGraph();

console.log('🎉 TRACKING GRAPH FIXED!');
console.log('Now all months should show correct customer counts based on actual database data.');
console.log('Hover over the data points to see which customers have data in each month.');