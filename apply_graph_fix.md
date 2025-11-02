# GRAPH REFRESH FIX - Implementation Guide

## Problem:
- Total cards, statistics cards, and table update correctly when trackers are generated
- Graphs (both 6-month tracking and active customers) don't update until page refresh
- This causes OPT_NC October showing 1 instead of 2 runs in graphs

## Solution:
The fix makes graphs use the same real-time data source as cards and tables.

## How to Apply:

### Method 1: Include the Fix Script (RECOMMENDED)

1. **Add the script to your dashboard template:**
   
   Open `templates/customer_dashboard.html` and add this line before the closing `</body>` tag:
   
   ```html
   <script src="/static/js/fix_graph_refresh.js"></script>
   ```
   
   OR add the script directly inline by copying the content of `fix_graph_refresh.js` into a `<script>` tag in the template.

### Method 2: Copy and Apply Directly

1. **Copy the fix script content** from `fix_graph_refresh.js`
2. **Add it to your customer dashboard HTML** at the end of the JavaScript section (before the closing `{% endblock %}`)

## What the Fix Does:

### 🔄 **Real-time Data Loading**
- Forces graphs to reload fresh data from the same API endpoint as cards/tables
- No more using cached `dashboardData` for graphs

### 📊 **Enhanced Graph Updates** 
- `updateTrackingGraph()` function now gets fresh data before rendering
- Both 6-month activity and active customers charts update together

### ⏱️ **Auto-refresh**
- Graphs refresh every 15 seconds automatically
- Also refresh when browser window gains focus
- Same behavior as cards and statistics

### 🎯 **Accurate Counting**
- Uses the same `getCustomerMonthRuns()` function as table
- Shows real-time session counts (like OPT_NC Oct: 2 runs)
- Matches table and card data exactly

## Testing:

1. **Apply the fix** using Method 1 or 2 above
2. **Generate a tracker** for a customer (like OPT_NC)  
3. **Check the dashboard:**
   - Total cards should update ✅ (already working)
   - Statistics cards should update ✅ (already working) 
   - Table should update ✅ (already working)
   - **Graphs should now update too** 🆕 (fixed!)

## Expected Results:

After applying the fix:
- **OPT_NC October** should show **2 runs** in both graphs (not 1)
- **Both graphs** update when trackers are generated
- **No page refresh** needed to see updated data
- **Consistent data** across cards, table, and graphs

## Files Modified:

- `fix_graph_refresh.js` - The fix script  
- `templates/customer_dashboard.html` - Include the script
- No other changes needed!

## Troubleshooting:

If graphs still don't update:
1. **Check browser console** for any JavaScript errors
2. **Clear browser cache** (Ctrl+F5)
3. **Verify script is loaded** - check browser dev tools Network tab
4. **Check API responses** - ensure `/api/customer-dashboard/customers/` returns updated data

The fix is backwards compatible and won't break existing functionality.