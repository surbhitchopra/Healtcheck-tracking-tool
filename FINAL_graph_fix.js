
// 🔧 FINAL GRAPH FIX - Paste this in browser console to update with REAL data

console.log('🚀 Updating graphs with REAL database data...');

const realCustomerData = {};
const realMonthlyData = {"May": 18, "Jun": 20, "Jul": 52, "Aug": 50, "Sep": 45, "Oct": 0};

console.log('📊 Real customer data from DB:', realCustomerData);
console.log('📈 Real monthly data from DB:', realMonthlyData);

// Update Active Customers chart (right side)
function updateCustomerChartWithRealData() {
    const chart = document.getElementById('customer-month-chart');
    if (!chart) {
        console.log('❌ Customer chart not found');
        return;
    }
    
    console.log('🔄 Updating customer chart...');
    
    const customers = Object.entries(realCustomerData).slice(0, 3);
    if (customers.length === 0) {
        chart.innerHTML = '<div style="padding: 10px; text-align: center; color: #6b7280;">No October 2025 sessions found</div>';
        return;
    }
    
    const maxRuns = Math.max(...Object.values(realCustomerData), 1);
    let html = '<div style="display: flex; align-items: end; height: 35px; gap: 4px; padding: 5px;">';
    
    const colors = ['#10b981', '#3b82f6', '#f59e0b'];
    
    customers.forEach(([name, count], i) => {
        const height = Math.max(8, (count / maxRuns) * 25);
        
        html += `
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
            <div style="background: ${colors[i] || '#6b7280'}; height: ${height}px; width: 100%; border-radius: 2px; position: relative;">
                <div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); 
                           background: ${colors[i] || '#6b7280'}; color: white; padding: 1px 4px; border-radius: 50%; 
                           font-size: 0.6rem; font-weight: 600; min-width: 16px; text-align: center;">${count}</div>
            </div>
            <div style="font-size: 0.6rem; font-weight: 600; color: #374151; margin-top: 2px; text-align: center;">
                ${name.length > 8 ? name.substring(0, 8) + '..' : name}
            </div>
            <div style="font-size: 0.5rem; color: #6b7280;">Oct</div>
        </div>`;
    });
    
    html += '</div>';
    chart.innerHTML = html;
    
    // Update title
    const title = document.getElementById('customer-chart-title');
    if (title) {
        title.textContent = '👥 Active Customers - October 2025 (REAL DATA)';
        title.style.color = '#059669';
    }
    
    console.log('✅ Customer chart updated with real data');
}

// Update Last 6 Months Activity chart (left side)  
function updateTrackingGraphWithRealData() {
    const graph = document.getElementById('tracking-graph');
    if (!graph) {
        console.log('❌ Tracking graph not found');
        return;
    }
    
    console.log('🔄 Updating tracking graph...');
    
    const months = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
    const data = months.map(m => realMonthlyData[m] || 0);
    const maxVal = Math.max(...data, 1);
    
    let html = '<div style="position: relative; height: 35px; padding: 5px;">';
    
    // Create SVG line chart
    html += '<svg style="position: absolute; width: 100%; height: 100%; z-index: 1;">';
    
    let pathData = '';
    data.forEach((val, i) => {
        const x = 10 + (i * 35);
        const y = 25 - (val / maxVal * 15);
        pathData += (i === 0 ? `M${x},${y}` : ` L${x},${y}`);
        
        // Add data points and labels
        html += `
        <circle cx="${x}" cy="${y}" r="2" fill="#3b82f6" stroke="white" stroke-width="1"/>
        <text x="${x}" y="${y-5}" text-anchor="middle" style="font-size: 8px; fill: #3b82f6; font-weight: 600;">${val} runs</text>
        <text x="${x}" y="32" text-anchor="middle" style="font-size: 8px; fill: #374151; font-weight: 600;">${months[i]}</text>
        `;
    });
    
    // Add line path
    html += `<path d="${pathData}" stroke="#3b82f6" stroke-width="2" fill="none" stroke-linecap="round"/>`;
    html += '</svg></div>';
    
    graph.innerHTML = html;
    console.log('✅ Tracking graph updated with real data');
}

// Apply both fixes
try {
    updateCustomerChartWithRealData();
    updateTrackingGraphWithRealData();
    
    console.log('🎉 SUCCESS: Both graphs updated with real database data!');
    console.log('📊 If you see this message, the graphs should now show correct data');
    
    // Show success notification if available
    if (window.showNotification) {
        window.showNotification('✅ Graphs updated with real database data!', 'success');
    }
    
} catch (error) {
    console.error('❌ Error updating graphs:', error);
}
