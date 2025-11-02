// EMERGENCY DOM FIX: Force Network Dates to Show in Dashboard Table
// This directly modifies the existing table cells

console.log('🚨 EMERGENCY DOM FIX: Forcing network dates to display...');

function forceNetworkDatesDisplay() {
    // Find all network detail rows
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`🔍 Found ${networkRows.length} network rows to fix`);
    
    if (networkRows.length === 0) {
        console.log('❌ No network rows found! Make sure dashboard is loaded.');
        return;
    }
    
    // Process each network row
    networkRows.forEach((row, rowIndex) => {
        const networkNameElement = row.querySelector('.network-name-main');
        const networkName = networkNameElement ? networkNameElement.textContent.replace('└─ ', '').trim() : `Network_${rowIndex}`;
        
        console.log(`🔧 Processing network row ${rowIndex + 1}: "${networkName}"`);
        
        // Find the customer for this network (previous customer summary row)
        let customerRow = row.previousElementSibling;
        while (customerRow && !customerRow.classList.contains('customer-summary-row')) {
            customerRow = customerRow.previousElementSibling;
        }
        
        if (!customerRow) {
            console.log(`⚠️ Could not find customer row for network: ${networkName}`);
            return;
        }
        
        // Get customer name from customer row
        const customerNameElement = customerRow.querySelector('.customer-name-main');
        const customerText = customerNameElement ? customerNameElement.textContent : '';
        const customerName = customerText.replace(/[📋📄💾🔄]/g, '').trim().split('\n')[0];
        
        console.log(`👤 Customer for ${networkName}: "${customerName}"`);
        
        // Find customer in dashboardData
        let customerData = null;
        if (window.dashboardData && window.dashboardData.customers) {
            customerData = Object.values(window.dashboardData.customers).find(c => 
                c.name && c.name.toLowerCase().includes(customerName.toLowerCase())
            );
        }
        
        if (!customerData) {
            console.log(`❌ Customer data not found for: ${customerName}`);
            return;
        }
        
        console.log(`✅ Found customer data for: ${customerName}`);
        
        // Find the specific network in customer.networks
        let targetNetwork = null;
        if (customerData.networks && Array.isArray(customerData.networks)) {
            targetNetwork = customerData.networks.find(net => {
                const netName = (net.name || net.network_name || '').toLowerCase();
                const searchName = networkName.toLowerCase();
                return netName.includes(searchName) || 
                       searchName.includes(netName) ||
                       netName === searchName ||
                       netName.endsWith(searchName);
            });
        }
        
        if (!targetNetwork) {
            console.log(`❌ Network not found in customer data: ${networkName}`);
            if (customerData.networks) {
                console.log(`Available networks:`, customerData.networks.map(n => n.name || n.network_name));
            }
            return;
        }
        
        console.log(`🎯 Found network data:`, {
            name: targetNetwork.name,
            runs: targetNetwork.runs,
            last_run_date: targetNetwork.last_run_date
        });
        
        // Find all TD elements in this row (month columns should be after first 6 columns)
        const allCells = Array.from(row.querySelectorAll('td'));
        console.log(`📊 Total cells in row: ${allCells.length}`);
        
        // Month columns are typically positions 6-17 (0-indexed)
        const monthCellsStart = 6; // After: Name, Country, Networks, NodeQty, NEType, GTAC
        const monthCells = allCells.slice(monthCellsStart, monthCellsStart + 12);
        
        if (monthCells.length !== 12) {
            console.log(`⚠️ Expected 12 month cells, found ${monthCells.length}`);
            // Try different approach - look for cells with class 'run-count'
            const runCountCells = Array.from(row.querySelectorAll('.run-count'));
            if (runCountCells.length >= 12) {
                monthCells.length = 0;
                monthCells.push(...runCountCells.slice(0, 12));
                console.log(`🔄 Using run-count cells: ${monthCells.length}`);
            }
        }
        
        if (monthCells.length === 12 && targetNetwork.last_run_date && targetNetwork.runs > 0) {
            const networkDate = new Date(targetNetwork.last_run_date);
            if (!isNaN(networkDate.getTime())) {
                const networkYear = networkDate.getFullYear();
                const networkMonth = networkDate.getMonth() + 1; // 1-based month
                
                console.log(`📅 Network "${networkName}" last run: ${targetNetwork.last_run_date} (Month: ${networkMonth}, Year: ${networkYear})`);
                
                // Update the specific month cell
                if (networkMonth >= 1 && networkMonth <= 12) {
                    const monthCellIndex = networkMonth - 1; // Convert to 0-based index
                    const monthCell = monthCells[monthCellIndex];
                    
                    if (monthCell) {
                        const day = networkDate.getDate();
                        const monthName = networkDate.toLocaleDateString('en-US', { month: 'short' });
                        const yearShort = networkDate.getFullYear().toString().slice(-2);
                        const formattedDate = `${day}-${monthName}-${yearShort}`;
                        
                        // Force update the cell
                        monthCell.textContent = formattedDate;
                        monthCell.style.color = '#374151';
                        monthCell.style.fontWeight = '600';
                        monthCell.title = `${targetNetwork.runs} runs from ${networkName} on ${formattedDate}`;
                        
                        console.log(`🟢 FIXED: ${networkName} month ${networkMonth} = "${formattedDate}"`);
                    }
                }
                
                // Set all other month cells to '-'
                monthCells.forEach((cell, index) => {
                    if (index !== (networkMonth - 1)) {
                        cell.textContent = '-';
                        cell.style.color = '#9ca3af';
                        cell.title = `No runs from ${networkName} in month ${index + 1}`;
                    }
                });
            }
        } else {
            console.log(`⚠️ Cannot fix dates for ${networkName}: monthCells=${monthCells.length}, runs=${targetNetwork.runs}`);
        }
    });
    
    console.log('🎉 DOM fix complete! Check the dashboard table now.');
}

// Run the fix
forceNetworkDatesDisplay();

// Also setup a mutation observer to fix new rows as they're created
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            const addedNodes = Array.from(mutation.addedNodes);
            const hasNetworkRows = addedNodes.some(node => 
                node.nodeType === Node.ELEMENT_NODE && 
                node.classList && 
                node.classList.contains('network-detail-row')
            );
            
            if (hasNetworkRows) {
                console.log('🔄 New network rows detected, applying fix...');
                setTimeout(forceNetworkDatesDisplay, 100);
            }
        }
    });
});

// Observe the table body for changes
const tableBody = document.getElementById('customer-table-body');
if (tableBody) {
    observer.observe(tableBody, { childList: true, subtree: true });
    console.log('👁️ Monitoring table for new rows...');
}

console.log('✅ Emergency DOM fix applied! Network dates should now be visible in the dashboard.');