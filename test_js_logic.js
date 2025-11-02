// Test the JavaScript logic fix for network monthly dates
// This simulates what the fixed getNetworkMonthRunDates function does

function testNetworkMonthlyDatesLogic() {
    console.log("=== TESTING NETWORK MONTHLY DATES LOGIC ===\n");
    
    // Sample network data structure (as it comes from API)
    const sampleNetwork = {
        name: "Bsnl - Timedotcom Default",
        network_name: "Timedotcom Default", 
        monthly_runs: ['15-05', '13-06', '28-06', '12-07', '25-08'],
        runs: 5,
        last_run_date: "2024-08-25"
    };
    
    console.log("Sample network data:", sampleNetwork);
    console.log("Network monthly_runs array:", sampleNetwork.monthly_runs);
    
    // Test the logic for each month
    for (let month = 1; month <= 12; month++) {
        const monthStr = month.toString().padStart(2, '0'); // Convert to "01", "02", etc.
        
        // Find dates matching this month in DD-MM format
        const monthDates = sampleNetwork.monthly_runs.filter(dateStr => {
            if (typeof dateStr === 'string' && dateStr.includes('-')) {
                const parts = dateStr.split('-');
                if (parts.length >= 2) {
                    const monthPart = parts[1]; // Get MM part from DD-MM
                    return monthPart === monthStr;
                }
            }
            return false;
        });
        
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthName = monthNames[month - 1];
        
        if (monthDates.length > 0) {
            // Use the latest date if multiple runs in the same month
            const latestDate = monthDates[monthDates.length - 1];
            
            // Format as DD-Mon-YY for display
            const parts = latestDate.split('-');
            const day = parts[0];
            const monthNum = parseInt(parts[1]);
            const yearShort = '24'; // Using 2024 as example year
            const formattedDate = `${day}-${monthName}-${yearShort}`;
            
            console.log(`${monthName}: ${formattedDate} (${monthDates.length} runs) ✅`);
        } else {
            console.log(`${monthName}: - (no runs) ⚪`);
        }
    }
    
    console.log("\n✅ Test completed! The fix should now show:");
    console.log("   - May: 15-May-24");
    console.log("   - Jun: 28-Jun-24 (latest of 2 runs)");
    console.log("   - Jul: 12-Jul-24");
    console.log("   - Aug: 25-Aug-24");
    console.log("   - All other months: -");
}

// Run the test
testNetworkMonthlyDatesLogic();