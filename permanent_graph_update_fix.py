#!/usr/bin/env python
"""
PERMANENT FIX: Graph Auto-Update After Tracker Generation
This script will implement a complete solution for automatic graph updates
"""

import os
import sqlite3
import json
from datetime import datetime

def check_sessions_table():
    """Check the sessions table structure and data"""
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Check session table structure
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%session%'")
    session_tables = cursor.fetchall()
    print(f"📋 Session tables found: {session_tables}")
    
    if session_tables:
        table_name = session_tables[0][0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Session columns: {[col[1] for col in columns]}")
        
        # Get recent sessions
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT 3")
        recent_sessions = cursor.fetchall()
        print(f"Recent sessions: {len(recent_sessions)}")
        for session in recent_sessions:
            print(f"   {session}")
    
    conn.close()

def fix_dashboard_api():
    """Fix the dashboard API to include real-time session counting"""
    
    api_fix = '''
// PERMANENT GRAPH UPDATE FIX
// Add this JavaScript to your dashboard template

// 1. Auto-refresh dashboard every 30 seconds
setInterval(function() {
    console.log("🔄 Auto-refreshing dashboard data...");
    loadCustomerData(true); // Force refresh
}, 30000);

// 2. Force refresh when page becomes visible (user returns to tab)
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        console.log("🔄 Tab became visible, refreshing data...");
        loadCustomerData(true);
    }
});

// 3. Enhanced loadCustomerData function with cache bypass
function loadCustomerData(forceRefresh = false) {
    const url = forceRefresh ? 
        '/api/customer-dashboard/customers/?refresh=' + Date.now() : 
        '/api/customer-dashboard/customers/';
        
    fetch(url, {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("📊 Received customer data:", data);
        updateChartsAndTable(data);
    })
    .catch(error => {
        console.error("❌ Error loading customer data:", error);
    });
}

// 4. Update both charts and table
function updateChartsAndTable(data) {
    if (data.success && data.customers) {
        // Update the main table
        updateCustomerTable(data.customers);
        
        // Update graphs
        updateActivityGraph(data.customers);
        updateActiveCustomersChart(data.customers);
        
        console.log("✅ Charts and table updated successfully");
    }
}
'''
    
    with open('dashboard_auto_refresh_fix.js', 'w') as f:
        f.write(api_fix)
    
    print("✅ Dashboard auto-refresh fix created: dashboard_auto_refresh_fix.js")

def create_backend_session_counter():
    """Create backend function to count sessions dynamically"""
    
    backend_fix = '''
def get_customer_runs_count(customer_name, network_name=None):
    """
    Dynamically count runs from sessions table
    This ensures graphs always show current data
    """
    from HealthCheck_app.models import HealthCheckSession
    from datetime import datetime, timedelta
    
    # Base query
    sessions = HealthCheckSession.objects.filter(
        customer_name__iexact=customer_name,
        is_deleted=False
    )
    
    if network_name:
        sessions = sessions.filter(network_name__iexact=network_name)
    
    # Count total runs
    total_runs = sessions.count()
    
    # Count monthly runs for last 6 months
    monthly_counts = {}
    current_date = datetime.now()
    
    for i in range(6):
        # Calculate month
        month_date = current_date - timedelta(days=30*i)
        month_key = month_date.strftime('%Y-%m')
        
        # Count sessions in this month
        month_sessions = sessions.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        
        monthly_counts[month_key] = month_sessions
    
    return {
        'total_runs': total_runs,
        'monthly_counts': monthly_counts,
        'last_updated': datetime.now().isoformat()
    }

def api_customer_dashboard_customers_FIXED(request):
    """
    FIXED API that counts sessions in real-time
    """
    try:
        from HealthCheck_app.models import Customer
        
        customers = Customer.objects.filter(is_deleted=False)
        customer_data = {}
        
        for customer in customers:
            # Get real-time session counts
            runs_data = get_customer_runs_count(customer.name, customer.network_name)
            
            customer_key = f"{customer.name}_{customer.network_name}_{customer.id}"
            
            customer_data[customer_key] = {
                'name': customer.name,
                'network_name': customer.network_name,
                'total_runs': runs_data['total_runs'],  # Real-time count
                'monthly_counts': runs_data['monthly_counts'],  # Real-time monthly
                'country': customer.country if hasattr(customer, 'country') else 'Unknown',
                'data_source': 'real_time_sessions',
                'last_updated': runs_data['last_updated']
            }
        
        return JsonResponse({
            'success': True,
            'customers': customer_data,
            'total_customers': len(customer_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
'''
    
    with open('backend_realtime_counter.py', 'w') as f:
        f.write(backend_fix)
    
    print("✅ Backend real-time counter created: backend_realtime_counter.py")

def create_complete_graph_fix():
    """Create JavaScript fix for graph updates"""
    
    graph_fix = '''
// COMPLETE GRAPH UPDATE FIX
// This will ensure graphs always show latest data

function getCustomerMonthRuns_FIXED(customerName, targetMonth, targetYear) {
    console.log(`📅 Getting runs for ${customerName} - ${targetMonth}/${targetYear}`);
    
    let totalRuns = 0;
    
    // Find customer in data
    const customer = Object.values(window.dashboardData || {}).find(c => 
        c.name === customerName
    );
    
    if (!customer) {
        console.log(`❌ Customer ${customerName} not found`);
        return 0;
    }
    
    // Use real-time monthly counts if available
    if (customer.monthly_counts) {
        const monthKey = `${targetYear}-${targetMonth.toString().padStart(2, '0')}`;
        totalRuns = customer.monthly_counts[monthKey] || 0;
        console.log(`✅ Real-time count for ${monthKey}: ${totalRuns}`);
        return totalRuns;
    }
    
    // Fallback to network counting
    if (customer.networks) {
        customer.networks.forEach(network => {
            if (network.monthly_runs) {
                const monthKey = `${targetYear}-${targetMonth.toString().padStart(2, '0')}`;
                if (network.monthly_runs[monthKey]) {
                    totalRuns += 1; // Count this network's run
                }
            }
        });
    }
    
    console.log(`📊 Final count for ${customerName} ${targetMonth}/${targetYear}: ${totalRuns}`);
    return totalRuns;
}

// Update activity graph with real-time data
function updateActivityGraph_FIXED(customerData) {
    if (!window.activityChart) return;
    
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
        Object.values(customerData).forEach(customer => {
            const runs = getCustomerMonthRuns_FIXED(customer.name, date.getMonth() + 1, date.getFullYear());
            monthTotal += runs;
        });
        
        data.push(monthTotal);
    }
    
    // Update chart
    window.activityChart.data.labels = months;
    window.activityChart.data.datasets[0].data = data;
    window.activityChart.update();
    
    console.log('📊 Activity graph updated:', months, data);
}

// Update active customers chart
function updateActiveCustomersChart_FIXED(customerData) {
    if (!window.activeCustomersChart) return;
    
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    
    const activeCustomers = [];
    const counts = [];
    const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];
    
    Object.values(customerData).forEach((customer, index) => {
        const runs = getCustomerMonthRuns_FIXED(customer.name, currentMonth, currentYear);
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
    
    console.log('🎯 Active customers chart updated:', activeCustomers, counts);
}

// Auto-refresh every 30 seconds
setInterval(() => {
    fetch('/api/customer-dashboard/customers/?t=' + Date.now())
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.dashboardData = data.customers;
                updateActivityGraph_FIXED(data.customers);
                updateActiveCustomersChart_FIXED(data.customers);
                console.log('🔄 Graphs auto-updated');
            }
        })
        .catch(error => console.error('❌ Auto-refresh error:', error));
}, 30000);

console.log('✅ Complete graph auto-update fix loaded');
'''
    
    with open('complete_graph_update_fix.js', 'w') as f:
        f.write(graph_fix)
    
    print("✅ Complete graph update fix created: complete_graph_update_fix.js")

def main():
    print("🚀 Creating PERMANENT Graph Update Fix...")
    
    # 1. Check current database structure
    check_sessions_table()
    
    # 2. Create backend fix
    create_backend_session_counter()
    
    # 3. Create frontend auto-refresh
    fix_dashboard_api()
    
    # 4. Create complete graph fix
    create_complete_graph_fix()
    
    print("\n✅ PERMANENT FIX COMPLETE!")
    print("\n📋 Next Steps:")
    print("1. Add backend_realtime_counter.py code to your views.py")
    print("2. Add complete_graph_update_fix.js to your dashboard template")
    print("3. Replace your current API endpoint with the fixed version")
    print("4. Graphs will now auto-update every 30 seconds")
    print("5. Real-time session counting will ensure accurate data")

if __name__ == "__main__":
    main()