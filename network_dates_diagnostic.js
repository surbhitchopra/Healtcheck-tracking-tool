// Network Dates Parsing & Formatting Diagnostic Script
// Run this in browser console to check exact formatting issues

console.log("🔍 NETWORK DATES DIAGNOSTIC STARTED");
console.log("=====================================");

// Step 1: Check raw data formats
function checkDataFormats() {
    console.log("\n📊 CHECKING RAW DATA FORMATS:");
    
    if (window.dashboardData && window.dashboardData.customers) {
        window.dashboardData.customers.forEach((customer, index) => {
            if (index < 3) { // Check first 3 customers only
                console.log(`\n🏢 Customer: ${customer.name}`);
                console.log(`Monthly runs type:`, typeof customer.monthly_runs);
                console.log(`Monthly runs value:`, customer.monthly_runs);
                
                if (customer.networks && customer.networks.length > 0) {
                    customer.networks.forEach((network, netIndex) => {
                        if (netIndex < 2) { // Check first 2 networks only
                            console.log(`  📡 Network: ${network.name}`);
                            console.log(`  Network monthly_runs type:`, typeof network.monthly_runs);
                            console.log(`  Network monthly_runs value:`, network.monthly_runs);
                            
                            // Check if it's an array and what's inside
                            if (Array.isArray(network.monthly_runs)) {
                                console.log(`  Array length:`, network.monthly_runs.length);
                                if (network.monthly_runs.length > 0) {
                                    console.log(`  First item:`, network.monthly_runs[0]);
                                    console.log(`  First item type:`, typeof network.monthly_runs[0]);
                                }
                            }
                        }
                    });
                }
            }
        });
    } else {
        console.log("❌ No dashboardData.customers found!");
    }
}

// Step 2: Test date parsing functions
function testDateParsing() {
    console.log("\n🗓️ TESTING DATE PARSING:");
    
    // Common date formats found in database
    const testDates = [
        "2024-10-15",
        "15-10-2024", 
        "Oct-15-24",
        "15-Oct-24",
        "2024/10/15",
        15, // Day only
        "15",
        { day: 15, month: 10, year: 2024 },
        new Date("2024-10-15")
    ];
    
    testDates.forEach(date => {
        console.log(`\nTesting: ${JSON.stringify(date)} (type: ${typeof date})`);
        
        // Try different parsing approaches
        try {
            let parsed = parseDateToFormat(date);
            console.log(`  Parsed result: ${parsed}`);
        } catch (e) {
            console.log(`  Parse error: ${e.message}`);
        }
    });
}

// Enhanced date parsing function
function parseDateToFormat(dateValue) {
    if (!dateValue) return '-';
    
    let day, month, year;
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;
    
    console.log(`    Processing: ${JSON.stringify(dateValue)}`);
    
    if (typeof dateValue === 'number') {
        // Just a day number
        day = dateValue;
        month = currentMonth;
        year = currentYear;
        console.log(`    Number format: day=${day}, month=${month}, year=${year}`);
    }
    else if (typeof dateValue === 'string') {
        // Try various string formats
        if (dateValue.includes('-')) {
            const parts = dateValue.split('-');
            if (parts.length === 3) {
                if (parts[0].length === 4) {
                    // YYYY-MM-DD format
                    year = parseInt(parts[0]);
                    month = parseInt(parts[1]);
                    day = parseInt(parts[2]);
                } else {
                    // DD-MM-YYYY or DD-Mon-YY format
                    day = parseInt(parts[0]);
                    if (isNaN(parseInt(parts[1]))) {
                        // Month name format
                        const monthNames = ['Jan','Feb','Mar','Apr','May','Jun',
                                          'Jul','Aug','Sep','Oct','Nov','Dec'];
                        month = monthNames.indexOf(parts[1]) + 1;
                    } else {
                        month = parseInt(parts[1]);
                    }
                    year = parseInt(parts[2]);
                    if (year < 100) year += 2000; // Convert 2-digit year
                }
            }
            console.log(`    String dash format: day=${day}, month=${month}, year=${year}`);
        }
        else if (dateValue.includes('/')) {
            const parts = dateValue.split('/');
            if (parts.length === 3) {
                year = parseInt(parts[0]);
                month = parseInt(parts[1]);
                day = parseInt(parts[2]);
            }
            console.log(`    String slash format: day=${day}, month=${month}, year=${year}`);
        }
        else if (!isNaN(dateValue)) {
            // String number
            day = parseInt(dateValue);
            month = currentMonth;
            year = currentYear;
            console.log(`    String number format: day=${day}, month=${month}, year=${year}`);
        }
    }
    else if (dateValue instanceof Date) {
        day = dateValue.getDate();
        month = dateValue.getMonth() + 1;
        year = dateValue.getFullYear();
        console.log(`    Date object format: day=${day}, month=${month}, year=${year}`);
    }
    else if (typeof dateValue === 'object' && dateValue.day) {
        day = dateValue.day;
        month = dateValue.month || currentMonth;
        year = dateValue.year || currentYear;
        console.log(`    Object format: day=${day}, month=${month}, year=${year}`);
    }
    
    // Validate and format
    if (!day || !month || !year || day < 1 || day > 31 || month < 1 || month > 12) {
        console.log(`    ❌ Invalid date components: day=${day}, month=${month}, year=${year}`);
        return '-';
    }
    
    const monthNames = ['Jan','Feb','Mar','Apr','May','Jun',
                       'Jul','Aug','Sep','Oct','Nov','Dec'];
    const formattedDate = `${day.toString().padStart(2, '0')}-${monthNames[month-1]}-${year.toString().substr(-2)}`;
    console.log(`    ✅ Formatted result: ${formattedDate}`);
    return formattedDate;
}

