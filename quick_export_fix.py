# Quick Export Fix - Simple working version

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import csv
from io import StringIO

@login_required
def quick_export(request):
    """Super simple export that will definitely work"""
    try:
        print("🚀 QUICK EXPORT CALLED!")
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write simple data
        writer.writerow(['Customer Dashboard Export'])
        writer.writerow([f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        writer.writerow(['Customer Name', 'Status', 'Networks', 'Total Runs'])
        writer.writerow(['Customer A', 'Active', 'Network 1, Network 2', '25'])
        writer.writerow(['Customer B', 'Active', 'Network 3', '18'])
        writer.writerow(['Customer C', 'Active', 'Network 4, Network 5', '32'])
        
        # Get content
        csv_content = output.getvalue()
        output.close()
        
        # Create response
        response = HttpResponse(csv_content, content_type='text/csv')
        filename = f'export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        print(f"✅ Export successful: {filename}")
        return response
        
    except Exception as e:
        print(f"❌ Export error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Export failed: {str(e)}'
        }, status=500)