// ULTIMATE NETWORK DATES FIX - For Excel Migrated Customers
// This script forces network dates to display properly

console.log('🔥 ULTIMATE NETWORK DATES FIX STARTING...');

// Override the network row creation to force show Excel dates
window.getNetworkMonthRunDates = function(customer, networkName, year, month) {
    console.log(`🔥 ULTIMATE FIX: ${networkName} for month ${month}`);
    
    // PRIORITY 1: Excel customers with monthly_runs data
    if (customer.excel_source || customer.excel_data || customer.migrated_excel_data) {
        console.log(`📊 Excel customer detected: ${customer.name}`);
        
        // Check if customer has monthly_runs at customer level
        if (customer.monthly_runs && Array.isArray(customer.monthly_runs) && customer.monthly_runs.length >= 12) {
            const monthIndex = month - 1;
            const monthValue = customer.monthly_runs[monthIndex];
            
            if (monthValue && monthValue !== '-' && monthValue !== 'Not Run') {
                console.log(`✅ EXCEL CUSTOMER MONTH DATA: ${networkName} month ${month} = ${monthValue}`);
                return {
                    count: 1,
                    date: monthValue,
                    fullDate: monthValue
                };
            }
        }
        
        // Check if customer has networks with monthly_runs
        if (customer.networks && Array.isArray(customer.networks)) {
            const targetNetwork = customer.networks.find(net => {
                return net.name === networkName || 
                       net.network_name === networkName ||
                       net.name.includes(networkName) ||
                       networkName.includes(net.name);
            });
            
            if (targetNetwork) {
                console.log(`🎯 Found network: ${targetNetwork.name}`);
                
                // Check for monthly_runs dictionary
                if (targetNetwork.monthly_runs && typeof targetNetwork.monthly_runs === 'object') {
                    const monthKey = `${year}-${month.toString().padStart(2, '0')}`;
                    if (targetNetwork.monthly_runs[monthKey]) {
                        const monthValue = targetNetwork.monthly_runs[monthKey];
                        console.log(`✅ NETWORK MONTHLY_RUNS: ${networkName} ${monthKey} = ${monthValue}`);
                        
                        if (monthValue === 'Not Run' || monthValue === 'Not Started') {
                            return { count: 0, date: 'Not Run', fullDate: 'Not Run' };
                        } else {
                            // Parse date like '2025-05-21' to '21-May-25'
                            try {
                                const apiDate = new Date(monthValue);
                                if (!isNaN(apiDate.getTime())) {
                                    const day = apiDate.getDate();
                                    const monthName = apiDate.toLocaleDateString('en-US', { month: 'short' });
                                    const yearShort = apiDate.getFullYear().toString().slice(-2);
                                    return {
                                        count: 1,
                                        date: `${day}-${monthName}-${yearShort}`,
                                        fullDate: monthValue
                                    };
                                }
                            } catch (error) {
                                console.log(`❌ Date parsing error: ${error.message}`);
                            }
                        }
                    }
                }
                
                // Check for months array
                if (targetNetwork.months && Array.isArray(targetNetwork.months)) {
                    const monthIndex = month - 1;
                    const monthValue = targetNetwork.months[monthIndex];
                    
                    if (monthValue && monthValue !== '-') {
                        console.log(`✅ NETWORK MONTHS ARRAY: ${networkName} month ${month} = ${monthValue}`);
                        return {
                            count: monthValue === 'Not Run' ? 0 : 1,
                            date: monthValue,
                            fullDate: monthValue
                        };
                    }
                }
            }
        }
    }
    
    // PRIORITY 2: Database customers
    if (customer.networks && Array.isArray(customer.networks)) {
        const targetNetwork = customer.networks.find(network => {
            return network.network_name === networkName || 
                   network.name === networkName ||
                   network.name.includes(networkName) ||
                   networkName.includes(network.name);
        });
        
        if (targetNetwork && targetNetwork.last_run_date && targetNetwork.runs > 0) {
            try {
                const networkDate = new Date(targetNetwork.last_run_date);
                if (!isNaN(networkDate.getTime())) {
                    const networkYear = networkDate.getFullYear();
                    const networkMonth = networkDate.getMonth() + 1;
                    
                    if (networkYear === year && networkMonth === month) {
                        const day = networkDate.getDate();
                        const monthName = networkDate.toLocaleDateString('en-US', { month: 'short' });
                        const yearShort = networkDate.getFullYear().toString().slice(-2);
                        const formattedDate = `${day}-${monthName}-${yearShort}`;
                        
                        console.log(`✅ DB NETWORK: ${networkName} = ${formattedDate}`);
                        return {
                            count: targetNetwork.runs,
                            date: formattedDate,
                            fullDate: targetNetwork.last_run_date
                        };
                    }
                }
            } catch (error) {
                console.log(`❌ DB network date error: ${error.message}`);
            }
        }
    }
    
    console.log(`⚠️ No data found for ${networkName} in month ${month}`);
    return { count: 0, date: '-', fullDate: 'No data' };
};

