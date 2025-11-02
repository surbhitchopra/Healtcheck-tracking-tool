// 🎯 NEW SIMPLE GRAPHS - Sync directly with table data
// This replaces problematic graphs with simple ones that work

console.log('🚀 CREATING NEW SIMPLE GRAPHS...');

// 🔄 Function to get data directly from table
function getDataFromTable() {
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    const customers = {};
    const monthlyTotals = {
        'May': 0, 'Jun': 0, 'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0
    };
    
    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 10) {
            const customerName = cells[0]?.textContent?.trim();
            if (customerName && customerName !== 'No customers found') {
                // Get total runs from table
                const totalRuns = parseInt(cells[1]?.textContent?.trim() || '0');
                
                // Get monthly data from table columns (assuming months start from column 8)
                const mayRuns = cells[8]?.textContent?.includes('-') ? 0 : 1;
                const junRuns = cells[9]?.textContent?.includes('-') ? 0 : 1;
                const julRuns = cells[10]?.textContent?.includes('-') ? 0 : 1;
                const augRuns = cells[11]?.textContent?.includes('-') ? 0 : 1;
                const sepRuns = cells[12]?.textContent?.includes('-') ? 0 : 1;
                const octRuns = cells[13]?.textContent?.includes('-') ? 0 : 1;
                
                // Add to monthly totals
                monthlyTotals.May += mayRuns;
                monthlyTotals.Jun += junRuns;
                monthlyTotals.Jul += julRuns;
                monthlyTotals.Aug += augRuns;
                monthlyTotals.Sep += sepRuns;
                monthlyTotals.Oct += octRuns;
                
                // Store customer data
                customers[customerName] = {
                    name: customerName,
                    totalRuns: totalRuns,
                    octRuns: octRuns
                };
            }
        }
    });
    
    return { customers, monthlyTotals };
}

// 🎨 Create simple left graph (6-month activity)
function createSimpleLeftGraph() {
    const leftGraphContainer = document.getElementById('tracking-graph');
    if (!leftGraphContainer) return;
    
    const { monthlyTotals } = getDataFromTable();
    
    console.log('📊 Left graph data from table:', monthlyTotals);
    
    leftGraphContainer.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3 style="margin-bottom: 20px; color: #374151;">📈 Last 6 Months Activity</h3>
            <div style="display: flex; justify-content: space-around; align-items: end; height: 120px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                ${Object.entries(monthlyTotals).map(([month, runs]) => `
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <div style="
                            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                            color: white;
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-weight: bold;
                            font-size: 0.9rem;
                            margin-bottom: 8px;
                            min-width: 35px;
                            text-align: center;
                            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
                        ">${runs} runs</div>
                        <div style="
                            width: 20px;
                            height: ${Math.max(runs * 8, 8)}px;
                            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                            border-radius: 4px;
                            margin-bottom: 5px;
                        "></div>
                        <div style="font-weight: 600; color: #6b7280; font-size: 0.85rem;">${month}</div>
                    </div>
                `).join('')}
            </div>
            <div style="margin-top: 10px; color: #6b7280; font-size: 0.8rem;">
                ✅ Data synced with table
            </div>
        </div>
    `;
    
    console.log('✅ Simple left graph created with table data');
}

// 🎨 Create simple right graph (active customers)
function createSimpleRightGraph() {
    const rightGraphContainer = document.getElementById('customer-month-chart');
    if (!rightGraphContainer) return;
    
    const { customers } = getDataFromTable();
    
    // Get top 5 customers with October runs
    const activeCustomers = Object.values(customers)
        .filter(customer => customer.octRuns > 0)
        .sort((a, b) => b.totalRuns - a.totalRuns)
        .slice(0, 5);
    
    console.log('📊 Right graph data from table:', activeCustomers);
    
    if (activeCustomers.length === 0) {
        rightGraphContainer.innerHTML = `
            <div style="padding: 40px; text-align: center; color: #6b7280;">
                <div style="font-size: 2rem; margin-bottom: 16px;">📈</div>
                <div style="font-weight: 600;">No October Activity</div>
                <div style="font-size: 0.9rem; margin-top: 8px;">✅ Synced with table</div>
            </div>
        `;
        return;
    }
    
    rightGraphContainer.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3 style="margin-bottom: 20px; color: #374151;">👥 Active Customers - October 2025</h3>
            <div style="display: flex; justify-content: space-around; align-items: end; height: 100px;">
                ${activeCustomers.map((customer, index) => {
                    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];
                    const color = colors[index] || '#6b7280';
                    return `
                        <div style="display: flex; flex-direction: column; align-items: center; margin: 0 5px;">
                            <div style="
                                background: ${color};
                                color: white;
                                padding: 4px 8px;
                                border-radius: 50%;
                                font-weight: bold;
                                font-size: 0.8rem;
                                margin-bottom: 8px;
                                min-width: 25px;
                                text-align: center;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                            ">${customer.totalRuns}</div>
                            <div style="
                                width: 40px;
                                height: 60px;
                                background: linear-gradient(135deg, ${color}, ${color}dd);
                                border-radius: 6px;
                                margin-bottom: 5px;
                            "></div>
                            <div style="
                                font-weight: 600; 
                                color: #374151; 
                                font-size: 0.7rem; 
                                text-align: center;
                                max-width: 50px;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                white-space: nowrap;
                            " title="${customer.name}">${customer.name.length > 8 ? customer.name.substring(0, 8) + '..' : customer.name}</div>
                            <div style="font-size: 0.6rem; color: #6b7280;">Oct</div>
                        </div>
                    `;
                }).join('')}
            </div>
            <div style="margin-top: 15px; color: #6b7280; font-size: 0.8rem;">
                ✅ Data synced with table
            </div>
        </div>
    `;
    
    console.log('✅ Simple right graph created with table data');
}

// 🔄 Function to update both graphs
function updateSimpleGraphs() {
    console.log('🔄 Updating simple graphs with table data...');
    createSimpleLeftGraph();
    createSimpleRightGraph();
    console.log('✅ Simple graphs updated!');
}

// 🎯 Auto-update graphs when table changes
function startGraphTableSync() {
    // Update graphs every 2 seconds
    setInterval(() => {
        updateSimpleGraphs();
    }, 2000);
    
    // Also update when window gains focus
    window.addEventListener('focus', updateSimpleGraphs);
    
    console.log('🔄 Graph-table sync started');
}

// 🚀 Initialize new graphs
function initializeSimpleGraphs() {
    console.log('🚀 Initializing simple graphs...');
    
    // Wait for table to load, then create graphs
    setTimeout(() => {
        updateSimpleGraphs();
        startGraphTableSync();
        
        // Expose manual update function
        window.updateGraphs = updateSimpleGraphs;
        window.refreshGraphs = updateSimpleGraphs;
        
        console.log('🎉 NEW SIMPLE GRAPHS INITIALIZED!');
        console.log('📝 Manual update: updateGraphs() or refreshGraphs()');
        console.log('🔄 Auto-updates every 2 seconds from table data');
        
    }, 2000);
}

// Start the new graph system
initializeSimpleGraphs();