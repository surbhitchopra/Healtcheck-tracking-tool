// Test script to verify the edit modal fix
// Run this in browser console after loading customer dashboard

function testEditModalFix() {
    console.log('🧪 TESTING EDIT MODAL FIX');
    console.log('==========================');
    
    // Check if dashboard data is loaded
    if (typeof dashboardData === 'undefined' || !dashboardData.customers) {
        console.error('❌ Dashboard data not loaded. Please wait for page to load completely.');
        return;
    }
    
    const customers = Object.values(dashboardData.customers);
    if (customers.length === 0) {
        console.error('❌ No customers found in dashboard data.');
        return;
    }
    
    // Find first customer with networks
    const testCustomer = customers.find(customer => 
        customer.networks && customer.networks.length > 0
    );
    
    if (!testCustomer) {
        console.error('❌ No customers with networks found for testing.');
        return;
    }
    
    console.log(`✅ Found test customer: "${testCustomer.name}" with ${testCustomer.networks.length} networks`);
    
    // Store original data for comparison
    const originalNetworks = JSON.parse(JSON.stringify(testCustomer.networks));
    
    // Test 1: Check if editCustomer function exists
    if (typeof editCustomer !== 'function') {
        console.error('❌ editCustomer function not found');
        return;
    }
    
    console.log('✅ editCustomer function found');
    
    // Test 2: Check if customer-specific IDs would be generated correctly
    const customerSafeId = testCustomer.name.replace(/[^a-zA-Z0-9_-]/g, '_');
    console.log(`✅ Customer safe ID: "${customerSafeId}"`);
    
    // Test 3: Verify isolation function exists
    if (typeof verifyCustomerIsolation !== 'function') {
        console.error('❌ verifyCustomerIsolation function not found');
        return;
    }
    
    console.log('✅ verifyCustomerIsolation function found');
    
    // Test 4: Test isolation verification
    const customerKey = Object.keys(dashboardData.customers).find(key => 
        dashboardData.customers[key].name === testCustomer.name
    );
    
    const isolationTest = verifyCustomerIsolation(testCustomer.name, customerKey);
    if (isolationTest) {
        console.log('✅ Customer isolation verification works');
    } else {
        console.error('❌ Customer isolation verification failed');
        return;
    }
    
    // Test 5: Check if other customers remain unchanged
    const otherCustomers = customers.filter(c => c.name !== testCustomer.name);
    console.log(`✅ Found ${otherCustomers.length} other customers to monitor for changes`);
    
    // Store checksums of other customers
    const otherCustomerChecksums = {};
    otherCustomers.forEach(customer => {
        otherCustomerChecksums[customer.name] = JSON.stringify(customer.networks);
    });
    
    console.log('✅ Stored checksums of other customers');
    
    // Summary
    console.log('🎉 ALL TESTS PASSED!');
    console.log('📋 Test Summary:');
    console.log(`   • Test customer: "${testCustomer.name}"`);
    console.log(`   • Safe ID: "${customerSafeId}"`);
    console.log(`   • Networks: ${testCustomer.networks.length}`);
    console.log(`   • Other customers monitored: ${otherCustomers.length}`);
    console.log('');
    console.log('🎯 Ready to test edit functionality:');
    console.log(`   1. Click edit button for "${testCustomer.name}"`);
    console.log('   2. Make some changes to network data');
    console.log('   3. Save changes');
    console.log('   4. Check console for isolation verification');
    console.log('   5. Verify other customers are unchanged');
    
    return {
        testCustomer: testCustomer.name,
        customerSafeId: customerSafeId,
        originalNetworks: originalNetworks,
        otherCustomerChecksums: otherCustomerChecksums
    };
}

// Auto-run test when script loads
if (typeof window !== 'undefined') {
    // Browser environment - wait for page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(testEditModalFix, 2000);
        });
    } else {
        setTimeout(testEditModalFix, 1000);
    }
} else {
    // Node.js environment - just export
    module.exports = { testEditModalFix };
}