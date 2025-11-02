import sqlite3
import json
from datetime import datetime

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("🔍 Checking HealthCheck sessions...")

# Check HealthCheck sessions table structure
cursor.execute("PRAGMA table_info(HealthCheck_app_healthchecksession)")
columns = cursor.fetchall()
print(f"HealthCheck Sessions columns: {[col[1] for col in columns]}")

# Get recent HealthCheck sessions
cursor.execute("""
    SELECT * FROM HealthCheck_app_healthchecksession 
    ORDER BY id DESC 
    LIMIT 5
""")

sessions = cursor.fetchall()
print(f"\n📊 Found {len(sessions)} recent HealthCheck sessions:")

for session in sessions:
    print(f"   Session: {session}")

# Count OPT_NC sessions specifically
cursor.execute("""
    SELECT COUNT(*) FROM HealthCheck_app_healthchecksession 
    WHERE customer_name LIKE '%OPT%'
""")

opt_count = cursor.fetchone()[0]
print(f"\n🔸 OPT sessions count: {opt_count}")

# Check if there are sessions from October 2024
cursor.execute("""
    SELECT customer_name, COUNT(*) as session_count
    FROM HealthCheck_app_healthchecksession 
    WHERE created_at LIKE '2024-10%'
    GROUP BY customer_name
    ORDER BY session_count DESC
""")

oct_sessions = cursor.fetchall()
print(f"\n📅 October 2024 sessions by customer:")
for customer_data in oct_sessions:
    print(f"   {customer_data[0]}: {customer_data[1]} sessions")

conn.close()
print("\n✅ Sessions check complete")