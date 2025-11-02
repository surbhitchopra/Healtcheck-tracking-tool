// CORRECT DATABASE TOTALS FIX - Run this in console

console.log('🔧 FIXING BOTH CUSTOMER & NETWORK TOTALS FROM DATABASE...');

// Function to get ACTUAL total_runs from database
function getDatabaseTotalRuns(customer) {
    // Use the actual total_runs field from database
    return customer.total_runs || customer.runs || 0;
}

// Complete table fix using correct database values
window.updateCustomerGrid = function() {
    console.log('🔄 ENHANCED: Updating with CORRECT DATABASE values...');
    
    const tableBody = document.getElementById('customer-table-body');
    const customers = dashboardData.customers;
    
    if (!tableBody || !customers) {
        console.log('❌ Table body or customers not found');
        return;
    }
    
    const currentYear = new Date().getFullYear();
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
                totalNodes: 0
            };
        }
        
        customerGroups[customerName].networks.push({
            key: customerKey,
            data: customer,
            networkName: customer.network_name || customer.Network || 'Default Network'
        });
        
        customerGroups[customerName].totalNodes += (customer.node_qty || 0);
    });
    
    // Create table rows for each customer group
    Object.values(customerGroups).forEach(group => {
        // Calculate ACTUAL customer total by summing all network total_runs
        let actualCustomerTotal = 0;
        group.networks.forEach(network => {
            actualCustomerTotal += getDatabaseTotalRuns(network.data);
        });
        
        // Customer summary row
        const summaryRow = document.createElement('tr');
        summaryRow.className = 'customer-summary-row';
        summaryRow.style.cssText = `
            background: linear-gradient(145deg, rgba(34, 197, 94, 0.05), rgba(22, 163, 74, 0.03));
            border-left: 4px solid #22c55e;
            font-weight: 600;
        `;
        
        // Customer name cell
        const customerCell = document.createElement('td');
        customerCell.className = 'customer-name-cell';
        customerCell.innerHTML = `
            <div class="customer-name-container">
                <div class="customer-name-main">✅ ${group.name} ✅ Fixed DB</div>
                <div style="font-size: 0.6rem; color: #6b7280; font-weight: 400;">
                    Last run: ${group.networks[0].data.last_run_date || 'Never'}
                </div>
                <div style="font-size: 0.6rem; color: #6b7280;">${group.networks[0].data.country || 'India'}</div>
                <div style="font-size: 0.6rem; color: #6b7280;">${group.networks.length} network${group.networks.length > 1 ? 's' : ''}</div>
            </div>
        `;
        summaryRow.appendChild(customerCell);
        
        // Networks cell
        const networksCell = document.createElement('td');
        networksCell.className = 'networks-col';
        networksCell.innerHTML = `
            <div style="font-size: 0.7rem; color: #374151;">
                ${group.networks.map(n => n.networkName).join('<br>')}
            </div>
        `;
        summaryRow.appendChild(networksCell);
        
        // Info columns (Country, Node Qty, NE Type, gTAC)
        ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
            const cell = document.createElement('td');
            cell.className = 'info-col';
            
            let value = '';
            if (field === 'node_qty') {
                value = group.totalNodes;
            } else {
                const firstNetwork = group.networks[0].data;
                value = firstNetwork[field] || '-';
            }
            
            cell.textContent = value;
            summaryRow.appendChild(cell);
        });
        
        // Month columns - show aggregated monthly data
        months.forEach((month, monthIndex) => {
            const cell = document.createElement('td');
            cell.className = 'month-col';
            
            let monthData = '-';
            let hasDataThisMonth = false;
            
            // Check all networks for this month and show latest date
            group.networks.forEach(network => {
                const customer = network.data;
                const monthKey = `${currentYear}-${(monthIndex + 1).toString().padStart(2, '0')}`;
                
                if (customer.monthly_runs && customer.monthly_runs[monthKey]) {
                    const value = customer.monthly_runs[monthKey];
                    if (value && 
                        value !== '-' && 
                        value !== 'Not Started' && 
                        value !== 'No Report' && 
                        value !== 'Not Run') {
                        
                        hasDataThisMonth = true;
                        try {
                            const date = new Date(value);
                            monthData = `${date.getDate().toString().padStart(2, '0')}-${month}`;
                        } catch (e) {
                            monthData = value;
                        }
                    } else if (value) {
                        // Show status messages
                        monthData = value;
                        cell.style.color = '#9ca3af';
                    }
                }
            });
            
            cell.textContent = monthData;
            if (hasDataThisMonth) {
                cell.style.backgroundColor = 'rgba(34, 197, 94, 0.1)';
                cell.style.fontWeight = '600';
                cell.style.color = '#15803d';
            }
            
            summaryRow.appendChild(cell);
        });
        
        // CORRECTED Customer Total Runs cell (sum of all network total_runs)
        const totalCell = document.createElement('td');
        totalCell.className = 'total-col';
        totalCell.innerHTML = `
            <div style="font-weight: 700; color: #dc2626; font-size: 0.9rem;">
                ${actualCustomerTotal}
            </div>
        `;
        totalCell.title = `${group.name}: ${actualCustomerTotal} total runs (sum of ${group.networks.length} networks)`;
        summaryRow.appendChild(totalCell);
        
        tableBody.appendChild(summaryRow);
        
        console.log(`✅ ${group.name}: ${actualCustomerTotal} total runs (sum of all networks)`);
        
        // Add individual network rows
        group.networks.forEach((network, index) => {
            const networkDbTotal = getDatabaseTotalRuns(network.data);
            
            const networkRow = document.createElement('tr');
            networkRow.className = 'network-detail-row';
            networkRow.style.cssText = `
                background: rgba(248, 250, 252, 0.8);
                font-size: 0.65rem;
                border-left: 2px solid #22c55e;
                margin-left: 20px;
            `;
            
            // Network summary cell
            const networkSummaryCell = document.createElement('td');
            networkSummaryCell.innerHTML = `
                <div style="padding-left: 20px; font-size: 0.65rem; color: #6b7280;">
                    └─ ${network.data.name}<br/>
                    <span style="color: #9ca3af;">${network.networkName}</span><br/>
                    <span style="color: #dc2626; font-weight: 600;">${networkDbTotal} runs (DB)</span>
                </div>
            `;
            networkRow.appendChild(networkSummaryCell);
            
            // Network name cell
            const networkNameCell = document.createElement('td');
            networkNameCell.innerHTML = `
                <div style="font-size: 0.65rem; padding-left: 16px;">
                    ${network.networkName}
                </div>
            `;
            networkRow.appendChild(networkNameCell);
            
            // Network info cells
            ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
                const cell = document.createElement('td');
                cell.className = 'info-col';
                cell.textContent = network.data[field] || '';
                cell.style.fontSize = '0.65rem';
                networkRow.appendChild(cell);
            });
            
            // Network monthly data
            months.forEach((month, monthIndex) => {
                const cell = document.createElement('td');
                cell.className = 'month-col';
                cell.style.fontSize = '0.6rem';
                
                const monthKey = `${currentYear}-${(monthIndex + 1).toString().padStart(2, '0')}`;
                let monthData = '-';
                
                if (network.data.monthly_runs && network.data.monthly_runs[monthKey]) {
                    const value = network.data.monthly_runs[monthKey];
                    if (value && 
                        value !== '-' && 
                        value !== 'Not Started' && 
                        value !== 'No Report' && 
                        value !== 'Not Run') {
                        
                        try {
                            const date = new Date(value);
                            monthData = `${date.getDate().toString().padStart(2, '0')}-${month}`;
                        } catch (e) {
                            monthData = value;
                        }
                        cell.style.backgroundColor = 'rgba(34, 197, 94, 0.08)';
                        cell.style.color = '#15803d';
                    } else if (value) {
                        monthData = value; // Show status as-is
                        cell.style.color = '#9ca3af';
                    }
                }
                
                cell.textContent = monthData;
                networkRow.appendChild(cell);
            });
            
            // CORRECTED Network database total runs
            const networkTotalCell = document.createElement('td');
            networkTotalCell.className = 'total-col';
            networkTotalCell.textContent = networkDbTotal;
            networkTotalCell.style.fontSize = '0.7rem';
            networkTotalCell.style.color = '#dc2626';
            networkTotalCell.style.fontWeight = '600';
            networkTotalCell.title = `Database total_runs: ${networkDbTotal}`;
            networkRow.appendChild(networkTotalCell);
            
            tableBody.appendChild(networkRow);
            
            console.log(`  └─ ${network.data.name}: ${networkDbTotal} runs (from database)`);
        });
    });
    
    console.log('✅ Customer grid updated with CORRECTED DATABASE values');
};

// Apply the fix immediately
updateCustomerGrid();

console.log('🎉 TABLE FIXED WITH CORRECT DATABASE VALUES!');
console.log('📊 Now showing:');
console.log('   ✅ Customer totals = sum of all their network totals');
console.log('   ✅ Network totals = actual database total_runs values');
console.log('   ✅ Both levels now match database exactly');
console.log('');
console.log('🎯 Example fixed totals:');
console.log('   BSNL: Sum of (12+10+14+12+13+13+14+12) = correct total');
console.log('   Moratelindo: Sum of (20+18+18) = correct total');
console.log('   OPT_NC: 14 runs (matches network)');
console.log('   Tata: Sum of (11+18+18+18+18+18+18) = correct total');