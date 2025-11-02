#!/usr/bin/env python3
"""
Fixed script to check real database sessions and verify graph data
Uses correct database relationships to get customer data
"""

import sqlite3
from datetime import datetime, timedelta
import json

def check_database_sessions():
    print("🔍 CHECKING REAL DATABASE SESSIONS (FIXED)")
    print("=" * 60)
    
    # Connect to SQLite database
    db_path = "C:\\Users\\surchopr\\Hc_Final\\db.sqlite3"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, understand the database structure
        print("📊 Checking database structure...")
        
        # Check HealthCheck sessions table
        cursor.execute("PRAGMA table_info(HealthCheck_app_healthchecksession)")
        session_columns = [row[1] for row in cursor.fetchall()]
        print(f"HealthCheck Sessions columns: {session_columns}")
        
        # Check NetworkDetails table  
        cursor.execute("PRAGMA table_info(HealthCheck_app_networkdetails)")
        network_columns = [row[1] for row in cursor.fetchall()]
        print(f"NetworkDetails columns: {network_columns}")
        
        # Get total sessions count
        cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession")
        total_sessions = cursor.fetchone()[0]
        print(f"📈 Total HealthCheck sessions in database: {total_sessions}")
        
        # Get recent sessions with customer info
        print(f"\n📊 Getting sessions with customer information...")
        
        cursor.execute("""
        SELECT hcs.id, hcs.session_id, hcs.created_at, hcs.status,
               nd.customer_name, nd.network_name
        FROM HealthCheck_app_healthchecksession hcs
        LEFT JOIN HealthCheck_app_networkdetails nd ON hcs.customer_id = nd.id
        ORDER BY hcs.created_at DESC
        LIMIT 20
        """)
        
        recent_sessions = cursor.fetchall()
        
        print(f"📋 Found {len(recent_sessions)} recent sessions:")
        for session in recent_sessions[:10]:  # Show top 10
            session_id, uuid, created_at, status, customer, network = session
            print(f"   Session {session_id}: {customer or 'Unknown'} - {network or 'Unknown'} ({created_at})")
        
        # Check October 2025 sessions specifically
        print(f"\n🎯 OCTOBER 2025 SESSIONS:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT nd.customer_name, COUNT(hcs.id) as session_count,
               GROUP_CONCAT(DATE(hcs.created_at)) as dates
        FROM HealthCheck_app_healthchecksession hcs
        LEFT JOIN HealthCheck_app_networkdetails nd ON hcs.customer_id = nd.id  
        WHERE hcs.created_at >= '2025-10-01' 
        AND hcs.created_at < '2025-11-01'
        GROUP BY nd.customer_name
        ORDER BY session_count DESC
        """)
        
        october_data = cursor.fetchall()
        
        if october_data:
            print("✅ October 2025 sessions found:")
            customer_counts = {}
            for customer, count, dates in october_data:
                customer_name = customer or "Unknown"
                customer_counts[customer_name] = count
                dates_list = dates.split(',') if dates else []
                print(f"🏢 {customer_name}: {count} sessions")
                if dates_list:
                    print(f"   📅 Dates: {', '.join(dates_list[:5])}{'...' if len(dates_list) > 5 else ''}")
        else:
            print("❌ No October 2025 sessions found")
            customer_counts = {}
            
        # Check last 6 months
        print(f"\n📊 LAST 6 MONTHS BREAKDOWN:")
        print("-" * 40)
        
        monthly_counts = {}
        for i in range(6):
            # Calculate month boundaries
            if i == 0:
                # Current month (October 2025)
                start_date = '2025-10-01'
                end_date = '2025-11-01'
                month_name = 'Oct'
            elif i == 1:
                start_date = '2025-09-01'
                end_date = '2025-10-01'
                month_name = 'Sep'
            elif i == 2:
                start_date = '2025-08-01' 
                end_date = '2025-09-01'
                month_name = 'Aug'
            elif i == 3:
                start_date = '2025-07-01'
                end_date = '2025-08-01'
                month_name = 'Jul'
            elif i == 4:
                start_date = '2025-06-01'
                end_date = '2025-07-01'
                month_name = 'Jun'
            elif i == 5:
                start_date = '2025-05-01'
                end_date = '2025-06-01'
                month_name = 'May'
            
            cursor.execute("""
            SELECT COUNT(*) FROM HealthCheck_app_healthchecksession
            WHERE created_at >= ? AND created_at < ?
            """, (start_date, end_date))
            
            count = cursor.fetchone()[0]
            monthly_counts[month_name] = count
            print(f"📅 {month_name} 2025: {count} sessions")
        
        # Compare with graph data
        print(f"\n🎯 GRAPH vs DATABASE COMPARISON:")
        print("=" * 50)
        
        print("👥 Active Customers - October 2025:")
        graph_customers = {'BSNL': 3, 'Moratelindo': 1, 'OPT_NC': 1}
        print(f"   Graph shows: {graph_customers}")
        print(f"   Database shows: {customer_counts}")
        
        print(f"\n📈 Last 6 Months Activity:")
        graph_months = {'May': 18, 'Jun': 23, 'Jul': 20, 'Aug': 19, 'Sep': 11, 'Oct': 5}
        print(f"   Graph shows: {graph_months}")
        print(f"   Database shows: {monthly_counts}")
        
        # Generate JavaScript fix
        print(f"\n🔧 GENERATING JAVASCRIPT FIX:")
        print("-" * 35)
        
        js_fix = f"""
// 🔧 REAL DATABASE DATA FIX - Paste this in browser console

console.log('🔄 Updating graphs with REAL database data...');

const realCustomerData = {json.dumps(customer_counts)};
const realMonthlyData = {json.dumps(monthly_counts)};

// Update customer chart with real data
function updateCustomerChartReal() {{
    const chart = document.getElementById('customer-month-chart');
    if (!chart) return;
    
    const customers = Object.entries(realCustomerData).slice(0, 3);
    const maxRuns = Math.max(...Object.values(realCustomerData));
    
    let html = '<div style="display: flex; align-items: end; height: 35px; gap: 4px; padding: 5px;">';
    
    customers.forEach(([name, count], i) => {{
        const height = Math.max(8, (count / maxRuns) * 25);
        const colors = ['#10b981', '#3b82f6', '#f59e0b'];
        
        html += `
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
            <div style="background: ${{colors[i]}}; height: ${{height}}px; width: 100%; border-radius: 2px; position: relative;">
                <div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); 
                           background: ${{colors[i]}}; color: white; padding: 1px 4px; border-radius: 50%; 
                           font-size: 0.6rem; font-weight: 600; min-width: 16px; text-align: center;">${{count}}</div>
            </div>
            <div style="font-size: 0.6rem; font-weight: 600; color: #374151; margin-top: 2px; text-align: center;">
                ${{name.length > 8 ? name.substring(0, 8) + '..' : name}}
            </div>
            <div style="font-size: 0.5rem; color: #6b7280;">Oct</div>
        </div>`;
    }});
    
    html += '</div>';
    chart.innerHTML = html;
    
    // Update title
    const title = document.getElementById('customer-chart-title');
    if (title) title.textContent = '👥 Active Customers - October 2025 (REAL DATA)';
}}

// Update tracking graph with real data  
function updateTrackingGraphReal() {{
    const graph = document.getElementById('tracking-graph');
    if (!graph) return;
    
    const months = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
    const data = months.map(m => realMonthlyData[m] || 0);
    const maxVal = Math.max(...data);
    
    let html = '<div style="position: relative; height: 35px; padding: 5px;">';
    
    // Add SVG line chart
    html += '<svg style="position: absolute; width: 100%; height: 100%;">';
    
    let pathData = '';
    data.forEach((val, i) => {{
        const x = 10 + (i * 40);
        const y = 25 - (val / maxVal * 15);
        pathData += (i === 0 ? `M${{x}},${{y}}` : ` L${{x}},${{y}}`);
        
        // Add points and labels
        html += `
        <circle cx="${{x}}" cy="${{y}}" r="2" fill="#3b82f6"/>
        <text x="${{x}}" y="${{y-5}}" text-anchor="middle" style="font-size: 8px; fill: #3b82f6; font-weight: 600;">${{val}}</text>
        <text x="${{x}}" y="32" text-anchor="middle" style="font-size: 8px; fill: #374151; font-weight: 600;">${{months[i]}}</text>
        `;
    }});
    
    html += `<path d="${{pathData}}" stroke="#3b82f6" stroke-width="1.5" fill="none"/>`;
    html += '</svg></div>';
    
    graph.innerHTML = html;
}}

// Apply fixes
updateCustomerChartReal();
updateTrackingGraphReal();

console.log('✅ Graphs updated with REAL database data!');
console.log('📊 Customer data:', realCustomerData);  
console.log('📈 Monthly data:', realMonthlyData);
"""
        
        # Save JavaScript fix to file
        with open('C:\\Users\\surchopr\\Hc_Final\\real_data_fix.js', 'w', encoding='utf-8') as f:
            f.write(js_fix)
        
        print("✅ JavaScript fix saved to: real_data_fix.js")
        print("📋 Copy and paste the content into browser console to update graphs")
        
        conn.close()
        
        return customer_counts, monthly_counts
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return {}, {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}, {}

if __name__ == "__main__":
    check_database_sessions()