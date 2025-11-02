// DEBUG NETWORK DATA STRUCTURE
console.log('🔍 DEBUGGING NETWORK DATA STRUCTURE...');

// Check dashboard data
if (window.dashboardData && window.dashboardData.customers) {
    const customers = Object.values(window.dashboardData.customers);
    console.log(`📊 Found ${customers.length} customers`);
    
    // Find a customer with networks (like BSNL or Tata)
    const customerWithNetworks = customers.find(c => 
        c.networks && c.networks.length > 1 && 
        (c.name.toLowerCase().includes('bsnl') || c.name.toLowerCase().includes('tata'))
    );
    
    if (customerWithNetworks) {
        console.log(`🎯 Examining customer: ${customerWithNetworks.name}`);
        console.log(`📊 Customer data structure:`, {
            name: customerWithNetworks.name,
            networks_count: customerWithNetworks.networks ? customerWithNetworks.networks.length : 0,
            excel_source: customerWithNetworks.excel_source,
            months: customerWithNetworks.months
        });
        
        if (customerWithNetworks.networks) {
            customerWithNetworks.networks.forEach((network, index) => {
                console.log(`🔗 Network ${index + 1}: ${network.name || network.network_name}`);
                console.log(`   - months array:`, network.months);
                console.log(`   - monthly_runs:`, network.monthly_runs);
                console.log(`   - runs:`, network.runs);
                console.log(`   - last_run_date:`, network.last_run_date);
            });
        }
    }
} else {
    console.log('❌ No dashboard data found');
}

// Function to force update network dates
function forceUpdateNetworkDates() {
    console.log('🚀 FORCING NETWORK DATES UPDATE...');
    
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`Found ${networkRows.length} network rows`);
    
    networkRows.forEach((row, index) => {
        const nameEl = row.querySelector('.network-name-main');
        if (!nameEl) return;
        
        const networkName = nameEl.textContent.replace('└─ ', '').trim();
        
        // Find customer for this network
        let customerRow = row.previousElementSibling;
        while (customerRow && !customerRow.classList.contains('customer-summary-row')) {
            customerRow = customerRow.previousElementSibling;
        }
        
        if (!customerRow) return;
        
        const custNameEl = customerRow.querySelector('.customer-name-main');
        if (!custNameEl) return;
        
        const customerName = custNameEl.textContent.replace(/[📋📄💾🔄]/g, '').trim().split('\n')[0];
        
        console.log(`\n🔧 Processing: ${customerName} -> ${networkName}`);
        
        // Find customer data
        if (window.dashboardData && window.dashboardData.customers) {
            const customers = Object.values(window.dashboardData.customers);
            const customerData = customers.find(c => 
                c.name && c.name.toLowerCase().includes(customerName.toLowerCase())
            );
            
            if (customerData && customerData.networks) {
                console.log(`✅ Found customer data for: ${customerData.name}`);
                console.log(`📊 Networks available: ${customerData.networks.map(n => n.name || n.network_name).join(', ')}`);
                
                // Find matching network
                const networkData = customerData.networks.find(net => {
                    const netName = (net.name || net.network_name || '').toLowerCase();
                    const searchName = networkName.toLowerCase();
                    
                    return netName === searchName || 
                           netName.includes(searchName) || 
                           searchName.includes(netName) ||
                           (netName.includes('_') && netName.replace(/_/g, ' ').includes(searchName.replace(/_/g, ' ')));
                });
                
                if (networkData) {
                    console.log(`🎯 Found network data:`, {
                        name: networkData.name || networkData.network_name,
                        months: networkData.months,
                        monthly_runs: networkData.monthly_runs
                    });
                    
                    // Update month cells
                    const cells = Array.from(row.querySelectorAll('td')).slice(6, 18);
                    if (cells.length === 12) {
                        cells.forEach((cell, i) => {
                            let dateToShow = '-';
                            
                            // Try months array first
                            if (networkData.months && networkData.months[i] && networkData.months[i] !== '-') {
                                dateToShow = networkData.months[i];
                                console.log(`📅 Month ${i+1} from months array: ${dateToShow}`);
                            }
                            // Try monthly_runs dictionary
                            else if (networkData.monthly_runs) {
                                const key2024 = `2024-${(i + 1).toString().padStart(2, '0')}`;
                                const key2025 = `2025-${(i + 1).toString().padStart(2, '0')}`;
                                
                                if (networkData.monthly_runs[key2024]) {
                                    dateToShow = networkData.monthly_runs[key2024];
                                    console.log(`📅 Month ${i+1} from monthly_runs 2024: ${dateToShow}`);
                                } else if (networkData.monthly_runs[key2025]) {
                                    dateToShow = networkData.monthly_runs[key2025];
                                    console.log(`📅 Month ${i+1} from monthly_runs 2025: ${dateToShow}`);
                                }
                            }
                            
                            // Update cell
                            if (dateToShow && dateToShow !== '-') {
                                cell.textContent = dateToShow;
                                cell.style.color = '#374151';
                                cell.style.fontWeight = '500';
                                console.log(`✅ Updated ${networkName} month ${i+1}: ${dateToShow}`);
                            }
                        });
                    }
                } else {
                    console.log(`❌ No matching network found for: ${networkName}`);
                    console.log(`Available networks: ${customerData.networks.map(n => n.name || n.network_name).join(', ')}`);
                }
            } else {
                console.log(`❌ No customer data found for: ${customerName}`);
            }
        }
    });
    
    console.log('✅ Network dates update completed!');
}

// Run the debug
console.log('📋 Running network data debug...');
setTimeout(() => {
    forceUpdateNetworkDates();
}, 2000);

// Make function available globally
window.forceUpdateNetworkDates = forceUpdateNetworkDates;