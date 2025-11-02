// COMPREHENSIVE FIX FOR BSNL TOTAL RUNS AND EXPORT
// Paste this in browser console to instantly fix both dashboard and export

console.log('🚀 COMPREHENSIVE FIX: BSNL Total Runs and Export');
console.log('=' * 60);

// 1. Fix Dashboard Statistics (Header)
function fixDashboardStatistics() {
    console.log('📊 Fixing dashboard header statistics...');
    
    const customers = dashboardData.customers || {};
    const customerGroups = {};
    let totalCustomers = 0;
    let totalRuns = 0;
    let totalTrackers = 0;
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        // Skip if already counted
        if (customerGroups[customerName]) {
            console.log(`⚪ Skipping duplicate: ${customerName}`);
            return;
        }
        
        customerGroups[customerName] = true;
        totalCustomers++;
        
        // Calculate total runs for this customer (sum all networks)
        let customerTotalRuns = 0;
        Object.entries(customers).forEach(([key, cust]) => {
            const custName = cust.name || cust.Customer || key.split('_')[0];
            if (custName === customerName) {
                customerTotalRuns += parseInt(cust.total_runs || cust.runs || cust.run_count || 0);
            }
        });
        
        totalRuns += customerTotalRuns;
        
        // Calculate trackers (1 per 5 runs, minimum 1)
        const customerTrackers = Math.max(1, Math.ceil(customerTotalRuns / 5));
        totalTrackers += customerTrackers;
        
        console.log(`📊 ${customerName}: ${customerTotalRuns} runs, ${customerTrackers} trackers`);
    });
    
    // Update header display
    const customerEl = document.getElementById('header-total-customers');
    const runsEl = document.getElementById('header-total-runs');
    const trackersEl = document.getElementById('header-total-trackers');
    
    if (customerEl) customerEl.textContent = totalCustomers;
    if (runsEl) runsEl.textContent = totalRuns;
    if (trackersEl) trackersEl.textContent = totalTrackers;
    
    // Update dashboardData
    dashboardData.statistics = {
        ...dashboardData.statistics,
        total_customers: totalCustomers,
        total_runs: totalRuns,
        total_trackers: totalTrackers
    };
    
    console.log(`✅ Header fixed: ${totalCustomers} customers, ${totalRuns} runs, ${totalTrackers} trackers`);
    return { totalCustomers, totalRuns, totalTrackers };
}

// 2. Fix Table Total Runs Column
function fixTableTotalRuns() {
    console.log('📋 Fixing table total runs column...');
    
    const customers = dashboardData.customers || {};
    const customerGroups = {};
    
    // Group customers by name
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = [];
        }
        customerGroups[customerName].push({key: customerKey, data: customer});
    });
    
    // Update table rows
    Object.entries(customerGroups).forEach(([customerName, networks]) => {
        let customerTotalRuns = 0;
        
        // Calculate total for this customer
        networks.forEach(network => {
            customerTotalRuns += parseInt(network.data.total_runs || network.data.runs || 0);
        });
        
        // Find and update table row
        const tableRows = document.querySelectorAll('#customer-table-body tr.customer-summary-row');
        tableRows.forEach(row => {
            const customerNameCell = row.querySelector('.customer-name-main');
            if (customerNameCell && customerNameCell.textContent.includes(customerName)) {
                const totalCell = row.querySelector('.total-runs-cell');
                if (totalCell) {
                    totalCell.textContent = customerTotalRuns;
                    totalCell.style.fontWeight = '700';
                    totalCell.style.color = '#059669';
                    console.log(`✅ Table updated: ${customerName} -> ${customerTotalRuns} runs`);
                }
            }
        });
    });
}

