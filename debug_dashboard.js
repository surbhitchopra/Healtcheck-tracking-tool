// 🐛 QUICK DASHBOARD DEBUG
// Quick inspection of current dashboard state

console.log('🐛 Loading dashboard debug tools...');

// 🐛 Quick function to show what's in the table right now
window.inspectCurrentTable = function() {
    console.log('🐛 INSPECTING CURRENT TABLE STATE');
    console.log('=================================');
    
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    console.log(`📊 Found ${tableRows.length} rows`);
    
    // Show first 10 rows in detail
    Array.from(tableRows).slice(0, 10).forEach((row, index) => {
        const cells = Array.from(row.querySelectorAll('td'));
        console.log(`\n📋 ROW ${index}:`);
        
        cells.forEach((cell, cellIndex) => {
            const text = cell.textContent.trim();
            console.log(`  [${cellIndex}] "${text}"`);
        });
    });
    
    // Show table headers
    const headers = document.querySelectorAll('#customer-table thead th');
    if (headers.length > 0) {
        console.log('\n📋 TABLE HEADERS:');
        Array.from(headers).forEach((header, index) => {
            console.log(`  [${index}] "${header.textContent.trim()}"`);
        });
    }
};

// 🐛 Function to compare table vs data
window.compareTableVsData = function() {
    console.log('🐛 COMPARING TABLE vs DATA');
    console.log('==========================');
    
    // Count table rows
    const tableRows = document.querySelectorAll('#customer-table-body tr').length;
    console.log(`📊 Table rows: ${tableRows}`);
    
    // Count data customers
    if (window.dashboardData && window.dashboardData.customers) {
        const dataCustomers = Object.keys(window.dashboardData.customers).length;
        console.log(`📊 Data customers: ${dataCustomers}`);
        
        // Show first few customer names from data
        console.log('📊 Data customer names:');
        Object.keys(window.dashboardData.customers).slice(0, 10).forEach((name, index) => {
            console.log(`  [${index}] "${name}"`);
        });
    } else {
        console.log('❌ No dashboardData.customers found');
    }
    
    // Show first few row names from table
    console.log('📊 Table customer names:');
    document.querySelectorAll('#customer-table-body tr').forEach((row, index) => {
        if (index >= 10) return; // Only first 10
        const nameCell = row.querySelector('.customer-name-cell, td:first-child');
        if (nameCell) {
            console.log(`  [${index}] "${nameCell.textContent.trim()}"`);
        }
    });
};

// 🐛 Function to inspect specific customer
window.inspectCustomer = function(customerName) {
    console.log(`🐛 INSPECTING CUSTOMER: ${customerName}`);
    console.log('=====================================');
    
    // Find in data
    if (window.dashboardData && window.dashboardData.customers && window.dashboardData.customers[customerName]) {
        const customer = window.dashboardData.customers[customerName];
        console.log('📊 FOUND IN DATA:');
        console.log('  Properties:', Object.keys(customer));
        console.log('  Full data:', customer);
        
        if (customer.networks) {
            console.log(`  Networks (${customer.networks.length}):`);
            customer.networks.forEach((net, index) => {
                console.log(`    [${index}] ${net.name || 'No name'} - ${net.runs || net.total_runs || 0} runs`);
            });
        }
    } else {
        console.log('❌ NOT FOUND IN DATA');
    }
    
    // Find in table
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    const matchingRows = [];
    
    tableRows.forEach((row, index) => {
        const nameCell = row.querySelector('.customer-name-cell, td:first-child');
        if (nameCell && nameCell.textContent.trim().includes(customerName)) {
            matchingRows.push({ row, index });
        }
    });
    
    if (matchingRows.length > 0) {
        console.log(`📊 FOUND IN TABLE (${matchingRows.length} rows):`);
        matchingRows.forEach(({ row, index }) => {
            const cells = Array.from(row.querySelectorAll('td'));
            console.log(`  Row ${index}:`);
            cells.forEach((cell, cellIndex) => {
                console.log(`    [${cellIndex}] "${cell.textContent.trim()}"`);
            });
        });
    } else {
        console.log('❌ NOT FOUND IN TABLE');
    }
};

// 🐛 Show a sample of what the export would capture
window.previewExportData = function() {
    console.log('🐛 PREVIEWING EXPORT DATA');
    console.log('=========================');
    
    const tableRows = document.querySelectorAll('#customer-table-body tr');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Process first 5 rows
    Array.from(tableRows).slice(0, 5).forEach((row, index) => {
        const cells = Array.from(row.querySelectorAll('td'));
        
        console.log(`\n📋 ROW ${index} EXPORT PREVIEW:`);
        
        const exportRow = {
            'Customer': cells[0]?.textContent.trim() || 'Unknown',
            'Country': cells[1]?.textContent.trim() || 'Unknown',
            'Networks': cells[2]?.textContent.trim() || '0',
            'Node Qty': cells[3]?.textContent.trim() || '0',
            'NE Type': cells[4]?.textContent.trim() || '1830 PSS',
            'GTAC': cells[5]?.textContent.trim() || 'PSS'
        };
        
        // Try to find month columns (assuming they start around column 6)
        months.forEach((month, monthIndex) => {
            const columnIndex = 6 + monthIndex; // Guess: months start at column 6
            if (columnIndex < cells.length) {
                const value = cells[columnIndex]?.textContent.trim() || '-';
                exportRow[month] = value;
            } else {
                exportRow[month] = '-';
            }
        });
        
        // Find total runs (probably last column)
        exportRow['Total Runs'] = cells[cells.length - 1]?.textContent.trim() || '0';
        
        console.log('  Export data:', exportRow);
    });
};

// 🐛 Auto-run basic inspection
setTimeout(() => {
    console.log('🐛 Auto-running basic inspection...');
    inspectCurrentTable();
    compareTableVsData();
}, 1000);

console.log('✅ DEBUG TOOLS LOADED!');
console.log('🐛 Available functions:');
console.log('  - inspectCurrentTable() - Show table contents');
console.log('  - compareTableVsData() - Compare table vs JavaScript data');
console.log('  - inspectCustomer("name") - Deep dive into specific customer');
console.log('  - previewExportData() - Show what export would capture');
console.log('🔄 Auto-inspection will run in 1 second...');