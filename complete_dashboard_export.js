// 🎯 COMPLETE DASHBOARD EXPORT SYSTEM
// New Export/Download buttons with ALL data exactly as shown in dashboard

console.log('🎯 Loading COMPLETE DASHBOARD EXPORT SYSTEM...');

// 🎯 MAIN EXPORT FUNCTION - EXACTLY AS DASHBOARD SHOWS
window.exportCompleteDashboard = async function() {
    console.log('🎯 COMPLETE EXPORT: All data exactly as shown in dashboard...');
    
    try {
        const token = getCsrfToken();
        if (!token) throw new Error('No CSRF token found');
        
        showNotification('🎯 Exporting COMPLETE dashboard data (Live + Migrated)...', 'info');
        
        const exportData = [];
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        
        console.log(`🎯 Processing ${tableRows.length} dashboard rows...`);
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, skipping`);
                return;
            }
            
            // Get raw customer name to determine row type
            const rawCustomerName = cells[0]?.textContent.trim() || 'Unknown';
            const isNetworkRow = rawCustomerName.includes('└─');
            
            console.log(`🎯 Row ${index}: "${rawCustomerName}" (${isNetworkRow ? 'NETWORK' : 'CUSTOMER'})`);
            
            // Clean customer name but preserve important info
            let cleanCustomerName = rawCustomerName
                .replace('💾 ', '')
                .replace('💾 Live DB', '')
                .replace(/Last run: [^\n]*/g, '')
                .trim();
            
            // For network rows, clean the └─ prefix
            if (isNetworkRow) {
                cleanCustomerName = cleanCustomerName.replace('└─ ', '');
            }
            
            // Extract ALL data exactly as shown
            const rowData = {
                'Customer': cleanCustomerName,
                'Row_Type': isNetworkRow ? 'Network Detail' : 'Customer Summary',
                'Country': cells[1]?.textContent.trim() || '',
                'Networks': cells[2]?.textContent.trim() || '',
                'Node_Qty': cells[3]?.textContent.trim() || '0',
                'NE_Type': cells[4]?.textContent.trim() || '',
                'GTAC': cells[5]?.textContent.trim() || '',
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
            
            // Log important data
            console.log(`  📊 ${cleanCustomerName}: ${rowData.Node_Qty} nodes, ${rowData.Total_Runs} runs`);
            
            // Log months with data
            const monthsWithData = [];
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].forEach(month => {
                if (rowData[month] && rowData[month] !== '-') {
                    monthsWithData.push(`${month}: "${rowData[month]}"`);
                }
            });
            if (monthsWithData.length > 0) {
                console.log(`    📅 ${monthsWithData.join(', ')}`);
            }
            
            exportData.push(rowData);
        });
        
        console.log(`🎯 COMPLETE EXPORT SUMMARY:`);
        console.log(`  📊 Total rows processed: ${exportData.length}`);
        console.log(`  📊 Customer summaries: ${exportData.filter(row => row.Row_Type === 'Customer Summary').length}`);
        console.log(`  📊 Network details: ${exportData.filter(row => row.Row_Type === 'Network Detail').length}`);
        
        // Show sample data
        console.log(`📊 SAMPLE EXPORTED DATA:`);
        exportData.slice(0, 3).forEach((row, index) => {
            console.log(`  [${index}] ${row.Customer} (${row.Row_Type}): ${row.Node_Qty} nodes, ${row.Total_Runs} runs`);
        });
        
        if (exportData.length === 0) {
            throw new Error('No data found to export');
        }
        
        // Create FormData for API
        const formData = new FormData();
        formData.append('data', JSON.stringify(exportData));
        formData.append('filename', `Complete_Dashboard_Export_${new Date().toISOString().split('T')[0]}.xlsx`);
        formData.append('csrfmiddlewaretoken', token);
        formData.append('complete_export', 'true');
        
        console.log('🎯 Sending COMPLETE data to export API...');
        
        // Send to export API
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
        
        // Download the Excel file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Complete_Dashboard_Export_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ COMPLETE export finished successfully!');
        showNotification(`✅ Excel exported: ${exportData.length} rows (ALL dashboard data)!`, 'success');
        
    } catch (error) {
        console.error('❌ Complete export failed:', error);
        showNotification(`❌ Export failed: ${error.message}`, 'error');
    }
};

// 🎯 MAIN DOWNLOAD FUNCTION - CSV WITH ALL DATA
window.downloadCompleteDashboard = function() {
    console.log('🎯 COMPLETE DOWNLOAD: CSV with all data exactly as shown...');
    
    try {
        showNotification('🎯 Creating CSV with COMPLETE dashboard data...', 'info');
        
        const downloadData = [];
        const tableRows = document.querySelectorAll('#customer-table-body tr');
        
        console.log(`🎯 Processing ${tableRows.length} rows for CSV...`);
        
        // CSV headers
        const headers = [
            'Customer', 'Row_Type', 'Country', 'Networks', 'Node_Qty', 'NE_Type', 'GTAC',
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
            'Total_Runs'
        ];
        
        downloadData.push(headers);
        
        tableRows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            
            if (cells.length < 19) {
                console.log(`⚠️ Row ${index}: Only ${cells.length} cells, skipping`);
                return;
            }
            
            // Get and clean customer name
            const rawCustomerName = cells[0]?.textContent.trim() || 'Unknown';
            const isNetworkRow = rawCustomerName.includes('└─');
            
            let cleanCustomerName = rawCustomerName
                .replace('💾 ', '')
                .replace('💾 Live DB', '')
                .replace(/Last run: [^\n]*/g, '')
                .replace('└─ ', '')
                .trim();
            
            // Create row data array
            const rowDataArray = [
                cleanCustomerName,
                isNetworkRow ? 'Network Detail' : 'Customer Summary',
                cells[1]?.textContent.trim() || '',
                cells[2]?.textContent.trim() || '',
                cells[3]?.textContent.trim() || '0',
                cells[4]?.textContent.trim() || '',
                cells[5]?.textContent.trim() || '',
                cells[6]?.textContent.trim() || '-',   // Jan
                cells[7]?.textContent.trim() || '-',   // Feb
                cells[8]?.textContent.trim() || '-',   // Mar
                cells[9]?.textContent.trim() || '-',   // Apr
                cells[10]?.textContent.trim() || '-',  // May
                cells[11]?.textContent.trim() || '-',  // Jun
                cells[12]?.textContent.trim() || '-',  // Jul
                cells[13]?.textContent.trim() || '-',  // Aug
                cells[14]?.textContent.trim() || '-',  // Sep
                cells[15]?.textContent.trim() || '-',  // Oct
                cells[16]?.textContent.trim() || '-',  // Nov
                cells[17]?.textContent.trim() || '-',  // Dec
                cells[18]?.textContent.trim() || '0'   // Total_Runs
            ];
            
            downloadData.push(rowDataArray);
            console.log(`🎯 Row ${index}: ${cleanCustomerName} - ${rowDataArray[4]} nodes - ${rowDataArray[19]} runs`);
        });
        
        console.log(`🎯 Prepared ${downloadData.length - 1} data rows + 1 header for CSV`);
        
        // Create CSV content with proper escaping
        const csvContent = downloadData.map(row => {
            return row.map(cell => {
                const cellValue = String(cell || '');
                // If cell contains comma, newline, or quotes, wrap in quotes and escape internal quotes
                if (cellValue.includes(',') || cellValue.includes('\n') || cellValue.includes('"')) {
                    return '"' + cellValue.replace(/"/g, '""') + '"';
                }
                return cellValue;
            }).join(',');
        }).join('\n');
        
        // Trigger CSV download
        const encodedUri = 'data:text/csv;charset=utf-8,\uFEFF' + encodeURIComponent(csvContent);
        const link = document.createElement('a');
        link.href = encodedUri;
        link.download = `Complete_Dashboard_Download_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ COMPLETE download finished successfully!');
        showNotification(`✅ CSV downloaded: ${downloadData.length - 1} rows (ALL dashboard data)!`, 'success');
        
    } catch (error) {
        console.error('❌ Complete download failed:', error);
        showNotification(`❌ Download failed: ${error.message}`, 'error');
    }
};