// 3. Override Export Function
function fixExportFunction() {
    console.log('📤 Fixing export function...');
    
    window.originalExportToExcel = window.exportToExcel;
    
    window.exportToExcel = async function() {
        console.log('📤 ENHANCED Export starting...');
        
        try {
            const customers = dashboardData.customers || {};
            const customerGroups = {};
            
            // Group customers
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customerKey.split('_')[0];
                
                if (!customerGroups[customerName]) {
                    customerGroups[customerName] = {
                        name: customerName,
                        networks: []
                    };
                }
                
                customerGroups[customerName].networks.push({
                    key: customerKey,
                    data: customer
                });
            });
            
            let exportData = [];
            
            // Create export data with correct totals
            Object.values(customerGroups).forEach(group => {
                let customerTotalRuns = 0;
                
                // Calculate customer total
                group.networks.forEach(network => {
                    customerTotalRuns += parseInt(network.data.total_runs || network.data.runs || 0);
                });
                
                // Add each network as a row
                group.networks.forEach(network => {
                    const customer = network.data;
                    const rowData = {
                        'Customer': group.name,
                        'Network': customer.network_name || 'Default Network',
                        'Country': customer.country || 'Unknown',
                        'Node Qty': customer.node_count || customer.node_qty || 0,
                        'NE Type': customer.ne_type || '1830 PSS',
                        'gTAC': customer.gtac || 'PSS',
                        'Individual Runs': customer.total_runs || customer.runs || 0,
                        'Customer Total Runs': customerTotalRuns
                    };
                    
                    // Add monthly data
                    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    months.forEach((month, index) => {
                        let monthValue = '-';
                        
                        if (customer.monthly_runs && typeof customer.monthly_runs === 'object') {
                            const monthKey = `2024-${(index + 1).toString().padStart(2, '0')}`;
                            if (customer.monthly_runs[monthKey]) {
                                monthValue = customer.monthly_runs[monthKey];
                            }
                        }
                        
                        rowData[month] = monthValue;
                    });
                    
                    exportData.push(rowData);
                });
            });
            
            // Convert to CSV
            const headers = Object.keys(exportData[0]);
            let csvContent = headers.join(',') + '\n';
            
            exportData.forEach(row => {
                const values = headers.map(header => {
                    let value = row[header] || '';
                    if (value.toString().includes(',')) {
                        value = `"${value}"`;
                    }
                    return value;
                });
                csvContent += values.join(',') + '\n';
            });
            
            // Download
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Health_Check_Dashboard_CORRECTED_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log(`✅ Export completed: ${exportData.length} rows with CORRECT totals`);
            
            if (typeof showNotification === 'function') {
                showNotification(`✅ Exported ${exportData.length} records with corrected totals!`, 'success');
            }
            
        } catch (error) {
            console.error('❌ Export error:', error);
            if (typeof showNotification === 'function') {
                showNotification('❌ Export failed. Please try again.', 'error');
            }
        }
    };
}

// Apply all fixes
const stats = fixDashboardStatistics();
fixTableTotalRuns();
fixExportFunction();

console.log('🎉 COMPREHENSIVE FIX APPLIED!');
console.log('✅ Fixed Issues:');
console.log('   📊 Header statistics use correct customer grouping');
console.log('   📋 Table shows correct total runs per customer');
console.log('   📤 Export function groups customers properly');
console.log('');
console.log('📈 Current Corrected Values:');
console.log(`   👥 Customers: ${stats.totalCustomers}`);
console.log(`   🏃 Total Runs: ${stats.totalRuns}`);
console.log(`   📋 Trackers: ${stats.totalTrackers}`);
console.log('');
console.log('🎯 BSNL should now show 53 runs (not 70)');
console.log('📤 Export will now include both Individual and Customer Total columns');
console.log('');
console.log('✅ All fixes are now active! Test the export button.');

// Test BSNL specifically
const bsnlData = Object.entries(dashboardData.customers || {}).filter(([key, customer]) => 
    (customer.name || key).toLowerCase().includes('bsnl')
);

if (bsnlData.length > 0) {
    let bsnlTotalRuns = 0;
    console.log('\n🔍 BSNL Networks Check:');
    bsnlData.forEach(([key, customer]) => {
        const runs = customer.total_runs || customer.runs || 0;
        bsnlTotalRuns += runs;
        console.log(`   ${customer.network_name || key}: ${runs} runs`);
    });
    console.log(`📊 BSNL CORRECT Total: ${bsnlTotalRuns} runs`);
}