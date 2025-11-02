// 🎯 DIRECT TABLE SCRAPER
// Exports EXACTLY what you see in the dashboard table

console.log('🎯 Loading DIRECT TABLE SCRAPER...');

// 🎯 DIRECT EXPORT FROM VISIBLE TABLE
window.exportExactTableData = async function() {
    console.log('🎯 DIRECT EXPORT: Reading EXACTLY what is visible in table...');
    
    try {
        const token = getCsrfToken();
        if (!token) throw new Error('No CSRF token found');
        
        showNotification('🎯 Exporting EXACT table data...', 'info');
        
        const exportData = [];
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        
        console.log(`🎯 Found ${tableRows.length} visible table rows`);
        
        // Process each visible row
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, skipping`);
                return;
            }
            
            console.log(`🎯 Processing row ${index}:`);
            
            // Extract data EXACTLY as shown in table
            const rowData = {
                'Customer': cells[0]?.textContent.trim().replace('💾 ', '').replace('💾 Live DB', '').replace('Last run: Never', '').replace('Last run: Oct 9, 25', '').replace('Last run: Oct 8, 25', '').replace('Last run: Oct 10, 25', '').replace('Last run: Date missing', '').replace('└─ ', '') || 'Unknown',
                'Country': cells[1]?.textContent.trim() || 'Unknown',
                'Networks': cells[2]?.textContent.trim() || '0',
                'Node_Qty': cells[3]?.textContent.trim() || '0',
                'NE_Type': cells[4]?.textContent.trim() || '1830 PSS',
                'GTAC': cells[5]?.textContent.trim() || 'PSS',
                'Jan': cells[6]?.textContent.trim() || '-',
                'Feb': cells[7]?.textContent.trim() || '-',
                'Mar': cells[8]?.textContent.trim() || '-',
                'Apr': cells[9]?.textContent.trim() || '-',
                'May': cells[10]?.textContent.trim() || '-',
                'Jun': cells[11]?.textContent.trim() || '-',
                'Jul': cells[12]?.textContent.trim() || '-',
                'Aug': cells[13]?.textContent.trim() || '-',
                'Sep': cells[14]?.textContent.trim() || '-',
                'Oct': cells[15]?.textContent.trim() || '-',
                'Nov': cells[16]?.textContent.trim() || '-',
                'Dec': cells[17]?.textContent.trim() || '-',
                'Total_Runs': cells[18]?.textContent.trim() || '0'
            };
            
            // Log what we extracted
            console.log(`  Customer: "${rowData.Customer}"`);
            console.log(`  Node_Qty: "${rowData.Node_Qty}"`);
            console.log(`  Total_Runs: "${rowData.Total_Runs}"`);
            
            // Log months with data
            const monthsWithData = [];
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].forEach(month => {
                if (rowData[month] && rowData[month] !== '-') {
                    monthsWithData.push(`${month}: "${rowData[month]}"`);
                }
            });
            if (monthsWithData.length > 0) {
                console.log(`  Months: ${monthsWithData.join(', ')}`);
            }
            
            exportData.push(rowData);
            console.log(`  ✅ Added row ${index}`);
        });
        
        console.log(`🎯 Extracted ${exportData.length} rows from visible table`);
        
        // Show some sample data
        console.log('📊 SAMPLE EXTRACTED DATA:');
        exportData.slice(0, 3).forEach((row, index) => {
            console.log(`  [${index}] ${row.Customer}: ${row.Node_Qty} nodes, ${row.Total_Runs} runs`);
        });
        
        if (exportData.length === 0) {
            throw new Error('No data extracted from table');
        }
        
        // Create FormData for API
        const formData = new FormData();
        formData.append('data', JSON.stringify(exportData));
        formData.append('filename', `Direct_Table_Export_${new Date().toISOString().split('T')[0]}.xlsx`);
        formData.append('csrfmiddlewaretoken', token);
        
        console.log('🎯 Sending direct table data to export API...');
        
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
        a.download = `Direct_Table_Export_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ Direct table export finished successfully!');
        showNotification(`✅ Excel exported with ${exportData.length} rows (direct from table)!`, 'success');
        
    } catch (error) {
        console.error('❌ Direct export failed:', error);
        showNotification(`❌ Export failed: ${error.message}`, 'error');
    }
};

