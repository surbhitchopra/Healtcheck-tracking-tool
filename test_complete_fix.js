// Final test for complete network monthly dates fix
// This simulates all the different data formats our fix should handle

function testCompleteNetworkDatesFix() {
    console.log("=== TESTING COMPLETE NETWORK DATES FIX ===\n");
    
    // Test different network data formats that our fix should handle
    const testCases = [
        {
            name: "Array Format with DD-MM dates",
            network: {
                name: "Bsnl - Timedotcom Default",
                network_name: "Timedotcom Default",
                monthly_runs: ['15-05', '13-06', '28-06', '12-07', '25-08']
            }
        },
        {
            name: "Object Format with YYYY-MM keys", 
            network: {
                name: "Bsnl - Nokia East",
                network_name: "Nokia East",
                monthly_runs: {
                    '2024-01': 'Not Started',
                    '2024-02': 'Not Started', 
                    '2024-05': '2024-05-15',
                    '2024-06': '2024-06-13',
                    '2024-07': 'No Report',
                    '2024-08': '2024-08-25'
                }
            }
        }
    ];
    
    testCases.forEach(testCase => {
        console.log(`\n📋 Testing: ${testCase.name}`);
        console.log(`Network: ${testCase.network.network_name}`);
        console.log(`Data:`, testCase.network.monthly_runs);
        
        // Test our logic for each month
        for (let month = 1; month <= 12; month++) {
            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const monthName = monthNames[month - 1];
            
            let result = simulateGetNetworkMonthRunDates(testCase.network, month, 2024);
            
            if (result.date && result.date !== '-') {
                console.log(`  ${monthName}: ${result.date} ✅`);
            } else {
                console.log(`  ${monthName}: - ⚪`);
            }
        }
    });
    
    console.log("\n✅ Complete fix test finished!");
    console.log("Expected results:");
    console.log("  - Array format should show: 15-May, 28-Jun (latest), 12-Jul, 25-Aug");
    console.log("  - Object format should show: Not Started, Not Started, 15-May, 13-Jun, No Report, 25-Aug");
    console.log("  - All dates without year (DD-Mon format only)");
}

function simulateGetNetworkMonthRunDates(network, month, year) {
    // Simulate our fixed logic
    let monthValue = null;
    
    if (Array.isArray(network.monthly_runs)) {
        // Array format: ['15-05', '13-06', ...]
        const monthStr = month.toString().padStart(2, '0');
        const monthDates = network.monthly_runs.filter(dateStr => {
            if (typeof dateStr === 'string' && dateStr.includes('-')) {
                const parts = dateStr.split('-');
                if (parts.length >= 2) {
                    const monthPart = parts[1]; // Get MM part from DD-MM
                    return monthPart === monthStr;
                }
            }
            return false;
        });
        
        if (monthDates.length > 0) {
            monthValue = monthDates[monthDates.length - 1]; // Latest date
        }
    } else if (typeof network.monthly_runs === 'object') {
        // Object format: {'2024-01': 'Not Started', '2024-05': '2024-05-15'}
        const yearMonth = `${year}-${month.toString().padStart(2, '0')}`;
        monthValue = network.monthly_runs[yearMonth];
    }
    
    if (monthValue) {
        // Handle different types of values
        if (monthValue === 'Not Started' || monthValue === 'Not Run' || monthValue === 'No Report') {
            return {
                count: 0,
                date: monthValue,
                fullDate: monthValue
            };
        } else if (typeof monthValue === 'string' && monthValue.includes('-')) {
            // Handle actual dates
            if (monthValue.match(/^\d{4}-\d{2}-\d{2}$/)) {
                // Full date format: 2024-05-15
                const dateObj = new Date(monthValue);
                const day = dateObj.getDate();
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                const monthName = monthNames[dateObj.getMonth()];
                const formattedDate = `${day}-${monthName}`; // No year
                
                return {
                    count: 1,
                    date: formattedDate,
                    fullDate: `${day} ${monthName} ${dateObj.getFullYear()}`
                };
            } else if (monthValue.match(/^\d{1,2}-\d{2}$/)) {
                // DD-MM format: 15-05
                const parts = monthValue.split('-');
                const day = parts[0];
                const monthNum = parseInt(parts[1]);
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                const monthName = monthNames[monthNum - 1] || parts[1];
                const formattedDate = `${day}-${monthName}`; // No year
                
                return {
                    count: 1,
                    date: formattedDate,
                    fullDate: `${day} ${monthName} ${year}`
                };
            }
        }
    }
    
    return { count: 0, date: '-', fullDate: 'No runs' };
}

// Run the test
testCompleteNetworkDatesFix();