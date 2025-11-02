// ADD ICONS TO SAVE & CANCEL BUTTONS IN EDIT MODE - Run this in console

console.log('🎨 ADDING ICONS TO SAVE & CANCEL BUTTONS...');

// Override the edit functionality to include icons
window.originalMakeEditable = window.makeEditable;
window.makeEditable = function(element, field, customerKey) {
    console.log('🔧 Enhanced makeEditable with icons...');
    
    if (window.originalMakeEditable) {
        window.originalMakeEditable(element, field, customerKey);
    }
    
    // Add icons to the buttons after they're created
    setTimeout(() => {
        const saveButton = element.querySelector('.save-btn');
        const cancelButton = element.querySelector('.cancel-btn');
        
        if (saveButton) {
            // Add save icon
            saveButton.innerHTML = `
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    💾 Save
                </span>
            `;
            saveButton.style.cssText = `
                background: linear-gradient(145deg, #10b981, #059669);
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.7rem;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
                transition: all 0.2s ease;
            `;
            
            // Add hover effect
            saveButton.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-1px)';
                this.style.boxShadow = '0 4px 8px rgba(16, 185, 129, 0.4)';
            });
            
            saveButton.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 4px rgba(16, 185, 129, 0.3)';
            });
        }
        
        if (cancelButton) {
            // Add cancel icon
            cancelButton.innerHTML = `
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    ❌ Cancel
                </span>
            `;
            cancelButton.style.cssText = `
                background: linear-gradient(145deg, #ef4444, #dc2626);
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.7rem;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
                transition: all 0.2s ease;
                margin-left: 4px;
            `;
            
            // Add hover effect
            cancelButton.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-1px)';
                this.style.boxShadow = '0 4px 8px rgba(239, 68, 68, 0.4)';
            });
            
            cancelButton.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 4px rgba(239, 68, 68, 0.3)';
            });
        }
    }, 50);
};

// Also enhance any existing edit buttons
function enhanceExistingEditButtons() {
    const saveButtons = document.querySelectorAll('.save-btn');
    const cancelButtons = document.querySelectorAll('.cancel-btn');
    
    saveButtons.forEach(button => {
        if (!button.innerHTML.includes('💾')) {
            button.innerHTML = `
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    💾 Save
                </span>
            `;
            button.style.cssText = `
                background: linear-gradient(145deg, #10b981, #059669);
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.7rem;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
                transition: all 0.2s ease;
            `;
        }
    });
    
    cancelButtons.forEach(button => {
        if (!button.innerHTML.includes('❌')) {
            button.innerHTML = `
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    ❌ Cancel
                </span>
            `;
            button.style.cssText = `
                background: linear-gradient(145deg, #ef4444, #dc2626);
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.7rem;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
                transition: all 0.2s ease;
                margin-left: 4px;
            `;
        }
    });
}

// Enhanced version with better icons
window.createEditButtons = function(element, field, customerKey) {
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: inline-flex;
        gap: 6px;
        margin-left: 8px;
        align-items: center;
    `;
    
    // Save button with icon
    const saveButton = document.createElement('button');
    saveButton.className = 'save-btn';
    saveButton.innerHTML = `
        <span style="display: inline-flex; align-items: center; gap: 4px;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V7L17 3M19 19H5V5H16.17L19 7.83V19M12 12C10.34 12 9 13.34 9 15S10.34 18 12 18 15 16.66 15 15 13.66 12 12 12M6 6H15V10H6V6Z"/>
            </svg>
            Save
        </span>
    `;
    saveButton.style.cssText = `
        background: linear-gradient(145deg, #10b981, #059669);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25);
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    `;
    
    // Cancel button with icon
    const cancelButton = document.createElement('button');
    cancelButton.className = 'cancel-btn';
    cancelButton.innerHTML = `
        <span style="display: inline-flex; align-items: center; gap: 4px;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"/>
            </svg>
            Cancel
        </span>
    `;
    cancelButton.style.cssText = `
        background: linear-gradient(145deg, #ef4444, #dc2626);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.25);
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    `;
    
    // Add hover effects
    saveButton.addEventListener('mouseenter', () => {
        saveButton.style.transform = 'translateY(-1px)';
        saveButton.style.boxShadow = '0 4px 8px rgba(16, 185, 129, 0.35)';
    });
    
    saveButton.addEventListener('mouseleave', () => {
        saveButton.style.transform = 'translateY(0)';
        saveButton.style.boxShadow = '0 2px 4px rgba(16, 185, 129, 0.25)';
    });
    
    cancelButton.addEventListener('mouseenter', () => {
        cancelButton.style.transform = 'translateY(-1px)';
        cancelButton.style.boxShadow = '0 4px 8px rgba(239, 68, 68, 0.35)';
    });
    
    cancelButton.addEventListener('mouseleave', () => {
        cancelButton.style.transform = 'translateY(0)';
        cancelButton.style.boxShadow = '0 2px 4px rgba(239, 68, 68, 0.25)';
    });
    
    buttonContainer.appendChild(saveButton);
    buttonContainer.appendChild(cancelButton);
    
    return { container: buttonContainer, saveButton, cancelButton };
};

// Apply to existing buttons
enhanceExistingEditButtons();

// Also monitor for new edit buttons
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const saveButtons = node.querySelectorAll ? node.querySelectorAll('.save-btn') : [];
                    const cancelButtons = node.querySelectorAll ? node.querySelectorAll('.cancel-btn') : [];
                    
                    if (node.classList && (node.classList.contains('save-btn') || node.classList.contains('cancel-btn'))) {
                        enhanceExistingEditButtons();
                    } else if (saveButtons.length > 0 || cancelButtons.length > 0) {
                        enhanceExistingEditButtons();
                    }
                }
            });
        }
    });
});

observer.observe(document.body, { childList: true, subtree: true });

console.log('✅ EDIT BUTTON ICONS ENHANCED!');
console.log('🎨 Features added:');
console.log('   💾 Save button with disk icon');
console.log('   ❌ Cancel button with X icon');
console.log('   🎯 Gradient backgrounds');
console.log('   ✨ Hover animations');
console.log('   🔄 Auto-applies to new edit buttons');