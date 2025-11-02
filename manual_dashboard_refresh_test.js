// Manual Dashboard Refresh Test
// Copy and paste this in browser console after completing a health check session

console.log('🔄 MANUAL DASHBOARD REFRESH TEST');
console.log('====================================');

// Store original values
const originalData = { ...window.dashboardData };
console.log('📊 Original Dashboard Data:', originalData);

// Force refresh from database
fetch('/api/customer-dashboard/customers/')
    .then(response => response.json())
    .then(data => {
        console.log('📡 Fresh data from server:', data);
        
        if (data.success && data.customers) {
            // Update global data
            window.dashboardData = data;
            
            // Compare BSNL East Zone DWDM
            const bsnlEast = Object.values(data.customers).find(c => 
                c.name === 'BSNL' && c.network_name && c.network_name.includes('East_Zone_DWDM')
            );
            
            if (bsnlEast) {
                console.log('🎯 BSNL East Zone DWDM:');
                console.log('   Name:', bsnlEast.name);
                console.log('   Network:', bsnlEast.network_name);
                console.log('   Database total_runs:', bsnlEast.total_runs);
                console.log('   Excel runs (old):', bsnlEast.runs || 'N/A');
                console.log('   Should display:', bsnlEast.total_runs);
            }
            
            // Force use database values
            Object.values(window.dashboardData.customers).forEach(customer => {
                const dbTotalRuns = customer.total_runs || 0;
                customer.runs = dbTotalRuns;
                customer.run_count = dbTotalRuns;
                customer.total_run_count = dbTotalRuns;
            });
            
            // Update display
            if (window.updateCustomerGrid) {
                console.log('🔄 Updating customer grid...');
                window.updateCustomerGrid();
            }
            
            if (window.updateStatistics) {
                console.log('📊 Updating statistics...');
                window.updateStatistics();
            }
            
            console.log('✅ Dashboard refreshed with latest database values!');
            console.log('📋 Check the table - total runs should now reflect database values');
            
        } else {
            console.error('❌ Invalid response from server');
        }
    })
    .catch(error => {
        console.error('❌ Refresh failed:', error);
    });

// Also check current table values
setTimeout(() => {
    console.log('\n🔍 CHECKING TABLE DISPLAY VALUES:');
    
    const rows = document.querySelectorAll('.customer-row');
    rows.forEach(row => {
        const customerName = row.querySelector('.customer-name')?.textContent?.trim();
        const networkName = row.querySelector('.network-name')?.textContent?.trim();
        const totalRunsCell = row.querySelector('.total-runs');
        const totalRuns = totalRunsCell?.textContent?.trim();
        
        if (customerName && customerName.includes('BSNL') && networkName && networkName.includes('East')) {
            console.log(`📊 Table shows: ${customerName} - ${networkName} = ${totalRuns} runs`);
        }
    });
}, 2000);