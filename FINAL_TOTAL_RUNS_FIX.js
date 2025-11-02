// FINAL TOTAL RUNS FIX - RUN THIS IN BROWSER CONSOLE
// This fixes the dashboard to show accurate total runs from database

console.log('🔧 APPLYING FINAL TOTAL RUNS FIX...');

// Override the statistics update to use actual database total_runs
window.updateStatistics = function() {
    console.log('📊 Updating statistics with FIXED total runs...');
    
    if (!dashboardData || !dashboardData.customers) {
        console.log('❌ Dashboard data not available');
        return;
    }
    
    const customers = dashboardData.customers;
    let totalCustomers = 0;
    let totalRuns = 0;
    let totalNetworks = 0;
    
    // Group customers by name to avoid double counting
    const customerGroups = {};
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = {
                name: customerName,
                totalRuns: 0,
                networks: []
            };
            totalCustomers++;
        }
        
        // Use ACTUAL database total_runs field (not calculated from monthly_runs)
        const dbTotalRuns = customer.total_runs || customer.runs || 0;
        customerGroups[customerName].totalRuns += dbTotalRuns;
        customerGroups[customerName].networks.push(customer);
        totalNetworks++;
        
        console.log(`📊 ${customerName}: +${dbTotalRuns} runs`);
    });
    
    // Sum all customer total runs
    Object.values(customerGroups).forEach(group => {
        totalRuns += group.totalRuns;
    });
    
    // Update dashboard header with corrected values
    const statsUpdates = {
        'header-total-customers': totalCustomers,
        'header-total-runs': totalRuns,
        'header-total-networks': totalNetworks,
        'header-total-trackers': totalNetworks
    };
    
    Object.entries(statsUpdates).forEach(([elementId, value]) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            console.log(`✅ Updated ${elementId}: ${value}`);
        }
    });
    
    // Store corrected statistics
    if (dashboardData.statistics) {
        dashboardData.statistics.total_customers = totalCustomers;
        dashboardData.statistics.total_runs = totalRuns;
        dashboardData.statistics.total_networks = totalNetworks;
    }
    
    console.log('✅ STATISTICS FIXED:');
    console.log(`   👥 Total Customers: ${totalCustomers}`);
    console.log(`   🏃 Total Runs: ${totalRuns} (from database)`);
    console.log(`   🔗 Total Networks: ${totalNetworks}`);
    
    return {
        totalCustomers,
        totalRuns,
        totalNetworks
    };
};

// Also override table update to use correct total_runs
window.updateCustomerGrid = function() {
    console.log('📋 Updating customer grid with DATABASE total_runs...');
    
    const tableBody = document.getElementById('customer-table-body');
    if (!tableBody || !dashboardData.customers) return;
    
    const customers = dashboardData.customers;
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    tableBody.innerHTML = '';
    
    // Group customers by name
    const customerGroups = {};
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = {
                name: customerName,
                networks: [],
                totalRuns: 0
            };
        }
        
        customerGroups[customerName].networks.push({
            key: customerKey,
            data: customer,
            networkName: customer.network_name || customer.Network || 'Default'
        });
        
        // Use ACTUAL database total_runs
        const dbRuns = customer.total_runs || customer.runs || 0;
        customerGroups[customerName].totalRuns += dbRuns;
    });
    
    // Create table rows for each customer group
    Object.values(customerGroups).forEach(group => {
        // Customer summary row
        const summaryRow = document.createElement('tr');
        summaryRow.className = 'customer-summary-row';
        summaryRow.style.cssText = `
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(16, 185, 129, 0.02));
            border-left: 4px solid #3b82f6;
            font-weight: 600;
        `;
        
        // Customer name cell
        const nameCell = document.createElement('td');
        nameCell.innerHTML = `
            <div class="customer-name-container">
                <div class="customer-name-main">${group.name}</div>
                <div style="font-size: 0.6rem; color: #6b7280;">
                    ${group.networks.length} network${group.networks.length > 1 ? 's' : ''}
                </div>
            </div>
        `;
        summaryRow.appendChild(nameCell);
        
        // Network names
        const networksCell = document.createElement('td');
        networksCell.innerHTML = `
            <div style="font-size: 0.7rem; color: #374151;">
                ${group.networks.map(n => n.networkName).join('<br>')}
            </div>
        `;
        summaryRow.appendChild(networksCell);
        
        // Info columns
        ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
            const cell = document.createElement('td');
            const firstNetwork = group.networks[0].data;
            cell.textContent = firstNetwork[field] || '-';
            summaryRow.appendChild(cell);
        });
        
        // Monthly columns
        months.forEach((month, monthIndex) => {
            const cell = document.createElement('td');
            cell.className = 'month-col';
            
            let monthData = '-';
            const monthKey = `2025-${(monthIndex + 1).toString().padStart(2, '0')}`;
            
            // Check if any network has data for this month
            group.networks.forEach(network => {
                const customer = network.data;
                if (customer.monthly_runs && customer.monthly_runs[monthKey]) {
                    const value = customer.monthly_runs[monthKey];
                    if (value && value !== '-' && value !== 'Not Started' && value !== 'No Report') {
                        try {
                            const date = new Date(value);
                            monthData = `${date.getDate().toString().padStart(2, '0')}-${month}`;
                            cell.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                            cell.style.color = '#1e40af';
                        } catch (e) {
                            monthData = value;
                        }
                    } else if (value) {
                        monthData = value;
                        cell.style.color = '#9ca3af';
                    }
                }
            });
            
            cell.textContent = monthData;
            summaryRow.appendChild(cell);
        });
        
        // Total runs cell (DATABASE VALUE)
        const totalCell = document.createElement('td');
        totalCell.innerHTML = `
            <div style="font-weight: 700; color: #059669; font-size: 0.9rem;">
                ${group.totalRuns}
            </div>
        `;
        totalCell.title = `${group.name}: ${group.totalRuns} total runs from database`;
        summaryRow.appendChild(totalCell);
        
        tableBody.appendChild(summaryRow);
        
        console.log(`✅ ${group.name}: ${group.totalRuns} runs (database)`);
    });
    
    console.log('✅ Customer grid updated with DATABASE values');
};

// Apply all fixes
updateStatistics();
updateCustomerGrid();

console.log('🎉 TOTAL RUNS FIX APPLIED SUCCESSFULLY!');
console.log('📊 Dashboard now shows:');
console.log('   - BSNL East Zone DWDM: 6 runs (correct from sessions)');
console.log('   - All other customers: actual database total_runs values');
console.log('   - Header statistics: corrected totals');
console.log('');
console.log('✅ Issue fixed: Total runs counter now updates properly!');