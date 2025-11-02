// 🎯 PERFECT EXPORT/DOWNLOAD FIX
// Based on exact dashboard structure analysis

console.log('🎯 Loading PERFECT export/download fix...');

// 🎯 EXACT COLUMN MAPPING based on your dashboard
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

// 🎯 PERFECT EXPORT with exact column mapping
window.exportPerfectData = async function() {
    console.log('🎯 PERFECT EXPORT: Using exact column positions...');
    
    try {
        const token = getCsrfToken();
        if (!token) throw new Error('No CSRF token found');
        
        showNotification('🎯 Exporting with perfect structure...', 'info');
        
        const exportData = [];
        
        // Get all table rows
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        console.log(`🎯 Processing ${tableRows.length} rows with perfect mapping...`);
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, expected 19. Skipping.`);
                return;
            }
            
            const customerName = cells[EXACT_COLUMNS.customer]?.textContent.trim() || 'Unknown';
            const isNetworkRow = customerName.includes('└─');
            
            console.log(`🎯 Row ${index}: "${customerName}" (${isNetworkRow ? 'NETWORK' : 'CUSTOMER'}) - ${cells.length} cells`);
            
            const rowData = {
                'Customer': isNetworkRow ? customerName.replace('└─ ', '') : customerName.replace('💾 ', '').replace('💾 Live DB', ''),
                'Network': isNetworkRow ? 'Network Detail' : 'Customer Summary',
                'Country': cells[EXACT_COLUMNS.country]?.textContent.trim() || 'Unknown',
                'Node Qty': cells[EXACT_COLUMNS.nodeQty]?.textContent.trim() || '0',
                'NE Type': cells[EXACT_COLUMNS.neType]?.textContent.trim() || '1830 PSS',
                'GTAC': cells[EXACT_COLUMNS.gtac]?.textContent.trim() || 'PSS',
                'Total Runs': cells[EXACT_COLUMNS.totalRuns]?.textContent.trim() || '0'
            };
            
            // Extract monthly data using EXACT positions
            MONTHS.forEach((month, monthIndex) => {
                const columnIndex = EXACT_COLUMNS[month.toLowerCase()];
                const cellValue = cells[columnIndex]?.textContent.trim() || '-';
                rowData[month] = cellValue;
                
                if (cellValue && cellValue !== '-') {
                    console.log(`    📅 ${month}: "${cellValue}"`);
                }
            });
            
            exportData.push(rowData);
            console.log(`    ✅ Added: ${rowData.Customer} (${rowData['Total Runs']} runs)`);
        });
        
        console.log(`🎯 Prepared ${exportData.length} rows for perfect export`);
        
        if (exportData.length === 0) {
            throw new Error('No data available for export');
        }
        
        // Create FormData for API
        const formData = new FormData();
        formData.append('data', JSON.stringify(exportData));
        formData.append('filename', `Perfect_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`);
        formData.append('csrfmiddlewaretoken', token);
        
        console.log('🎯 Sending perfect data to export API...');
        
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
        a.download = `Perfect_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ Perfect export finished successfully!');
        showNotification(`✅ Excel exported with ${exportData.length} rows (perfect structure)!`, 'success');
        
    } catch (error) {
        console.error('❌ Perfect export failed:', error);
        showNotification(`❌ Export failed: ${error.message}`, 'error');
    }
};

