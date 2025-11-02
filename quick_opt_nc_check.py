import sqlite3
import json
from datetime import datetime

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("🔍 Checking OPT_NC customer data...")

# Check Customer table structure
cursor.execute("PRAGMA table_info(HealthCheck_app_customer)")
columns = cursor.fetchall()
print(f"Customer table columns: {[col[1] for col in columns]}")

# Find OPT_NC customers
cursor.execute("""
    SELECT name, network_name, network_type, setup_status, created_at 
    FROM HealthCheck_app_customer 
    WHERE (name LIKE '%OPT%' OR name LIKE '%NC%') 
    AND is_deleted = 0
    ORDER BY created_at DESC
""")

customers = cursor.fetchall()
print(f"\n📊 Found {len(customers)} OPT/NC customers:")

for customer in customers:
    name, network, network_type, setup_status, created_at = customer
    print(f"\n🔸 Customer: {name}")
    print(f"   Network: {network}")
    print(f"   Network Type: {network_type}")
    print(f"   Setup Status: {setup_status}")
    print(f"   Created: {created_at}")

# Check if there are any OPT_NC sessions
print(f"\n🔍 Checking recent sessions for OPT_NC...")
cursor.execute("""
    SELECT customer_name, created_at, status 
    FROM HealthCheck_app_healthchecksession 
    WHERE customer_name LIKE '%OPT%' 
    ORDER BY created_at DESC 
    LIMIT 5
""")

sessions = cursor.fetchall()
print(f"Recent OPT sessions: {len(sessions)}")
for session in sessions:
    print(f"   {session}")

conn.close()
print("\n✅ Database check complete")