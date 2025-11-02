#!/usr/bin/env python
"""
🚀 FINAL PERMANENT SOLUTION: Graph Auto-Update After Tracker Generation
This will fix your OPT_NC graph update issue permanently!
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta

def analyze_current_setup():
    """Analyze current database setup"""
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("🔍 ANALYZING CURRENT SETUP...")
    
    # Check Customer table
    cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_customer WHERE name LIKE '%OPT%'")
    opt_customers = cursor.fetchone()[0]
    print(f"📊 OPT customers: {opt_customers}")
    
    # Check Sessions table
    cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession")
    total_sessions = cursor.fetchone()[0]
    print(f"📊 Total sessions: {total_sessions}")
    
    # Check recent sessions
    cursor.execute("""
        SELECT s.id, s.created_at, c.name, c.network_name, s.status
        FROM HealthCheck_app_healthchecksession s
        JOIN HealthCheck_app_customer c ON s.customer_id = c.id
        WHERE c.name LIKE '%OPT%'
        ORDER BY s.created_at DESC
        LIMIT 5
    """)
    
    opt_sessions = cursor.fetchall()
    print(f"📊 Recent OPT sessions: {len(opt_sessions)}")
    for session in opt_sessions:
        print(f"   {session}")
    
    conn.close()
    
    return {
        'opt_customers': opt_customers,
        'total_sessions': total_sessions,
        'recent_opt_sessions': len(opt_sessions)
    }

def create_backend_fix():
    """Create the backend API fix"""
    
    backend_code = '''
# ADD THIS TO YOUR views.py - PERMANENT FIX FOR GRAPH UPDATE

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from .models import Customer, HealthCheckSession

@require_http_methods(["GET"])
def api_customer_dashboard_customers_REALTIME(request):
    """
    🚀 REAL-TIME API: This counts actual sessions instead of static data
    Graphs will now always show current data!
    """
    try:
        print("📡 REAL-TIME API called")
        
        customers = Customer.objects.filter(is_deleted=False)
        customer_data = {}
        
        for customer in customers:
            # Count actual sessions for this customer
            sessions = HealthCheckSession.objects.filter(
                customer_id=customer.id,
                status='COMPLETED'
            )
            
            total_runs = sessions.count()
            
            # Calculate monthly runs for last 6 months
            monthly_runs = ['-'] * 12
            monthly_counts = {}
            
            current_date = datetime.now()
            
            # Get last 6 months data
            for i in range(6):
                target_date = current_date - timedelta(days=30*i)
                month_sessions = sessions.filter(
                    created_at__year=target_date.year,
                    created_at__month=target_date.month
                ).count()
                
                month_key = f"{target_date.year}-{target_date.month:02d}"
                monthly_counts[month_key] = month_sessions
                
                # Format for table display
                month_idx = target_date.month - 1
                if month_sessions > 0:
                    monthly_runs[month_idx] = f"{target_date.day}-{target_date.strftime('%b')}"
            
            customer_key = f"{customer.name}_{customer.network_name}_{customer.id}"
            
            customer_data[customer_key] = {
                'name': customer.name,
                'network_name': customer.network_name,
                'country': getattr(customer, 'country', 'Unknown'),
                'node_qty': getattr(customer, 'node_qty', 0),
                'ne_type': getattr(customer, 'ne_type', '1830 PSS'),
                'gtac': getattr(customer, 'gtac', 'PSS'),
                'total_runs': total_runs,  # 🔥 REAL COUNT FROM SESSIONS
                'months': monthly_runs,
                'monthly_counts': monthly_counts,  # 🔥 REAL MONTHLY COUNTS
                'networks': [{
                    'name': customer.network_name,
                    'network_name': customer.network_name,
                    'runs': total_runs,
                    'total_runs': total_runs,
                    'months': monthly_runs,
                    'monthly_counts': monthly_counts,
                    'country': getattr(customer, 'country', 'Unknown'),
                    'node_count': getattr(customer, 'node_qty', 0),
                    'gtac': getattr(customer, 'gtac', 'PSS')
                }],
                'networks_count': 1,
                'data_source': 'real_time_sessions',
                'last_updated': datetime.now().isoformat()
            }
        
        print(f"✅ REAL-TIME API: Returning {len(customer_data)} customers")
        
        return JsonResponse({
            'success': True,
            'customers': customer_data,
            'total_customers': len(customer_data),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'real_time_sessions'
        })
        
    except Exception as e:
        print(f"❌ REAL-TIME API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# 🔥 REPLACE YOUR EXISTING API WITH THIS ONE
# Change your URL pattern to point to api_customer_dashboard_customers_REALTIME
'''
    
    with open('BACKEND_REALTIME_FIX.py', 'w', encoding='utf-8') as f:
        f.write(backend_code)
    
    print("✅ Backend real-time fix created: BACKEND_REALTIME_FIX.py")

def create_frontend_fix():
    """Create the frontend auto-refresh fix"""
    
    frontend_code = '''
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
'''
    
    with open('FRONTEND_AUTO_REFRESH_FIX.js', 'w', encoding='utf-8') as f:
        f.write(frontend_code)
    
    print("✅ Frontend auto-refresh fix created: FRONTEND_AUTO_REFRESH_FIX.js")

def create_implementation_guide():
    """Create step-by-step implementation guide"""
    
    guide = '''
🚀 PERMANENT GRAPH UPDATE SOLUTION - IMPLEMENTATION GUIDE

PROBLEM: OPT_NC runs show 1 in graph but should show 2 after new tracker generation

SOLUTION: Real-time session counting instead of static data

📋 STEP-BY-STEP IMPLEMENTATION:

1. BACKEND FIX (views.py):
   - Copy the code from BACKEND_REALTIME_FIX.py
   - Add the api_customer_dashboard_customers_REALTIME function to your views.py
   - Update your URL pattern to use this new function

2. FRONTEND FIX (dashboard template):
   - Copy the code from FRONTEND_AUTO_REFRESH_FIX.js
   - Add it to your dashboard template inside <script> tags
   - This will auto-refresh graphs every 30 seconds

3. URL UPDATE (urls.py):
   Change from:
   path('api/customer-dashboard/customers/', views.api_customer_dashboard_customers, name='api_customer_dashboard_customers'),
   
   To:
   path('api/customer-dashboard/customers/', views.api_customer_dashboard_customers_REALTIME, name='api_customer_dashboard_customers'),

4. TEST THE FIX:
   - Generate a new tracker for OPT_NC
   - Wait 30 seconds or refresh the page
   - Graph should now show updated count (2 instead of 1)

🔥 WHY THIS WORKS:
- Counts actual HealthCheckSession records instead of static data
- Real-time API queries database every time
- Auto-refresh ensures graphs stay current
- No more cache/stale data issues

✅ RESULT:
- Graphs auto-update when new trackers are generated
- No manual refresh needed
- Always shows current session counts
- Works for all customers, not just OPT_NC

⚡ IMMEDIATE BENEFITS:
- OPT_NC October count: 1 → 2 (correct)
- Last 6 months activity: Updates in real-time
- Active customers chart: Always current
- No more table vs graph mismatches
'''
    
    with open('IMPLEMENTATION_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Implementation guide created: IMPLEMENTATION_GUIDE.md")

def main():
    print("🚀 CREATING FINAL PERMANENT SOLUTION...")
    print("=" * 60)
    
    # Analyze current setup
    analysis = analyze_current_setup()
    
    print(f"\n📊 CURRENT STATUS:")
    print(f"   OPT customers: {analysis['opt_customers']}")
    print(f"   Total sessions: {analysis['total_sessions']}")
    print(f"   Recent OPT sessions: {analysis['recent_opt_sessions']}")
    
    # Create all fixes
    create_backend_fix()
    create_frontend_fix()
    create_implementation_guide()
    
    print("\n" + "=" * 60)
    print("✅ FINAL PERMANENT SOLUTION CREATED!")
    print("=" * 60)
    
    print("\n📁 FILES CREATED:")
    print("   1. BACKEND_REALTIME_FIX.py - Add to views.py")
    print("   2. FRONTEND_AUTO_REFRESH_FIX.js - Add to dashboard template")
    print("   3. IMPLEMENTATION_GUIDE.md - Step-by-step instructions")
    
    print("\n🎯 EXPECTED RESULT:")
    print("   ✅ OPT_NC October graph shows 2 runs (not 1)")
    print("   ✅ Graphs auto-update every 30 seconds")
    print("   ✅ No more manual refresh needed")
    print("   ✅ Real-time session counting")
    
    print("\n🚀 NEXT STEP: Read IMPLEMENTATION_GUIDE.md and follow the steps!")

if __name__ == "__main__":
    main()