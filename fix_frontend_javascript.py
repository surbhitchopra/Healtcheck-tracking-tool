#!/usr/bin/env python
"""
Fix the frontend JavaScript in customer_dashboard.html to properly use individual network months arrays
"""

import os
from datetime import datetime

# Create backup
template_file = 'templates/customer_dashboard.html'
backup_filename = f"customer_dashboard_js_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
backup_path = os.path.join('templates', backup_filename)

print(f"🔒 Creating backup: {backup_filename}")

with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Backup created: {backup_path}")

# The fix: Replace the network month cell generation logic
old_network_logic = '''        // DIRECT FIX: Get date from network's monthly_runs dictionary
        let networkDateValue = '-';
        
        // Find the specific network object
        const targetNetwork = customer.networks && customer.networks.find(net => {
            const netName = net.network_name || net.name || '';
            return netName === networkName || netName.includes(networkName) || networkName.includes(netName);
        });
        
        console.log(`🔍 NETWORK DEBUG: Looking for "${networkName}" in customer "${customer.name}"`);
        console.log(`🔍 Available networks:`, customer.networks ? customer.networks.map(n => n.network_name || n.name) : 'none');
        
        if (targetNetwork) {
            console.log(`✅ Found target network:`, targetNetwork.network_name || targetNetwork.name);
            console.log(`📅 Network monthly_runs:`, targetNetwork.monthly_runs);
            
            if (targetNetwork.monthly_runs && typeof targetNetwork.monthly_runs === 'object') {
                const monthKey = `2025-${String(actualIndex + 1).padStart(2, '0')}`; // Force 2025
                const dbDate = targetNetwork.monthly_runs[monthKey];
                
                console.log(`🔍 Checking monthKey: ${monthKey} -> ${dbDate}`);
                
                if (dbDate && dbDate !== '-' && dbDate !== 'Not Run' && dbDate !== 'Not Started') {
                    try {
                        // Convert "2025-01-03" to "03-Jan"
                        const dateObj = new Date(dbDate);
                        if (!isNaN(dateObj.getTime())) {
                            networkDateValue = dateObj.toLocaleDateString('en-GB', { 
                                day: '2-digit', 
                                month: 'short' 
                            }).replace(' ', '-');
                            console.log(`✅ NETWORK DATE SUCCESS: ${networkName} ${monthKey} = ${dbDate} -> ${networkDateValue}`);
                        }
                    } catch (e) {
                        console.log(`⚠️ Date parsing error:`, e);
                    }
                } else {
                    console.log(`⚪ No valid date for ${networkName} in ${monthKey}`);
                }
            } else {
                console.log(`❌ No monthly_runs data for ${networkName}`);
            }
        } else {
            console.log(`❌ Network "${networkName}" not found in customer.networks`);
        }'''

new_network_logic = '''        // FIXED LOGIC: Use network's months array (formatted by backend)
        let networkDateValue = '-';
        
        // Find the specific network object
        const targetNetwork = customer.networks && customer.networks.find(net => {
            const netName = net.network_name || net.name || '';
            return netName === networkName || netName.includes(networkName) || networkName.includes(netName);
        });
        
        console.log(`🔍 NETWORK DEBUG: Looking for "${networkName}" in customer "${customer.name}"`);
        
        if (targetNetwork) {
            console.log(`✅ Found target network:`, targetNetwork.network_name || targetNetwork.name);
            console.log(`📅 Network months array:`, targetNetwork.months);
            
            // PRIORITY 1: Use the formatted months array from backend API
            if (targetNetwork.months && Array.isArray(targetNetwork.months) && actualIndex < targetNetwork.months.length) {
                const monthValue = targetNetwork.months[actualIndex];
                if (monthValue && monthValue !== '-') {
                    networkDateValue = monthValue;
                    console.log(`✅ USING MONTHS ARRAY: ${networkName} month ${actualIndex + 1} = ${monthValue}`);
                }
            }
            // FALLBACK: Try monthly_runs dictionary if months array not available
            else if (targetNetwork.monthly_runs && typeof targetNetwork.monthly_runs === 'object') {
                const monthKey = `2025-${String(actualIndex + 1).padStart(2, '0')}`;
                const dbDate = targetNetwork.monthly_runs[monthKey];
                
                console.log(`🔄 FALLBACK: Checking monthKey: ${monthKey} -> ${dbDate}`);
                
                if (dbDate && dbDate !== '-') {
                    if (dbDate === 'Not Started' || dbDate === 'No Report' || dbDate === 'Not Run') {
                        networkDateValue = dbDate;
                    } else {
                        try {
                            // Convert "2025-01-03" to "3-Jan"
                            const dateObj = new Date(dbDate);
                            if (!isNaN(dateObj.getTime())) {
                                const day = dateObj.getDate();
                                const monthName = dateObj.toLocaleDateString('en-US', { month: 'short' });
                                networkDateValue = `${day}-${monthName}`;
                                console.log(`✅ FALLBACK SUCCESS: ${networkName} ${monthKey} = ${dbDate} -> ${networkDateValue}`);
                            }
                        } catch (e) {
                            networkDateValue = String(dbDate);
                            console.log(`⚠️ Using raw value: ${dbDate}`);
                        }
                    }
                }
            } else {
                console.log(`❌ No months array or monthly_runs data for ${networkName}`);
            }
        } else {
            console.log(`❌ Network "${networkName}" not found in customer.networks`);
        }'''

