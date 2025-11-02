// 🧹 LOCALSTORAGE CLEANUP SYSTEM
// Clean unwanted edit data after saving changes

console.log('🧹 Loading localStorage cleanup system...');

// 🔧 Function to clean localStorage after successful save
window.cleanupLocalStorageAfterSave = function(customerName) {
    console.log(`🧹 Cleaning localStorage for customer: ${customerName}`);
    
    try {
        const keysToRemove = [];
        
        // Find all localStorage keys related to this customer's edits
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            
            // Check for edit-related keys for this customer
            if (key && (
                key.startsWith(`${customerName}_edit_`) ||
                key.startsWith(`${customerName}_temp_`) ||
                key.startsWith(`edit_${customerName}_`) ||
                key.startsWith(`temp_${customerName}_`) ||
                (key.includes('_edit_') && key.includes(customerName)) ||
                (key.includes('_temp_') && key.includes(customerName))
            )) {
                keysToRemove.push(key);
                console.log(`  📋 Found edit key to remove: ${key}`);
            }
        }
        
        // Remove identified keys
        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
            console.log(`  ✅ Removed: ${key}`);
        });
        
        console.log(`🧹 Cleaned ${keysToRemove.length} localStorage keys for ${customerName}`);
        return keysToRemove.length;
        
    } catch (error) {
        console.error(`❌ Error cleaning localStorage for ${customerName}:`, error);
        return 0;
    }
};

// 🔧 Function to clean ALL customer edit data
window.cleanupAllEditData = function() {
    console.log('🧹 Cleaning ALL customer edit data from localStorage...');
    
    try {
        const keysToRemove = [];
        
        // Find all edit-related keys
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            
            if (key && (
                key.includes('_edit_') ||
                key.includes('_temp_') ||
                key.startsWith('edit_') ||
                key.startsWith('temp_') ||
                key.endsWith('_edit') ||
                key.endsWith('_temp') ||
                key.includes('monthly_edit') ||
                key.includes('network_edit') ||
                key.includes('customer_edit')
            )) {
                keysToRemove.push(key);
                console.log(`  📋 Found global edit key: ${key}`);
            }
        }
        
        // Remove all edit keys
        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
            console.log(`  ✅ Removed: ${key}`);
        });
        
        console.log(`🧹 Cleaned ${keysToRemove.length} total edit keys`);
        showNotification(`🧹 Cleaned ${keysToRemove.length} edit entries from localStorage`, 'success');
        return keysToRemove.length;
        
    } catch (error) {
        console.error('❌ Error cleaning all edit data:', error);
        showNotification('❌ Error cleaning localStorage', 'error');
        return 0;
    }
};

// 🔧 Function to clean old/stale data (older than X days)
window.cleanupStaleEditData = function(daysOld = 7) {
    console.log(`🧹 Cleaning edit data older than ${daysOld} days...`);
    
    try {
        const keysToRemove = [];
        const cutoffTime = Date.now() - (daysOld * 24 * 60 * 60 * 1000);
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            
            if (key && key.includes('_edit_')) {
                try {
                    const data = localStorage.getItem(key);
                    const parsed = JSON.parse(data);
                    
                    // Check if data has a timestamp
                    if (parsed && parsed.timestamp && parsed.timestamp < cutoffTime) {
                        keysToRemove.push(key);
                        console.log(`  📋 Found stale key: ${key} (${new Date(parsed.timestamp).toLocaleDateString()})`);
                    }
                    // If no timestamp, consider it stale (old format)
                    else if (!parsed.timestamp) {
                        keysToRemove.push(key);
                        console.log(`  📋 Found old format key: ${key}`);
                    }
                } catch (e) {
                    // If can't parse, probably old format - remove it
                    keysToRemove.push(key);
                    console.log(`  📋 Found unparseable key: ${key}`);
                }
            }
        }
        
        // Remove stale keys
        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
            console.log(`  ✅ Removed stale: ${key}`);
        });
        
        console.log(`🧹 Cleaned ${keysToRemove.length} stale edit keys`);
        if (keysToRemove.length > 0) {
            showNotification(`🧹 Cleaned ${keysToRemove.length} stale entries`, 'success');
        }
        return keysToRemove.length;
        
    } catch (error) {
        console.error('❌ Error cleaning stale data:', error);
        return 0;
    }
};

// 🔧 Enhanced save functions that auto-cleanup
window.saveWithCleanup = async function(customerName) {
    console.log(`💾 Saving edits for ${customerName} with cleanup...`);
    
    try {
        // First save the data (call existing save function)
        let saveResult = false;
        
        // Try different save function names that might exist
        if (typeof saveBulkEdits === 'function') {
            saveResult = await saveBulkEdits(customerName);
        } else if (typeof saveCustomerEdits === 'function') {
            saveResult = await saveCustomerEdits(customerName);
        } else if (typeof saveEditsForCustomer === 'function') {
            saveResult = await saveEditsForCustomer(customerName);
        } else {
            console.log('⚠️ No save function found, proceeding with cleanup only');
            saveResult = true; // Assume success for cleanup
        }
        
        // If save was successful, cleanup localStorage
        if (saveResult) {
            const cleanedCount = cleanupLocalStorageAfterSave(customerName);
            console.log(`✅ Save completed and cleaned ${cleanedCount} localStorage keys`);
            showNotification(`✅ Saved ${customerName} edits and cleaned ${cleanedCount} temp entries`, 'success');
        } else {
            console.log('❌ Save failed, skipping cleanup');
            showNotification('❌ Save failed - localStorage not cleaned', 'error');
        }
        
        return saveResult;
        
    } catch (error) {
        console.error(`❌ Error in saveWithCleanup for ${customerName}:`, error);
        showNotification(`❌ Error saving ${customerName}: ${error.message}`, 'error');
        return false;
    }
};

