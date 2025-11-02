// TABLE TOTAL RUNS REAL-TIME UPDATE FIX
// This ensures table total runs column updates when health check completes

console.log('🔧 Loading table total runs real-time update fix...');

// Function to update total runs in table after health check completion
function updateTableTotalRuns(customerName, networkName) {
    console.log(`🔄 Updating table total runs for ${customerName} - ${networkName}`);
    
    // Force refresh data from database
    fetch('/api/customer-dashboard/customers/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.customers) {
                console.log('📊 Got fresh database data, updating table...');
                
                // Find the customer in the data
                const customerKey = Object.keys(data.customers).find(key => {
                    const customer = data.customers[key];
                    return customer.name === customerName && 
                           (customer.network_name === networkName || customer.Network === networkName);
                });
                
                if (customerKey) {
                    const customer = data.customers[customerKey];
                    const newTotalRuns = customer.total_runs || 0;
                    
                    console.log(`📊 ${customerName} - ${networkName}: ${newTotalRuns} runs (from database)`);
                    
                    // Update the dashboard data
                    if (window.dashboardData && window.dashboardData.customers) {
                        if (window.dashboardData.customers[customerKey]) {
                            // Update all run-related fields
                            window.dashboardData.customers[customerKey].total_runs = newTotalRuns;
                            window.dashboardData.customers[customerKey].runs = newTotalRuns;
                            window.dashboardData.customers[customerKey].run_count = newTotalRuns;
                            
                            // Also update networks array if exists
                            if (window.dashboardData.customers[customerKey].networks) {
                                window.dashboardData.customers[customerKey].networks.forEach(network => {
                                    if (network.network_name === networkName || network.name === networkName) {
                                        network.total_runs = newTotalRuns;
                                        network.runs = newTotalRuns;
                                        network.run_count = newTotalRuns;
                                    }
                                });
                            }
                        }
                    }
                    
                    // Force update table display
                    if (window.updateCustomerGrid) {
                        console.log('📋 Updating customer grid...');
                        updateCustomerGrid();
                    }
                    
                    // Force update statistics
                    if (window.updateStatistics) {
                        console.log('📊 Updating statistics...');
                        updateStatistics();
                    }
                    
                    // Also manually update the specific table cell
                    updateSpecificTableCell(customerName, networkName, newTotalRuns);
                    
                    console.log(`✅ Table updated: ${customerName} now shows ${newTotalRuns} runs`);
                    
                } else {
                    console.log(`❌ Customer ${customerName} - ${networkName} not found in API response`);
                }
            }
        })
        .catch(error => {
            console.error('❌ Error updating table total runs:', error);
        });
}

// Function to manually update specific table cell
function updateSpecificTableCell(customerName, networkName, newTotalRuns) {
    console.log(`🔧 Manually updating table cell for ${customerName} - ${networkName}`);
    
    // Find all table cells that might contain total runs
    const tableCells = document.querySelectorAll('td');
    
    tableCells.forEach(cell => {
        // Check if this cell is in a row for our customer
        const row = cell.closest('tr');
        if (row) {
            const rowText = row.textContent;
            
            // If this row contains our customer and network
            if (rowText.includes(customerName) && (rowText.includes(networkName) || networkName.includes('_'))) {
                // Check if this is likely a total runs cell (last column, numeric)
                const cells = row.querySelectorAll('td');
                const lastCell = cells[cells.length - 1];
                
                // If this is the last cell and contains a number, it's likely total runs
                if (cell === lastCell && /^\d+$/.test(cell.textContent.trim())) {
                    console.log(`🔄 Updating cell from ${cell.textContent} to ${newTotalRuns}`);
                    cell.textContent = newTotalRuns;
                    
                    // Add visual feedback
                    cell.style.background = 'rgba(16, 185, 129, 0.1)';
                    cell.style.color = '#059669';
                    cell.style.fontWeight = '700';
                    
                    setTimeout(() => {
                        cell.style.background = '';
                        cell.style.color = '#059669';
                        cell.style.fontWeight = '700';
                    }, 2000);
                }
            }
        }
    });
}

// Override the original increment function to use our table update
if (typeof window.incrementRunsAfterHealthCheck !== 'undefined') {
    const originalIncrementRuns = window.incrementRunsAfterHealthCheck;
    
    window.incrementRunsAfterHealthCheck = function(customerName, networkName) {
        console.log(`🚀 Enhanced increment runs for ${customerName} - ${networkName}`);
        
        // Call original function first
        if (originalIncrementRuns) {
            originalIncrementRuns(customerName, networkName);
        }
        
        // Then update table with fresh database data
        setTimeout(() => {
            updateTableTotalRuns(customerName, networkName);
        }, 1000);
    };
    
    console.log('✅ Enhanced incrementRunsAfterHealthCheck function');
}

// Also create specific increment functions for common customers
window.incrementOPT_NC = function() {
    console.log('🚀 Incrementing OPT_NC runs');
    updateTableTotalRuns('OPT_NC', 'OPT_NC');
};

window.incrementBSNL_East_DWDM = function() {
    console.log('🚀 Incrementing BSNL East DWDM runs');
    updateTableTotalRuns('BSNL', 'BSNL_East_Zone_DWDM');
};

window.incrementBSNL_North_DWDM = function() {
    console.log('🚀 Incrementing BSNL North DWDM runs');
    updateTableTotalRuns('BSNL', 'BSNL_North_Zone_DWDM');
};

window.incrementBSNL_West_DWDM = function() {
    console.log('🚀 Incrementing BSNL West DWDM runs');
    updateTableTotalRuns('BSNL', 'BSNL_West_Zone_DWDM');
};

window.incrementMoratelindo = function() {
    console.log('🚀 Incrementing Moratelindo PSS24 runs');
    updateTableTotalRuns('Moratelindo', 'Moratelindo_PSS24');
};

// Auto-refresh table every 30 seconds to catch any missed updates
setInterval(() => {
    if (window.dashboardData && window.updateCustomerGrid) {
        console.log('🔄 Auto-refreshing table total runs...');
        
        // Fetch fresh data and update table
        fetch('/api/customer-dashboard/customers/')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.customers) {
                    // Check if any total_runs values have changed
                    let hasChanges = false;
                    
                    Object.entries(data.customers).forEach(([key, customer]) => {
                        if (window.dashboardData.customers[key]) {
                            const oldRuns = window.dashboardData.customers[key].total_runs || 0;
                            const newRuns = customer.total_runs || 0;
                            
                            if (oldRuns !== newRuns) {
                                hasChanges = true;
                                console.log(`📊 ${customer.name}: ${oldRuns} → ${newRuns} runs`);
                                
                                // Update cached data
                                window.dashboardData.customers[key].total_runs = newRuns;
                                window.dashboardData.customers[key].runs = newRuns;
                                window.dashboardData.customers[key].run_count = newRuns;
                            }
                        }
                    });
                    
                    if (hasChanges) {
                        console.log('🔄 Changes detected, refreshing table...');
                        updateCustomerGrid();
                        updateStatistics();
                    }
                }
            })
            .catch(error => {
                console.log('📡 Auto-refresh error (normal):', error);
            });
    }
}, 30000); // Every 30 seconds

console.log('✅ Table total runs real-time update fix loaded!');