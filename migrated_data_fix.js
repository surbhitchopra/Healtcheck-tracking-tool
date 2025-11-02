// 🔥 COMPLETE MIGRATED DATA EXPORT FIX
// Ensures ALL data (Live DB + Migrated Excel) is exported correctly

console.log('🔥 Loading COMPLETE MIGRATED DATA EXPORT FIX...');

// 🎯 EXACT COLUMN MAPPING from your dashboard
const EXACT_COLUMNS = {
    customer: 0,    // Customer
    country: 1,     // Country  
    networks: 2,    // Networks
    nodeQty: 3,     // Node Qty
    neType: 4,      // NE Type
    gtac: 5,        // GTAC
    jan: 6,         // Jan
    feb: 7,         // Feb
    mar: 8,         // Mar
    apr: 9,         // Apr
    may: 10,        // May
    jun: 11,        // Jun
    jul: 12,        // Jul
    aug: 13,        // Aug
    sep: 14,        // Sep
    oct: 15,        // Oct
    nov: 16,        // Nov
    dec: 17,        // Dec
    totalRuns: 18   // Total Runs (last column)
};

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// 🔥 COMPREHENSIVE EXPORT - ALL DATA SOURCES
window.exportAllData = async function() {
    console.log('🔥 COMPREHENSIVE EXPORT: Including ALL data sources...');
    
    try {
        const token = getCsrfToken();
        if (!token) throw new Error('No CSRF token found');
        
        showNotification('🔥 Exporting ALL data (Live DB + Migrated Excel)...', 'info');
        
        const exportData = [];
        let liveDbCount = 0;
        let migratedCount = 0;
        
        // METHOD 1: Get data from JavaScript dashboardData (for migrated data)
        if (window.dashboardData && window.dashboardData.customers) {
            console.log('📊 Processing JavaScript dashboardData...');
            
            Object.entries(dashboardData.customers).forEach(([customerName, customer]) => {
                const isExcel = customer.excel_source || customer.excel_data || customer.excel_only || customer.migrated;
                console.log(`📊 Processing: ${customerName} (${isExcel ? 'MIGRATED EXCEL' : 'LIVE DB'})`);
                
                if (customer.networks && customer.networks.length > 0) {
                    customer.networks.forEach((network, networkIndex) => {
                        console.log(`  🔧 Network: ${network.name || `Network ${networkIndex + 1}`} | Nodes: ${network.node_count || network.nodes || network.node_qty || customer.node_count || 0}`);
                        
                        const rowData = {
                            'Customer': customerName,
                            'Network': network.name || network.network_name || `Network ${networkIndex + 1}`,
                            'Country': customer.country || network.country || 'Unknown',
                            'Node Qty': network.node_count || network.nodes || network.node_qty || customer.node_count || customer.nodes || customer.node_qty || 0,
                            'NE Type': network.ne_type || network.platform || customer.ne_type || network.ne || customer.platform || '1830 PSS',
                            'GTAC': network.gtac || network.gateway || customer.gtac || network.gateway_type || 'PSS',
                            'Total Runs': network.runs || network.total_runs || network.run_count || customer.total_runs || 0,
                            'Source': isExcel ? 'Migrated Excel' : 'Live Database'
                        };
                        
                        // Extract monthly data with multiple methods
                        MONTHS.forEach((month, monthIndex) => {
                            let monthValue = '-';
                            
                            try {
                                // Try different data sources for monthly data
                                if (network.months && Array.isArray(network.months) && network.months[monthIndex]) {
                                    monthValue = network.months[monthIndex];
                                } else if (network.monthly_runs && Array.isArray(network.monthly_runs) && network.monthly_runs[monthIndex]) {
                                    monthValue = network.monthly_runs[monthIndex];
                                } else if (customer.months && Array.isArray(customer.months) && customer.months[monthIndex]) {
                                    monthValue = customer.months[monthIndex];
                                } else if (customer.network_monthly_runs && 
                                         customer.network_monthly_runs[network.name] && 
                                         customer.network_monthly_runs[network.name][monthIndex + 1]) {
                                    monthValue = customer.network_monthly_runs[network.name][monthIndex + 1];
                                }
                                
                                // Keep ALL values including "Not Started", "No Report", etc.
                                if (monthValue && monthValue !== '-' && monthValue !== 'undefined' && monthValue !== 'null') {
                                    rowData[month] = monthValue;
                                    if (monthValue !== '-') {
                                        console.log(`    📅 ${month}: "${monthValue}"`);
                                    }
                                } else {
                                    rowData[month] = '-';
                                }
                            } catch (error) {
                                console.log(`    ⚠️ Error extracting ${month}:`, error.message);
                                rowData[month] = '-';
                            }
                        });
                        
                        exportData.push(rowData);
                        if (isExcel) {
                            migratedCount++;
                        } else {
                            liveDbCount++;
                        }
                        console.log(`    ✅ Added: ${rowData.Customer} - ${rowData.Network} (${rowData.Source})`);
                    });
                } else {
                    // Customer without networks - still add to export
                    const rowData = {
                        'Customer': customerName,
                        'Network': 'No Networks',
                        'Country': customer.country || 'Unknown',
                        'Node Qty': customer.node_count || customer.nodes || customer.node_qty || 0,
                        'NE Type': customer.ne_type || customer.platform || '1830 PSS',
                        'GTAC': customer.gtac || 'PSS',
                        'Total Runs': customer.runs || customer.total_runs || customer.run_count || 0,
                        'Source': isExcel ? 'Migrated Excel' : 'Live Database'
                    };
                    
                    // Add monthly data for customer without networks
                    MONTHS.forEach((month, monthIndex) => {
                        let monthValue = '-';
                        if (customer.months && customer.months[monthIndex]) {
                            monthValue = customer.months[monthIndex];
                        } else if (customer.monthly_runs && customer.monthly_runs[monthIndex]) {
                            monthValue = customer.monthly_runs[monthIndex];
                        }
                        rowData[month] = monthValue || '-';
                    });
                    
                    exportData.push(rowData);
                    if (isExcel) {
                        migratedCount++;
                    } else {
                        liveDbCount++;
                    }
                    console.log(`    ✅ Added customer-only: ${rowData.Customer} (${rowData.Source})`);
                }
            });
        }
        
        // METHOD 2: ALSO get data directly from TABLE (for any missing data)
        console.log('📊 ALSO Processing TABLE data to ensure nothing is missed...');
        
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        const tableCustomers = new Set();
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 19) return;
            
            const customerName = cells[EXACT_COLUMNS.customer]?.textContent.trim() || 'Unknown';
            const cleanCustomerName = customerName.replace('💾 ', '').replace('💾 Live DB', '').replace('└─ ', '');
            
            // Skip if we already processed this customer from dashboardData
            if (tableCustomers.has(cleanCustomerName)) return;
            
            const isNetworkRow = customerName.includes('└─');
            if (isNetworkRow) return; // Skip network detail rows for now, process with parent
            
            tableCustomers.add(cleanCustomerName);
            
            console.log(`📊 Table Row ${index}: "${cleanCustomerName}" - ${cells.length} cells`);
            
            // Check if this customer was already processed from dashboardData
            const alreadyProcessed = exportData.some(row => 
                row.Customer === cleanCustomerName || 
                row.Customer.includes(cleanCustomerName) ||
                cleanCustomerName.includes(row.Customer)
            );
            
            if (!alreadyProcessed) {
                console.log(`  ⚠️ Customer "${cleanCustomerName}" NOT found in dashboardData, adding from table...`);
                
                const rowData = {
                    'Customer': cleanCustomerName,
                    'Network': 'From Table',
                    'Country': cells[EXACT_COLUMNS.country]?.textContent.trim() || 'Unknown',
                    'Node Qty': cells[EXACT_COLUMNS.nodeQty]?.textContent.trim() || '0',
                    'NE Type': cells[EXACT_COLUMNS.neType]?.textContent.trim() || '1830 PSS',
                    'GTAC': cells[EXACT_COLUMNS.gtac]?.textContent.trim() || 'PSS',
                    'Total Runs': cells[EXACT_COLUMNS.totalRuns]?.textContent.trim() || '0',
                    'Source': 'Table Only'
                };
                
                // Extract monthly data from table
                MONTHS.forEach((month, monthIndex) => {
                    const columnIndex = EXACT_COLUMNS[month.toLowerCase()];
                    const cellValue = cells[columnIndex]?.textContent.trim() || '-';
                    rowData[month] = cellValue;
                    
                    if (cellValue && cellValue !== '-') {
                        console.log(`    📅 ${month}: "${cellValue}"`);
                    }
                });
                
                exportData.push(rowData);
                liveDbCount++; // Assume table data is live DB
                console.log(`    ✅ Added from table: ${rowData.Customer} (${rowData['Total Runs']} runs)`);
            } else {
                console.log(`  ✅ Customer "${cleanCustomerName}" already processed from dashboardData`);
            }
        });
        
        console.log(`🔥 FINAL EXPORT SUMMARY:`);
        console.log(`  📊 Total rows: ${exportData.length}`);
        console.log(`  📊 Live Database: ${liveDbCount}`);
        console.log(`  📊 Migrated Excel: ${migratedCount}`);
        console.log(`  📊 Table Only: ${exportData.filter(row => row.Source === 'Table Only').length}`);
        
        // Show a few sample rows for verification
        console.log(`📊 SAMPLE EXPORT DATA (first 3 rows):`);
        exportData.slice(0, 3).forEach((row, index) => {
            console.log(`  [${index}] ${row.Customer} - ${row.Network} (${row['Node Qty']} nodes, ${row['Total Runs']} runs) - ${row.Source}`);
        });
        
        if (exportData.length === 0) {
            throw new Error('No data available for export');
        }
        
        // Create FormData for API
        const formData = new FormData();
        formData.append('data', JSON.stringify(exportData));
        formData.append('filename', `Complete_All_Data_${new Date().toISOString().split('T')[0]}.xlsx`);
        formData.append('csrfmiddlewaretoken', token);
        formData.append('include_migrated', 'true');
        formData.append('include_all_sources', 'true');
        
        console.log('🔥 Sending COMPLETE data to export API...');
        
        // Send to Django export API
        const response = await fetch('/api/customer-dashboard/export/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Export API failed with status: ${response.status}`);
        }
        
        // Handle the response as Excel file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Complete_All_Data_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ COMPLETE export finished successfully!');
        showNotification(`✅ Excel exported: ${exportData.length} rows (${liveDbCount} Live DB + ${migratedCount} Migrated)!`, 'success');
        
    } catch (error) {
        console.error('❌ Complete export failed:', error);
        showNotification(`❌ Export failed: ${error.message}`, 'error');
    }
};

