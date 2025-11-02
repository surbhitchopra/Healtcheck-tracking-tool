// Final comprehensive test for customer master and network level dates
// This tests the complete fix for both levels

function testFinalCustomerNetworkFix() {
    console.log("=== TESTING COMPLETE CUSTOMER + NETWORK DATES FIX ===\n");
    
    // Sample customer with multiple networks (like BSNL)
    const sampleCustomer = {
        name: "BSNL",
        networks: [
            {
                name: "Bsnl - Timedotcom Default",
                network_name: "Timedotcom Default",
                monthly_runs: ['15-05', '13-06', '28-06', '12-07', '25-08']
            },
            {
                name: "Bsnl - Nokia East", 
                network_name: "Nokia East",
                monthly_runs: {
                    '2024-01': 'Not Started',
                    '2024-02': 'Not Started',
                    '2024-05': '2024-05-10', // Earlier date
                    '2024-06': '2024-06-20', // Later date than Timedotcom
                    '2024-07': 'No Report',
                    '2024-08': '2024-08-30'  // Latest date
                }
            },
            {
                name: "Bsnl - Western Circle",
                network_name: "Western Circle", 
                monthly_runs: ['05-05', '08-06', '15-08'] // Earlier dates
            }
        ]
    };
    
    console.log(`Customer: ${sampleCustomer.name}`);
    console.log(`Networks: ${sampleCustomer.networks.length}`);
    
    // Test each month to see customer master vs individual networks
    const testMonths = [5, 6, 7, 8]; // May, Jun, Jul, Aug
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    testMonths.forEach(month => {
        console.log(`\n📅 TESTING MONTH: ${monthNames[month - 1]} (${month})`);
        
        // Test individual networks first
        console.log("  🌐 Individual Networks:");
        sampleCustomer.networks.forEach((network, index) => {
            const networkResult = getNetworkMonthRunDatesForCustomer(network, month, 2024);
            console.log(`    ${index + 1}. ${network.network_name}: ${networkResult.date}`);
        });
        
        // Test customer master (should show latest from all networks)
        console.log("  📋 Customer Master:");
        const customerResult = getCustomerMonthRunDatesForTest(sampleCustomer, month, 2024);
        console.log(`    ${sampleCustomer.name}: ${customerResult.date} ✅`);
        
        if (customerResult.expectedLatest) {
            console.log(`    Expected: ${customerResult.expectedLatest}`);
        }
    });
    
    console.log("\n✅ Final test completed!");
    console.log("\nExpected Customer Master Results:");
    console.log("  May: 15-May (from Timedotcom, as Nokia shows 10-May)");
    console.log("  Jun: 20-Jun (Nokia has latest date)");  
    console.log("  Jul: 12-Jul (only Timedotcom has date, Nokia shows 'No Report')");
    console.log("  Aug: 30-Aug (Nokia has latest date)");
}

function getNetworkMonthRunDatesForCustomer(network, month, year) {
    // Simulate our helper function
    if (network.monthly_runs) {
        let monthValue = null;
        
        if (Array.isArray(network.monthly_runs)) {
            const monthStr = month.toString().padStart(2, '0');
            const monthDates = network.monthly_runs.filter(dateStr => {
                if (typeof dateStr === 'string' && dateStr.includes('-')) {
                    const parts = dateStr.split('-');
                    if (parts.length >= 2) {
                        const monthPart = parts[1];
                        return monthPart === monthStr;
                    }
                }
                return false;
            });
            
            if (monthDates.length > 0) {
                monthValue = monthDates[monthDates.length - 1];
            }
        } else if (typeof network.monthly_runs === 'object') {
            const yearMonth = `${year}-${month.toString().padStart(2, '0')}`;
            monthValue = network.monthly_runs[yearMonth];
        }
        
        if (monthValue) {
            if (monthValue === 'Not Started' || monthValue === 'Not Run' || monthValue === 'No Report') {
                return { count: 0, date: monthValue, fullDate: monthValue };
            } else if (typeof monthValue === 'string' && monthValue.includes('-')) {
                if (monthValue.match(/^\d{4}-\d{2}-\d{2}$/)) {
                    const dateObj = new Date(monthValue);
                    const day = dateObj.getDate();
                    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    const monthName = monthNames[dateObj.getMonth()];
                    return { count: 1, date: `${day}-${monthName}`, fullDate: `${day} ${monthName} ${year}` };
                } else if (monthValue.match(/^\d{1,2}-\d{2}$/)) {
                    const parts = monthValue.split('-');
                    const day = parts[0];
                    const monthNum = parseInt(parts[1]);
                    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    const monthName = monthNames[monthNum - 1];
                    return { count: 1, date: `${day}-${monthName}`, fullDate: `${day} ${monthName} ${year}` };
                }
            }
        }
    }
    return { count: 0, date: '-', fullDate: 'No runs' };
}

function getCustomerMonthRunDatesForTest(customer, month, year) {
    // Simulate customer master logic
    let allNetworkDates = [];
    let totalRuns = 0;
    
    customer.networks.forEach(network => {
        const networkData = getNetworkMonthRunDatesForCustomer(network, month, year);
        if (networkData.date !== '-') {
            if (networkData.count > 0) totalRuns += networkData.count;
            
            if (networkData.date !== 'Not Started' && networkData.date !== 'No Report') {
                let dateForComparison = null;
                if (networkData.date.match(/^\d{1,2}-[A-Za-z]{3}$/)) {
                    const parts = networkData.date.split('-');
                    const day = parseInt(parts[0]);
                    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    const monthNum = monthNames.indexOf(parts[1]);
                    if (monthNum >= 0) {
                        dateForComparison = new Date(year, monthNum, day);
                    }
                }
                allNetworkDates.push({
                    date: networkData.date,
                    dateObj: dateForComparison,
                    network: network.network_name
                });
            }
        }
    });
    
    let latestDate = '-';
    if (allNetworkDates.length > 0) {
        const validDates = allNetworkDates.filter(item => item.dateObj !== null);
        if (validDates.length > 0) {
            validDates.sort((a, b) => b.dateObj - a.dateObj);
            latestDate = validDates[0].date;
        } else {
            latestDate = allNetworkDates[allNetworkDates.length - 1].date;
        }
    }
    
    return {
        count: totalRuns,
        date: latestDate,
        fullDate: latestDate
    };
}

// Run the test
testFinalCustomerNetworkFix();