// SIMPLE NETWORK DATES FIX - Direct DOM injection
// Yeh script network rows mein unke apne dates inject karega

console.log('🚀 SIMPLE NETWORK DATES FIX STARTING...');

function injectNetworkDatesDirectly() {
    console.log('🔧 Direct injection of network dates starting...');
    
    // Sabse pehle dashboard data check karte hain
    if (!window.dashboardData || !window.dashboardData.customers) {
        console.log('❌ Dashboard data not available');
        return false;
    }
    
    const customers = Object.values(window.dashboardData.customers);
    console.log(`📊 Found ${customers.length} customers in data`);
    
    // Har network row find karte hain
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`🔍 Found ${networkRows.length} network rows in DOM`);
    
    let updatedCount = 0;
    
    networkRows.forEach((row, index) => {
        // Network name nikaalte hain
        const networkNameElement = row.querySelector('.network-name-main');
        if (!networkNameElement) {
            console.log(`⚠️ No network name found for row ${index}`);
            return;
        }
        
        const networkName = networkNameElement.textContent.replace('└─ ', '').trim();
        console.log(`\n🔍 Processing network: ${networkName}`);
        
        // Customer find karte hain for this network
        let customerRow = row.previousElementSibling;
        while (customerRow && !customerRow.classList.contains('customer-summary-row')) {
            customerRow = customerRow.previousElementSibling;
        }
        
        if (!customerRow) {
            console.log(`❌ Customer row not found for ${networkName}`);
            return;
        }
        
        const customerNameElement = customerRow.querySelector('.customer-name-main');
        if (!customerNameElement) {
            console.log(`❌ Customer name element not found for ${networkName}`);
            return;
        }
        
        const customerText = customerNameElement.textContent;
        const customerName = customerText.replace(/[📋📄💾🔄]/g, '').trim().split('\n')[0];
        console.log(`👤 Customer: ${customerName}`);
        
        // Customer data find karte hain
        const customerData = customers.find(c => 
            c.name && c.name.toLowerCase().includes(customerName.toLowerCase())
        );
        
        if (!customerData) {
            console.log(`❌ Customer data not found for ${customerName}`);
            return;
        }
        
        console.log(`✅ Found customer data for: ${customerData.name}`);
        console.log(`📊 Customer type:`, {
            excel_source: !!customerData.excel_source,
            networks_count: customerData.networks ? customerData.networks.length : 0
        });
        
        // Network data find karte hain
        if (!customerData.networks || !Array.isArray(customerData.networks)) {
            console.log(`❌ No networks array for customer ${customerData.name}`);
            return;
        }
        
        const networkData = customerData.networks.find(net => {
            return net.name === networkName || 
                   net.network_name === networkName ||
                   net.name.includes(networkName) ||
                   networkName.includes(net.name);
        });
        
        if (!networkData) {
            console.log(`❌ Network data not found for ${networkName}`);
            return;
        }
        
        console.log(`🎯 Found network data:`, {
            name: networkData.name,
            has_months: !!networkData.months,
            has_monthly_runs: !!networkData.monthly_runs,
            last_run_date: networkData.last_run_date
        });
        
        // Month cells find karte hain (column 6 se 17 tak)
        const allCells = Array.from(row.querySelectorAll('td'));
        const monthCells = allCells.slice(6, 18); // Jan to Dec
        
        if (monthCells.length !== 12) {
            console.log(`❌ Expected 12 month cells, found ${monthCells.length}`);
            return;
        }
        
        let cellsUpdated = 0;
        
        // Har month cell update karte hain
        monthCells.forEach((cell, monthIndex) => {
            const monthNum = monthIndex + 1;
            const monthName = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][monthIndex];
            
            let dateToShow = '-';
            let foundDate = false;
            
            // Method 1: Check months array (for Excel customers)
            if (networkData.months && Array.isArray(networkData.months) && networkData.months[monthIndex]) {
                const monthValue = networkData.months[monthIndex];
                if (monthValue && monthValue !== '-' && monthValue !== 'Not Run') {
                    dateToShow = monthValue;
                    foundDate = true;
                    console.log(`  ✅ ${monthName}: Found in months array - ${monthValue}`);
                }
            }
            
            // Method 2: Check monthly_runs dictionary (for Excel customers)
            if (!foundDate && networkData.monthly_runs && typeof networkData.monthly_runs === 'object') {
                const monthKey2024 = `2024-${monthNum.toString().padStart(2, '0')}`;
                const monthKey2025 = `2025-${monthNum.toString().padStart(2, '0')}`;
                
                if (networkData.monthly_runs[monthKey2024]) {
                    dateToShow = networkData.monthly_runs[monthKey2024];
                    foundDate = true;
                    console.log(`  ✅ ${monthName}: Found in monthly_runs 2024 - ${dateToShow}`);
                } else if (networkData.monthly_runs[monthKey2025]) {
                    dateToShow = networkData.monthly_runs[monthKey2025];
                    foundDate = true;
                    console.log(`  ✅ ${monthName}: Found in monthly_runs 2025 - ${dateToShow}`);
                }
            }
            
            // Method 3: Check if this network's last_run_date falls in this month (for DB customers)
            if (!foundDate && networkData.last_run_date && networkData.last_run_date !== 'Never' && networkData.runs > 0) {
                try {
                    const networkDate = new Date(networkData.last_run_date);
                    if (!isNaN(networkDate.getTime())) {
                        const networkMonth = networkDate.getMonth() + 1;
                        const networkYear = networkDate.getFullYear();
                        
                        if (networkMonth === monthNum && (networkYear === 2024 || networkYear === 2025)) {
                            const day = networkDate.getDate();
                            const monthShort = networkDate.toLocaleDateString('en-US', { month: 'short' });
                            const yearShort = networkDate.getFullYear().toString().slice(-2);
                            dateToShow = `${day}-${monthShort}-${yearShort}`;
                            foundDate = true;
                            console.log(`  ✅ ${monthName}: Found in last_run_date - ${dateToShow}`);
                        }
                    }
                } catch (error) {
                    console.log(`  ❌ Error parsing last_run_date: ${error.message}`);
                }
            }
            
            // Cell update karte hain
            if (foundDate && dateToShow !== '-') {
                cell.textContent = dateToShow;
                cell.style.color = '#374151';
                cell.style.fontWeight = '600';
                cell.style.backgroundColor = '#f3f4f6';
                cellsUpdated++;
                console.log(`  📝 Updated ${monthName}: ${dateToShow}`);
            } else {
                cell.textContent = '-';
                cell.style.color = '#9ca3af';
                cell.style.fontWeight = 'normal';
                console.log(`  ➖ ${monthName}: No date found`);
            }
        });
        
        if (cellsUpdated > 0) {
            updatedCount++;
            console.log(`✅ Updated ${cellsUpdated} cells for network ${networkName}`);
        } else {
            console.log(`⚠️ No dates found for network ${networkName}`);
        }
    });
    
    console.log(`\n🎉 INJECTION COMPLETE! Updated ${updatedCount} network rows`);
    return updatedCount > 0;
}

