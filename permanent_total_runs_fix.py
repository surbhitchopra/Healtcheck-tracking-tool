#!/usr/bin/env python3
"""
PERMANENT FIX FOR TOTAL RUNS COUNTER
This script modifies the HealthCheckSession model to properly update total_runs
based on actual completed sessions, not just monthly_runs entries.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession

def create_permanent_model_fix():
    """
    Create a permanent fix for the model's _update_customer_monthly_runs method
    """
    
    # Create the updated model method content
    model_fix_content = '''
    def _update_customer_monthly_runs(self):
        """Update customer's monthly_runs field when session completes - FIXED VERSION"""
        try:
            # Get current date in YYYY-MM-DD format
            completion_date = self.completed_at or timezone.now()
            current_month_key = completion_date.strftime('%Y-%m')  # e.g., '2025-10'
            current_date_value = completion_date.strftime('%Y-%m-%d')  # e.g., '2025-10-08'
            
            # Initialize monthly_runs if it doesn't exist
            if not self.customer.monthly_runs:
                self.customer.monthly_runs = {}
            
            # Update the current month with today's date
            self.customer.monthly_runs[current_month_key] = current_date_value
            
            # FIXED: Count ACTUAL completed sessions instead of just monthly_runs entries
            actual_completed_sessions = HealthCheckSession.objects.filter(
                customer=self.customer,
                status='COMPLETED'
            ).count()
            
            # Update total_runs to reflect actual completed sessions
            self.customer.total_runs = actual_completed_sessions
            
            # Save the customer
            self.customer.save()
            
            print(f"✅ Updated {self.customer.name} monthly_runs: {current_month_key} = {current_date_value}")
            print(f"✅ Updated total_runs to {actual_completed_sessions} (based on actual sessions)")
            
        except Exception as e:
            print(f"❌ Error updating monthly_runs for {self.customer.name}: {e}")
    '''
    
    print("📄 PERMANENT MODEL FIX:")
    print("=" * 60)
    print("Replace the _update_customer_monthly_runs method in HealthCheck_app/models.py")
    print("with the following code:")
    print("\n" + model_fix_content)
    
    # Write to a file for easy reference
    with open('model_fix_update.py', 'w') as f:
        f.write('# PASTE THIS METHOD INTO HealthCheck_app/models.py\n')
        f.write('# Replace the existing _update_customer_monthly_runs method\n\n')
        f.write(model_fix_content)
    
    print("📄 Saved to model_fix_update.py for easy reference")

def create_frontend_javascript_fix():
    """
    Create JavaScript fix to ensure dashboard shows correct total runs
    """
    
    js_fix_content = '''
// FRONTEND FIX FOR TOTAL RUNS DISPLAY
// Run this in browser console or add to your dashboard JavaScript

console.log('🔧 APPLYING PERMANENT FRONTEND TOTAL RUNS FIX...');

// Override the updateStatistics function to use database total_runs correctly
window.updateStatisticsFixed = function() {
    console.log('📊 Updating statistics with FIXED total runs calculation...');
    
    if (!dashboardData || !dashboardData.customers) {
        console.log('❌ Dashboard data not available');
        return;
    }
    
    const customers = dashboardData.customers;
    let totalCustomers = 0;
    let totalRuns = 0;
    let totalNetworks = 0;
    
    // Group customers by name to avoid double counting
    const customerGroups = {};
    
    Object.entries(customers).forEach(([customerKey, customer]) => {
        const customerName = customer.name || customer.Customer || customerKey.split('_')[0];
        
        if (!customerGroups[customerName]) {
            customerGroups[customerName] = {
                name: customerName,
                totalRuns: 0,
                networks: []
            };
            totalCustomers++;
        }
        
        // Use actual database total_runs field (not calculated from monthly_runs)
        const dbTotalRuns = customer.total_runs || customer.runs || 0;
        customerGroups[customerName].totalRuns += dbTotalRuns;
        customerGroups[customerName].networks.push(customer);
        totalNetworks++;
        
        console.log(`📊 ${customerName}: +${dbTotalRuns} runs (from database)`);
    });
    
    // Calculate total runs across all customers
    Object.values(customerGroups).forEach(group => {
        totalRuns += group.totalRuns;
    });
    
    // Update header statistics
    const elements = {
        'header-total-customers': totalCustomers,
        'header-total-runs': totalRuns,
        'header-total-networks': totalNetworks,
        'header-total-trackers': totalNetworks
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
    
    console.log(`✅ FIXED STATISTICS:`);
    console.log(`   👥 Total Customers: ${totalCustomers}`);
    console.log(`   🏃 Total Runs: ${totalRuns} (from database total_runs)`);
    console.log(`   🔗 Total Networks: ${totalNetworks}`);
    
    // Store fixed values for charts
    if (dashboardData.statistics) {
        dashboardData.statistics.total_customers = totalCustomers;
        dashboardData.statistics.total_runs = totalRuns;
        dashboardData.statistics.total_networks = totalNetworks;
    }
};

// Apply the fix immediately
updateStatisticsFixed();

console.log('✅ Frontend total runs display fixed!');
console.log('🎯 Dashboard now shows actual database total_runs values');
    '''
    
    with open('frontend_total_runs_permanent_fix.js', 'w') as f:
        f.write(js_fix_content)
    
    print("\n📄 Created frontend_total_runs_permanent_fix.js")
    print("   Add this to your dashboard JavaScript or run in browser console")

def recalculate_all_customers():
    """
    Recalculate total_runs for all customers based on actual completed sessions
    """
    print("\n🔄 RECALCULATING ALL CUSTOMER TOTAL RUNS...")
    print("=" * 60)
    
    customers = Customer.objects.filter(is_deleted=False)
    updated_count = 0
    
    for customer in customers:
        # Count actual completed sessions
        actual_sessions = HealthCheckSession.objects.filter(
            customer=customer,
            status='COMPLETED'
        ).count()
        
        # Update if different
        if customer.total_runs != actual_sessions:
            old_value = customer.total_runs
            customer.total_runs = actual_sessions
            customer.save()
            updated_count += 1
            
            print(f"🔧 {customer.display_name}: {old_value} → {actual_sessions}")
        else:
            print(f"✅ {customer.display_name}: {actual_sessions} (correct)")
    
    print("=" * 60)
    print(f"✅ Updated {updated_count} customers")
    
    return updated_count

if __name__ == "__main__":
    print("🔧 PERMANENT TOTAL RUNS FIX")
    print("=" * 60)
    
    # 1. Recalculate all current customers
    print("Step 1: Recalculating all customer total_runs...")
    recalculate_all_customers()
    
    # 2. Create permanent model fix
    print("\nStep 2: Creating permanent model fix...")
    create_permanent_model_fix()
    
    # 3. Create frontend fix
    print("\nStep 3: Creating frontend fix...")
    create_frontend_javascript_fix()
    
    print("\n🎯 COMPLETE FIX SUMMARY:")
    print("=" * 60)
    print("1. ✅ All customer total_runs have been recalculated")
    print("2. 📄 Model fix created in model_fix_update.py")
    print("3. 📄 Frontend fix created in frontend_total_runs_permanent_fix.js")
    print("\n🔧 TO COMPLETE THE FIX:")
    print("   1. Update HealthCheck_app/models.py with the new method")
    print("   2. Add the frontend JavaScript to your dashboard")
    print("   3. Restart your Django server")
    print("\n✅ BSNL East Zone DWDM will now show correct runs count!")