// 🎯 ADD NEW EXPORT/DOWNLOAD BUTTONS TO UI
window.addCompleteDashboardButtons = function() {
    console.log('🎯 Adding COMPLETE dashboard export/download buttons...');
    
    try {
        // Look for existing export buttons or good place to add new ones
        const buttonContainer = document.querySelector('.export-buttons') || 
                              document.querySelector('.dashboard-controls') ||
                              document.querySelector('.top-controls') ||
                              document.querySelector('header') ||
                              document.body;
        
        // Check if our buttons already exist
        if (document.getElementById('complete-dashboard-buttons')) {
            console.log('ℹ️ Complete dashboard buttons already exist');
            return;
        }
        
        // Create container for new buttons
        const completeButtonsDiv = document.createElement('div');
        completeButtonsDiv.id = 'complete-dashboard-buttons';
        completeButtonsDiv.style.cssText = `
            margin: 15px 0;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 1px solid #5a67d8;
        `;
        
        completeButtonsDiv.innerHTML = `
            <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                <strong style="color: white; font-size: 16px;">
                    🎯 Complete Dashboard Export (Live + Migrated Data)
                </strong>
                <button 
                    onclick="exportCompleteDashboard()" 
                    class="btn btn-success" 
                    style="
                        background: #48bb78; 
                        border: none; 
                        padding: 10px 20px; 
                        border-radius: 6px; 
                        color: white; 
                        font-weight: bold;
                        cursor: pointer;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    "
                    title="Export ALL dashboard data to Excel exactly as shown"
                >
                    📊 Export Complete Excel
                </button>
                <button 
                    onclick="downloadCompleteDashboard()" 
                    class="btn btn-info" 
                    style="
                        background: #4299e1; 
                        border: none; 
                        padding: 10px 20px; 
                        border-radius: 6px; 
                        color: white; 
                        font-weight: bold;
                        cursor: pointer;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    "
                    title="Download ALL dashboard data as CSV exactly as shown"
                >
                    📋 Download Complete CSV
                </button>
                <button 
                    onclick="showDashboardPreview()" 
                    class="btn btn-secondary" 
                    style="
                        background: #718096; 
                        border: none; 
                        padding: 10px 20px; 
                        border-radius: 6px; 
                        color: white; 
                        font-weight: bold;
                        cursor: pointer;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    "
                    title="Preview what will be exported"
                >
                    👀 Preview Data
                </button>
            </div>
            <div style="color: white; font-size: 12px; margin-top: 8px; opacity: 0.9;">
                ✅ Includes ALL rows, dates, "Not Started" values, Live DB + Migrated Excel data exactly as shown in dashboard
            </div>
        `;
        
        // Insert buttons at the top of the container
        if (buttonContainer.firstChild) {
            buttonContainer.insertBefore(completeButtonsDiv, buttonContainer.firstChild);
        } else {
            buttonContainer.appendChild(completeButtonsDiv);
        }
        
        console.log('✅ Complete dashboard buttons added successfully');
        
    } catch (error) {
        console.error('❌ Error adding complete dashboard buttons:', error);
    }
};

