import sqlite3

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("🔍 Checking current OPT sessions...")

# Get OPT customer ID
cursor.execute("SELECT id, name FROM HealthCheck_app_customer WHERE name LIKE '%OPT%'")
opt_customer = cursor.fetchone()

if opt_customer:
    customer_id, customer_name = opt_customer
    print(f"📊 Customer: {customer_name} (ID: {customer_id})")
    
    # Count ALL sessions for this customer
    cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE customer_id = ? AND status = 'COMPLETED'", (customer_id,))
    total_sessions = cursor.fetchone()[0]
    print(f"🔢 Total completed sessions: {total_sessions}")
    
    # Count October 2025 sessions (current year)
    cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE customer_id = ? AND status = 'COMPLETED' AND created_at LIKE '2025-10%'", (customer_id,))
    oct_2025_sessions = cursor.fetchone()[0]
    print(f"📅 October 2025 sessions: {oct_2025_sessions}")
    
    # Count October 2024 sessions for comparison
    cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE customer_id = ? AND status = 'COMPLETED' AND created_at LIKE '2024-10%'", (customer_id,))
    oct_2024_sessions = cursor.fetchone()[0]
    print(f"📅 October 2024 sessions: {oct_2024_sessions}")
    
    # Show recent sessions
    cursor.execute("SELECT created_at, status FROM HealthCheck_app_healthchecksession WHERE customer_id = ? ORDER BY created_at DESC LIMIT 3", (customer_id,))
    recent_sessions = cursor.fetchall()
    print(f"📋 Recent sessions:")
    for session in recent_sessions:
        print(f"   {session[0]} - {session[1]}")
    
else:
    print("❌ No OPT customer found")

conn.close()
print("\n✅ Test complete")