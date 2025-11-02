// DIRECT RUNS FIX - Force table to use database total_runs
// Copy and paste this ENTIRE code in browser console

console.log('🔧 DIRECT RUNS FIX - Forcing database values...');

// Step 1: Override the table update function completely
window.updateCustomerGrid = function() {
    console.log('📊 OVERRIDDEN updateCustomerGrid - using DATABASE values only');
    
    const tableBody = document.getElementById('customer-table-body');
    if (!tableBody || !window.dashboardData || !window.dashboardData.customers) {
        console.log('❌ Missing table or data');
        return;
    }
    
    const customers = window.dashboardData.customers;
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
            networkName: customer.network_name || customer.Network || 'Default Network'
        });
        
        // CRITICAL: Use DATABASE total_runs field ONLY
        const dbRuns = customer.total_runs || 0;
        customerGroups[customerName].totalRuns += dbRuns;
    });
    
    // Create table rows
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
                <div class="customer-name-main">💾 ${group.name}💾 Live DB</div>
                <div style="font-size: 0.6rem; color: #6b7280;">
                    ${group.networks.length} network${group.networks.length > 1 ? 's' : ''}
                </div>
            </div>
        `;
        summaryRow.appendChild(nameCell);
        
        // Network names cell
        const networksCell = document.createElement('td');
        networksCell.innerHTML = `
            <div style="font-size: 0.7rem; color: #374151;">
                ${group.networks.map(n => n.networkName).join('<br>')}
            </div>
        `;
        summaryRow.appendChild(networksCell);
        
        // Info columns (Country, Node Qty, NE Type, gTAC)
        ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
            const cell = document.createElement('td');
            const firstNetwork = group.networks[0].data;
            cell.textContent = firstNetwork[field] || '-';
            summaryRow.appendChild(cell);
        });
        
        // Monthly columns - show combined monthly data
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
        
        // CRITICAL: Total runs cell - USE DATABASE VALUE ONLY
        const totalCell = document.createElement('td');
        totalCell.innerHTML = `
            <div style="font-weight: 700; color: #059669; font-size: 0.9rem;">
                ${group.totalRuns}
            </div>
        `;
        totalCell.title = `${group.name}: ${group.totalRuns} total runs FROM DATABASE`;
        summaryRow.appendChild(totalCell);
        
        tableBody.appendChild(summaryRow);
        
        console.log(`📊 ${group.name}: ${group.totalRuns} runs (DATABASE VALUE)`);
        
        // Add individual network rows
        group.networks.forEach(network => {
            const networkRow = document.createElement('tr');
            networkRow.className = 'network-detail-row';
            networkRow.style.cssText = `
                background: rgba(248, 250, 252, 0.5);
                font-size: 0.65rem;
            `;
            
            // Network name cell
            const networkNameCell = document.createElement('td');
            networkNameCell.innerHTML = `
                <div style="padding-left: 20px; font-size: 0.65rem;">
                    └─ ${network.data.name}<br/>
                    <span style="color: #9ca3af;">${network.networkName}</span>
                </div>
            `;
            networkRow.appendChild(networkNameCell);
            
            // Network details
            const networkDetailsCell = document.createElement('td');
            networkDetailsCell.innerHTML = `
                <div style="font-size: 0.65rem;">
                    ${network.networkName}
                </div>
            `;
            networkRow.appendChild(networkDetailsCell);
            
            // Network info cells
            ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
                const cell = document.createElement('td');
                cell.textContent = network.data[field] || '';
                cell.style.fontSize = '0.65rem';
                networkRow.appendChild(cell);
            });
            
            // Network monthly data
            months.forEach((month, monthIndex) => {
                const cell = document.createElement('td');
                cell.className = 'month-col';
                cell.style.fontSize = '0.6rem';
                
                const monthKey = `2025-${(monthIndex + 1).toString().padStart(2, '0')}`;
                let monthData = '-';
                
                if (network.data.monthly_runs && network.data.monthly_runs[monthKey]) {
                    const value = network.data.monthly_runs[monthKey];
                    if (value && value !== '-' && value !== 'Not Started' && value !== 'No Report') {
                        try {
                            const date = new Date(value);
                            monthData = `${date.getDate().toString().padStart(2, '0')}-${month}`;
                            cell.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
                            cell.style.color = '#1e40af';
                        } catch (e) {
                            monthData = value;
                        }
                    } else if (value) {
                        monthData = value;
                        cell.style.color = '#9ca3af';
                    }
                }
                
                cell.textContent = monthData;
                networkRow.appendChild(cell);
            });
            
            // CRITICAL: Network database total runs
            const networkTotalCell = document.createElement('td');
            const networkDbRuns = network.data.total_runs || 0;
            networkTotalCell.innerHTML = `
                <div style="font-weight: 700; color: #059669; font-size: 0.65rem;">
                    ${networkDbRuns} runs
                </div>
            `;
            networkTotalCell.title = `DATABASE: ${networkDbRuns} runs`;
            networkRow.appendChild(networkTotalCell);
            
            tableBody.appendChild(networkRow);
        });
    });
    
    console.log('✅ Table updated with DATABASE total_runs values ONLY');
};

// Step 2: Force refresh with database values
fetch('/api/customer-dashboard/customers/')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('📊 Got fresh database data...');
            
            // Store data
            window.dashboardData = data;
            
            // Force all customers to use database total_runs
            Object.values(data.customers).forEach(customer => {
                customer.runs = customer.total_runs || 0;
                customer.run_count = customer.total_runs || 0;
                
                console.log(`${customer.name}: FORCED to ${customer.total_runs} runs`);
            });
            
            // Update table with overridden function
            updateCustomerGrid();
            
            // Update statistics
            if (window.updateStatistics) {
                updateStatistics();
            }
            
            console.log('🎉 COMPLETE! Check table now:');
            console.log('  OPT_NC should show: 19 runs');
            console.log('  BSNL East DWDM should show: 6 runs');
            console.log('  All others: Database session counts');
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
    });

console.log('🎯 DIRECT FIX APPLIED - Table now uses DATABASE values only!');