// 🎯 PREVIEW FUNCTION - Show what will be exported
window.showDashboardPreview = function() {
    console.log('👀 DASHBOARD PREVIEW: Showing what will be exported...');
    
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    const preview = [];
    
    tableRows.forEach((row, index) => {
        if (index >= 5) return; // Only preview first 5 rows
        
        const cells = row.querySelectorAll('td');
        if (cells.length < 19) return;
        
        const rawName = cells[0]?.textContent.trim() || 'Unknown';
        const cleanName = rawName.replace('💾 ', '').replace('💾 Live DB', '').replace(/Last run: [^\n]*/g, '').replace('└─ ', '').trim();
        const isNetwork = rawName.includes('└─');
        
        preview.push({
            customer: cleanName,
            type: isNetwork ? 'Network' : 'Customer',
            nodes: cells[3]?.textContent.trim() || '0',
            runs: cells[18]?.textContent.trim() || '0',
            oct: cells[15]?.textContent.trim() || '-'
        });
    });
    
    console.log('👀 PREVIEW (first 5 rows):');
    preview.forEach((row, index) => {
        console.log(`  [${index}] ${row.customer} (${row.type}): ${row.nodes} nodes, ${row.runs} runs, Oct: "${row.oct}"`);
    });
    
    alert(`📊 PREVIEW: Will export ${tableRows.length} rows\n\nFirst 5 rows:\n${preview.map((row, i) => `${i+1}. ${row.customer} (${row.type}): ${row.nodes} nodes, Oct: "${row.oct}"`).join('\n')}\n\n✅ Includes ALL dashboard data exactly as shown!`);
};

// 🎯 Initialize - Add buttons when page loads
function initializeCompleteDashboard() {
    console.log('🎯 Initializing Complete Dashboard Export System...');
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addCompleteDashboardButtons);
    } else {
        addCompleteDashboardButtons();
    }
    
    // Also try again after a short delay to ensure everything is loaded
    setTimeout(addCompleteDashboardButtons, 2000);
}

// Start initialization
initializeCompleteDashboard();

console.log('✅ COMPLETE DASHBOARD EXPORT SYSTEM LOADED!');
console.log('🎯 Features:');
console.log('  📊 New Export Excel button - ALL dashboard data');
console.log('  📋 New Download CSV button - ALL dashboard data');
console.log('  👀 Preview button - See what will be exported');
console.log('  ✅ Includes: Live DB + Migrated Excel + All rows + All dates');
console.log('  ✅ Preserves: "Not Started", "No Report", network details');
console.log('🎯 Functions available:');
console.log('  - exportCompleteDashboard() - Export all data to Excel');
console.log('  - downloadCompleteDashboard() - Download all data as CSV');
console.log('  - showDashboardPreview() - Preview export data');
console.log('🔄 New buttons will be added to your dashboard automatically!');