// Step 3: Check DOM elements
function checkDOMElements() {
    console.log("\n🎯 CHECKING DOM ELEMENTS:");
    
    const networkRows = document.querySelectorAll('tr.network-row, tr[data-network], .network-detail-row');
    console.log(`Found ${networkRows.length} network rows`);
    
    networkRows.forEach((row, index) => {
        if (index < 5) { // Check first 5 rows only
            console.log(`\nRow ${index + 1}:`);
            console.log(`  Classes: ${row.className}`);
            console.log(`  Data attributes:`, row.dataset);
            
            // Find date cell
            const dateCells = row.querySelectorAll('td');
            dateCells.forEach((cell, cellIndex) => {
                if (cell.textContent.includes('-') || cellIndex > 2) {
                    console.log(`  Cell ${cellIndex}: "${cell.textContent}" (class: ${cell.className})`);
                }
            });
        }
    });
}

// Step 4: Force update network dates
function forceUpdateNetworkDates() {
    console.log("\n🚀 FORCE UPDATING NETWORK DATES:");
    
    if (!window.dashboardData || !window.dashboardData.customers) {
        console.log("❌ No dashboard data available");
        return;
    }
    
    let updateCount = 0;
    
    // Find all network rows and update them
    const allRows = document.querySelectorAll('tr');
    allRows.forEach(row => {
        // Check if this is a network row
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            const networkNameCell = cells[1]; // Usually second cell has network name
            const dateCell = cells[3]; // Usually fourth cell has date
            
            if (networkNameCell && dateCell) {
                const networkName = networkNameCell.textContent.trim();
                
                // Skip if it's a customer row or header
                if (networkName.includes('Total') || networkName.includes('Customer') || networkName === '') {
                    return;
                }
                
                // Find this network in dashboard data
                window.dashboardData.customers.forEach(customer => {
                    if (customer.networks) {
                        customer.networks.forEach(network => {
                            if (network.name === networkName) {
                                console.log(`\n🔧 Processing network: ${networkName}`);
                                console.log(`Current date cell: "${dateCell.textContent}"`);
                                console.log(`Network monthly_runs:`, network.monthly_runs);
                                
                                let newDate = '-';
                                if (network.monthly_runs && network.monthly_runs.length > 0) {
                                    // Get the latest date
                                    const latestRun = network.monthly_runs[network.monthly_runs.length - 1];
                                    newDate = parseDateToFormat(latestRun);
                                    console.log(`Parsed date: ${newDate}`);
                                }
                                
                                // Update the cell
                                if (newDate !== '-') {
                                    dateCell.textContent = newDate;
                                    dateCell.style.color = '#28a745';
                                    dateCell.style.fontWeight = 'bold';
                                    updateCount++;
                                    console.log(`✅ Updated ${networkName} with date: ${newDate}`);
                                } else {
                                    console.log(`⚠️ No valid date found for ${networkName}`);
                                }
                            }
                        });
                    }
                });
            }
        }
    });
    
    console.log(`\n🎉 COMPLETED: Updated ${updateCount} network dates`);
}

// Run all diagnostics
console.log("Starting comprehensive diagnostic...");
checkDataFormats();
testDateParsing();
checkDOMElements();
forceUpdateNetworkDates();

console.log("\n✅ DIAGNOSTIC COMPLETE!");
console.log("Check the output above to identify the exact issue with network dates.");