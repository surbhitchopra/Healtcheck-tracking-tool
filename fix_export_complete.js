// 🔥 COMPLETE FIX: Export/Download with MIGRATED DATA + NODE QTY
// This includes ALL customers: Live DB + Migrated Excel with proper node counts

console.log('🔥 Loading COMPLETE EXPORT/DOWNLOAD FIX...');

// 📊 COMPREHENSIVE EXPORT WITH ALL DATA
window.exportCompleteData = async function() {
    console.log('📊 COMPREHENSIVE EXPORT: Including ALL customers + migrated data + node qty...');
    
    try {
        const token = getCsrfToken();
        if (!token) throw new Error('No CSRF token found');
        
        showNotification('📊 Generating complete export with ALL data...', 'info');
        
        const exportData = [];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        console.log('📊 Processing ALL customers (Live DB + Migrated Excel)...');
        
        // 🔥 PROCESS ALL CUSTOMERS - NO EXCLUSIONS
        Object.values(dashboardData.customers).forEach(customer => {
            const isExcel = customer.excel_source || customer.excel_data || customer.excel_only;
            console.log(`📊 Processing: ${customer.name} (${isExcel ? 'MIGRATED EXCEL' : 'LIVE DB'})`);
            
            // Check if customer has networks
            if (customer.networks && customer.networks.length > 0) {
                customer.networks.forEach((network, networkIndex) => {
                    console.log(`  🔧 Network: ${network.name} | Node Qty: ${network.node_count || network.nodes || network.node_qty || 0}`);
                    
                    const rowData = {
                        'Customer': customer.name || 'Unknown',
                        'Network': network.name || network.network_name || `Network ${networkIndex + 1}`,
                        'Country': customer.country || 'Unknown',
                        'Node Qty': network.node_count || network.nodes || network.node_qty || customer.node_count || customer.nodes || customer.node_qty || 0,
                        'NE Type': network.ne_type || network.platform || customer.ne_type || network.ne || '1830 PSS',
                        'GTAC': network.gtac || network.gateway || customer.gtac || 'PSS',
                        'Total Runs': network.runs || network.total_runs || network.run_count || 0,
                        'Last Run Date': network.last_run_date || customer.last_run_date || 'Never',
                        'Source': isExcel ? 'Migrated Excel' : 'Live Database'
                    };
                    
                    // 📅 EXTRACT MONTH DATA WITH COMPREHENSIVE METHODS
                    months.forEach((month, monthIndex) => {
                        let monthValue = '-';
                        
                        try {
                            // METHOD 1: Network months array
                            if (network.months && Array.isArray(network.months) && network.months[monthIndex]) {
                                monthValue = network.months[monthIndex];
                                console.log(`    ✅ ${month}: "${monthValue}" (network.months)`);
                            }
                            // METHOD 2: Network monthly_runs array
                            else if (network.monthly_runs && Array.isArray(network.monthly_runs) && network.monthly_runs[monthIndex]) {
                                monthValue = network.monthly_runs[monthIndex];
                                console.log(`    ✅ ${month}: "${monthValue}" (network.monthly_runs)`);
                            }
                            // METHOD 3: Customer level months array
                            else if (customer.months && Array.isArray(customer.months) && customer.months[monthIndex]) {
                                monthValue = customer.months[monthIndex];
                                console.log(`    ✅ ${month}: "${monthValue}" (customer.months)`);
                            }
                            // METHOD 4: Customer network_monthly_runs object
                            else if (customer.network_monthly_runs && 
                                     customer.network_monthly_runs[network.name] && 
                                     customer.network_monthly_runs[network.name][monthIndex + 1]) {
                                monthValue = customer.network_monthly_runs[network.name][monthIndex + 1];
                                console.log(`    ✅ ${month}: "${monthValue}" (customer.network_monthly_runs)`);
                            }
                            // METHOD 5: Try dashboard extraction function
                            else if (typeof getNetworkMonthRunDates === 'function') {
                                try {
                                    const currentYear = new Date().getFullYear();
                                    const monthData = getNetworkMonthRunDates(customer, network.name, currentYear, monthIndex + 1);
                                    if (monthData && monthData.date && monthData.date !== '-') {
                                        monthValue = monthData.date;
                                        console.log(`    ✅ ${month}: "${monthValue}" (extraction function)`);
                                    }
                                } catch (e) {
                                    // Silent fallback
                                }
                            }
                        } catch (error) {
                            console.log(`    ⚠️ Error extracting ${month} for ${network.name}:`, error.message);
                        }
                        
                        // Clean and validate the value
                        if (monthValue && 
                            monthValue !== '-' && 
                            monthValue !== 'Never' && 
                            monthValue !== 'Not Run' && 
                            monthValue !== 'Not Started' &&
                            monthValue !== 'No Report') {
                            rowData[month] = monthValue;
                        } else {
                            rowData[month] = '-';
                        }
                    });
                    
                    exportData.push(rowData);
                    console.log(`    ✅ Added network: ${rowData.Customer} - ${rowData.Network} (${rowData.Source})`);
                });
            } else {
                // Customer without networks - still include in export
                console.log(`  ℹ️ Customer has no networks, adding customer-level entry`);
                
                const rowData = {
                    'Customer': customer.name || 'Unknown',
                    'Network': 'No Networks',
                    'Country': customer.country || 'Unknown',
                    'Node Qty': customer.node_count || customer.nodes || customer.node_qty || 0,
                    'NE Type': customer.ne_type || '1830 PSS',
                    'GTAC': customer.gtac || 'PSS',
                    'Total Runs': customer.runs || customer.total_runs || customer.run_count || 0,
                    'Last Run Date': customer.last_run_date || 'Never',
                    'Source': isExcel ? 'Migrated Excel' : 'Live Database'
                };
                
                // Add customer-level monthly data
                months.forEach((month, monthIndex) => {
                    let monthValue = '-';
                    
                    if (customer.months && customer.months[monthIndex]) {
                        monthValue = customer.months[monthIndex];
                    } else if (customer.monthly_runs && customer.monthly_runs[monthIndex]) {
                        monthValue = customer.monthly_runs[monthIndex];
                    }
                    
                    rowData[month] = (monthValue && monthValue !== '-') ? monthValue : '-';
                });
                
                exportData.push(rowData);
                console.log(`    ✅ Added customer-only: ${rowData.Customer} (${rowData.Source})`);
            }
        });
        
        console.log(`📊 Prepared ${exportData.length} total rows for export`);
        console.log(`📊 Breakdown:`);
        const liveDbCount = exportData.filter(row => row.Source === 'Live Database').length;
        const excelCount = exportData.filter(row => row.Source === 'Migrated Excel').length;
        console.log(`  📊 Live Database entries: ${liveDbCount}`);
        console.log(`  📊 Migrated Excel entries: ${excelCount}`);
        
        if (exportData.length === 0) {
            throw new Error('No data available for export');
        }
        
        // Create FormData for API
        const formData = new FormData();
        formData.append('data', JSON.stringify(exportData));
        formData.append('filename', `Complete_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`);
        formData.append('csrfmiddlewaretoken', token);
        formData.append('include_all', 'true'); // Flag to include all data types
        
        console.log('📊 Sending complete data to export API...');
        
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
        a.download = `Complete_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ Complete export finished successfully!');
        showNotification(`✅ Excel exported with ${exportData.length} rows (${liveDbCount} Live DB + ${excelCount} Migrated)!`, 'success');
        
    } catch (error) {
        console.error('❌ Complete export failed:', error);
        showNotification(`❌ Export failed: ${error.message}`, 'error');
    }
};

// 📋 COMPREHENSIVE DOWNLOAD WITH ALL DATA
window.downloadCompleteData = function() {
    console.log('📋 COMPREHENSIVE DOWNLOAD: Reading ALL table data...');
    
    try {
        showNotification('📋 Preparing complete download...', 'info');
        
        const downloadData = [];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        // Read ALL table rows (customer summary + network details)
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        console.log(`📋 Found ${tableRows.length} table rows to process`);
        
        tableRows.forEach((row, index) => {
            const nameCell = row.querySelector('.customer-name-cell');
            if (!nameCell) return;
            
            const customerName = nameCell.textContent.trim();
            const cells = row.querySelectorAll('td');
            
            if (cells.length < 12) {
                console.log(`  ⚠️ Row ${index}: Not enough cells (${cells.length}), skipping`);
                return;
            }
            
            // Determine if this is a customer summary or network detail row
            const isNetworkRow = customerName.includes('└─') || row.classList.contains('network-detail');
            const isCustomerSummary = !isNetworkRow && !customerName.includes('└─');
            
            console.log(`📋 Processing row ${index}: ${customerName} (${isNetworkRow ? 'NETWORK' : 'CUSTOMER'})`);
            
            // Extract basic data
            const rowData = {
                'Customer': isNetworkRow ? customerName.replace('└─ ', '') : customerName,
                'Network': isNetworkRow ? 'Network Detail' : 'Customer Summary',
                'Country': cells[1]?.textContent.trim() || 'Unknown',
                'Node Qty': cells[2]?.textContent.trim() || '0',
                'NE Type': cells[3]?.textContent.trim() || '1830 PSS',
                'GTAC': cells[4]?.textContent.trim() || 'PSS',
                'Total Runs': cells[cells.length - 1]?.textContent.trim() || '0'
            };
            
            // Extract monthly data from table cells
            months.forEach((month, monthIndex) => {
                // Month columns typically start after the first few columns
                // Adjust the column index based on your table structure
                const monthColumnIndex = 5 + monthIndex; // Assuming months start at column 5
                
                if (monthColumnIndex < cells.length) {
                    const monthCell = cells[monthColumnIndex];
                    const cellValue = monthCell ? monthCell.textContent.trim() : '-';
                    
                    // Include all values, even special ones like "Not Started", "No Report"
                    rowData[month] = cellValue || '-';
                    
                    if (cellValue && cellValue !== '-') {
                        console.log(`    📅 ${month}: "${cellValue}"`);
                    }
                } else {
                    rowData[month] = '-';
                }
            });
            
            downloadData.push(rowData);
            console.log(`    ✅ Added: ${rowData.Customer} - ${rowData.Network}`);
        });
        
        console.log(`📋 Prepared ${downloadData.length} rows from table`);
        
        if (downloadData.length === 0) {
            throw new Error('No data found in table to download');
        }
        
        // Create CSV content
        const headers = ['Customer', 'Network', 'Country', 'Node Qty', 'NE Type', 'GTAC', 'Total Runs']
            .concat(months)
            .join(',');
        
        const csvRows = downloadData.map(row => {
            const values = [
                row['Customer'] || '',
                row['Network'] || '',
                row['Country'] || '',
                row['Node Qty'] || '',
                row['NE Type'] || '',
                row['GTAC'] || '',
                row['Total Runs'] || ''
            ].concat(months.map(month => row[month] || '-'));
            
            // Wrap each value in quotes and escape any existing quotes
            return values.map(value => {
                const stringValue = String(value);
                const escapedValue = stringValue.replace(/"/g, '""'); // Escape quotes
                return `"${escapedValue}"`; // Wrap in quotes
            }).join(',');
        });
        
        const csvContent = [headers, ...csvRows].join('\\n');
        
        // Trigger download
        const encodedUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        const link = document.createElement('a');
        link.href = encodedUri;
        link.download = `Complete_Dashboard_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Complete download finished successfully!');
        showNotification(`✅ CSV downloaded with ${downloadData.length} rows!`, 'success');
        
    } catch (error) {
        console.error('❌ Complete download failed:', error);
        showNotification(`❌ Download failed: ${error.message}`, 'error');
    }
};

// 🔄 OVERRIDE ALL EXPORT/DOWNLOAD FUNCTIONS
window.exportToExcel = window.exportCompleteData;
window.directExcelDownload = window.exportCompleteData;
window.exportToExcelFixed = window.exportCompleteData;
window.exportWithDates = window.exportCompleteData;

window.downloadFilteredData = window.downloadCompleteData;
window.downloadFromTable = window.downloadCompleteData;
window.downloadFixedData = window.downloadCompleteData;

console.log('✅ COMPLETE EXPORT/DOWNLOAD FIX LOADED!');
console.log('📊 Export: Includes ALL customers (Live DB + Migrated Excel)');
console.log('📋 Download: Includes ALL table data with proper node quantities');
console.log('🔥 Now both export and download will have complete data!');