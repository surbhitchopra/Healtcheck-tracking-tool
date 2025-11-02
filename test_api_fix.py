#!/usr/bin/env python
import requests
import json

def test_api_fix():
    """Test the fixed API to see if October runs are now properly reflected"""
    
    api_url = "http://127.0.0.1:8000/api/customer-dashboard-customers/"
    
    try:
        # Make API request without date filtering (should show all data)
        print("Testing API fix for October runs...")
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'customers' in data:
                customers = data['customers']
                
                # Find OPT_NC customer
                opt_customer = None
                for key, customer in customers.items():
                    if 'OPT' in customer.get('name', '') or 'OPT' in key:
                        opt_customer = customer
                        print(f"Found OPT customer: {customer.get('name')} (key: {key})")
                        break
                
                if opt_customer:
                    print(f"OPT Customer data:")
                    print(f"  - Name: {opt_customer.get('name')}")
                    print(f"  - Total runs: {opt_customer.get('total_runs')}")
                    print(f"  - Last run date: {opt_customer.get('last_run_date')}")
                    print(f"  - Monthly runs array: {opt_customer.get('monthly_runs')}")
                    
                    # Check October specifically (month 10 = index 9)
                    monthly_runs = opt_customer.get('monthly_runs', [])
                    if len(monthly_runs) >= 10:
                        october_runs = monthly_runs[9]  # October = index 9
                        print(f"  - October runs: {october_runs}")
                        
                        if october_runs != '-':
                            print("✅ SUCCESS: October runs are now showing!")
                        else:
                            print("❌ ISSUE: October runs still showing as '-'")
                    
                    # Check total runs count
                    total_runs = opt_customer.get('total_runs', 0)
                    if total_runs >= 19:
                        print(f"✅ SUCCESS: Total runs count is correct: {total_runs}")
                    else:
                        print(f"❌ ISSUE: Total runs count still incorrect: {total_runs} (should be 19)")
                        
                else:
                    print("❌ OPT customer not found in API response")
                    print("Available customers:", list(customers.keys()))
            else:
                print("❌ No customers data in API response")
                print("Response:", data)
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api_fix()