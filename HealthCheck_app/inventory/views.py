"""
Inventory views for HealthCheck application

This module contains views for handling inventory-related functionality
in the health check system.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import csv
import os
from pathlib import Path


def inventory_dashboard(request):
    """
    Display the inventory dashboard with summary statistics
    """
    context = {
        'title': 'Inventory Dashboard',
        'total_nodes': 0,
        'active_nodes': 0,
        'inventory_files': []
    }
    return render(request, 'inventory/dashboard.html', context)


def inventory_report(request, customer_name=None):
    """
    Display inventory report for a specific customer
    """
    if customer_name:
        # Path to customer inventory files
        inventory_path = Path(f'Script/customer_files/{customer_name}/inventory_files')
        
        inventory_data = []
        if inventory_path.exists():
            # Read inventory files and prepare data
            for file_path in inventory_path.glob('*.csv'):
                # Process CSV files here
                pass
    
    context = {
        'customer_name': customer_name,
        'inventory_data': inventory_data,
    }
    return render(request, 'inventory/report.html', context)


@csrf_exempt
def api_inventory_data(request):
    """
    API endpoint to get inventory data in JSON format
    """
    if request.method == 'GET':
        customer = request.GET.get('customer', 'timedotcom')
        
        # Return inventory data as JSON
        data = {
            'status': 'success',
            'customer': customer,
            'inventory': []
        }
        return JsonResponse(data)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})
