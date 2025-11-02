from datetime import datetime, date
from collections import defaultdict
from healthcheck.models import Session, Customer, Network

def check_database_runs():
    print("🔍 DATABASE ANALYSIS - Actual vs Dashboard Comparison")
    print("=" * 70)
    
    # Get total sessions from database
    total_sessions = Session.objects.count()
    print(f"📊 TOTAL SESSIONS IN DATABASE: {total_sessions}")
    
    # Get October 2025 sessions specifically
    october_2025_sessions = Session.objects.filter(
        created_at__year=2025,
        created_at__month=10
    ).count()
    print(f"🗓️ OCTOBER 2025 SESSIONS: {october_2025_sessions}")
    
    # Get sessions by customer
    print(f"\n📋 SESSIONS BY CUSTOMER:")
    customers = Customer.objects.all()
    
    customer_runs = defaultdict(int)
    october_customer_runs = defaultdict(int)
    
    for customer in customers:
        # Total runs for this customer
        customer_sessions = Session.objects.filter(network__customer=customer).count()
        customer_runs[customer.name] = customer_sessions
        
        # October 2025 runs for this customer  
        october_sessions = Session.objects.filter(
            network__customer=customer,
            created_at__year=2025,
            created_at__month=10
        ).count()
        october_customer_runs[customer.name] = october_sessions
        
        if customer_sessions > 0:
            print(f"  🏢 {customer.name}: {customer_sessions} total runs, {october_sessions} in Oct 2025")
    
    # Recent sessions (last 10)
    print(f"\n🕒 RECENT SESSIONS (Last 10):")
    recent_sessions = Session.objects.order_by('-created_at')[:10]
    
    for session in recent_sessions:
        customer_name = session.network.customer.name if session.network else "Unknown"
        created_date = session.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  📅 {created_date}: {customer_name} (ID: {session.id})")
    
    # Monthly breakdown for 2025
    print(f"\n📅 MONTHLY BREAKDOWN FOR 2025:")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month_num, month_name in enumerate(months, 1):
        monthly_count = Session.objects.filter(
            created_at__year=2025,
            created_at__month=month_num
        ).count()
        print(f"  {month_name} 2025: {monthly_count} sessions")
    
    # Check specific customers that should have October data
    print(f"\n🎯 SPECIFIC CUSTOMER CHECK FOR OCTOBER 2025:")
    test_customers = ['BSNL', 'Moratelindo', 'Tata', 'LTV', 'Maxix']
    
    for customer_name in test_customers:
        try:
            customer = Customer.objects.get(name=customer_name)
            oct_sessions = Session.objects.filter(
                network__customer=customer,
                created_at__year=2025,
                created_at__month=10
            ).count()
            total_sessions = Session.objects.filter(network__customer=customer).count()
            print(f"  🏢 {customer_name}: {oct_sessions} Oct sessions / {total_sessions} total")
            
            # Show latest session date
            latest_session = Session.objects.filter(network__customer=customer).order_by('-created_at').first()
            if latest_session:
                latest_date = latest_session.created_at.strftime("%Y-%m-%d")
                print(f"    📅 Latest session: {latest_date}")
            else:
                print(f"    ❌ No sessions found")
                
        except Customer.DoesNotExist:
            print(f"  ❌ {customer_name}: Customer not found in database")
    
    return {
        'total_sessions': total_sessions,
        'october_2025_sessions': october_2025_sessions,
        'customer_runs': dict(customer_runs),
        'october_customer_runs': dict(october_customer_runs)
    }

# Execute the check
db_data = check_database_runs()

print(f"\n🔢 SUMMARY:")
print(f"  Total DB Sessions: {db_data['total_sessions']}")
print(f"  October 2025 Sessions: {db_data['october_2025_sessions']}")
print(f"  Customers with data: {len([c for c, r in db_data['customer_runs'].items() if r > 0])}")
