// COMPREHENSIVE CHART DISPLAY FIX
// This script addresses the issue where charts show "No activity" despite data being available

// PROBLEM ANALYSIS:
// 1. Database has 32 customers with monthly_runs data
// 2. Recent data exists for October (BSNL, OPT_NC, Moratelindo) 
// 3. Tata has 9 months of data through September
// 4. But charts show "No activity data" and "No activity this month"

// ROOT CAUSE: Chart functions need enhanced data detection logic

// ENHANCED CHART UPDATE FUNCTIONS
// These replace the existing functions in customer_dashboard.html

function updateTrackingGraphEnhanced() {
    console.log('🔄 ENHANCED: Updating tracking graph with improved data detection...');
    
    const graphContainer = document.getElementById('tracking-graph');
    const trackingContainer = graphContainer.parentElement;
    const customers = dashboardData.customers;
    
    console.log('📊 Available customers for tracking graph:', Object.keys(customers || {}));
    
    // Get last 6 months data with enhanced real data detection
    const currentDate = new Date();
    const monthsData = [];
    
    // Generate last 6 months
    for (let i = 5; i >= 0; i--) {
        const monthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'short' });
        const monthNumber = monthDate.getMonth() + 1;
        const year = monthDate.getFullYear();
        
        // Calculate total runs for this month from all customers - ENHANCED LOGIC
        let monthTotal = 0;
        let monthDetailsFound = [];
        
        if (customers && Object.keys(customers).length > 0) {
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                
                // ENHANCED: Try multiple approaches to get month data
                let monthRuns = 0;
                
                // Method 1: Use enhanced getCustomerMonthRuns
                monthRuns = getCustomerMonthRunsEnhanced(customer, year, monthNumber);
                
                // Method 2: If no result, try direct monthly_runs lookup
                if (monthRuns === 0 && customer.monthly_runs) {
                    const monthKey = `${year}-${monthNumber.toString().padStart(2, '0')}`;
                    const monthData = customer.monthly_runs[monthKey];
                    if (monthData && monthData !== '-' && monthData !== 'Not Started' && monthData !== 'No Report') {
                        monthRuns = 1; // Found valid data
                        console.log(`📅 Direct lookup: ${customerName} has data for ${monthKey}: ${monthData}`);
                    }
                }
                
                // Method 3: Check individual networks if available
                if (monthRuns === 0 && customer.networks && Array.isArray(customer.networks)) {
                    customer.networks.forEach(network => {
                        if (network.monthly_runs || network.months) {
                            const networkData = network.monthly_runs || network.months;
                            if (Array.isArray(networkData) && networkData[monthNumber - 1]) {
                                const monthValue = networkData[monthNumber - 1];
                                if (monthValue && monthValue !== '-' && monthValue !== 'Not Started') {
                                    monthRuns += 1;
                                    console.log(`📅 Network lookup: ${customerName}/${network.name} has data for month ${monthNumber}`);
                                }
                            } else if (typeof networkData === 'object') {
                                const monthKey = `${year}-${monthNumber.toString().padStart(2, '0')}`;
                                if (networkData[monthKey] && networkData[monthKey] !== '-') {
                                    monthRuns += 1;
                                }
                            }
                        }
                    });
                }
                
                if (monthRuns > 0) {
                    monthTotal += monthRuns;
                    monthDetailsFound.push(`${customerName}: ${monthRuns}`);
                }
            });
        }
        
        console.log(`📅 Enhanced month ${monthName} ${year}: ${monthTotal} total runs (${monthDetailsFound.join(', ')})`);
        
        monthsData.push({
            month: monthName,
            runs: monthTotal,
            fullDate: monthDate,
            details: monthDetailsFound
        });
    }
    
    const maxRuns = Math.max(...monthsData.map(m => m.runs), 1);
    const totalRuns = monthsData.reduce((sum, month) => sum + month.runs, 0);
    
    graphContainer.innerHTML = '';
    
    console.log(`📊 Tracking graph summary: ${totalRuns} total runs, max: ${maxRuns}`);
    
    // Handle empty data state with enhanced detection
    if (totalRuns === 0) {
        // ENHANCED: Check if customers have ANY data at all
        let hasAnyCustomerData = false;
        let anyMonthCustomers = [];
        
        if (customers && Object.keys(customers).length > 0) {
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                
                // Check for any month data
                if (customer.monthly_runs && Object.keys(customer.monthly_runs).length > 0) {
                    const validEntries = Object.entries(customer.monthly_runs).filter(([key, value]) => 
                        value && value !== '-' && value !== 'Not Started' && value !== 'No Report'
                    );
                    if (validEntries.length > 0) {
                        hasAnyCustomerData = true;
                        anyMonthCustomers.push(`${customerName} (${validEntries.length} months)`);
                    }
                }
                
                // Check total_runs
                if ((customer.total_runs || customer.runs || 0) > 0) {
                    hasAnyCustomerData = true;
                    anyMonthCustomers.push(`${customerName} (${customer.total_runs || customer.runs} total)`);
                }
            });
        }
        
        if (hasAnyCustomerData) {
            console.log('✅ Found customer data outside 6-month window:', anyMonthCustomers.join(', '));
            graphContainer.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #6b7280;">
                    <div style="font-size: 2rem; margin-bottom: 16px;">📊</div>
                    <div style="font-weight: 600; margin-bottom: 8px;">Data exists but not in last 6 months</div>
                    <div style="font-size: 0.9rem; margin-bottom: 8px;">Found activity from: ${anyMonthCustomers.slice(0, 3).join(', ')}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">Try applying date filters to see historical data</div>
                </div>
            `;
        } else {
            graphContainer.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #6b7280;">
                    <div style="font-size: 2rem; margin-bottom: 16px;">📈</div>
                    <div style="font-weight: 600; margin-bottom: 8px;">No activity data</div>
                    <div style="font-size: 0.9rem;">Start by uploading health checks</div>
                </div>
            `;
        }
        return;
    }
    
    // Render the enhanced line chart (rest of original code continues...)
    graphContainer.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: center;
        height: 140px;
        padding: 20px;
        position: relative;
        background: linear-gradient(to top, rgba(102, 126, 234, 0.03) 0%, transparent 40%);
        border-radius: 12px;
    `;
    
    // Create enhanced chart visualization
    const chartWidth = 320;
    const chartHeight = 120;
    const padding = { left: 25, right: 25, top: 25, bottom: 25 };
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', chartHeight);
    svg.setAttribute('viewBox', `0 0 ${chartWidth} ${chartHeight}`);
    
    const innerWidth = chartWidth - padding.left - padding.right;
    const innerHeight = chartHeight - padding.top - padding.bottom;
    
    // Create data points
    const points = monthsData.map((month, i) => {
        const x = padding.left + (i / Math.max(monthsData.length - 1, 1)) * innerWidth;
        const normalizedValue = maxRuns > 0 ? month.runs / maxRuns : 0;
        const y = padding.top + innerHeight - (normalizedValue * innerHeight * 0.9);
        
        return { x, y, runs: month.runs, month: month.month };
    });
    
    // Draw line
    let pathData = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
        pathData += ` L ${points[i].x} ${points[i].y}`;
    }
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathData);
    path.setAttribute('stroke', '#3b82f6');
    path.setAttribute('stroke-width', '3');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke-linecap', 'round');
    svg.appendChild(path);
    
    // Add data points
    points.forEach(point => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', point.x);
        circle.setAttribute('cy', point.y);
        circle.setAttribute('r', '5');
        circle.setAttribute('fill', '#3b82f6');
        circle.setAttribute('stroke', 'white');
        circle.setAttribute('stroke-width', '2');
        svg.appendChild(circle);
        
        // Add value labels
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', point.x);
        text.setAttribute('y', point.y - 12);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('fill', '#1f2937');
        text.textContent = point.runs;
        svg.appendChild(text);
        
        // Add month labels
        const monthText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        monthText.setAttribute('x', point.x);
        monthText.setAttribute('y', chartHeight - 8);
        monthText.setAttribute('text-anchor', 'middle');
        monthText.setAttribute('font-size', '12');
        monthText.setAttribute('font-weight', '600');
        monthText.setAttribute('fill', '#4b5563');
        monthText.textContent = point.month;
        svg.appendChild(monthText);
    });
    
    graphContainer.appendChild(svg);
    console.log('✅ Enhanced tracking graph rendered successfully');
}

function updateCustomerMonthChartEnhanced() {
    console.log('🔄 ENHANCED: Updating customer month chart with improved data detection...');
    
    const chartContainer = document.getElementById('customer-month-chart');
    const chartContainerParent = chartContainer.parentElement;
    const customers = dashboardData.customers;
    
    // Determine target month - use current month or filtered month
    const currentDate = new Date();
    let targetMonth = currentDate.getMonth() + 1;
    let targetYear = currentDate.getFullYear();
    let targetMonthName = currentDate.toLocaleDateString('en-US', { month: 'long' });
    
    // Check if filter is active
    const isFilterActive = currentStartDate && currentEndDate;
    if (isFilterActive) {
        const filterStartDate = new Date(currentStartDate);
        targetMonth = filterStartDate.getMonth() + 1;
        targetYear = filterStartDate.getFullYear();
        targetMonthName = filterStartDate.toLocaleDateString('en-US', { month: 'long' });
        console.log(`📅 Using filtered month: ${targetMonthName} ${targetYear} (filter active)`);
    }
    
    // Update the chart title
    const chartTitle = document.getElementById('customer-chart-title');
    if (chartTitle) {
        const filterText = isFilterActive ? ' (Filtered)' : '';
        chartTitle.textContent = `👥 Active Customers - ${targetMonthName} ${targetYear}${filterText}`;
    }
    
    const customersData = [];
    
    console.log(`📊 Available customers for month chart:`, Object.keys(customers || {}));
    
    if (customers && Object.keys(customers).length > 0) {
        Object.entries(customers).forEach(([customerKey, customer]) => {
            const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
            
            // ENHANCED: Try multiple approaches to get month data
            let monthRuns = getCustomerMonthRunsEnhanced(customer, targetYear, targetMonth);
            
            console.log(`🔍 Customer ${customerName}: Enhanced month runs = ${monthRuns}`);
            
            if (monthRuns > 0) {
                customersData.push({
                    name: customerName,
                    runs: monthRuns,
                    customer: customer,
                    source: 'enhanced_detection'
                });
            }
        });
        
        console.log(`📊 Found ${customersData.length} customers with data in ${targetMonthName} ${targetYear}`);
        
        // FALLBACK: If target month has no data, try other months
        if (customersData.length === 0 && !isFilterActive) {
            console.log('📊 No data in target month, trying all months for any activity...');
            
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                let totalRuns = 0;
                let foundMonths = [];
                
                // Check all 12 months
                for (let month = 1; month <= 12; month++) {
                    const monthRuns = getCustomerMonthRunsEnhanced(customer, targetYear, month);
                    if (monthRuns > 0) {
                        totalRuns += monthRuns;
                        foundMonths.push(month);
                    }
                }
                
                if (totalRuns > 0) {
                    customersData.push({
                        name: customerName,
                        runs: totalRuns,
                        customer: customer,
                        source: `fallback_any_month (months: ${foundMonths.join(',')})`
                    });
                }
            });
            
            if (customersData.length > 0) {
                console.log(`✅ Fallback: Found ${customersData.length} customers with activity in any month`);
                // Update chart title to reflect fallback
                if (chartTitle) {
                    chartTitle.textContent = `👥 Active Customers - Any Month ${targetYear} (Showing Available Data)`;
                }
            }
        }
        
        // Sort by runs (highest first) and limit
        customersData.sort((a, b) => b.runs - a.runs);
        customersData.splice(10); // Keep only top 10
    }
    
    console.log('📊 Final customer data for chart:', customersData.map(c => `${c.name}: ${c.runs} (${c.source})`));
    
    chartContainer.innerHTML = '';
    
    // Handle empty data state
    if (customersData.length === 0) {
        // ENHANCED: Check if ANY customer data exists
        let hasAnyData = false;
        let sampleCustomers = [];
        
        if (customers && Object.keys(customers).length > 0) {
            Object.entries(customers).forEach(([customerKey, customer]) => {
                const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
                
                // Check various data indicators
                if ((customer.total_runs || 0) > 0) {
                    hasAnyData = true;
                    sampleCustomers.push(`${customerName} (${customer.total_runs} total)`);
                } else if (customer.monthly_runs && Object.keys(customer.monthly_runs).length > 0) {
                    const validMonths = Object.entries(customer.monthly_runs).filter(([k, v]) => 
                        v && v !== '-' && v !== 'Not Started' && v !== 'No Report'
                    );
                    if (validMonths.length > 0) {
                        hasAnyData = true;
                        sampleCustomers.push(`${customerName} (${validMonths.length} months)`);
                    }
                }
            });
        }
        
        if (hasAnyData) {
            chartContainer.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #6b7280;">
                    <div style="font-size: 2rem; margin-bottom: 16px;">👥</div>
                    <div style="font-weight: 600; margin-bottom: 8px;">No activity in ${targetMonthName}</div>
                    <div style="font-size: 0.9rem; margin-bottom: 8px;">But found data for: ${sampleCustomers.slice(0, 3).join(', ')}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">Try different date filters or check the table below</div>
                </div>
            `;
        } else {
            chartContainer.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #6b7280;">
                    <div style="font-size: 2rem; margin-bottom: 16px;">📈</div>
                    <div style="font-weight: 600; margin-bottom: 8px;">No activity this month</div>
                    <div style="font-size: 0.9rem;">Customers will appear here when they run health checks in ${targetMonthName}</div>
                </div>
            `;
        }
        return;
    }
    
    // Render customer bars
    const maxRuns = Math.max(...customersData.map(c => c.runs), 1);
    
    chartContainer.style.cssText = `
        display: flex;
        align-items: flex-end;
        justify-content: space-evenly;
        padding: 8px;
        height: 100px;
        gap: 4px;
        overflow-x: auto;
        overflow-y: hidden;
        background: rgba(248, 250, 252, 0.3);
        border-radius: 6px;
    `;
    
    // Create chart bars for each customer
    customersData.forEach((customerData, index) => {
        const height = 40; // Fixed height for all bars
        const isTopPerformer = index < 3;
        
        const chartBar = document.createElement('div');
        chartBar.className = 'customer-chart-bar';
        chartBar.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
            margin: 0 6px;
            flex: 1;
            max-width: 85px;
            min-width: 70px;
            height: 85px;
            cursor: pointer;
            transition: all 0.3s ease;
            filter: drop-shadow(0 1px 3px rgba(0,0,0,0.1));
        `;
        
        const barColor = isTopPerformer ? 
            (index === 0 ? '#10b981' : index === 1 ? '#3b82f6' : '#f59e0b') : 
            '#6b7280';
        
        chartBar.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; width: 100%;">
                <div style="
                    background: ${barColor};
                    color: white;
                    font-weight: 800;
                    font-size: 0.8rem;
                    padding: 3px 8px;
                    border-radius: 6px;
                    margin-bottom: 4px;
                    min-width: 24px;
                    text-align: center;
                    box-shadow: 0 3px 8px rgba(0,0,0,0.25);
                " title="${customerData.name}: ${customerData.runs} runs (${customerData.source})">
                    ${customerData.runs}
                </div>
                <div style="width: 80%; height: ${height}px; background: linear-gradient(135deg, ${barColor} 0%, ${barColor}cc 100%); border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"></div>
                <div style="font-size: 0.65rem; font-weight: 700; color: #374151; text-align: center; margin-top: 6px; line-height: 1.1;">
                    ${customerData.name}
                </div>
            </div>
        `;
        
        // Add hover effects
        chartBar.addEventListener('mouseenter', () => {
            chartBar.style.transform = 'scale(1.08) translateY(-2px)';
            chartBar.style.filter = 'drop-shadow(0 3px 8px rgba(0,0,0,0.15))';
        });
        chartBar.addEventListener('mouseleave', () => {
            chartBar.style.transform = 'scale(1) translateY(0)';
            chartBar.style.filter = 'drop-shadow(0 1px 3px rgba(0,0,0,0.1))';
        });
        
        chartContainer.appendChild(chartBar);
    });
    
    console.log('✅ Enhanced customer month chart rendered successfully');
}

// ENHANCED HELPER FUNCTION
function getCustomerMonthRunsEnhanced(customer, year, month) {
    if (!customer) return 0;
    
    let runs = 0;
    
    // Method 1: Check monthly_runs with proper key format
    if (customer.monthly_runs && typeof customer.monthly_runs === 'object') {
        const monthKey = `${year}-${month.toString().padStart(2, '0')}`;
        const monthData = customer.monthly_runs[monthKey];
        
        if (monthData && monthData !== '-' && monthData !== 'Not Started' && monthData !== 'No Report' && monthData !== 'Not Run') {
            runs = 1;
            console.log(`✅ Found monthly_runs data: ${customer.name} ${monthKey} = ${monthData}`);
            return runs;
        }
    }
    
    // Method 2: Check months array (0-based index)
    if (customer.months && Array.isArray(customer.months) && customer.months.length >= month) {
        const monthValue = customer.months[month - 1];
        if (monthValue && monthValue !== '-' && monthValue !== 'Not Started' && monthValue !== 'No Report') {
            runs = 1;
            console.log(`✅ Found months array data: ${customer.name} month[${month-1}] = ${monthValue}`);
            return runs;
        }
    }
    
    // Method 3: Check networks array
    if (customer.networks && Array.isArray(customer.networks)) {
        customer.networks.forEach(network => {
            if (network.monthly_runs && typeof network.monthly_runs === 'object') {
                const monthKey = `${year}-${month.toString().padStart(2, '0')}`;
                const networkMonthData = network.monthly_runs[monthKey];
                if (networkMonthData && networkMonthData !== '-' && networkMonthData !== 'Not Started') {
                    runs += 1;
                    console.log(`✅ Found network monthly_runs: ${customer.name}/${network.name} ${monthKey} = ${networkMonthData}`);
                }
            } else if (network.months && Array.isArray(network.months) && network.months.length >= month) {
                const monthValue = network.months[month - 1];
                if (monthValue && monthValue !== '-' && monthValue !== 'Not Started') {
                    runs += 1;
                    console.log(`✅ Found network months: ${customer.name}/${network.name} month[${month-1}] = ${monthValue}`);
                }
            }
        });
    }
    
    return runs;
}

// ENHANCED REFRESH FUNCTION
function forceRefreshChartsEnhanced() {
    console.log('🔄 FORCE REFRESH: Enhanced charts with improved data detection');
    
    // Add delay to ensure DOM is ready
    setTimeout(() => {
        console.log('📊 Dashboard data before enhanced refresh:', {
            customersCount: Object.keys(dashboardData.customers || {}).length,
            sampleCustomer: Object.keys(dashboardData.customers || {})[0]
        });
        
        updateTrackingGraphEnhanced();
        updateCustomerMonthChartEnhanced();
        
        console.log('✅ Enhanced chart refresh completed');
    }, 100);
}

// DEBUG FUNCTIONS
function debugChartDataFlow() {
    console.log('🔍 DEBUGGING CHART DATA FLOW');
    console.log('='.repeat(50));
    
    console.log('1. Dashboard Data Structure:');
    console.log('   customers:', Object.keys(dashboardData.customers || {}));
    console.log('   statistics:', dashboardData.statistics);
    
    console.log('\\n2. Sample Customer Analysis:');
    const sampleKey = Object.keys(dashboardData.customers || {})[0];
    if (sampleKey) {
        const sampleCustomer = dashboardData.customers[sampleKey];
        console.log(`   Customer: ${sampleKey}`);
        console.log(`   Name: ${sampleCustomer.name || sampleCustomer.Customer}`);
        console.log(`   Monthly runs:`, sampleCustomer.monthly_runs);
        console.log(`   Networks:`, sampleCustomer.networks?.length || 0);
        console.log(`   Total runs:`, sampleCustomer.total_runs || sampleCustomer.runs);
    }
    
    console.log('\\n3. Current Month Test:');
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    console.log(`   Target: ${currentYear}-${currentMonth.toString().padStart(2, '0')}`);
    
    if (sampleKey) {
        const testRuns = getCustomerMonthRunsEnhanced(dashboardData.customers[sampleKey], currentYear, currentMonth);
        console.log(`   Test result for ${sampleKey}: ${testRuns} runs`);
    }
    
    console.log('\\n4. Available Data Summary:');
    let totalCustomersWithData = 0;
    let monthlyDataSummary = {};
    
    Object.entries(dashboardData.customers || {}).forEach(([key, customer]) => {
        if (customer.monthly_runs && Object.keys(customer.monthly_runs).length > 0) {
            totalCustomersWithData++;
            Object.keys(customer.monthly_runs).forEach(monthKey => {
                monthlyDataSummary[monthKey] = (monthlyDataSummary[monthKey] || 0) + 1;
            });
        }
    });
    
    console.log(`   Customers with monthly_runs: ${totalCustomersWithData}`);
    console.log(`   Monthly data distribution:`, monthlyDataSummary);
    
    console.log('='.repeat(50));
}

// EXPOSE FUNCTIONS FOR MANUAL TESTING
window.updateTrackingGraphEnhanced = updateTrackingGraphEnhanced;
window.updateCustomerMonthChartEnhanced = updateCustomerMonthChartEnhanced;
window.forceRefreshChartsEnhanced = forceRefreshChartsEnhanced;
window.debugChartDataFlow = debugChartDataFlow;
window.getCustomerMonthRunsEnhanced = getCustomerMonthRunsEnhanced;

console.log('✅ Enhanced chart functions loaded. Use forceRefreshChartsEnhanced() to apply fixes.');