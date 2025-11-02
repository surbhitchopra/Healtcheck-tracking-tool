#!/usr/bin/env python3
"""
COMPLETE NETWORK DATES DEBUG SCRIPT
This script will check everything from database to frontend
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
sys.path.append('C:\\Users\\surchopr\\Hc_Final')

try:
    django.setup()
    from HealthCheck_app.models import Customer
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def debug_database_customers():
    """Debug database customers and their monthly_runs data"""
    print("\n🔍 DEBUGGING DATABASE CUSTOMERS...")
    
    customers = Customer.objects.filter(is_deleted=False)
    print(f"📊 Found {customers.count()} customers in database")
    
    # Group by customer name
    customer_groups = {}
    for customer in customers:
        if customer.name not in customer_groups:
            customer_groups[customer.name] = []
        customer_groups[customer.name].append(customer)
    
    for customer_name, customer_list in customer_groups.items():
        print(f"\n👤 Customer: {customer_name}")
        print(f"   Networks: {len(customer_list)}")
        
        for i, customer in enumerate(customer_list):
            print(f"   🔗 Network {i+1}: {customer.network_name}")
            print(f"      ID: {customer.id}")
            print(f"      Total runs: {customer.total_runs}")
            print(f"      Node qty: {customer.node_qty}")
            print(f"      Country: {customer.country}")
            print(f"      Monthly runs: {customer.monthly_runs}")
            
            if customer.monthly_runs:
                print(f"      Monthly runs breakdown:")
                for month_key, date_value in customer.monthly_runs.items():
                    print(f"         {month_key}: {date_value}")

def debug_api_response():
    """Debug what the API returns"""
    print("\n🔍 DEBUGGING API RESPONSE...")
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/api/customer-dashboard/customers/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful")
            print(f"📊 Total customers in API: {len(data.get('customers', {}))}")
            
            # Check a few customers
            customers = data.get('customers', {})
            for i, (key, customer) in enumerate(customers.items()):
                if i >= 3:  # Only show first 3
                    break
                    
                print(f"\n🔍 API Customer {i+1}: {customer.get('name')}")
                print(f"   Networks count: {customer.get('networks_count', 0)}")
                print(f"   Networks array length: {len(customer.get('networks', []))}")
                
                if customer.get('networks'):
                    for j, network in enumerate(customer['networks']):
                        print(f"   🔗 Network {j+1}: {network.get('name', network.get('network_name'))}")
                        print(f"      months: {network.get('months', [])[:6]}...")  # Show first 6 months
                        print(f"      monthly_runs keys: {list(network.get('monthly_runs', {}).keys())}")
        else:
            print(f"❌ API Response failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ API request failed: {e}")
    except Exception as e:
        print(f"❌ API debug failed: {e}")

def check_template_file():
    """Check template file for network date rendering logic"""
    print("\n🔍 CHECKING TEMPLATE FILE...")
    
    template_path = 'C:\\Users\\surchopr\\Hc_Final\\templates\\customer_dashboard.html'
    if os.path.exists(template_path):
        print("✅ Template file exists")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key functions
        functions_to_check = [
            'getNetworkMonthRunDates',
            'createNetworkDetailRow',
            'fixNetworkDatesDisplay'
        ]
        
        for func in functions_to_check:
            if func in content:
                print(f"✅ Found function: {func}")
            else:
                print(f"❌ Missing function: {func}")
                
        # Check for auto-fix script
        if 'fixNetworkDatesDisplay' in content and 'window.addEventListener(\'load\'' in content:
            print("✅ Auto-fix script is present")
        else:
            print("❌ Auto-fix script missing or incomplete")
    else:
        print("❌ Template file not found")

def generate_frontend_fix():
    """Generate a simple frontend fix script"""
    print("\n🔧 GENERATING FRONTEND FIX SCRIPT...")
    
    fix_script = """
// NETWORK DATES FIX - Paste this in browser console
console.log('🔥 NETWORK DATES FIX STARTING...');

setTimeout(() => {
    const networkRows = document.querySelectorAll('tr.network-detail-row');
    console.log(`Found ${networkRows.length} network rows`);
    
    let fixedCount = 0;
    
    networkRows.forEach(row => {
        const nameEl = row.querySelector('.network-name-main');
        if (!nameEl) return;
        
        const networkName = nameEl.textContent.replace('└─ ', '').trim();
        console.log(`Processing: ${networkName}`);
        
        // Find customer row
        let customerRow = row.previousElementSibling;
        while (customerRow && !customerRow.classList.contains('customer-summary-row')) {
            customerRow = customerRow.previousElementSibling;
        }
        
        if (!customerRow) return;
        
        const custNameEl = customerRow.querySelector('.customer-name-main');
        if (!custNameEl) return;
        
        const customerName = custNameEl.textContent.replace(/[📋📄💾🔄]/g, '').trim().split('\\n')[0];
        
        // Find customer data
        if (window.dashboardData?.customers) {
            const customers = Object.values(window.dashboardData.customers);
            const customerData = customers.find(c => 
                c.name?.toLowerCase().includes(customerName.toLowerCase())
            );
            
            if (customerData?.networks) {
                const networkData = customerData.networks.find(net => {
                    const netName = (net.name || net.network_name || '').toLowerCase();
                    const searchName = networkName.toLowerCase();
                    return netName.includes(searchName) || searchName.includes(netName);
                });
                
                if (networkData) {
                    console.log(`Found data for ${networkName}:`, {
                        months: networkData.months,
                        monthly_runs: networkData.monthly_runs
                    });
                    
                    // Update cells
                    const cells = Array.from(row.querySelectorAll('td')).slice(6, 18);
                    cells.forEach((cell, i) => {
                        let date = networkData.months?.[i];
                        
                        if (!date || date === '-') {
                            // Try monthly_runs
                            const key2025 = `2025-${(i+1).toString().padStart(2,'0')}`;
                            const key2024 = `2024-${(i+1).toString().padStart(2,'0')}`;
                            date = networkData.monthly_runs?.[key2025] || networkData.monthly_runs?.[key2024];
                            
                            // Format date
                            if (date && date.includes('-') && date.length > 8) {
                                try {
                                    const d = new Date(date);
                                    date = `${d.getDate()}-${d.toLocaleDateString('en-US', {month: 'short'})}`;
                                } catch (e) {}
                            }
                        }
                        
                        if (date && date !== '-') {
                            cell.textContent = date;
                            cell.style.color = '#374151';
                            cell.style.fontWeight = '500';
                            fixedCount++;
                        }
                    });
                }
            }
        }
    });
    
    console.log(`✅ Fixed ${fixedCount} network date cells`);
}, 2000);
"""
    
    with open('C:\\Users\\surchopr\\Hc_Final\\browser_fix.js', 'w') as f:
        f.write(fix_script)
    
    print("✅ Created browser_fix.js")
    print("📋 Copy the content of browser_fix.js and paste in browser console")

def main():
    print("🚀 COMPLETE NETWORK DATES DIAGNOSTIC")
    print("="*50)
    
    # Step 1: Check database
    debug_database_customers()
    
    # Step 2: Check API (if server is running)
    debug_api_response()
    
    # Step 3: Check template
    check_template_file()
    
    # Step 4: Generate fix
    generate_frontend_fix()
    
    print("\n🎯 SUMMARY:")
    print("1. Check database customers above")
    print("2. Check API response above")
    print("3. Check template functions above")
    print("4. Use browser_fix.js in browser console")

if __name__ == "__main__":
    main()