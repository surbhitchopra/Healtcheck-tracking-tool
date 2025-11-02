// 🚨 COMPLETE FIX FOR EDIT CONTAMINATION
// This replaces all edit functions with 100% isolated versions

console.log('🔒 Loading ISOLATED EDIT SYSTEM...');

// 🔒 COMPLETELY ISOLATED SAVE FUNCTION
window.saveCustomerEditIsolated = function(customerName) {
    console.log(`🎯 ISOLATED EDIT: ${customerName}`);
    
    // Find ONLY target customer
    const targetCustomerKey = Object.keys(dashboardData.customers).find(key => 
        dashboardData.customers[key].name === customerName
    );
    
    if (!targetCustomerKey) {
        console.error(`❌ Customer ${customerName} not found`);
        return;
    }
    
    console.log(`🔍 Target customer key: ${targetCustomerKey}`);
    
    // Create COMPLETELY ISOLATED copy
    const originalCustomer = dashboardData.customers[targetCustomerKey];
    const isolatedCustomer = JSON.parse(JSON.stringify(originalCustomer));
    
    // Update ONLY isolated customer's networks
    if (isolatedCustomer.networks && isolatedCustomer.networks.length > 0) {
        const customerSafeId = customerName.replace(/[^a-zA-Z0-9_-]/g, '_');
        
        isolatedCustomer.networks.forEach((network, networkIndex) => {
            const updatedMonths = [];
            
            // Collect form data
            for (let monthIndex = 0; monthIndex < 12; monthIndex++) {
                const inputId = `${customerSafeId}_network_${networkIndex}_month_${monthIndex}`;
                const input = document.getElementById(inputId);
                
                if (input) {
                    updatedMonths[monthIndex] = input.value || '-';
                } else {
                    updatedMonths[monthIndex] = network.months && network.months[monthIndex] ? 
                                               network.months[monthIndex] : '-';
                }
            }
            
            // Update ONLY this network
            network.months = updatedMonths;
            network.monthly_runs = updatedMonths;
            network.editedData = true;
            
            console.log(`📝 Updated network: ${network.name} for ${customerName}`);
        });
    }
    
    // CRITICAL: Replace ONLY target customer, leave others untouched
    const cleanDashboardData = {};
    
    // Copy all customers EXCEPT target
    Object.keys(dashboardData.customers).forEach(key => {
        if (key !== targetCustomerKey) {
            cleanDashboardData[key] = dashboardData.customers[key]; // Keep original reference
        }
    });
    
    // Add ONLY edited customer
    cleanDashboardData[targetCustomerKey] = isolatedCustomer;
    
    // Replace dashboard data
    dashboardData.customers = cleanDashboardData;
    
    // Store in localStorage (ONLY for this customer)
    try {
        localStorage.removeItem(`edited_${customerName}`); // Clear old data
        
        const storageData = {
            customerName: customerName,
            customerKey: targetCustomerKey,
            networks: isolatedCustomer.networks,
            timestamp: Date.now()
        };
        
        localStorage.setItem(`edited_${customerName}`, JSON.stringify(storageData));
        console.log(`💾 Stored isolated edit for: ${customerName}`);
    } catch (e) {
        console.warn('⚠️ localStorage save failed:', e);
    }
    
    // Success notification
    showNotification(`✅ ${customerName} updated successfully! Others unchanged.`, 'success');
    closeEditModal();
    
    // Update ONLY target customer display
    setTimeout(() => {
        updateOnlyTargetCustomer(customerName);
        
        // Update graphs
        if (window.updateAllSimpleGraphs) {
            window.updateAllSimpleGraphs();
        }
    }, 200);
    
    console.log(`✅ ISOLATED EDIT COMPLETE: Only ${customerName} modified`);
};

// 🎯 UPDATE ONLY TARGET CUSTOMER
function updateOnlyTargetCustomer(targetName) {
    console.log(`🎯 Updating display for ONLY: ${targetName}`);
    
    const tableBody = document.getElementById('customer-table-body');
    if (!tableBody) return;
    
    // Find and remove ONLY target customer rows
    const allRows = Array.from(tableBody.querySelectorAll('tr'));
    const targetRows = [];
    
    allRows.forEach(row => {
        const nameCell = row.querySelector('.customer-name-cell');
        if (nameCell && nameCell.textContent.includes(targetName)) {
            targetRows.push(row);
        }
    });
    
    console.log(`🔍 Found ${targetRows.length} rows for ${targetName}`);
    
    // Remove target rows
    targetRows.forEach(row => row.remove());
    
    // Find target customer data
    const targetCustomerKey = Object.keys(dashboardData.customers).find(key => 
        dashboardData.customers[key].name === targetName
    );
    
    if (!targetCustomerKey) return;
    
    const targetCustomer = dashboardData.customers[targetCustomerKey];
    const currentYear = new Date().getFullYear();
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Create new rows for target customer
    const customerRow = createCustomerSummaryRow(targetCustomer, currentYear, months);
    tableBody.appendChild(customerRow);
    
    // Add network rows
    if (targetCustomer.networks && targetCustomer.networks.length > 0) {
        targetCustomer.networks.forEach((network, index) => {
            const networkRow = createNetworkDetailRow(targetCustomer, network, index, currentYear, months);
            tableBody.appendChild(networkRow);
        });
    }
    
    console.log(`✅ Display updated for ONLY: ${targetName}`);
}

// 🔄 OVERRIDE ORIGINAL SAVE FUNCTION
window.saveCustomerEdit = window.saveCustomerEditIsolated;

console.log('✅ ISOLATED EDIT SYSTEM LOADED!');
console.log('🔒 Now only edited customers will change, others stay untouched!');