// 🎯 DIRECT DOWNLOAD FROM VISIBLE TABLE
window.downloadExactTableData = function() {
    console.log('🎯 DIRECT DOWNLOAD: Creating CSV from visible table...');
    
    try {
        showNotification('🎯 Creating CSV from exact table data...', 'info');
        
        const downloadData = [];
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        
        console.log(`🎯 Processing ${tableRows.length} visible rows for CSV...`);
        
        // Process each visible row
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, skipping`);
                return;
            }
            
            // Extract EXACTLY what's visible
            const rowData = [];
            cells.forEach((cell, cellIndex) => {
                let cellText = cell.textContent.trim();
                
                // Clean up customer names
                if (cellIndex === 0) {
                    cellText = cellText.replace('💾 ', '').replace('💾 Live DB', '')
                                     .replace(/Last run: [^\n]*/g, '')
                                     .replace('└─ ', '')
                                     .trim();
                }
                
                rowData.push(cellText || '-');
            });
            
            downloadData.push(rowData);
            console.log(`🎯 Row ${index}: ${rowData[0]} - ${rowData[3]} nodes - ${rowData[18]} runs`);
        });
        
        console.log(`🎯 Prepared ${downloadData.length} rows for CSV`);
        
        if (downloadData.length === 0) {
            throw new Error('No data found in table for download');
        }
        
        // Create CSV headers
        const headers = [
            'Customer', 'Country', 'Networks', 'Node_Qty', 'NE_Type', 'GTAC',
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
            'Total_Runs'
        ];
        
        // Create CSV content
        const csvRows = [headers.join(',')];
        
        downloadData.forEach(rowData => {
            // Properly escape CSV values
            const escapedRow = rowData.map(value => {
                const stringValue = String(value || '');
                // If value contains comma, newline, or quote, wrap in quotes
                if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
                    const escapedValue = stringValue.replace(/"/g, '""');
                    return `"${escapedValue}"`;
                }
                return stringValue;
            });
            
            csvRows.push(escapedRow.join(','));
        });
        
        const csvContent = csvRows.join('\n');
        
        // Trigger download
        const encodedUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        const link = document.createElement('a');
        link.href = encodedUri;
        link.download = `Direct_Table_Download_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Direct table download finished successfully!');
        showNotification(`✅ CSV downloaded with ${downloadData.length} rows (direct from table)!`, 'success');
        
    } catch (error) {
        console.error('❌ Direct download failed:', error);
        showNotification(`❌ Download failed: ${error.message}`, 'error');
    }
};

// 🔍 Function to inspect what's actually in the table right now
window.inspectTableData = function() {
    console.log('🔍 INSPECTING CURRENT TABLE DATA');
    console.log('================================');
    
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    console.log(`📊 Found ${tableRows.length} table rows`);
    
    // Check first few rows in detail
    tableRows.forEach((row, index) => {
        if (index >= 5) return; // Only check first 5 rows
        
        const cells = row.querySelectorAll('td');
        console.log(`\n🔍 ROW ${index} (${cells.length} cells):`);
        
        cells.forEach((cell, cellIndex) => {
            const text = cell.textContent.trim();
            if (text && text !== '-') {
                console.log(`  [${cellIndex}] "${text}"`);
            }
        });
    });
    
    // Specifically look for BSNL
    const bsnlRows = Array.from(tableRows).filter(row => {
        const firstCell = row.querySelector('td:first-child');
        return firstCell && firstCell.textContent.includes('BSNL');
    });
    
    console.log(`\n🔍 BSNL ROWS FOUND: ${bsnlRows.length}`);
    bsnlRows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        console.log(`  BSNL Row ${index}:`);
        console.log(`    Customer: "${cells[0]?.textContent.trim()}"`);
        console.log(`    Node Qty: "${cells[3]?.textContent.trim()}"`);
        console.log(`    Total Runs: "${cells[18]?.textContent.trim()}"`);
        console.log(`    Oct: "${cells[15]?.textContent.trim()}"`);
    });
};

// 🔄 Override existing export/download functions
window.exportToExcel = window.exportExactTableData;
window.directExcelDownload = window.exportExactTableData;
window.exportPerfectData = window.exportExactTableData;
window.exportCompleteData = window.exportExactTableData;
window.exportAllData = window.exportExactTableData;

window.downloadFilteredData = window.downloadExactTableData;
window.downloadPerfectData = window.downloadExactTableData;
window.downloadCompleteData = window.downloadExactTableData;
window.downloadAllData = window.downloadExactTableData;

// 🔄 Auto-inspect table on load
setTimeout(() => {
    console.log('🔍 Auto-inspecting table data...');
    inspectTableData();
}, 1000);

console.log('✅ DIRECT TABLE SCRAPER LOADED!');
console.log('🎯 This will export EXACTLY what you see in the table');
console.log('📊 Functions available:');
console.log('  - exportExactTableData() - Export exactly what\'s in table');
console.log('  - downloadExactTableData() - Download exactly what\'s in table');
console.log('  - inspectTableData() - See what\'s in table right now');
console.log('🔄 Auto-inspection will run in 1 second...');