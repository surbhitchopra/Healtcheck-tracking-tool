
// 🚀 FRONTEND AUTO-REFRESH FIX
// Add this to your dashboard template

// Store original functions
window.originalUpdateCharts = window.updateActivityGraph;
window.dashboardData = {};

// Enhanced real-time data fetching
function fetchRealTimeData() {
    const timestamp = new Date().getTime();
    const url = `/api/customer-dashboard/customers/?t=${timestamp}`;
    
    console.log("🔄 Fetching real-time data...");
    
    return fetch(url, {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.dashboardData = data.customers;
            console.log("✅ Real-time data loaded:", Object.keys(data.customers).length, "customers");
            return data.customers;
        } else {
            throw new Error(data.error || 'API returned success=false');
        }
    });
}

// Real-time month runs calculation
function getCustomerMonthRuns_REALTIME(customerName, targetMonth, targetYear) {
    console.log(`📊 Getting REAL-TIME runs for ${customerName} - ${targetMonth}/${targetYear}`);
    
    // Find customer in real-time data
    const customer = Object.values(window.dashboardData || {}).find(c => 
        c.name.toLowerCase().includes(customerName.toLowerCase()) ||
        customerName.toLowerCase().includes(c.name.toLowerCase())
    );
    
    if (!customer) {
        console.log(`❌ Customer ${customerName} not found in real-time data`);
        return 0;
    }
    
    // Use real-time monthly counts
    if (customer.monthly_counts) {
        const monthKey = `${targetYear}-${targetMonth.toString().padStart(2, '0')}`;
        const count = customer.monthly_counts[monthKey] || 0;
        console.log(`✅ REAL-TIME count for ${customerName} ${monthKey}: ${count}`);
        return count;
    }
    
    console.log(`⚠️ No monthly_counts for ${customerName}`);
    return 0;
}

// Update activity graph with real-time data
function updateActivityGraph_REALTIME() {
    if (!window.activityChart) {
        console.log("❌ Activity chart not found");
        return;
    }
    
    console.log("📊 Updating activity graph with real-time data...");
    
    const currentDate = new Date();
    const months = [];
    const data = [];
    
    // Get last 6 months
    for (let i = 5; i >= 0; i--) {
        const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
        const monthName = date.toLocaleString('default', { month: 'short' });
        months.push(monthName);
        
        // Count runs for this month across all customers
        let monthTotal = 0;
        Object.values(window.dashboardData || {}).forEach(customer => {
            const runs = getCustomerMonthRuns_REALTIME(customer.name, date.getMonth() + 1, date.getFullYear());
            monthTotal += runs;
        });
        
        data.push(monthTotal);
    }
    
    // Update chart
    window.activityChart.data.labels = months;
    window.activityChart.data.datasets[0].data = data;
    window.activityChart.update();
    
    console.log('✅ Activity graph updated with real-time data:', months, data);
}

// Update active customers chart with real-time data
function updateActiveCustomersChart_REALTIME() {
    if (!window.activeCustomersChart) {
        console.log("❌ Active customers chart not found");
        return;
    }
    
    console.log("🎯 Updating active customers chart with real-time data...");
    
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    
    const activeCustomers = [];
    const counts = [];
    const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6366F1'];
    
    Object.values(window.dashboardData || {}).forEach(customer => {
        const runs = getCustomerMonthRuns_REALTIME(customer.name, currentMonth, currentYear);
        if (runs > 0) {
            activeCustomers.push(customer.name);
            counts.push(runs);
        }
    });
    
    // Update chart
    window.activeCustomersChart.data.labels = activeCustomers;
    window.activeCustomersChart.data.datasets[0].data = counts;
    window.activeCustomersChart.data.datasets[0].backgroundColor = colors.slice(0, activeCustomers.length);
    window.activeCustomersChart.update();
    
    console.log('✅ Active customers chart updated with real-time data:', activeCustomers, counts);
}

// Main refresh function
function refreshDashboard() {
    fetchRealTimeData()
        .then(data => {
            updateActivityGraph_REALTIME();
            updateActiveCustomersChart_REALTIME();
            console.log("🎉 Dashboard refreshed with real-time data!");
        })
        .catch(error => {
            console.error("❌ Dashboard refresh error:", error);
        });
}

// Auto-refresh every 30 seconds
setInterval(refreshDashboard, 30000);

// Refresh when tab becomes visible
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        console.log("👁️ Tab became visible, refreshing...");
        refreshDashboard();
    }
});

// Initial load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(refreshDashboard, 2000); // Wait for charts to be ready
    console.log("✅ Real-time dashboard system initialized!");
});

console.log("🚀 FRONTEND AUTO-REFRESH SYSTEM LOADED!");