// FORCE UPDATE ALL NETWORK ROWS
function forceUpdateNetworkDates() {
    console.log('🔄 FORCING UPDATE OF ALL NETWORK ROWS...');
    
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`Found ${networkRows.length} network rows to update`);
    
    networkRows.forEach((row, index) => {
        const networkNameElement = row.querySelector('.network-name-main');
        if (!networkNameElement) return;
        
        const networkName = networkNameElement.textContent.replace('└─ ', '').trim();
        console.log(`🔧 Updating row ${index + 1}: ${networkName}`);
        
        // Find customer for this network
        let customerRow = row.previousElementSibling;
        while (customerRow && !customerRow.classList.contains('customer-summary-row')) {
            customerRow = customerRow.previousElementSibling;
        }
        
        if (customerRow) {
            const customerNameElement = customerRow.querySelector('.customer-name-main');
            if (customerNameElement) {
                const customerText = customerNameElement.textContent;
                const customerName = customerText.replace(/[📋📄💾🔄]/g, '').trim().split('\n')[0];
                
                // Find customer data
                if (window.dashboardData && window.dashboardData.customers) {
                    const customerData = Object.values(window.dashboardData.customers).find(c => 
                        c.name && c.name.toLowerCase().includes(customerName.toLowerCase())
                    );
                    
                    if (customerData) {
                        console.log(`📊 Found customer data for: ${customerName}`);
                        console.log(`Customer type:`, {
                            excel_source: customerData.excel_source,
                            excel_data: customerData.excel_data,
                            migrated_excel_data: customerData.migrated_excel_data
                        });
                        
                        // Update month cells
                        const monthCells = Array.from(row.querySelectorAll('td')).slice(6, 18);
                        if (monthCells.length === 12) {
                            monthCells.forEach((cell, monthIndex) => {
                                const monthNum = monthIndex + 1;
                                const result = window.getNetworkMonthRunDates(customerData, networkName, 2024, monthNum);
                                
                                if (result.date && result.date !== '-' && result.date !== 'No data') {
                                    cell.textContent = result.date;
                                    cell.style.color = '#374151';
                                    cell.style.fontWeight = '600';
                                    console.log(`✅ Updated ${networkName} month ${monthNum}: ${result.date}`);
                                } else {
                                    cell.textContent = '-';
                                    cell.style.color = '#9ca3af';
                                }
                            });
                        }
                    }
                }
            }
        }
    });
    
    console.log('🎉 FORCE UPDATE COMPLETE!');
}

// Apply the fix
updateCustomerGrid();

// Force update after a delay
setTimeout(() => {
    forceUpdateNetworkDates();
}, 1000);

console.log('✅ ULTIMATE NETWORK DATES FIX APPLIED!');
console.log('📋 Excel customers should now show network dates properly!');