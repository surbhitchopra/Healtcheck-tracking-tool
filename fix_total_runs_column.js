// FIX TOTAL RUNS COLUMN IN TABLE - Run this in console

console.log('🔧 FIXING TOTAL RUNS COLUMN IN TABLE...');

// Function to calculate correct total runs for a customer from monthly_runs
function calculateCorrectTotalRuns(customer) {
    let totalRuns = 0;
    
    if (customer.monthly_runs && typeof customer.monthly_runs === 'object') {
        // Count valid monthly entries
        Object.entries(customer.monthly_runs).forEach(([monthKey, monthValue]) => {
            if (monthValue && 
                monthValue !== '-' && 
                monthValue !== 'Not Started' && 
                monthValue !== 'No Report' && 
                monthValue !== 'Not Run') {
                totalRuns++;
            }
        });
    }
    
    return totalRuns;
}

// Override the customer table creation functions
console.log('📊 Overriding table creation functions...');

// Fix the network runs calculation
window.getNetworkRuns = function(customer, networkName) {
    // For database customers, use the actual total_runs from database
    if (customer.total_runs !== undefined) {
        return customer.total_runs || 0;
    }
    
    // For other cases, calculate from monthly_runs
    return calculateCorrectTotalRuns(customer);
};

// Override the table row creation to show correct totals
const originalUpdateCustomerGrid = window.updateCustomerGrid;

window.updateCustomerGrid = function() {
    console.log('🔄 ENHANCED: Updating customer grid with CORRECT total runs...');
    
    const tableBody = document.getElementById('customer-table-body');
    const customers = dashboardData.customers;
    
    if (!tableBody || !customers) {
        console.log('❌ Table body or customers not found');
        return;
    }
    
    const currentYear = new Date().getFullYear();
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    tableBody.innerHTML = '';
    
    // Group customers by name to show properly
    const customerGroups = {};
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = {
                name: customerName,
                networks: [],
                totalRuns: 0,
                totalNodes: 0
            };
        }
        
        customerGroups[customerName].networks.push({
            key: customerKey,
            data: customer,
            networkName: customer.network_name || customer.Network || 'Default Network'
        });
        
        // Calculate CORRECT total runs from monthly_runs data
        const correctRuns = calculateCorrectTotalRuns(customer);
        customerGroups[customerName].totalRuns += correctRuns;
        customerGroups[customerName].totalNodes += (customer.node_qty || 0);
    });
    
    // Create table rows for each customer group
    Object.values(customerGroups).forEach(group => {
        // Customer summary row
        const summaryRow = document.createElement('tr');
        summaryRow.className = 'customer-summary-row';
        summaryRow.style.cssText = `
            background: linear-gradient(145deg, rgba(59, 130, 246, 0.03), rgba(96, 165, 250, 0.02));
            border-left: 4px solid #3b82f6;
            font-weight: 600;
        `;
        
        // Create customer name cell
        const customerCell = document.createElement('td');
        customerCell.className = 'customer-name-cell';
        customerCell.innerHTML = `
            <div class="customer-name-container">
                <div class="customer-name-main">${group.name}</div>
                <div style="font-size: 0.6rem; color: #6b7280; font-weight: 400;">${group.networks.length} networks</div>
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
        
        // Info columns
        ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
            const cell = document.createElement('td');
            cell.className = 'info-col';
            
            let value = '';
            if (field === 'node_qty') {
                value = group.totalNodes;
            } else {
                // Use first network's value as representative
                const firstNetwork = group.networks[0].data;
                value = firstNetwork[field] || firstNetwork[field.replace('_', ' ')] || '-';
            }
            
            cell.textContent = value;
            summaryRow.appendChild(cell);
        });
        
        // Month columns - show aggregated data
        months.forEach((month, monthIndex) => {
            const cell = document.createElement('td');
            cell.className = 'month-col';
            
            let monthData = '-';
            let hasDataThisMonth = false;
            
            // Check all networks for this month
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
                        // Format date for display
                        try {
                            const date = new Date(value);
                            monthData = `${date.getDate()}-${month}`;
                        } catch (e) {
                            monthData = value;
                        }
                    }
                }
            });
            
            cell.textContent = monthData;
            if (hasDataThisMonth) {
                cell.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                cell.style.fontWeight = '600';
            }
            
            summaryRow.appendChild(cell);
        });
        
        // CORRECTED Total Runs cell
        const totalCell = document.createElement('td');
        totalCell.className = 'total-col';
        totalCell.innerHTML = `
            <div style="font-weight: 700; color: #059669; font-size: 0.8rem;">
                ${group.totalRuns}
            </div>
        `;
        totalCell.title = `${group.name}: ${group.totalRuns} total runs from monthly data`;
        summaryRow.appendChild(totalCell);
        
        tableBody.appendChild(summaryRow);
        
        console.log(`✅ ${group.name}: Showing ${group.totalRuns} total runs (calculated from monthly_runs)`);
        
        // Add individual network rows
        group.networks.forEach((network, index) => {
            const networkRow = document.createElement('tr');
            networkRow.className = 'network-detail-row';
            networkRow.style.cssText = `
                background: rgba(248, 250, 252, 0.5);
                font-size: 0.65rem;
                border-left: 2px solid #e5e7eb;
            `;
            
            // Empty customer cell for network rows
            networkRow.appendChild(document.createElement('td'));
            
            // Network name
            const networkCell = document.createElement('td');
            networkCell.textContent = network.networkName;
            networkCell.style.paddingLeft = '16px';
            networkRow.appendChild(networkCell);
            
            // Network info
            ['country', 'node_qty', 'ne_type', 'gtac'].forEach(field => {
                const cell = document.createElement('td');
                cell.className = 'info-col';
                cell.textContent = network.data[field] || '-';
                networkRow.appendChild(cell);
            });
            
            // Network monthly data
            months.forEach((month, monthIndex) => {
                const cell = document.createElement('td');
                cell.className = 'month-col';
                
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
                            monthData = `${date.getDate()}-${month}`;
                        } catch (e) {
                            monthData = value;
                        }
                        cell.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
                    } else {
                        monthData = value; // Show status as-is
                        cell.style.color = '#9ca3af';
                    }
                }
                
                cell.textContent = monthData;
                networkRow.appendChild(cell);
            });
            
            // Network total runs
            const networkTotalCell = document.createElement('td');
            networkTotalCell.className = 'total-col';
            const networkTotalRuns = calculateCorrectTotalRuns(network.data);
            networkTotalCell.textContent = networkTotalRuns;
            networkTotalCell.style.fontSize = '0.65rem';
            networkRow.appendChild(networkTotalCell);
            
            tableBody.appendChild(networkRow);
        });
    });
    
    console.log('✅ Customer grid updated with CORRECTED total runs');
};

// Apply the fix immediately
updateCustomerGrid();

console.log('🎉 TOTAL RUNS COLUMN FIXED!');
console.log('📊 Total Runs column now shows correct values calculated from monthly_runs data');
console.log('✅ Each customer total = count of valid monthly entries (dates, not status messages)');