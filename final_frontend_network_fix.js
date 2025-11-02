// FINAL FRONTEND FIX - Force individual network dates to display
// Copy and paste this entire script in your browser console

console.log('🔥 FINAL FRONTEND FIX FOR NETWORK DATES STARTING...');

// Step 1: Override the network row rendering function
function fixNetworkDatesDisplay() {
    console.log('🔧 Fixing network dates display...');
    
    // Find all network rows
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`📊 Found ${networkRows.length} network rows to fix`);
    
    let totalFixed = 0;
    
    networkRows.forEach((row, index) => {
        const networkNameElement = row.querySelector('.network-name-main');
        if (!networkNameElement) return;
        
        const networkName = networkNameElement.textContent.replace('└─ ', '').trim();
        console.log(`\n🔧 Processing: ${networkName}`);
        
        // Find the parent customer row
        let customerRow = row.previousElementSibling;
        while (customerRow && !customerRow.classList.contains('customer-summary-row')) {
            customerRow = customerRow.previousElementSibling;
        }
        
        if (!customerRow) {
            console.log(`❌ No customer row found for ${networkName}`);
            return;
        }
        
        // Get customer name from customer row
        const customerNameElement = customerRow.querySelector('.customer-name-main');
        if (!customerNameElement) {
            console.log(`❌ No customer name found for ${networkName}`);
            return;
        }
        
        const customerText = customerNameElement.textContent;
        const customerName = customerText.replace(/[📋📄💾🔄]/g, '').trim().split('\n')[0];
        
        console.log(`📋 Customer: ${customerName}`);
        
        // Find customer data in global dashboardData
        if (window.dashboardData && window.dashboardData.customers) {
            let customerData = null;
            
            // Find the customer data
            for (const [key, customer] of Object.entries(window.dashboardData.customers)) {
                if (customer.name && customer.name.toLowerCase().includes(customerName.toLowerCase())) {
                    customerData = customer;
                    break;
                }
            }
            
            if (!customerData) {
                console.log(`❌ Customer data not found for ${customerName}`);
                return;
            }
            
            console.log(`✅ Found customer data with ${customerData.networks ? customerData.networks.length : 0} networks`);
            
            // Find the specific network in customer.networks
            let targetNetwork = null;
            if (customerData.networks) {
                targetNetwork = customerData.networks.find(net => {
                    const netName = net.network_name || net.name || '';
                    return netName === networkName || 
                           netName.includes(networkName) || 
                           networkName.includes(netName);
                });
            }
            
            if (!targetNetwork) {
                console.log(`❌ Network data not found for ${networkName}`);
                return;
            }
            
            console.log(`🎯 Found network data:`, {
                name: targetNetwork.network_name,
                runs: targetNetwork.runs || targetNetwork.total_runs,
                months: targetNetwork.months
            });
            
            // Get month cells (columns 6-17 are typically the month columns)
            const monthCells = Array.from(row.querySelectorAll('td')).slice(6, 18);
            if (monthCells.length < 12) {
                console.log(`❌ Expected 12 month cells, found ${monthCells.length}`);
                return;
            }
            
            // Update month cells with network's individual dates
            let cellsUpdated = 0;
            if (targetNetwork.months && Array.isArray(targetNetwork.months)) {
                targetNetwork.months.forEach((monthValue, monthIndex) => {
                    if (monthIndex < monthCells.length) {
                        const cell = monthCells[monthIndex];
                        const oldValue = cell.textContent.trim();
                        
                        if (monthValue && monthValue !== '-') {
                            // Update cell with new value
                            cell.textContent = monthValue;
                            
                            // Style the cell based on content
                            if (monthValue === 'Not Started' || monthValue === 'No Report' || monthValue === 'Not Run') {
                                cell.style.color = '#9ca3af';
                                cell.style.fontStyle = 'italic';
                                cell.style.fontWeight = 'normal';
                            } else {
                                cell.style.color = '#374151';
                                cell.style.fontWeight = '600';
                                cell.style.fontStyle = 'normal';
                            }
                            
                            if (oldValue !== monthValue) {
                                console.log(`   ✅ Month ${monthIndex + 1}: "${oldValue}" → "${monthValue}"`);
                                cellsUpdated++;
                            }
                        } else {
                            // Set to dash if no data
                            if (oldValue !== '-') {
                                cell.textContent = '-';
                                cell.style.color = '#9ca3af';
                                cell.style.fontStyle = 'normal';
                                console.log(`   🔹 Month ${monthIndex + 1}: "${oldValue}" → "-"`);
                                cellsUpdated++;
                            }
                        }
                    }
                });
                
                console.log(`📊 ${networkName}: Updated ${cellsUpdated} cells`);
                totalFixed += cellsUpdated > 0 ? 1 : 0;
            } else {
                console.log(`❌ No months array found for ${networkName}`);
            }
        } else {
            console.log(`❌ No dashboardData available`);
        }
    });
    
    console.log(`\n🎉 COMPLETED: Fixed ${totalFixed} networks with individual dates`);
    return totalFixed;
}

// Step 2: Wait for dashboard data to load and apply fix
function applyFixWhenReady() {
    if (window.dashboardData && window.dashboardData.customers) {
        console.log('✅ Dashboard data available, applying fix...');
        const fixed = fixNetworkDatesDisplay();
        
        if (fixed > 0) {
            console.log('🎉 SUCCESS! Network dates should now be visible');
            console.log('📋 Check your dashboard - individual networks should show their monthly dates');
        } else {
            console.log('⚠️ No networks were updated. Check browser console for details.');
        }
    } else {
        console.log('⏳ Dashboard data not ready, retrying in 1 second...');
        setTimeout(applyFixWhenReady, 1000);
    }
}

// Step 3: Apply the fix immediately and set up auto-retry
console.log('🚀 Starting frontend fix...');
applyFixWhenReady();

// Make function available globally for manual triggering
window.fixNetworkDatesDisplay = fixNetworkDatesDisplay;

// Step 4: Also hook into any dashboard refresh events
const originalUpdateCustomerGrid = window.updateCustomerGrid;
if (originalUpdateCustomerGrid) {
    window.updateCustomerGrid = function(...args) {
        const result = originalUpdateCustomerGrid.apply(this, args);
        setTimeout(() => {
            console.log('🔄 Dashboard refreshed, re-applying network dates fix...');
            fixNetworkDatesDisplay();
        }, 500);
        return result;
    };
}

console.log('📋 MANUAL COMMANDS AVAILABLE:');
console.log('   - fixNetworkDatesDisplay() - Re-run the network fix');
console.log('   - window.dashboardData - Check dashboard data');

console.log('🔥 FINAL FRONTEND FIX LOADED AND RUNNING!');
console.log('💡 If networks still show dashes, run: fixNetworkDatesDisplay()');