// Debug function to see all network data
function debugNetworkData() {
    console.log('🐛 DEBUGGING NETWORK DATA...');
    
    if (!window.dashboardData || !window.dashboardData.customers) {
        console.log('❌ No dashboard data');
        return;
    }
    
    const customers = Object.values(window.dashboardData.customers);
    
    customers.forEach(customer => {
        console.log(`\n👤 Customer: ${customer.name}`);
        console.log(`   Type: ${customer.excel_source ? 'Excel' : 'Database'}`);
        
        if (customer.networks && Array.isArray(customer.networks)) {
            console.log(`   Networks: ${customer.networks.length}`);
            
            customer.networks.forEach((network, idx) => {
                console.log(`   🔗 Network ${idx + 1}: ${network.name || network.network_name}`);
                console.log(`      - has months: ${!!network.months}`);
                console.log(`      - has monthly_runs: ${!!network.monthly_runs}`);
                console.log(`      - last_run_date: ${network.last_run_date}`);
                console.log(`      - runs: ${network.runs}`);
                
                if (network.months && Array.isArray(network.months)) {
                    const nonEmptyMonths = network.months.filter(m => m && m !== '-').length;
                    console.log(`      - months array: ${nonEmptyMonths} non-empty dates`);
                }
                
                if (network.monthly_runs && typeof network.monthly_runs === 'object') {
                    const keys = Object.keys(network.monthly_runs);
                    console.log(`      - monthly_runs keys: ${keys.length} (${keys.slice(0, 3).join(', ')}...)`);
                }
            });
        }
    });
}

// Main execution
console.log('🚀 Starting network dates fix...');

// Debug first
debugNetworkData();

// Apply fix
setTimeout(() => {
    injectNetworkDatesDirectly();
    console.log('✅ Network dates fix completed!');
}, 1000);

// Make functions available globally
window.injectNetworkDatesDirectly = injectNetworkDatesDirectly;
window.debugNetworkData = debugNetworkData;

console.log('📋 Available commands:');
console.log('   - debugNetworkData() - Shows all network data');
console.log('   - injectNetworkDatesDirectly() - Forces network dates to display');