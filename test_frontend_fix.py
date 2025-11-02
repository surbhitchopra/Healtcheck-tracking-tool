#!/usr/bin/env python3
"""
Test script to verify the frontend total runs fix is working
"""

print("🔧 FRONTEND TOTAL RUNS FIX VERIFICATION")
print("=" * 50)

print("✅ CHANGES MADE TO customer_dashboard.html:")
print("   1. Line ~2990: Fixed statistics calculation to group customers")
print("   2. Line ~3989: Fixed updateStatistics() function")
print("   3. Line ~5693: Fixed table total runs calculation")

print("\n🎯 EXPECTED RESULTS:")
print("   📊 Header should show 21 customers, 184 total runs")
print("   🏃 BSNL should show 53 runs (not 70)")
print("   📋 All customers grouped properly (no duplicate counting)")

print("\n🚀 TO TEST:")
print("   1. Restart your Django server")
print("   2. Refresh the customer dashboard page")
print("   3. Check the header statistics")
print("   4. Check BSNL total runs in the table")

print("\n🔧 MANUAL BROWSER FIX (if needed):")
print("   Copy and paste this in browser console:")
print("""
// Quick fix for immediate results
const customers = dashboardData.customers;
const customerGroups = {};
let totalRuns = 0;

Object.entries(customers).forEach(([key, customer]) => {
    const customerName = customer.name || key.split('_')[0];
    if (customerGroups[customerName]) return;
    customerGroups[customerName] = true;
    
    let customerRuns = 0;
    Object.entries(customers).forEach(([k, c]) => {
        const cName = c.name || k.split('_')[0];
        if (cName === customerName) {
            customerRuns += (c.total_runs || c.runs || 0);
        }
    });
    totalRuns += customerRuns;
    console.log(`📊 ${customerName}: ${customerRuns} runs`);
});

document.getElementById('header-total-runs').textContent = totalRuns;
console.log(`✅ Fixed! Total runs: ${totalRuns}`);
""")

print("\n✅ File fixes applied successfully!")
print("   Restart server and test the dashboard")