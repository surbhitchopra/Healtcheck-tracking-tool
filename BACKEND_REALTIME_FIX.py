
# ADD THIS TO YOUR views.py - PERMANENT FIX FOR GRAPH UPDATE

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from .models import Customer, HealthCheckSession

@require_http_methods(["GET"])
def api_customer_dashboard_customers_REALTIME(request):
    """
    🚀 REAL-TIME API: This counts actual sessions instead of static data
    Graphs will now always show current data!
    """
    try:
        print("📡 REAL-TIME API called")
        
        customers = Customer.objects.filter(is_deleted=False)
        customer_data = {}
        
        for customer in customers:
            # Count actual sessions for this customer
            sessions = HealthCheckSession.objects.filter(
                customer_id=customer.id,
                status='COMPLETED'
            )
            
            total_runs = sessions.count()
            
            # Calculate monthly runs for last 6 months
            monthly_runs = ['-'] * 12
            monthly_counts = {}
            
            current_date = datetime.now()
            
            # Get last 6 months data
            for i in range(6):
                target_date = current_date - timedelta(days=30*i)
                month_sessions = sessions.filter(
                    created_at__year=target_date.year,
                    created_at__month=target_date.month
                ).count()
                
                month_key = f"{target_date.year}-{target_date.month:02d}"
                monthly_counts[month_key] = month_sessions
                
                # Format for table display
                month_idx = target_date.month - 1
                if month_sessions > 0:
                    monthly_runs[month_idx] = f"{target_date.day}-{target_date.strftime('%b')}"
            
            customer_key = f"{customer.name}_{customer.network_name}_{customer.id}"
            
            customer_data[customer_key] = {
                'name': customer.name,
                'network_name': customer.network_name,
                'country': getattr(customer, 'country', 'Unknown'),
                'node_qty': getattr(customer, 'node_qty', 0),
                'ne_type': getattr(customer, 'ne_type', '1830 PSS'),
                'gtac': getattr(customer, 'gtac', 'PSS'),
                'total_runs': total_runs,  # 🔥 REAL COUNT FROM SESSIONS
                'months': monthly_runs,
                'monthly_counts': monthly_counts,  # 🔥 REAL MONTHLY COUNTS
                'networks': [{
                    'name': customer.network_name,
                    'network_name': customer.network_name,
                    'runs': total_runs,
                    'total_runs': total_runs,
                    'months': monthly_runs,
                    'monthly_counts': monthly_counts,
                    'country': getattr(customer, 'country', 'Unknown'),
                    'node_count': getattr(customer, 'node_qty', 0),
                    'gtac': getattr(customer, 'gtac', 'PSS')
                }],
                'networks_count': 1,
                'data_source': 'real_time_sessions',
                'last_updated': datetime.now().isoformat()
            }
        
        print(f"✅ REAL-TIME API: Returning {len(customer_data)} customers")
        
        return JsonResponse({
            'success': True,
            'customers': customer_data,
            'total_customers': len(customer_data),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'real_time_sessions'
        })
        
    except Exception as e:
        print(f"❌ REAL-TIME API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# 🔥 REPLACE YOUR EXISTING API WITH THIS ONE
# Change your URL pattern to point to api_customer_dashboard_customers_REALTIME
