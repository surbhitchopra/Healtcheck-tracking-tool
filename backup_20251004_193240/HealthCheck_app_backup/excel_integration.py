"""
Excel Data Integration Utility
Integrates Excel tracker files with the customer/network management system
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from django.conf import settings

class ExcelDataReader:
    """Utility class to read customer and network data from Excel files"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent
        self.excel_directories = [
            self.base_dir,
            self.base_dir / "Script",
            self.base_dir / "scripts",
            self.base_dir / "healthcheck",  # if it exists
        ]
        
    def get_excel_files(self) -> List[Path]:
        """Get all Excel tracker files from project directories"""
        excel_files = []
        
        for directory in self.excel_directories:
            if directory.exists():
                # Look for Excel files with health check patterns
                patterns = [
                    "*HC_Issues_Tracker*.xlsx",
                    "*Issues_Tracker*.xlsx", 
                    "*HC_Tracker*.xlsx",
                    "*health*check*.xlsx",
                ]
                
                for pattern in patterns:
                    excel_files.extend(directory.glob(pattern))
        
        return list(set(excel_files))  # Remove duplicates
    
    def parse_customer_network_from_filename(self, filename: str) -> Dict[str, str]:
        """Parse customer name and network type from Excel filename"""
        # Convert to uppercase for pattern matching
        filename_upper = filename.upper()
        
        # Remove common suffixes
        clean_name = filename_upper.replace('_HC_ISSUES_TRACKER.XLSX', '')
        clean_name = clean_name.replace('_ISSUES_TRACKER.XLSX', '')
        clean_name = clean_name.replace('_HC_TRACKER.XLSX', '')
        clean_name = clean_name.replace('.XLSX', '')
        
        # Split by underscores
        parts = clean_name.split('_')
        
        # Common customer name patterns
        customer_name = None
        network_type = None
        
        # Look for known customer patterns
        if 'BSNL' in parts:
            customer_name = 'BSNL'
            # Look for zone information
            for part in parts:
                if any(zone in part for zone in ['NORTH', 'SOUTH', 'EAST', 'WEST']):
                    network_type = f"{part} Zone"
                    break
            
            # Look for technology type
            for part in parts:
                if part in ['DWDM', 'OTN', 'SDH', 'IP']:
                    if network_type:
                        network_type = f"{network_type} {part}"
                    else:
                        network_type = part
                    break
        
        elif any(telecom in parts for telecom in ['AIRTEL', 'JIO', 'IDEA', 'VODAFONE']):
            for part in parts:
                if part in ['AIRTEL', 'JIO', 'IDEA', 'VODAFONE']:
                    customer_name = part
                    break
            
            # Look for circle or region
            for part in parts:
                if any(region in part for region in ['DELHI', 'MUMBAI', 'BANGALORE', 'CHENNAI', 'KOLKATA']):
                    network_type = f"{part} Circle"
                    break
        
        else:
            # Try to extract customer name from first meaningful part
            for part in parts:
                if len(part) > 2 and part not in ['HC', 'ISSUES', 'TRACKER', 'REPORTS']:
                    customer_name = part.title()
                    break
        
        # Default values if not found
        if not customer_name:
            customer_name = parts[0].title() if parts else "Unknown"
        
        if not network_type:
            network_type = "HealthCheck"
        
        return {
            'customer_name': customer_name,
            'network_type': network_type,
            'filename': filename,
            'source': 'excel'
        }
    
    def get_excel_customers_networks(self) -> Dict[str, List[Dict]]:
        """Get all customer-network combinations from Health_Check_Tracker_1.xlsx"""
        customers_networks = {}
        
        try:
            import pandas as pd
            from pathlib import Path
            
            # Read the main Excel tracker file
            excel_path = self.base_dir / "Script" / "Health_Check_Tracker_1.xlsx"
            
            if not excel_path.exists():
                print(f"Warning: Excel file not found at {excel_path}")
                return customers_networks
            
            # Read from Summary sheet
            df = pd.read_excel(excel_path, sheet_name='Summary')
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Process each row to extract customer-network combinations
            for index, row in df.iterrows():
                try:
                    customer_name = str(row.get('Customer', '')).strip()
                    network_name = str(row.get('Network', '')).strip()
                    
                    if not customer_name or customer_name == 'nan' or not network_name or network_name == 'nan':
                        continue
                    
                    # Group by customer name
                    if customer_name not in customers_networks:
                        customers_networks[customer_name] = []
                    
                    # Add network information
                    network_info = {
                        'customer_name': customer_name,
                        'network_type': network_name,  # Use actual network name from Excel
                        'filename': 'Health_Check_Tracker_1.xlsx',
                        'source': 'excel',
                        'file_path': str(excel_path),
                        'file_size': excel_path.stat().st_size,
                        'modified_date': excel_path.stat().st_mtime,
                        'country': str(row.get('Country', 'Unknown')).strip(),
                        'node_qty': row.get('Node Qty', 0),
                        'ne_type': str(row.get('NE Type', '1830 PSS')).strip(),
                        'gtac': str(row.get('gTAC', 'Classic')).strip()
                    }
                    
                    customers_networks[customer_name].append(network_info)
                    
                except Exception as row_error:
                    print(f"Warning: Error processing row {index}: {row_error}")
                    continue
            
            print(f"✅ Loaded {len(customers_networks)} customers from Excel file")
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
        
        return customers_networks
    
    def get_unified_customer_choices(self) -> List[Tuple[str, str]]:
        """Get unified customer choices for form dropdown"""
        excel_customers = self.get_excel_customers_networks()
        choices = []
        
        # Add Excel customers with clean names
        for customer_name, networks in excel_customers.items():
            # Create a unique identifier that includes source
            customer_id = f"excel_{customer_name.lower().replace(' ', '_')}"
            # Clean display name - just show customer name
            display_name = customer_name
            choices.append((customer_id, display_name))
        
        return sorted(choices, key=lambda x: x[1])
    
    def get_networks_for_customer(self, customer_identifier: str) -> List[Dict]:
        """Get networks for a specific customer (works with both DB and Excel)"""
        if customer_identifier.startswith('excel_'):
            # Extract actual customer name from identifier
            customer_name = customer_identifier.replace('excel_', '').replace('_', ' ').title()
            excel_customers = self.get_excel_customers_networks()
            
            # Find matching customer (case insensitive)
            for excel_customer, networks in excel_customers.items():
                if excel_customer.lower() == customer_name.lower():
                    return networks
        
        return []
    
    def get_customer_summary(self) -> Dict[str, int]:
        """Get summary statistics for Excel data"""
        excel_customers = self.get_excel_customers_networks()
        
        total_customers = len(excel_customers)
        total_networks = sum(len(networks) for networks in excel_customers.values())
        
        return {
            'total_excel_customers': total_customers,
            'total_excel_networks': total_networks,
            'excel_customers_data': excel_customers
        }


