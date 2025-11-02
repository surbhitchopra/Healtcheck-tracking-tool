// 🚀 SIMPLE TABLE-BASED GRAPHS - REAL-TIME UPDATE
// No complex API calls, just read from table data directly

console.log('🔥 Loading SIMPLE TABLE-BASED GRAPH SYSTEM...');

// 📊 SIMPLE TRACKING GRAPH - Last 6 months based on table data
function updateSimpleTrackingGraph() {
    console.log('📈 Updating simple tracking graph from table data...');
    
    const graphContainer = document.getElementById('tracking-graph');
    if (!graphContainer) return;
    
    // Get current date
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth() + 1;
    
    // Calculate last 6 months
    const monthsData = [];
    for (let i = 5; i >= 0; i--) {
        const date = new Date(currentYear, today.getMonth() - i, 1);
        const monthName = date.toLocaleDateString('en-US', { month: 'short' });
        const monthNum = date.getMonth() + 1;
        const year = date.getFullYear();
        
        // Count runs for this month from table
        let monthRuns = 0;
        
        // Read directly from customer table rows
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        tableRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 12) { // Make sure it has month columns
                // Check month column (Oct = index 11 for 12 months starting from index 1)
                const monthIndex = monthNum - 1; // Convert to 0-based
                if (monthIndex >= 0 && monthIndex < 12) {
                    const monthCell = cells[monthIndex + 1]; // +1 because first cell is customer name
                    if (monthCell && monthCell.textContent.trim() !== '-' && monthCell.textContent.trim() !== '') {
                        monthRuns++;
                        console.log(`Found run in ${monthName} ${year}: ${monthCell.textContent.trim()}`);
                    }
                }
            }
        });
        
        console.log(`${monthName} ${year}: ${monthRuns} runs`);
        monthsData.push({
            month: monthName,
            runs: monthRuns,
            year: year
        });
    }
    
    // Clear container
    graphContainer.innerHTML = '';
    graphContainer.style.cssText = `
        display: flex;
        align-items: flex-end;
        justify-content: space-around;
        height: 120px;
        padding: 10px;
        background: linear-gradient(to top, rgba(59, 130, 246, 0.1), transparent);
        border-radius: 8px;
        gap: 5px;
    `;
    
    const maxRuns = Math.max(...monthsData.map(m => m.runs), 1);
    
    // Create bars
    monthsData.forEach(data => {
        const barHeight = maxRuns > 0 ? (data.runs / maxRuns) * 80 : 5;
        
        const barContainer = document.createElement('div');
        barContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            max-width: 50px;
        `;
        
        const bar = document.createElement('div');
        bar.style.cssText = `
            width: 100%;
            height: ${Math.max(barHeight, 5)}px;
            background: linear-gradient(to top, #3b82f6, #60a5fa);
            border-radius: 4px 4px 0 0;
            margin-bottom: 5px;
            position: relative;
            cursor: pointer;
            transition: transform 0.2s ease;
        `;
        
        bar.addEventListener('mouseenter', () => {
            bar.style.transform = 'scale(1.1)';
        });
        
        bar.addEventListener('mouseleave', () => {
            bar.style.transform = 'scale(1)';
        });
        
        // Add count on top of bar
        const count = document.createElement('div');
        count.textContent = data.runs;
        count.style.cssText = `
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 11px;
            font-weight: bold;
            color: #374151;
        `;
        bar.appendChild(count);
        
        // Add month label with year (e.g., "Oct'25")
        const label = document.createElement('div');
        const yearShort = String(data.year).slice(-2); // Get last 2 digits (2025 -> 25)
        label.textContent = `${data.month}'${yearShort}`; // Format: Oct'25
        label.style.cssText = `
            font-size: 10px;
            color: #6b7280;
            font-weight: 500;
        `;
        label.title = `${data.month} ${data.year}`; // Tooltip shows full year on hover
        
        barContainer.appendChild(bar);
        barContainer.appendChild(label);
        graphContainer.appendChild(barContainer);
    });
    
    console.log('✅ Simple tracking graph updated!', monthsData);
}

