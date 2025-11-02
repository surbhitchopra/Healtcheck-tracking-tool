// INSTANT NETWORK DATES FIX - Browser console ke liye
// Yeh copy-paste karke browser console mein run karo

(function() {
    console.log('🚀 INSTANT NETWORK FIX RUNNING...');
    
    if (!window.dashboardData || !window.dashboardData.customers) {
        console.log('❌ Dashboard data missing! Please refresh page first.');
        return;
    }
    
    const customers = Object.values(window.dashboardData.customers);
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    
    console.log(`📊 Found: ${customers.length} customers, ${networkRows.length} network rows`);
    
    let fixed = 0;
    
    networkRows.forEach(row => {
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
        
        // Find customer data
        const customerData = customers.find(c => 
            c.name && c.name.toLowerCase().includes(customerName.toLowerCase())
        );
        
        if (!customerData || !customerData.networks) return;
        
        // Find network data
        const networkData = customerData.networks.find(net => {
            return net.name === networkName || 
                   net.network_name === networkName ||
                   (net.name && net.name.includes(networkName)) ||
                   (networkName.includes(net.name));
        });
        
        if (!networkData) return;
        
        console.log(`🔧 Fixing ${networkName}...`);
        
        // Get month cells (6-17 columns)
        const cells = Array.from(row.querySelectorAll('td')).slice(6, 18);
        
        if (cells.length !== 12) return;
        
        let cellsFixed = 0;
        
        cells.forEach((cell, i) => {
            let date = '-';
            
            // Try Excel months array
            if (networkData.months && networkData.months[i] && networkData.months[i] !== '-') {
                date = networkData.months[i];
            }
            // Try monthly_runs dictionary
            else if (networkData.monthly_runs) {
                const key2024 = `2024-${(i + 1).toString().padStart(2, '0')}`;
                const key2025 = `2025-${(i + 1).toString().padStart(2, '0')}`;
                if (networkData.monthly_runs[key2024]) {
                    date = networkData.monthly_runs[key2024];
                } else if (networkData.monthly_runs[key2025]) {
                    date = networkData.monthly_runs[key2025];
                }
            }
            // Try last_run_date for DB networks
            else if (networkData.last_run_date && networkData.last_run_date !== 'Never') {
                try {
                    const d = new Date(networkData.last_run_date);
                    if (d.getMonth() === i && (d.getFullYear() === 2024 || d.getFullYear() === 2025)) {
                        const day = d.getDate();
                        const month = d.toLocaleDateString('en-US', { month: 'short' });
                        const year = d.getFullYear().toString().slice(-2);
                        date = `${day}-${month}-${year}`;
                    }
                } catch (e) {}
            }
            
            if (date !== '-' && date !== 'Not Run') {
                cell.textContent = date;
                cell.style.color = '#374151';
                cell.style.fontWeight = '600';
                cell.style.backgroundColor = '#f0f9ff';
                cellsFixed++;
            } else {
                cell.textContent = '-';
                cell.style.color = '#9ca3af';
            }
        });
        
        if (cellsFixed > 0) {
            fixed++;
            console.log(`✅ ${networkName}: ${cellsFixed} dates fixed`);
        }
    });
    
    console.log(`🎉 DONE! Fixed ${fixed} networks`);
    
    if (fixed === 0) {
        console.log('🤔 No fixes applied. Debug info:');
        console.log('Dashboard data keys:', Object.keys(window.dashboardData));
        console.log('First customer:', customers[0] ? customers[0].name : 'None');
    }
})();