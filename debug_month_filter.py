#!/usr/bin/env python
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthCheck.settings')
django.setup()

from HealthCheck_app.models import Customer, HealthCheckSession
from django.utils import timezone
from django.db import connection

def debug_month_filter():
    customer = Customer.objects.get(name='OPT_NC')
    print(f"Testing month filter for customer: {customer.name} (ID: {customer.id})")
    
    # Get sessions using the same query as in the API
    sessions = HealthCheckSession.objects.filter(customer=customer)
    print(f"Total sessions found: {sessions.count()}")
    
    # Test month filtering
    print("\nTesting month filtering:")
    for month_num in range(9, 12):  # Test months 9, 10, 11
        month_sessions = sessions.filter(created_at__month=month_num)
        print(f"  Month {month_num}: {month_sessions.count()} sessions")
        
        if month_sessions.exists():
            latest = month_sessions.order_by('-created_at').first()
            print(f"    Latest: {latest.created_at}")
    
    # Check database backend and raw SQL
    print(f"\nDatabase backend: {connection.settings_dict['ENGINE']}")
    
    # Check what the SQL looks like
    month_10_query = sessions.filter(created_at__month=10)
    print(f"Month 10 SQL: {month_10_query.query}")
    
    # Test raw database query
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM HealthCheck_app_healthchecksession WHERE customer_id = %s", [customer.id])
    raw_count = cursor.fetchone()[0]
    print(f"Raw SQL count: {raw_count}")
    
    # Test manual month extraction
    cursor.execute("SELECT created_at, EXTRACT(month FROM created_at) as month_num FROM HealthCheck_app_healthchecksession WHERE customer_id = %s", [customer.id])
    month_results = cursor.fetchall()
    
    print("\nMonth extraction from database:")
    month_counts = {}
    for result in month_results:
        month_num = int(result[1])
        month_counts[month_num] = month_counts.get(month_num, 0) + 1
    
    for month, count in sorted(month_counts.items()):
        print(f"  Month {month}: {count} sessions")
    
    print("\nConclusion: The issue is likely in the Django month filter with timezone handling.")

if __name__ == "__main__":
    debug_month_filter()