// 👥 SIMPLE ACTIVE CUSTOMERS CHART - Current month only
function updateSimpleCustomerChart() {
    console.log('👥 Updating simple customer chart from table data...');
    
    const chartContainer = document.getElementById('customer-month-chart');
    if (!chartContainer) return;
    
    // Get current month
    const today = new Date();
    const currentMonth = today.getMonth() + 1; // 1-based
    const monthName = today.toLocaleDateString('en-US', { month: 'long' });
    
    // Update title
    const chartTitle = document.getElementById('customer-chart-title');
    if (chartTitle) {
        chartTitle.textContent = `👥 Active Customers - ${monthName} ${today.getFullYear()}`;
    }
    
    // Count customers with activity this month from table
    const customerData = [];
    const tableRows = document.querySelectorAll('#customer-table-body tr.customer-summary-row');
    
    tableRows.forEach(row => {
        const nameCell = row.querySelector('.customer-name-cell');
        const customerName = nameCell ? nameCell.textContent.trim() : 'Unknown';
        
        // Check current month column
        const cells = row.querySelectorAll('td');
        if (cells.length >= currentMonth + 1) {
            const monthCell = cells[currentMonth]; // currentMonth is 1-based, so index = currentMonth
            const monthValue = monthCell ? monthCell.textContent.trim() : '';
            
            if (monthValue && monthValue !== '-' && monthValue !== '') {
                customerData.push({
                    name: customerName,
                    runs: 1, // Count as 1 active session
                    monthValue: monthValue
                });
                console.log(`Active customer: ${customerName} - ${monthValue}`);
            }
        }
    });
    
    // Sort by name and take top 10
    customerData.sort((a, b) => a.name.localeCompare(b.name));
    const topCustomers = customerData.slice(0, 10);
    
    // Clear and style container
    chartContainer.innerHTML = '';
    chartContainer.style.cssText = `
        display: flex;
        align-items: flex-end;
        justify-content: space-around;
        height: 80px;
        padding: 8px;
        background: rgba(248, 250, 252, 0.5);
        border-radius: 6px;
        gap: 3px;
        overflow-x: auto;
    `;
    
    if (topCustomers.length === 0) {
        chartContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; width: 100%; color: #6b7280;">
                <span>No active customers in ${monthName}</span>
            </div>
        `;
        return;
    }
    
    // Create customer bars
    topCustomers.forEach((customer, index) => {
        const barContainer = document.createElement('div');
        barContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            min-width: 45px;
            max-width: 60px;
            cursor: pointer;
        `;
        
        const bar = document.createElement('div');
        const colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'];
        const color = colors[index % colors.length];
        
        bar.style.cssText = `
            width: 100%;
            height: 40px;
            background: ${color};
            border-radius: 4px 4px 0 0;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
            transition: transform 0.2s ease;
        `;
        
        bar.textContent = '✓';
        bar.title = `${customer.name}: Active in ${monthName}`;
        
        bar.addEventListener('mouseenter', () => {
            bar.style.transform = 'scale(1.05)';
        });
        
        bar.addEventListener('mouseleave', () => {
            bar.style.transform = 'scale(1)';
        });
        
        // Customer name label
        const label = document.createElement('div');
        const displayName = customer.name.length > 8 ? customer.name.substring(0, 8) + '...' : customer.name;
        label.textContent = displayName;
        label.style.cssText = `
            font-size: 9px;
            color: #374151;
            font-weight: 500;
            text-align: center;
            line-height: 1.2;
        `;
        label.title = customer.name;
        
        barContainer.appendChild(bar);
        barContainer.appendChild(label);
        chartContainer.appendChild(barContainer);
    });
    
    console.log('✅ Simple customer chart updated!', topCustomers);
}

// 🔄 UPDATE BOTH GRAPHS
function updateAllSimpleGraphs() {
    console.log('🔄 Updating all simple graphs...');
    updateSimpleTrackingGraph();
    updateSimpleCustomerChart();
    console.log('✅ All simple graphs updated!');
}

// 🎯 WATCH TABLE CHANGES - Update graphs when table updates
function watchTableChanges() {
    const tableBody = document.getElementById('customer-table-body');
    if (!tableBody) return;
    
    // Create observer to watch table changes
    const observer = new MutationObserver((mutations) => {
        let tableChanged = false;
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0)) {
                tableChanged = true;
            }
        });
        
        if (tableChanged) {
            console.log('📊 Table changed, updating graphs...');
            setTimeout(updateAllSimpleGraphs, 500); // Small delay to ensure table is fully updated
        }
    });
    
    observer.observe(tableBody, {
        childList: true,
        subtree: true
    });
    
    console.log('👀 Table watcher started - graphs will auto-update!');
}

// 🚀 INITIALIZE SYSTEM
function initSimpleGraphs() {
    console.log('🚀 Initializing simple graph system...');
    
    // Initial update
    setTimeout(updateAllSimpleGraphs, 1000);
    
    // Watch table changes
    watchTableChanges();
    
    // Auto refresh every 10 seconds
    setInterval(() => {
        console.log('⏰ Auto-refreshing simple graphs...');
        updateAllSimpleGraphs();
    }, 10000);
    
    console.log('✅ Simple graph system initialized!');
}

// 🎯 EXPOSE FUNCTIONS TO GLOBAL SCOPE
window.updateSimpleTrackingGraph = updateSimpleTrackingGraph;
window.updateSimpleCustomerChart = updateSimpleCustomerChart;
window.updateAllSimpleGraphs = updateAllSimpleGraphs;
window.initSimpleGraphs = initSimpleGraphs;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSimpleGraphs);
} else {
    initSimpleGraphs();
}

console.log('🎉 Simple Table-Based Graph System Loaded!');