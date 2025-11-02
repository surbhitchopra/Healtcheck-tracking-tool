// 🔍 DASHBOARD TABLE ANALYZER
// Analyze current table structure to understand data layout

console.log('🔍 Loading dashboard table analyzer...');

// 🔍 Function to analyze current table structure
window.analyzeDashboardTable = function() {
    console.log('🔍 ANALYZING DASHBOARD TABLE STRUCTURE');
    console.log('=====================================');
    
    try {
        const tableBody = document.querySelector('#customer-table-body');
        if (!tableBody) {
            console.log('❌ Table body not found');
            return;
        }
        
        const rows = tableBody.querySelectorAll('tr');
        console.log(`📊 Found ${rows.length} total rows`);
        
        // Analyze table headers
        const headerRow = document.querySelector('#customer-table thead tr');
        if (headerRow) {
            const headers = Array.from(headerRow.querySelectorAll('th')).map(th => th.textContent.trim());
            console.log('📋 TABLE HEADERS:', headers);
        }
        
        // Analyze first few rows in detail
        rows.forEach((row, index) => {
            if (index >= 5) return; // Only analyze first 5 rows
            
            const cells = row.querySelectorAll('td');
            console.log(`\n🔍 ROW ${index}:`);
            console.log(`  📊 Cell count: ${cells.length}`);
            
            cells.forEach((cell, cellIndex) => {
                const content = cell.textContent.trim();
                const classes = cell.className;
                console.log(`    [${cellIndex}] "${content}" (class: ${classes})`);
            });
            
            // Check for special row types
            const nameCell = row.querySelector('.customer-name-cell');
            if (nameCell) {
                const name = nameCell.textContent.trim();
                const isNetworkRow = name.includes('└─');
                const isCustomerSummary = !isNetworkRow;
                console.log(`  🏷️  Type: ${isNetworkRow ? 'NETWORK DETAIL' : 'CUSTOMER SUMMARY'}`);
                console.log(`  👤 Name: "${name}"`);
            }
        });
        
        return {
            totalRows: rows.length,
            analyzed: true
        };
        
    } catch (error) {
        console.error('❌ Error analyzing table:', error);
        return { error: error.message };
    }
};

// 🔍 Function to analyze dashboard data structure
window.analyzeDashboardData = function() {
    console.log('🔍 ANALYZING DASHBOARD DATA STRUCTURE');
    console.log('====================================');
    
    try {
        if (!window.dashboardData) {
            console.log('❌ dashboardData not found');
            return;
        }
        
        console.log('📊 dashboardData structure:');
        console.log('  Keys:', Object.keys(dashboardData));
        
        if (dashboardData.customers) {
            const customerNames = Object.keys(dashboardData.customers);
            console.log(`\n📊 Found ${customerNames.length} customers:`, customerNames);
            
            // Analyze first few customers in detail
            customerNames.slice(0, 3).forEach(customerName => {
                const customer = dashboardData.customers[customerName];
                console.log(`\n👤 CUSTOMER: ${customerName}`);
                console.log('  🔧 Properties:', Object.keys(customer));
                
                if (customer.networks) {
                    console.log(`  📡 Networks (${customer.networks.length}):`);
                    customer.networks.forEach((network, netIndex) => {
                        console.log(`    [${netIndex}] ${network.name || 'No name'}`);
                        console.log(`        Properties: ${Object.keys(network).join(', ')}`);
                        console.log(`        Node count: ${network.node_count || network.nodes || network.node_qty || 'N/A'}`);
                        console.log(`        Runs: ${network.runs || network.total_runs || network.run_count || 'N/A'}`);
                        if (network.months) {
                            console.log(`        Months: ${network.months.join(', ')}`);
                        }
                    });
                }
                
                // Check for different data sources
                const isExcel = customer.excel_source || customer.excel_data || customer.excel_only;
                console.log(`  📋 Source: ${isExcel ? 'MIGRATED EXCEL' : 'LIVE DATABASE'}`);
            });
        }
        
        return {
            totalCustomers: dashboardData.customers ? Object.keys(dashboardData.customers).length : 0,
            analyzed: true
        };
        
    } catch (error) {
        console.error('❌ Error analyzing dashboard data:', error);
        return { error: error.message };
    }
};

