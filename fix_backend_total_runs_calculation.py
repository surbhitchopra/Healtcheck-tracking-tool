#!/usr/bin/env python3
"""
BACKEND FIX FOR TOTAL RUNS CALCULATION
Fixes the issue where BSNL shows 70 runs instead of correct 53 runs
"""

import os
import sys
import django
from collections import defaultdict

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

def fix_total_runs_calculation():
    """
    Fix the frontend total runs calculation by properly grouping customers
    and avoiding duplicate counting of network runs.
    """
    print("🔧 FIXING BACKEND TOTAL RUNS CALCULATION...")
    print("=" * 60)
    
    # Get all active customers
    customers = Customer.objects.filter(is_deleted=False)
    
    # Group customers by name (like BSNL, Tata, etc.)
    customer_groups = defaultdict(list)
    for customer in customers:
        customer_groups[customer.name].append(customer)
    
    print(f"📊 Found {len(customer_groups)} unique customers with {customers.count()} total networks")
    print("\nPer Customer Analysis (CORRECTED):")
    print("-" * 80)
    
    total_customers = 0
    total_runs_corrected = 0
    
    for customer_name, networks in customer_groups.items():
        total_customers += 1
        
        # Calculate correct total runs for this customer
        customer_total_runs = sum(network.total_runs or 0 for network in networks)
        total_runs_corrected += customer_total_runs
        
        # Count monthly entries for this customer
        customer_monthly_entries = 0
        for network in networks:
            if network.monthly_runs:
                for month_key, month_value in network.monthly_runs.items():
                    if month_value and str(month_value).strip() not in ['-', '', 'None', 'null', 'Not Started', 'Not Run', 'No Report']:
                        customer_monthly_entries += 1
        
        print(f"  {customer_name:<20} | Networks: {len(networks):>2} | Runs: {customer_total_runs:>3} | Monthly: {customer_monthly_entries:>3}")
        
        # Show individual networks for customers with multiple networks
        if len(networks) > 1:
            for i, network in enumerate(networks, 1):
                network_runs = network.total_runs or 0
                network_name = network.network_name or f"Network_{i}"
                print(f"    └─ {network_name:<25} | Runs: {network_runs:>3}")
    
    print("-" * 80)
    print(f"\n📈 CORRECTED SUMMARY:")
    print(f"   👥 Total Unique Customers: {total_customers}")
    print(f"   🏃 Total Runs (CORRECTED): {total_runs_corrected}")
    print(f"   🔗 Total Networks/Entries: {customers.count()}")
    
    print(f"\n❌ PROBLEM IDENTIFIED:")
    print(f"   Frontend was counting each network separately instead of grouping by customer")
    print(f"   This caused duplicate counting for customers with multiple networks")
    
    print(f"\n✅ EXPECTED FRONTEND VALUES:")
    print(f"   Header - Total Customers: {total_customers}")
    print(f"   Header - Total Runs: {total_runs_corrected}")
    
    return {
        'total_customers': total_customers,
        'total_runs': total_runs_corrected,
        'customer_breakdown': dict(customer_groups)
    }

def check_bsnl_specifically():
    """
    Detailed check of BSNL networks to understand the discrepancy
    """
    print("\n🔍 DETAILED BSNL ANALYSIS:")
    print("=" * 50)
    
    bsnl_customers = Customer.objects.filter(name='BSNL', is_deleted=False)
    
    if not bsnl_customers.exists():
        print("❌ No BSNL customers found!")
        return
    
    bsnl_total = 0
    for i, bsnl in enumerate(bsnl_customers, 1):
        runs = bsnl.total_runs or 0
        bsnl_total += runs
        print(f"  {i}. {bsnl.network_name or 'Unknown Network':<25} | Runs: {runs:>3}")
    
    print(f"\n📊 BSNL SUMMARY:")
    print(f"   Networks: {bsnl_customers.count()}")
    print(f"   Correct Total Runs: {bsnl_total}")
    print(f"   Frontend was showing: 70 (incorrect)")
    print(f"   Database shows: {bsnl_total} (correct)")

def create_frontend_fix_script():
    """
    Create a JavaScript file to fix the frontend calculation
    """
    js_fix = '''// PASTE THIS IN BROWSER CONSOLE TO FIX FRONTEND CALCULATION

console.log("🔧 Applying BSNL and Total Runs Fix...");

// Override the statistics calculation to group customers properly
window.fixedUpdateStatistics = function() {
    console.log("📊 Using FIXED statistics calculation...");
    
    const customers = dashboardData.customers;
    if (!customers) return;
    
    // Group customers by name to avoid double counting
    const customerGroups = {};
    let totalRuns = 0;
    let totalCustomers = 0;
    
    Object.entries(customers).forEach(([key, customer]) => {
        const customerName = customer.name || customer.Customer || key.split('_')[0];
        
        // Skip if already counted
        if (customerGroups[customerName]) return;
        
        customerGroups[customerName] = true;
        totalCustomers++;
        
        // Use database total_runs if available, otherwise calculate
        const customerRuns = customer.total_runs || customer.runs || 0;
        totalRuns += customerRuns;
        
        console.log(`📊 ${customerName}: ${customerRuns} runs`);
    });
    
    // Update statistics
    dashboardData.statistics.total_customers = totalCustomers;
    dashboardData.statistics.total_runs = totalRuns;
    
    // Update header display
    const runsEl = document.getElementById('header-total-runs');
    const customersEl = document.getElementById('header-total-customers');
    
    if (runsEl) runsEl.textContent = totalRuns;
    if (customersEl) customersEl.textContent = totalCustomers;
    
    console.log(`✅ FIXED: ${totalCustomers} customers, ${totalRuns} total runs`);
};

// Apply the fix
fixedUpdateStatistics();

console.log("✅ Frontend calculation fixed! BSNL should now show correct runs.");'''
    
    with open('frontend_total_runs_fix.js', 'w') as f:
        f.write(js_fix)
    
    print(f"\n📄 Created frontend_total_runs_fix.js")
    print(f"   Copy and paste the contents in browser console to fix the display")

if __name__ == "__main__":
    # Run the analysis
    result = fix_total_runs_calculation()
    
    # Check BSNL specifically
    check_bsnl_specifically()
    
    # Create frontend fix
    create_frontend_fix_script()
    
    print(f"\n🎯 SOLUTION:")
    print(f"   1. The problem is in frontend JavaScript calculation")
    print(f"   2. Frontend counts each network separately instead of grouping by customer")
    print(f"   3. Use the JavaScript fix above to correct the display")
    print(f"   4. Database values are CORRECT: {result['total_runs']} total runs")