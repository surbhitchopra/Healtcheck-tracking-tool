// ADD ICONS TO CUSTOMER DASHBOARD EDIT BUTTONS - Run this in console

console.log('🎨 FIXING CUSTOMER DASHBOARD EDIT BUTTONS...');

// Function to enhance dashboard edit buttons
function enhanceDashboardEditButtons() {
    // Find Save All Changes button
    const saveAllButton = document.querySelector('button:contains("Save All Changes")') || 
                         Array.from(document.querySelectorAll('button')).find(btn => 
                             btn.textContent.includes('Save All Changes') || 
                             btn.textContent.includes('Save All') ||
                             btn.textContent.includes('Save')
                         );
    
    // Find Cancel button
    const cancelButton = document.querySelector('button:contains("Cancel")') ||
                        Array.from(document.querySelectorAll('button')).find(btn => 
                            btn.textContent.includes('Cancel')
                        );
    
    // Enhance Save All Changes button
    if (saveAllButton && !saveAllButton.innerHTML.includes('💾')) {
        console.log('✅ Enhancing Save All Changes button...');
        
        saveAllButton.innerHTML = `
            <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="flex-shrink: 0;">
                    <path d="M17 3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V7L17 3M19 19H5V5H16.17L19 7.83V19M12 12C10.34 12 9 13.34 9 15S10.34 18 12 18 15 16.66 15 15 13.66 12 12 12M6 6H15V10H6V6Z"/>
                </svg>
                Save All Changes
            </span>
        `;
        
        saveAllButton.style.cssText = `
            background: linear-gradient(145deg, #10b981, #059669) !important;
            color: white !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
            transition: all 0.3s ease !important;
            min-width: 180px !important;
            height: 48px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        `;
        
        // Add enhanced hover effects
        saveAllButton.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
            this.style.boxShadow = '0 8px 20px rgba(16, 185, 129, 0.35)';
            this.style.background = 'linear-gradient(145deg, #059669, #047857)';
        });
        
        saveAllButton.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.25)';
            this.style.background = 'linear-gradient(145deg, #10b981, #059669)';
        });
        
        // Add click animation
        saveAllButton.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0) scale(0.98)';
        });
        
        saveAllButton.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
    }
    
    // Enhance Cancel button
    if (cancelButton && !cancelButton.innerHTML.includes('✕')) {
        console.log('✅ Enhancing Cancel button...');
        
        cancelButton.innerHTML = `
            <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="flex-shrink: 0;">
                    <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"/>
                </svg>
                Cancel
            </span>
        `;
        
        cancelButton.style.cssText = `
            background: linear-gradient(145deg, #ef4444, #dc2626) !important;
            color: white !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25) !important;
            transition: all 0.3s ease !important;
            min-width: 120px !important;
            height: 48px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin-left: 12px !important;
        `;
        
        // Add enhanced hover effects
        cancelButton.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
            this.style.boxShadow = '0 8px 20px rgba(239, 68, 68, 0.35)';
            this.style.background = 'linear-gradient(145deg, #dc2626, #b91c1c)';
        });
        
        cancelButton.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.25)';
            this.style.background = 'linear-gradient(145deg, #ef4444, #dc2626)';
        });
        
        // Add click animation
        cancelButton.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0) scale(0.98)';
        });
        
        cancelButton.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
    }
}

// Also look for buttons by class names commonly used in dashboards
function findAndEnhanceEditButtons() {
    // Common selectors for edit mode buttons
    const saveSelectors = [
        '.save-all-btn',
        '.save-changes-btn',
        '.submit-btn',
        '.confirm-btn',
        'button[type="submit"]',
        '#save-all-changes',
        '.edit-save-btn'
    ];
    
    const cancelSelectors = [
        '.cancel-btn',
        '.cancel-edit-btn',
        '.discard-btn',
        '#cancel-edit',
        '.edit-cancel-btn'
    ];
    
    // Find save buttons
    let saveButton = null;
    for (const selector of saveSelectors) {
        saveButton = document.querySelector(selector);
        if (saveButton) break;
    }
    
    // Find cancel buttons
    let cancelBtn = null;
    for (const selector of cancelSelectors) {
        cancelBtn = document.querySelector(selector);
        if (cancelBtn) break;
    }
    
    // Also search by text content
    if (!saveButton) {
        saveButton = Array.from(document.querySelectorAll('button')).find(btn => {
            const text = btn.textContent.toLowerCase();
            return text.includes('save') && (text.includes('all') || text.includes('changes'));
        });
    }
    
    if (!cancelBtn) {
        cancelBtn = Array.from(document.querySelectorAll('button')).find(btn => {
            const text = btn.textContent.toLowerCase();
            return text.includes('cancel') && !btn.innerHTML.includes('✕');
        });
    }
    
    // Apply enhancements
    if (saveButton && !saveButton.innerHTML.includes('svg')) {
        enhanceSaveButton(saveButton);
    }
    
    if (cancelBtn && !cancelBtn.innerHTML.includes('svg')) {
        enhanceCancelButton(cancelBtn);
    }
}

function enhanceSaveButton(button) {
    button.innerHTML = `
        <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V7L17 3M19 19H5V5H16.17L19 7.83V19M12 12C10.34 12 9 13.34 9 15S10.34 18 12 18 15 16.66 15 15 13.66 12 12 12M6 6H15V10H6V6Z"/>
            </svg>
            Save All Changes
        </span>
    `;
    
    button.style.cssText = `
        background: linear-gradient(145deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
        transition: all 0.3s ease !important;
        min-width: 180px !important;
        height: 48px !important;
    `;
}

function enhanceCancelButton(button) {
    button.innerHTML = `
        <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"/>
            </svg>
            Cancel
        </span>
    `;
    
    button.style.cssText = `
        background: linear-gradient(145deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25) !important;
        transition: all 0.3s ease !important;
        min-width: 120px !important;
        height: 48px !important;
    `;
}

// Run the enhancement
enhanceDashboardEditButtons();
findAndEnhanceEditButtons();

// Monitor for edit mode activation
const editObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' || mutation.type === 'attributes') {
            // Check if edit mode buttons appeared
            setTimeout(() => {
                enhanceDashboardEditButtons();
                findAndEnhanceEditButtons();
            }, 100);
        }
    });
});

editObserver.observe(document.body, { 
    childList: true, 
    subtree: true, 
    attributes: true,
    attributeFilter: ['class', 'style']
});

console.log('✅ CUSTOMER DASHBOARD EDIT BUTTONS ENHANCED!');
console.log('🎨 Features added:');
console.log('   💾 Save All Changes with disk icon');
console.log('   ✕ Cancel with X icon');
console.log('   🎯 Larger, more prominent buttons');
console.log('   ✨ Enhanced hover and click animations');
console.log('   🔄 Auto-detects when edit mode is activated');