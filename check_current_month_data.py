#!/usr/bin/env python3
import sqlite3
from datetime import datetime, date

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Current month check
current_date = date.today()
current_month = current_date.strftime("%Y-%m")
print(f"Current date: {current_date}")
print(f"Checking for data in month: {current_month}")

# Check October 2025 data
cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE created_at LIKE '2025-10%'")
oct_count = cursor.fetchone()[0]
print(f"\nOctober 2025 sessions: {oct_count}")

# Check September 2025 data  
cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE created_at LIKE '2025-09%'")
sep_count = cursor.fetchone()[0]
print(f"September 2025 sessions: {sep_count}")

# Check all months with data
cursor.execute("""
    SELECT 
        strftime('%Y-%m', created_at) as month,
        COUNT(*) as session_count
    FROM HealthCheck_app_healthchecksession 
    GROUP BY strftime('%Y-%m', created_at)
    ORDER BY month DESC
    LIMIT 10
""")
monthly_data = cursor.fetchall()
print(f"\nMonthly session breakdown (last 10 months):")
for month, count in monthly_data:
    print(f"  {month}: {count} sessions")

# Check recent sessions
cursor.execute("""
    SELECT id, customer_id, created_at, status
    FROM HealthCheck_app_healthchecksession 
    ORDER BY created_at DESC 
    LIMIT 5
""")
recent_sessions = cursor.fetchall()
print(f"\nMost recent 5 sessions:")
for session_id, customer_id, created_at, status in recent_sessions:
    print(f"  Session {session_id}: Customer {customer_id}, Date: {created_at}, Status: {status}")

# Check if we have data for current date
today_str = current_date.strftime("%Y-%m-%d")
cursor.execute(f"SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE created_at LIKE '{today_str}%'")
today_count = cursor.fetchone()[0]
print(f"\nToday's sessions ({today_str}): {today_count}")

conn.close()