// 🎯 PERFECT DOWNLOAD with exact column mapping
window.downloadPerfectData = function() {
    console.log('🎯 PERFECT DOWNLOAD: Using exact column positions...');
    
    try {
        showNotification('🎯 Preparing perfect download...', 'info');
        
        const downloadData = [];
        
        // Get all table rows
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        console.log(`🎯 Processing ${tableRows.length} rows for perfect download...`);
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, expected 19. Skipping.`);
                return;
            }
            
            const customerName = cells[EXACT_COLUMNS.customer]?.textContent.trim() || 'Unknown';
            const isNetworkRow = customerName.includes('└─');
            
            console.log(`🎯 Row ${index}: "${customerName}" (${isNetworkRow ? 'NETWORK' : 'CUSTOMER'}) - ${cells.length} cells`);
            
            const rowData = {
                'Customer': isNetworkRow ? customerName.replace('└─ ', '') : customerName.replace('💾 ', '').replace('💾 Live DB', ''),
                'Network': isNetworkRow ? 'Network Detail' : 'Customer Summary',
                'Country': cells[EXACT_COLUMNS.country]?.textContent.trim() || 'Unknown',
                'Node Qty': cells[EXACT_COLUMNS.nodeQty]?.textContent.trim() || '0',
                'NE Type': cells[EXACT_COLUMNS.neType]?.textContent.trim() || '1830 PSS',
                'GTAC': cells[EXACT_COLUMNS.gtac]?.textContent.trim() || 'PSS',
                'Total Runs': cells[EXACT_COLUMNS.totalRuns]?.textContent.trim() || '0'
            };
            
            // Extract monthly data using EXACT positions
            MONTHS.forEach((month, monthIndex) => {
                const columnIndex = EXACT_COLUMNS[month.toLowerCase()];
                const cellValue = cells[columnIndex]?.textContent.trim() || '-';
                rowData[month] = cellValue;
                
                if (cellValue && cellValue !== '-') {
                    console.log(`    📅 ${month}: "${cellValue}"`);
                }
            });
            
            downloadData.push(rowData);
            console.log(`    ✅ Added: ${rowData.Customer} (${rowData['Total Runs']} runs)`);
        });
        
        console.log(`🎯 Prepared ${downloadData.length} rows for perfect download`);
        
        if (downloadData.length === 0) {
            throw new Error('No data found in table to download');
        }
        
        // Create CSV content with exact structure
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
            
            // Wrap each value in quotes and escape any existing quotes
            return values.map(value => {
                const stringValue = String(value);
                const escapedValue = stringValue.replace(/"/g, '""'); // Escape quotes
                return `"${escapedValue}"`; // Wrap in quotes
            }).join(',');
        });
        
        const csvContent = [headers, ...csvRows].join('\n');
        
        // Trigger download
        const encodedUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        const link = document.createElement('a');
        link.href = encodedUri;
        link.download = `Perfect_Dashboard_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Perfect download finished successfully!');
        showNotification(`✅ CSV downloaded with ${downloadData.length} rows (perfect structure)!`, 'success');
        
    } catch (error) {
        console.error('❌ Perfect download failed:', error);
        showNotification(`❌ Download failed: ${error.message}`, 'error');
    }
};

// 🎯 Test function to verify column mapping
window.testColumnMapping = function() {
    console.log('🎯 TESTING COLUMN MAPPING');
    console.log('=========================');
    
    const firstRow = document.querySelector('#customer-table-body tr');
    if (!firstRow) {
        console.log('❌ No rows found');
        return;
    }
    
    const cells = firstRow.querySelectorAll('td');
    console.log(`📊 First row has ${cells.length} cells`);
    
    // Test each mapped column
    Object.entries(EXACT_COLUMNS).forEach(([name, index]) => {
        const value = cells[index]?.textContent.trim() || 'EMPTY';
        console.log(`  [${index}] ${name}: "${value}"`);
    });
    
    // Test specifically for Worldlink issue
    const worldlinkRows = Array.from(document.querySelectorAll('#customer-table-body tr')).filter(row => {
        const nameCell = row.querySelector('td:first-child');
        return nameCell && nameCell.textContent.includes('Worldlink');
    });
    
    console.log(`\n🔍 Found ${worldlinkRows.length} Worldlink rows:`);
    worldlinkRows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        console.log(`  Worldlink row ${index}: ${cells.length} cells`);
        console.log(`    Aug: "${cells[EXACT_COLUMNS.aug]?.textContent.trim() || 'EMPTY'}"`);
        console.log(`    Total Runs: "${cells[EXACT_COLUMNS.totalRuns]?.textContent.trim() || 'EMPTY'}"`);
    });
};

// 🎯 Override existing functions with perfect versions
window.exportToExcel = window.exportPerfectData;
window.directExcelDownload = window.exportPerfectData;
window.exportToExcelFixed = window.exportPerfectData;
window.exportWithDates = window.exportPerfectData;
window.exportCompleteData = window.exportPerfectData;

window.downloadFilteredData = window.downloadPerfectData;
window.downloadFromTable = window.downloadPerfectData;
window.downloadFixedData = window.downloadPerfectData;
window.downloadCompleteData = window.downloadPerfectData;

// 🎯 Run test on load
setTimeout(() => {
    console.log('🎯 Auto-testing column mapping...');
    testColumnMapping();
}, 1000);

console.log('✅ PERFECT EXPORT/DOWNLOAD FIX LOADED!');
console.log('🎯 Based on your EXACT dashboard structure:');
console.log('  📊 19 columns total (Customer=0, Country=1, Networks=2, ..., Total Runs=18)');
console.log('  📅 Months at positions 6-17 (Jan=6, Feb=7, ..., Dec=17)');
console.log('  🔧 Handles network detail rows (└─) correctly');
console.log('  💾 Cleans customer names (removes 💾 symbols)');
console.log('🔄 Auto-testing will run in 1 second...');