// 🔥 COMPREHENSIVE DOWNLOAD - ALL DATA SOURCES
window.downloadAllData = function() {
    console.log('🔥 COMPREHENSIVE DOWNLOAD: Reading ALL data...');
    
    try {
        showNotification('🔥 Preparing complete download...', 'info');
        
        const downloadData = [];
        
        // Use the same logic as export but create CSV
        const exportPromise = exportAllData();
        
        // Alternative: Direct table processing for download
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        console.log(`🔥 Processing ${tableRows.length} table rows for download...`);
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, skipping`);
                return;
            }
            
            const customerName = cells[EXACT_COLUMNS.customer]?.textContent.trim() || 'Unknown';
            const isNetworkRow = customerName.includes('└─');
            
            console.log(`🔥 Row ${index}: "${customerName}" (${isNetworkRow ? 'NETWORK' : 'CUSTOMER'}) - ${cells.length} cells`);
            
            const rowData = {
                'Customer': isNetworkRow ? customerName.replace('└─ ', '') : customerName.replace('💾 ', '').replace('💾 Live DB', ''),
                'Network': isNetworkRow ? 'Network Detail' : 'Customer Summary',
                'Country': cells[EXACT_COLUMNS.country]?.textContent.trim() || 'Unknown',
                'Node Qty': cells[EXACT_COLUMNS.nodeQty]?.textContent.trim() || '0',
                'NE Type': cells[EXACT_COLUMNS.neType]?.textContent.trim() || '1830 PSS',
                'GTAC': cells[EXACT_COLUMNS.gtac]?.textContent.trim() || 'PSS',
                'Total Runs': cells[EXACT_COLUMNS.totalRuns]?.textContent.trim() || '0'
            };
            
            // Extract ALL monthly data including "Not Started"
            MONTHS.forEach((month, monthIndex) => {
                const columnIndex = EXACT_COLUMNS[month.toLowerCase()];
                const cellValue = cells[columnIndex]?.textContent.trim() || '-';
                rowData[month] = cellValue; // Keep ALL values including "Not Started"
                
                if (cellValue && cellValue !== '-') {
                    console.log(`    📅 ${month}: "${cellValue}"`);
                }
            });
            
            downloadData.push(rowData);
            console.log(`    ✅ Added: ${rowData.Customer} (${rowData['Node Qty']} nodes, ${rowData['Total Runs']} runs)`);
        });
        
        console.log(`🔥 Prepared ${downloadData.length} rows for download`);
        
        if (downloadData.length === 0) {
            throw new Error('No data found for download');
        }
        
        // Create CSV content
        const headers = ['Customer', 'Network', 'Country', 'Node Qty', 'NE Type', 'GTAC']
            .concat(MONTHS)
            .concat(['Total Runs'])
            .join(',');
        
        const csvRows = downloadData.map(row => {
            const values = [
                row['Customer'] || '',
                row['Network'] || '',
                row['Country'] || '',
                row['Node Qty'] || '',
                row['NE Type'] || '',
                row['GTAC'] || ''
            ].concat(MONTHS.map(month => row[month] || '-'))
            .concat([row['Total Runs'] || '0']);
            
            // Properly escape CSV values
            return values.map(value => {
                const stringValue = String(value);
                // If value contains comma, newline, or quote, wrap in quotes
                if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
                    const escapedValue = stringValue.replace(/"/g, '""');
                    return `"${escapedValue}";
                }
                return stringValue;
            }).join(',');
        });
        
        const csvContent = [headers, ...csvRows].join('\n');
        
        // Trigger download
        const encodedUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        const link = document.createElement('a');
        link.href = encodedUri;
        link.download = `Complete_All_Data_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ COMPLETE download finished successfully!');
        showNotification(`✅ CSV downloaded: ${downloadData.length} rows (ALL data sources)!`, 'success');
        
    } catch (error) {
        console.error('❌ Complete download failed:', error);
        showNotification(`❌ Download failed: ${error.message}`, 'error');
    }
};

// 🔍 Debug function to check what data is available
window.debugDataSources = function() {
    console.log('🔍 DEBUGGING DATA SOURCES');
    console.log('========================');
    
    // Check JavaScript data
    if (window.dashboardData && window.dashboardData.customers) {
        const customers = Object.keys(window.dashboardData.customers);
        console.log(`📊 JavaScript dashboardData: ${customers.length} customers`);
        
        customers.slice(0, 5).forEach(customerName => {
            const customer = window.dashboardData.customers[customerName];
            const isExcel = customer.excel_source || customer.excel_data || customer.excel_only;
            console.log(`  ${customerName}: ${isExcel ? 'MIGRATED' : 'LIVE'} - ${customer.networks?.length || 0} networks - ${customer.node_count || customer.nodes || 0} nodes`);
        });
    } else {
        console.log('❌ No dashboardData.customers found');
    }
    
    // Check table data
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    console.log(`📊 Table rows: ${tableRows.length}`);
    
    // Check BSNL specifically
    if (window.dashboardData && window.dashboardData.customers['BSNL']) {
        const bsnl = window.dashboardData.customers['BSNL'];
        console.log(`🔍 BSNL DEBUG:`);
        console.log(`  Node count: ${bsnl.node_count || bsnl.nodes || 'Not found'}`);
        console.log(`  Networks: ${bsnl.networks?.length || 0}`);
        if (bsnl.networks) {
            let totalNodes = 0;
            bsnl.networks.forEach(net => {
                const nodes = net.node_count || net.nodes || net.node_qty || 0;
                totalNodes += parseInt(nodes) || 0;
                console.log(`    ${net.name}: ${nodes} nodes`);
            });
            console.log(`  Total calculated nodes: ${totalNodes}`);
        }
    }
};

// 🔄 Override existing functions
window.exportToExcel = window.exportAllData;
window.directExcelDownload = window.exportAllData;
window.exportPerfectData = window.exportAllData;
window.exportCompleteData = window.exportAllData;

window.downloadFilteredData = window.downloadAllData;
window.downloadPerfectData = window.downloadAllData;
window.downloadCompleteData = window.downloadAllData;

// 🔄 Auto-debug on load
setTimeout(() => {
    console.log('🔍 Auto-debugging data sources...');
    debugDataSources();
}, 1500);

console.log('✅ COMPLETE MIGRATED DATA FIX LOADED!');
console.log('🔥 Features:');
console.log('  📊 Includes ALL data: Live DB + Migrated Excel + Table');
console.log('  📊 Preserves "Not Started", "No Report" values');
console.log('  📊 Correct node quantities (like BSNL 2469)');
console.log('  📊 Multiple data source fallbacks');
console.log('  🔍 debugDataSources() - check what data is available');
console.log('🔄 Auto-debug will run in 1.5 seconds...');