// 🔍 Function to find the correct column mapping
window.findColumnMapping = function() {
    console.log('🔍 FINDING COLUMN MAPPING');
    console.log('=========================');
    
    try {
        // Check table headers
        const headerRow = document.querySelector('#customer-table thead tr');
        if (!headerRow) {
            console.log('❌ No header row found');
            return null;
        }
        
        const headers = Array.from(headerRow.querySelectorAll('th')).map(th => th.textContent.trim());
        console.log('📋 Headers:', headers);
        
        // Find month columns
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthMapping = {};
        
        months.forEach(month => {
            const index = headers.findIndex(header => header.includes(month));
            if (index !== -1) {
                monthMapping[month] = index;
                console.log(`📅 ${month} is at column ${index}`);
            }
        });
        
        // Find other important columns
        const columnMapping = {
            customer: headers.findIndex(h => h.toLowerCase().includes('customer') || h.toLowerCase().includes('name')),
            country: headers.findIndex(h => h.toLowerCase().includes('country')),
            networks: headers.findIndex(h => h.toLowerCase().includes('network')),
            nodes: headers.findIndex(h => h.toLowerCase().includes('node')),
            neType: headers.findIndex(h => h.toLowerCase().includes('ne') || h.toLowerCase().includes('type')),
            gtac: headers.findIndex(h => h.toLowerCase().includes('gtac')),
            totalRuns: headers.findIndex(h => h.toLowerCase().includes('total') && h.toLowerCase().includes('run')),
            months: monthMapping
        };
        
        console.log('🗺️ Column mapping:', columnMapping);
        return columnMapping;
        
    } catch (error) {
        console.error('❌ Error finding column mapping:', error);
        return null;
    }
};

// 🔧 Corrected export function based on actual table structure
window.exportCorrectedData = async function() {
    console.log('📊 CORRECTED EXPORT based on table analysis...');
    
    try {
        // First analyze the structure
        const columnMapping = findColumnMapping();
        if (!columnMapping) {
            throw new Error('Could not determine column structure');
        }
        
        const token = getCsrfToken();
        if (!token) throw new Error('No CSRF token found');
        
        showNotification('📊 Exporting with corrected structure...', 'info');
        
        const exportData = [];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        // Read table rows with correct column mapping
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        console.log(`📊 Processing ${tableRows.length} rows with corrected mapping...`);
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 5) return; // Skip rows with too few cells
            
            const nameCell = row.querySelector('.customer-name-cell');
            if (!nameCell) return;
            
            const customerName = nameCell.textContent.trim();
            const isNetworkRow = customerName.includes('└─');
            
            console.log(`📊 Row ${index}: "${customerName}" (${isNetworkRow ? 'NETWORK' : 'CUSTOMER'})`);
            
            const rowData = {
                'Customer': isNetworkRow ? customerName.replace('└─ ', '') : customerName,
                'Network': isNetworkRow ? 'Network Detail' : 'Customer Summary',
                'Country': columnMapping.country >= 0 ? (cells[columnMapping.country]?.textContent.trim() || 'Unknown') : 'Unknown',
                'Node Qty': columnMapping.nodes >= 0 ? (cells[columnMapping.nodes]?.textContent.trim() || '0') : '0',
                'NE Type': columnMapping.neType >= 0 ? (cells[columnMapping.neType]?.textContent.trim() || '1830 PSS') : '1830 PSS',
                'GTAC': columnMapping.gtac >= 0 ? (cells[columnMapping.gtac]?.textContent.trim() || 'PSS') : 'PSS',
                'Total Runs': columnMapping.totalRuns >= 0 ? (cells[columnMapping.totalRuns]?.textContent.trim() || '0') : '0'
            };
            
            // Extract monthly data using correct column mapping
            months.forEach(month => {
                const columnIndex = columnMapping.months[month];
                if (columnIndex >= 0 && columnIndex < cells.length) {
                    const cellValue = cells[columnIndex]?.textContent.trim() || '-';
                    rowData[month] = cellValue;
                    
                    if (cellValue && cellValue !== '-') {
                        console.log(`    📅 ${month}: "${cellValue}"`);
                    }
                } else {
                    rowData[month] = '-';
                }
            });
            
            exportData.push(rowData);
            console.log(`    ✅ Added: ${rowData.Customer} (${rowData['Total Runs']} runs)`);
        });
        
        console.log(`📊 Prepared ${exportData.length} rows for corrected export`);
        
        if (exportData.length === 0) {
            throw new Error('No data available for export');
        }
        
        // Create FormData for API
        const formData = new FormData();
        formData.append('data', JSON.stringify(exportData));
        formData.append('filename', `Corrected_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`);
        formData.append('csrfmiddlewaretoken', token);
        
        console.log('📊 Sending corrected data to export API...');
        
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
        a.download = `Corrected_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ Corrected export finished successfully!');
        showNotification(`✅ Excel exported with ${exportData.length} rows (corrected structure)!`, 'success');
        
    } catch (error) {
        console.error('❌ Corrected export failed:', error);
        showNotification(`❌ Export failed: ${error.message}`, 'error');
    }
};

// 🔧 Run analysis automatically
setTimeout(() => {
    console.log('🔍 Auto-running dashboard analysis...');
    analyzeDashboardTable();
    analyzeDashboardData();
    findColumnMapping();
}, 1000);

console.log('✅ DASHBOARD ANALYZER LOADED!');
console.log('🔍 Available functions:');
console.log('  - analyzeDashboardTable() - Analyze HTML table structure');
console.log('  - analyzeDashboardData() - Analyze JavaScript data structure');
console.log('  - findColumnMapping() - Find correct column positions');
console.log('  - exportCorrectedData() - Export with corrected structure');
console.log('🔄 Auto-analysis will run in 1 second...');