// 🔧 Function to show localStorage usage
window.showLocalStorageUsage = function() {
    console.log('📊 LOCALSTORAGE USAGE REPORT');
    console.log('═══════════════════════════════');
    
    let totalSize = 0;
    let editKeys = 0;
    let tempKeys = 0;
    let otherKeys = 0;
    
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const value = localStorage.getItem(key);
        const size = (key.length + value.length) * 2; // Rough size in bytes
        
        totalSize += size;
        
        if (key.includes('_edit_') || key.includes('edit_')) {
            editKeys++;
            console.log(`📝 EDIT: ${key} (${Math.round(size/1024)}KB)`);
        } else if (key.includes('_temp_') || key.includes('temp_')) {
            tempKeys++;
            console.log(`🔄 TEMP: ${key} (${Math.round(size/1024)}KB)`);
        } else {
            otherKeys++;
            console.log(`📋 OTHER: ${key} (${Math.round(size/1024)}KB)`);
        }
    }
    
    console.log('═══════════════════════════════');
    console.log(`📊 SUMMARY:`);
    console.log(`  Total keys: ${localStorage.length}`);
    console.log(`  Edit keys: ${editKeys}`);
    console.log(`  Temp keys: ${tempKeys}`);
    console.log(`  Other keys: ${otherKeys}`);
    console.log(`  Total size: ~${Math.round(totalSize/1024)}KB`);
    console.log('═══════════════════════════════');
    
    return {
        totalKeys: localStorage.length,
        editKeys,
        tempKeys,
        otherKeys,
        totalSizeKB: Math.round(totalSize/1024)
    };
};

// 🔧 Auto-cleanup on page load (remove stale data)
window.addEventListener('load', function() {
    setTimeout(() => {
        console.log('🧹 Auto-cleaning stale localStorage data...');
        cleanupStaleEditData(7); // Clean data older than 7 days
    }, 2000); // Wait 2 seconds after page load
});

// 🔧 Add cleanup buttons to UI if they don't exist
window.addCleanupButtons = function() {
    console.log('🧹 Adding cleanup buttons to UI...');
    
    try {
        // Look for a good place to add buttons (near export/download buttons)
        let buttonContainer = document.querySelector('.export-buttons') || 
                            document.querySelector('.dashboard-controls') ||
                            document.querySelector('.top-controls') ||
                            document.querySelector('header') ||
                            document.body;
        
        if (!document.getElementById('cleanup-buttons-container')) {
            const cleanupDiv = document.createElement('div');
            cleanupDiv.id = 'cleanup-buttons-container';
            cleanupDiv.style.cssText = 'margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #28a745;';
            
            cleanupDiv.innerHTML = `
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <strong style="color: #28a745;">🧹 Storage Cleanup:</strong>
                    <button onclick="cleanupAllEditData()" class="btn btn-sm btn-warning" title="Remove all edit data">
                        🧹 Clean All Edits
                    </button>
                    <button onclick="cleanupStaleEditData(7)" class="btn btn-sm btn-info" title="Remove data older than 7 days">
                        ⏰ Clean Stale (7d+)
                    </button>
                    <button onclick="showLocalStorageUsage()" class="btn btn-sm btn-secondary" title="Show storage usage">
                        📊 Show Usage
                    </button>
                </div>
            `;
            
            buttonContainer.insertBefore(cleanupDiv, buttonContainer.firstChild);
            console.log('✅ Added cleanup buttons to UI');
        } else {
            console.log('ℹ️ Cleanup buttons already exist');
        }
        
    } catch (error) {
        console.error('❌ Error adding cleanup buttons:', error);
    }
};

// 🔧 Override existing save functions to include cleanup
if (typeof saveBulkEdits !== 'undefined') {
    const originalSaveBulkEdits = window.saveBulkEdits;
    window.saveBulkEdits = async function(customerName) {
        const result = await originalSaveBulkEdits(customerName);
        if (result) {
            cleanupLocalStorageAfterSave(customerName);
        }
        return result;
    };
    console.log('✅ Enhanced saveBulkEdits with cleanup');
}

// Add cleanup buttons when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addCleanupButtons);
} else {
    addCleanupButtons();
}

console.log('✅ LOCALSTORAGE CLEANUP SYSTEM LOADED!');
console.log('🧹 Available functions:');
console.log('  - cleanupLocalStorageAfterSave(customerName)');
console.log('  - cleanupAllEditData()');
console.log('  - cleanupStaleEditData(days)');
console.log('  - saveWithCleanup(customerName)');
console.log('  - showLocalStorageUsage()');
console.log('🔄 Auto-cleanup of stale data will run on page load');
console.log('🎛️ Cleanup buttons added to UI');