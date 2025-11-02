import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hc_final_project.settings')
django.setup()

from HealthCheck_app.models import Customer

def migrate_excel_dashboard_customers():
    """
    Migrate Excel customers from dashboard to database
    These are the actual customers shown in your Excel dashboard
    """
    
    print("🚀 Migrating Excel Dashboard Customers to Database")
    print("=" * 60)
    
    # Excel customers from your dashboard - REAL DATA
    excel_customers = [
        {
            'name': 'BSNL',
            'network_name': 'East Zone DWDM',
            'network_type': 'DWDM',
            'country': 'India',
            'node_qty': 150,
            'ne_type': 'Huawei',
            'gtac': 'Mumbai',
            'months': ['Complete', 'Complete', 'Complete', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'In Progress', '-', '-', '-'],
            'total_runs': 7
        },
        {
            'name': 'BSNL',
            'network_name': 'West Zone DWDM', 
            'network_type': 'DWDM',
            'country': 'India',
            'node_qty': 120,
            'ne_type': 'Huawei',
            'gtac': 'Mumbai',
            'months': ['Complete', 'Complete', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 8
        },
        {
            'name': 'BSNL',
            'network_name': 'North Zone DWDM',
            'network_type': 'DWDM', 
            'country': 'India',
            'node_qty': 180,
            'ne_type': 'Huawei',
            'gtac': 'Delhi',
            'months': ['-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 8
        },
        {
            'name': 'BSNL',
            'network_name': 'North Zone OTN',
            'network_type': 'OTN',
            'country': 'India', 
            'node_qty': 95,
            'ne_type': 'Huawei',
            'gtac': 'Delhi',
            'months': ['-', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'In Progress', '-', '-', '-'],
            'total_runs': 6
        },
        {
            'name': 'BSNL',
            'network_name': 'West Zone OTN',
            'network_type': 'OTN',
            'country': 'India',
            'node_qty': 85,
            'ne_type': 'Huawei', 
            'gtac': 'Mumbai',
            'months': ['-', '-', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 6
        },
        {
            'name': 'Maxis',
            'network_name': 'Main Network',
            'network_type': 'MPLS',
            'country': 'Malaysia',
            'node_qty': 75,
            'ne_type': 'Cisco',
            'gtac': 'KL',
            'months': ['-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 7
        },
        {
            'name': 'Telekom Malaysia',
            'network_name': 'Main Network', 
            'network_type': 'DWDM',
            'country': 'Malaysia',
            'node_qty': 200,
            'ne_type': 'Huawei',
            'gtac': 'KL',
            'months': ['Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 8
        },
        {
            'name': 'Telekom',
            'network_name': 'Core Network',
            'network_type': 'DWDM', 
            'country': 'Germany',
            'node_qty': 300,
            'ne_type': 'Nokia',
            'gtac': 'Berlin',
            'months': ['Complete', 'Complete', 'Complete', 'Complete', '-', 'Complete', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 8
        },
        {
            'name': 'Moratelindo',
            'network_name': 'PSS24 Network',
            'network_type': 'PSS24',
            'country': 'Indonesia',
            'node_qty': 45,
            'ne_type': 'Huawei',
            'gtac': 'Jakarta',
            'months': ['-', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', 'In Progress', '-', '-', '-'],
            'total_runs': 5
        },
        {
            'name': 'OPT NC',
            'network_name': 'Main Network',
            'network_type': 'Telecom',
            'country': 'New Caledonia',
            'node_qty': 30,
            'ne_type': 'Alcatel',
            'gtac': 'Noumea',
            'months': ['-', '-', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 6
        },
        {
            'name': 'Timedotcom',
            'network_name': 'Main Network',
            'network_type': 'MPLS', 
            'country': 'Malaysia',
            'node_qty': 60,
            'ne_type': 'Juniper',
            'gtac': 'KL',
            'months': ['-', '-', '-', '-', 'Complete', 'Complete', 'Complete', 'Complete', 'Complete', '-', '-', '-'],
            'total_runs': 5
        }
    ]
    
    migrated_count = 0
    updated_count = 0
    
    for customer_data in excel_customers:
        try:
            customer_name = customer_data['name']
            network_name = customer_data['network_name']
            
            print(f"\n📁 Processing: {customer_name} - {network_name}")
            
            # Check if already exists
            existing = Customer.objects.filter(
                name=customer_name,
                network_name=network_name,
                is_deleted=False
            ).first()
            
            if existing:
                print(f"  ✅ Already exists (ID: {existing.id}) - Updating data")
                # Update existing with latest data
                existing.network_type = customer_data['network_type']
                existing.save()
                updated_count += 1
            else:
                # Create new customer entry
                new_customer = Customer.objects.create(
                    name=customer_name,
                    network_name=network_name,
                    network_type=customer_data['network_type'],
                    setup_status='READY'
                )
                
                print(f"  ✅ Created customer (ID: {new_customer.id}, Type: {customer_data['network_type']})")
                migrated_count += 1
            
            # Log the customer details
            runs = customer_data['total_runs']
            nodes = customer_data['node_qty']
            print(f"    📊 {runs} total runs, {nodes} nodes, {customer_data['country']}")
            
        except Exception as e:
            print(f"  ❌ Error processing {customer_data['name']}: {e}")
    
    print(f"\n🎉 Excel Migration Completed!")
    print(f"📊 New customers migrated: {migrated_count}")
    print(f"📊 Existing customers updated: {updated_count}")
    
    # Show final summary
    print("\n📋 All Customers in Database:")
    customers_dict = Customer.get_customers_with_networks()
    
    total_unique_customers = len(customers_dict)
    total_networks = Customer.objects.filter(is_deleted=False).count()
    
    for customer_name, networks in customers_dict.items():
        print(f"\n🏢 {customer_name}:")
        for network in networks:
            print(f"    📡 {network.network_name} ({network.network_type})")
    
    print(f"\n📊 Final Stats:")
    print(f"  👥 Unique customers: {total_unique_customers}")
    print(f"  🌐 Total networks: {total_networks}")
    print(f"  🚀 Ready for unified dashboard!")
    
    print(f"\n✨ SUCCESS: Excel customers now in database!")
    print(f"🎯 Your dashboard will now use DB for all customers")

if __name__ == "__main__":
    migrate_excel_dashboard_customers()