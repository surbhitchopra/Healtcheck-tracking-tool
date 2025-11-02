import sqlite3
import os
from datetime import datetime

# Connect to the database
db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database file {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Available tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check health check related tables
hc_tables = [table[0] for table in tables if 'healthcheck' in table[0].lower()]
print(f"\nHealth Check related tables: {hc_tables}")

# Try to get recent entries from health check session table
if hc_tables:
    for table_name in hc_tables:
        print(f"\nChecking recent entries from {table_name}:")
        
        try:
            # Get column information first
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Columns: {column_names}")
            
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 5")
            rows = cursor.fetchall()
            
            print("Recent entries:")
            for row in rows:
                entry_dict = dict(zip(column_names, row))
                print(f"  {entry_dict}")
                
        except Exception as e:
            print(f"Error querying {table_name}: {e}")

print(f"\nCurrent system time: {datetime.now()}")
print(f"Current UTC time: {datetime.utcnow()}")

conn.close()
