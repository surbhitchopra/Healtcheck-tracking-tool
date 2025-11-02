#!/usr/bin/env python3
"""
Find all tables in database and understand the structure
"""

import sqlite3

def find_database_structure():
    print("🔍 FINDING DATABASE STRUCTURE")
    print("=" * 50)
    
    db_path = "C:\\Users\\surchopr\\Hc_Final\\db.sqlite3"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"\n🗃️ Table: {table_name}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default, primary_key = col
                pk_marker = " (PK)" if primary_key else ""
                print(f"     - {col_name}: {col_type}{pk_marker}")
            
            # Get row count if not too large
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   📈 Rows: {count}")
                
                # Sample some data for important tables
                if count > 0 and count < 1000:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_rows = cursor.fetchall()
                    if sample_rows:
                        print("   📋 Sample data:")
                        for i, row in enumerate(sample_rows):
                            print(f"     Row {i+1}: {row}")
                            
            except Exception as e:
                print(f"   ⚠️ Error getting count: {e}")
        
        # Check for customer-related data
        print(f"\n🎯 LOOKING FOR CUSTOMER DATA:")
        print("-" * 40)
        
        # Check HealthCheck sessions more closely
        cursor.execute("SELECT * FROM HealthCheck_app_healthchecksession ORDER BY created_at DESC LIMIT 10")
        sessions = cursor.fetchall()
        
        print(f"📊 Recent HealthCheck sessions:")
        for session in sessions[:5]:
            print(f"   ID: {session[0]}, Created: {session[4]}, Customer ID: {session[14]}")
            
        # Check if customer_id links to any table
        print(f"\n🔍 Checking customer_id relationships:")
        
        # Try to find which table contains customer info
        unique_customer_ids = set()
        for session in sessions:
            if session[14]:  # customer_id
                unique_customer_ids.add(session[14])
        
        print(f"📋 Found customer IDs in sessions: {list(unique_customer_ids)}")
        
        # Try to find customer names in other tables
        for table_name in [t[0] for t in tables if 'customer' in t[0].lower() or 'network' in t[0].lower()]:
            print(f"\n🔍 Checking table: {table_name}")
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"   {row}")
            except Exception as e:
                print(f"   Error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_database_structure()