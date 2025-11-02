// 🔄 COMPLETE FIX FOR DOWNLOAD FUNCTIONALITY
// This ensures downloads have proper dates and data

console.log('🔄 Loading DOWNLOAD FUNCTION FIX...');

// 🔄 FIXED DOWNLOAD FUNCTION - 100% correct data
window.downloadFixedData = async function() {
    console.log('🔄 Starting FIXED download with proper data...');
    
    try {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            throw new Error('No CSRF token found');
        }
        
        // Show loading notification
        showNotification('📊 Preparing download with all dates...', 'info');
        
        // Prepare download data with correct dates from table
        const downloadData = [];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        // Extract data from visible table
        console.log('📊 Reading data directly from visible table...');
        const tableRows = document.querySelectorAll('#customer-table tbody tr');
        
        tableRows.forEach(row => {
            // Get customer name from first cell
            const nameCell = row.querySelector('.customer-name-cell');
            if (!nameCell) return;
            
            const customerName = nameCell.textContent.trim();
            const isNetworkRow = row.classList.contains('network-detail');
            
            // Only process customer summary rows
            if (!isNetworkRow) {
                console.log(`📊 Processing customer row: ${customerName}`);
                
                const cells = row.querySelectorAll('td');
                if (cells.length < 12) return; // Ensure we have month cells
                
                // Create customer row data
                const rowData = {
                    'Customer': customerName,
                    'Network': 'All Networks',
                    'Country': cells[1]?.textContent.trim() || 'Unknown',
                    'Total Runs': cells[cells.length - 1]?.textContent.trim() || '0'
                };
                
                // Extract month data directly from table cells
                months.forEach((month, index) => {
                    const monthCell = cells[index + 4]; // Month cells start at index 4
                    if (monthCell) {
                        const cellValue = monthCell.textContent.trim();
                        rowData[month] = cellValue !== '-' ? cellValue : '-';
                    } else {
                        rowData[month] = '-';
                    }
                });
                
                downloadData.push(rowData);
            }
            // Process network rows
            else {
                const networkName = nameCell.textContent.trim();
                console.log(`  📊 Processing network: ${networkName}`);
                
                const cells = row.querySelectorAll('td');
                if (cells.length < 12) return;
                
                // Create network row data
                const rowData = {
                    'Customer': customerName.split('└─')[1]?.trim() || customerName,
                    'Network': networkName,
                    'Node Qty': cells[2]?.textContent.trim() || '0',
                    'NE Type': cells[3]?.textContent.trim() || '1830 PSS',
                    'Total Runs': cells[cells.length - 1]?.textContent.trim() || '0'
                };
                
                // Extract month data directly from table cells
                months.forEach((month, index) => {
                    const monthCell = cells[index + 4]; // Month cells start at index 4
                    if (monthCell) {
                        const cellValue = monthCell.textContent.trim();
                        rowData[month] = cellValue !== '-' ? cellValue : '-';
                    } else {
                        rowData[month] = '-';
                    }
                });
                
                downloadData.push(rowData);
            }
        });
        
        console.log(`📊 Prepared ${downloadData.length} rows from table`);
        
        if (downloadData.length === 0) {
            throw new Error('No data to download');
        }
        
        // Convert to CSV format
        const headers = ['Customer', 'Network', 'Country', 'Node Qty', 'NE Type', 'Total Runs']
            .concat(months)
            .join(',');
            
        const rows = downloadData.map(row => {
            return [
                `"${row['Customer'] || ''}"`,
                `"${row['Network'] || ''}"`,
                `"${row['Country'] || ''}"`,
                `"${row['Node Qty'] || ''}"`,
                `"${row['NE Type'] || ''}"`,
                `"${row['Total Runs'] || ''}"`,
                ...months.map(month => `"${row[month] || '-'}"`)
            ].join(',');
        });
        
        const csvContent = [headers, ...rows].join('\\n');
        const encodedUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        
        // Trigger download
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `Customer_Dashboard_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Download completed with all dates!');
        showNotification('✅ Downloaded successfully with all dates!', 'success');
        
    } catch (error) {
        console.error('❌ Download failed:', error);
        showNotification(`❌ Download failed: ${error.message}`, 'error');
    }
};

// 🔄 OVERRIDE ORIGINAL DOWNLOAD FUNCTIONS
window.downloadFilteredData = window.downloadFixedData;

console.log('✅ DOWNLOAD FIX LOADED!');
console.log('🔄 Downloads will now include all dates from table!');