def get_excel_integration():
    """Factory function to get Excel integration instance"""
    return ExcelDataReader()


def integrate_excel_with_database_choices(db_choices: List[Tuple], include_excel: bool = True) -> List[Tuple]:
    """Integrate Excel data with database choices for forms"""
    if not include_excel:
        return db_choices
    
    excel_reader = get_excel_integration()
    excel_choices = excel_reader.get_unified_customer_choices()
    
    # Combine choices with clear separation
    combined_choices = list(db_choices)
    
    if excel_choices:
        # Add separator if we have both DB and Excel data
        if db_choices and len(db_choices) > 1:  # More than just the empty option
            combined_choices.append(('separator_excel', '--- Excel Customers ---'))
        
        combined_choices.extend(excel_choices)
    
    return combined_choices


def get_customer_networks_unified(customer_identifier: str) -> Tuple[List[Dict], str]:
    """Get networks for customer from both database and Excel sources"""
    networks = []
    source_type = 'database'
    
    if customer_identifier.startswith('excel_'):
        # Excel source
        excel_reader = get_excel_integration()
        networks = excel_reader.get_networks_for_customer(customer_identifier)
        source_type = 'excel'
    else:
        # Database source - would need to be implemented in views.py
        # This is a placeholder for database integration
        pass
    
    return networks, source_type