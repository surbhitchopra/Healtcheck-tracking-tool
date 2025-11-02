#!/usr/bin/env python3
"""
FINAL SCRIPT: Get real database sessions and generate graph fix
Uses correct HealthCheck_app_customer table for customer names
"""

import sqlite3
import json
from datetime import datetime

def get_real_session_data():
    print("🔍 GETTING REAL DATABASE SESSION DATA")
    print("=" * 60)
    
    db_path = "C:\\Users\\surchopr\\Hc_Final\\db.sqlite3"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Analyzing HealthCheck sessions with customer names...")
        
        # Get October 2025 sessions with customer names
        cursor.execute("""
        SELECT c.name as customer_name, 
               COUNT(s.id) as session_count,
               GROUP_CONCAT(DATE(s.created_at)) as session_dates
        FROM HealthCheck_app_healthchecksession s
        JOIN HealthCheck_app_customer c ON s.customer_id = c.id
        WHERE s.created_at >= '2025-10-01' 
        AND s.created_at < '2025-11-01'
        GROUP BY c.name
        ORDER BY session_count DESC
        """)
        
        october_customers = cursor.fetchall()
        
        print(f"\n🎯 OCTOBER 2025 CUSTOMER SESSIONS:")
        print("-" * 45)
        
        customer_counts = {}
        if october_customers:
            for customer_name, count, dates in october_customers:
                customer_counts[customer_name] = count
                print(f"🏢 {customer_name}: {count} sessions")
                if dates:
                    date_list = dates.split(',')[:3]  # Show first 3 dates
                    print(f"   📅 Recent dates: {', '.join(date_list)}")
        else:
            print("❌ No October 2025 sessions found")
        
        # Get last 6 months data  
        print(f"\n📈 LAST 6 MONTHS BREAKDOWN:")
        print("-" * 35)
        
        months_data = [
            ('2025-05-01', '2025-06-01', 'May'),
            ('2025-06-01', '2025-07-01', 'Jun'), 
            ('2025-07-01', '2025-08-01', 'Jul'),
            ('2025-08-01', '2025-09-01', 'Aug'),
            ('2025-09-01', '2025-10-01', 'Sep'),
            ('2025-10-01', '2025-11-01', 'Oct')
        ]
        
        monthly_counts = {}
        for start, end, month_name in months_data:
            cursor.execute("""
            SELECT COUNT(*) FROM HealthCheck_app_healthchecksession
            WHERE created_at >= ? AND created_at < ?
            """, (start, end))
            
            count = cursor.fetchone()[0]
            monthly_counts[month_name] = count
            print(f"📅 {month_name} 2025: {count} sessions")
        
        # Show comparison
        print(f"\n📊 COMPARISON:")
        print("=" * 40)
        
        print("Current graphs show:")
        print("   👥 Customers: BSNL=3, Moratelindo=1, OPT_NC=1") 
        print("   📈 Monthly: May=18, Jun=23, Jul=20, Aug=19, Sep=11, Oct=5")
        
        print("\\nReal database shows:")
        print(f"   👥 Customers: {customer_counts}")
        print(f"   📈 Monthly: {monthly_counts}")
        
        # Generate JavaScript fix
        js_fix = f"""
// 🔧 FINAL GRAPH FIX - Paste this in browser console to update with REAL data

console.log('🚀 Updating graphs with REAL database data...');

const realCustomerData = {json.dumps(customer_counts)};
const realMonthlyData = {json.dumps(monthly_counts)};

console.log('📊 Real customer data from DB:', realCustomerData);
console.log('📈 Real monthly data from DB:', realMonthlyData);

// Update Active Customers chart (right side)
function updateCustomerChartWithRealData() {{
    const chart = document.getElementById('customer-month-chart');
    if (!chart) {{
        console.log('❌ Customer chart not found');
        return;
    }}
    
    console.log('🔄 Updating customer chart...');
    
    const customers = Object.entries(realCustomerData).slice(0, 3);
    if (customers.length === 0) {{
        chart.innerHTML = '<div style="padding: 10px; text-align: center; color: #6b7280;">No October 2025 sessions found</div>';
        return;
    }}
    
    const maxRuns = Math.max(...Object.values(realCustomerData), 1);
    let html = '<div style="display: flex; align-items: end; height: 35px; gap: 4px; padding: 5px;">';
    
    const colors = ['#10b981', '#3b82f6', '#f59e0b'];
    
    customers.forEach(([name, count], i) => {{
        const height = Math.max(8, (count / maxRuns) * 25);
        
        html += `
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
            <div style="background: ${{colors[i] || '#6b7280'}}; height: ${{height}}px; width: 100%; border-radius: 2px; position: relative;">
                <div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); 
                           background: ${{colors[i] || '#6b7280'}}; color: white; padding: 1px 4px; border-radius: 50%; 
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
    if (title) {{
        title.textContent = '👥 Active Customers - October 2025 (REAL DATA)';
        title.style.color = '#059669';
    }}
    
    console.log('✅ Customer chart updated with real data');
}}

// Update Last 6 Months Activity chart (left side)  
function updateTrackingGraphWithRealData() {{
    const graph = document.getElementById('tracking-graph');
    if (!graph) {{
        console.log('❌ Tracking graph not found');
        return;
    }}
    
    console.log('🔄 Updating tracking graph...');
    
    const months = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
    const data = months.map(m => realMonthlyData[m] || 0);
    const maxVal = Math.max(...data, 1);
    
    let html = '<div style="position: relative; height: 35px; padding: 5px;">';
    
    // Create SVG line chart
    html += '<svg style="position: absolute; width: 100%; height: 100%; z-index: 1;">';
    
    let pathData = '';
    data.forEach((val, i) => {{
        const x = 10 + (i * 35);
        const y = 25 - (val / maxVal * 15);
        pathData += (i === 0 ? `M${{x}},${{y}}` : ` L${{x}},${{y}}`);
        
        // Add data points and labels
        html += `
        <circle cx="${{x}}" cy="${{y}}" r="2" fill="#3b82f6" stroke="white" stroke-width="1"/>
        <text x="${{x}}" y="${{y-5}}" text-anchor="middle" style="font-size: 8px; fill: #3b82f6; font-weight: 600;">${{val}} runs</text>
        <text x="${{x}}" y="32" text-anchor="middle" style="font-size: 8px; fill: #374151; font-weight: 600;">${{months[i]}}</text>
        `;
    }});
    
    // Add line path
    html += `<path d="${{pathData}}" stroke="#3b82f6" stroke-width="2" fill="none" stroke-linecap="round"/>`;
    html += '</svg></div>';
    
    graph.innerHTML = html;
    console.log('✅ Tracking graph updated with real data');
}}

// Apply both fixes
try {{
    updateCustomerChartWithRealData();
    updateTrackingGraphWithRealData();
    
    console.log('🎉 SUCCESS: Both graphs updated with real database data!');
    console.log('📊 If you see this message, the graphs should now show correct data');
    
    // Show success notification if available
    if (window.showNotification) {{
        window.showNotification('✅ Graphs updated with real database data!', 'success');
    }}
    
}} catch (error) {{
    console.error('❌ Error updating graphs:', error);
}}
"""
        
        # Save JavaScript fix
        with open('C:\\Users\\surchopr\\Hc_Final\\FINAL_graph_fix.js', 'w', encoding='utf-8') as f:
            f.write(js_fix)
        
        print(f"\\n✅ FINAL JAVASCRIPT FIX READY!")
        print("=" * 40)
        print("📁 File saved: FINAL_graph_fix.js")
        print("📋 Copy the content and paste in browser console")
        print("🎯 This will update graphs with REAL database data")
        
        conn.close()
        return customer_counts, monthly_counts
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}, {}

if __name__ == "__main__":
    get_real_session_data()