# Apply the fix
if old_network_logic in content:
    content = content.replace(old_network_logic, new_network_logic)
    fixes_applied = 1
    print("✅ Fixed network date logic")
else:
    print("❌ Old logic not found - trying partial match")
    # Try a smaller, more specific pattern
    old_pattern = "const monthKey = `2025-${String(actualIndex + 1).padStart(2, '0')}`; // Force 2025"
    if old_pattern in content:
        # Find and replace the broader logic
        start_marker = "// DIRECT FIX: Get date from network's monthly_runs dictionary"
        end_marker = "} else {"
        
        start_pos = content.find(start_marker)
        if start_pos != -1:
            # Find the corresponding end position
            end_pos = content.find('console.log(`❌ Network "${networkName}" not found in customer.networks`);', start_pos)
            if end_pos != -1:
                end_pos = content.find('}', end_pos) + 1  # Include the closing brace
                
                old_section = content[start_pos:end_pos]
                new_section = '''// FIXED LOGIC: Use network's months array (formatted by backend)
        let networkDateValue = '-';
        
        // Find the specific network object
        const targetNetwork = customer.networks && customer.networks.find(net => {
            const netName = net.network_name || net.name || '';
            return netName === networkName || netName.includes(networkName) || networkName.includes(netName);
        });
        
        console.log(`🔍 NETWORK DEBUG: Looking for "${networkName}" in customer "${customer.name}"`);
        
        if (targetNetwork) {
            console.log(`✅ Found target network:`, targetNetwork.network_name || targetNetwork.name);
            console.log(`📅 Network months array:`, targetNetwork.months);
            
            // PRIORITY 1: Use the formatted months array from backend API
            if (targetNetwork.months && Array.isArray(targetNetwork.months) && actualIndex < targetNetwork.months.length) {
                const monthValue = targetNetwork.months[actualIndex];
                if (monthValue && monthValue !== '-') {
                    networkDateValue = monthValue;
                    console.log(`✅ USING MONTHS ARRAY: ${networkName} month ${actualIndex + 1} = ${monthValue}`);
                }
            }
            // FALLBACK: Try monthly_runs dictionary if months array not available
            else if (targetNetwork.monthly_runs && typeof targetNetwork.monthly_runs === 'object') {
                const monthKey = `2025-${String(actualIndex + 1).padStart(2, '0')}`;
                const dbDate = targetNetwork.monthly_runs[monthKey];
                
                console.log(`🔄 FALLBACK: Checking monthKey: ${monthKey} -> ${dbDate}`);
                
                if (dbDate && dbDate !== '-') {
                    if (dbDate === 'Not Started' || dbDate === 'No Report' || dbDate === 'Not Run') {
                        networkDateValue = dbDate;
                    } else {
                        try {
                            // Convert "2025-01-03" to "3-Jan"
                            const dateObj = new Date(dbDate);
                            if (!isNaN(dateObj.getTime())) {
                                const day = dateObj.getDate();
                                const monthName = dateObj.toLocaleDateString('en-US', { month: 'short' });
                                networkDateValue = `${day}-${monthName}`;
                                console.log(`✅ FALLBACK SUCCESS: ${networkName} ${monthKey} = ${dbDate} -> ${networkDateValue}`);
                            }
                        } catch (e) {
                            networkDateValue = String(dbDate);
                            console.log(`⚠️ Using raw value: ${dbDate}`);
                        }
                    }
                }
            } else {
                console.log(`❌ No months array or monthly_runs data for ${networkName}`);
            }
        } else {
            console.log(`❌ Network "${networkName}" not found in customer.networks`);
        }'''
                
                content = content.replace(old_section, new_section)
                fixes_applied = 1
                print("✅ Fixed network date logic with partial match")
            else:
                fixes_applied = 0
                print("❌ Could not find end of section")
        else:
            fixes_applied = 0
            print("❌ Could not find start marker")
    else:
        fixes_applied = 0
        print("❌ Could not find any matching pattern")

# Write the fixed content back
if fixes_applied > 0:
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎉 SUCCESS! Fixed frontend JavaScript logic")
    print("📋 Changes made:")
    print("   - Now uses individual network 'months' arrays from backend")
    print("   - Fallback to monthly_runs dictionary if needed")
    print("   - Proper handling of 'Not Started' and 'No Report' values")
    print("   - Each network will show its own specific dates")
    
    print(f"\n🔧 Next steps:")
    print("   1. Refresh your dashboard page in browser")
    print("   2. BSNL networks should now show individual dates!")
    print("   3. Check browser console for debug logs")
else:
    print(f"\n❌ FAILED to apply fix")
    print("   The template structure might be different")
    print("   Manual editing may be required")

print(f"\n📁 Backup available at: {backup_path}")
print("Use this backup to restore if needed")