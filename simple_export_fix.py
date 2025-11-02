# Simple Export Fix - Add this to views.py

@login_required
def simple_export_test(request):
    """Simple test export that will definitely work"""
    if request.method == 'POST':
        try:
            import csv
            from io import StringIO
            from django.http import HttpResponse
            from django.utils import timezone
            
            print("🚀 SIMPLE EXPORT TEST CALLED!")
            
            # Create simple CSV content
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['Customer Dashboard Export Test'])
            writer.writerow([f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Simple test data
            writer.writerow(['Customer Name', 'Networks', 'Total Runs', 'Status'])
            writer.writerow(['Test Customer 1', 'Network A, Network B', '15', 'Active'])
            writer.writerow(['Test Customer 2', 'Network C', '8', 'Active'])
            writer.writerow(['Test Customer 3', 'Network D, Network E, Network F', '23', 'Active'])
            
            # Get CSV content
            csv_content = output.getvalue()
            output.close()
            
            print(f"✅ CSV generated successfully, size: {len(csv_content)} characters")
            
            # Return as downloadable CSV file
            response = HttpResponse(
                csv_content.encode('utf-8'), 
                content_type='text/csv; charset=utf-8'
            )
            
            filename = f'customer_dashboard_test_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(csv_content.encode('utf-8'))
            
            print(f"✅ Returning test CSV file: {filename}")
            return response
            
        except Exception as e:
            print(f"❌ SIMPLE EXPORT ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'status': 'error',
                'message': f'Simple export failed: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


# Add this URL pattern to urls.py:
# path('api/simple-export-test/', views.simple_export_test, name='simple_export_test'),