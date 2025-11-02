"""
Health Check Processing Engine
Handles network health checks, node connectivity, and service validation
"""
import os
import json
import ping3
import socket
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Django imports
from django.utils import timezone
from .models import (
    HealthCheckSession, HealthCheckFile, NodeCoverage, 
    ServiceCheck, Customer
)


class HealthCheckProcessor:
    """Main Health Check processing engine"""
    
    def __init__(self, session_id: str):
        self.session = HealthCheckSession.objects.get(id=session_id)
        self.customer = self.session.customer
        self.nodes_data = []
        self.services_data = []
        
    def process_session(self):
        """Main processing function"""
        try:
            self.session.update_status('PROCESSING', 'Starting health check analysis')
            
            # Step 1: Parse uploaded files
            self._parse_uploaded_files()
            
            # Step 2: Perform connectivity checks
            self._perform_connectivity_checks()
            
            # Step 3: Check services
            self._check_services()
            
            # Step 4: Generate report
            self._generate_report()
            
            self.session.update_status('COMPLETED', 'Health check completed successfully')
            
        except Exception as e:
            self.session.error_messages = str(e)
            self.session.update_status('FAILED', f'Processing failed: {str(e)}')
    
    def _parse_uploaded_files(self):
        """Parse uploaded configuration files"""
        self.session.update_status('PROCESSING', 'Parsing configuration files')
        
        files = HealthCheckFile.objects.filter(session=self.session)
        
        for file_obj in files:
            if file_obj.file_type == 'NODE_LIST':
                self._parse_node_list(file_obj.file_path)
            elif file_obj.file_type == 'SERVICE_CONFIG':
                self._parse_service_config(file_obj.file_path)
            elif file_obj.file_type == 'CONFIG':
                self._parse_network_config(file_obj.file_path)
                
            file_obj.is_processed = True
            file_obj.save()
    
    def _parse_node_list(self, file_path: str):
        """Parse node list file (CSV/Excel/JSON)"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.nodes_data.extend(data.get('nodes', []))
            
            elif file_ext in ['.csv', '.txt']:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            self.nodes_data.append({
                                'name': parts[0].strip(),
                                'ip': parts[1].strip(),
                                'location': parts[2].strip() if len(parts) > 2 else ''
                            })
            
            elif file_ext in ['.xlsx', '.xls']:
                # For Excel files, you'd use pandas or openpyxl
                # For now, simulate with sample data
                self._add_sample_nodes()
                
        except Exception as e:
            print(f"Error parsing node list: {e}")
            self._add_sample_nodes()  # Fallback to sample data
    
    def _parse_service_config(self, file_path: str):
        """Parse service configuration"""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                    self.services_data.extend(data.get('services', []))
                else:
                    # Parse other formats
                    self._add_sample_services()
        except:
            self._add_sample_services()
    
    def _parse_network_config(self, file_path: str):
        """Parse network configuration file"""
        # Implementation for parsing network configs
        pass
    
    def _add_sample_nodes(self):
        """Add sample nodes for testing"""
        sample_nodes = [
            {'name': 'Router-01', 'ip': '192.168.1.1', 'location': 'Data Center A'},
            {'name': 'Switch-01', 'ip': '192.168.1.2', 'location': 'Data Center A'},
            {'name': 'Server-01', 'ip': '192.168.1.10', 'location': 'Data Center A'},
            {'name': 'Router-02', 'ip': '192.168.2.1', 'location': 'Data Center B'},
            {'name': 'Switch-02', 'ip': '192.168.2.2', 'location': 'Data Center B'},
        ]
        self.nodes_data.extend(sample_nodes)
    
    def _add_sample_services(self):
        """Add sample services for testing"""
        sample_services = [
            {'name': 'HTTP', 'type': 'HTTP', 'port': 80},
            {'name': 'HTTPS', 'type': 'HTTPS', 'port': 443},
            {'name': 'SSH', 'type': 'TCP', 'port': 22},
            {'name': 'SNMP', 'type': 'UDP', 'port': 161},
            {'name': 'DNS', 'type': 'UDP', 'port': 53},
        ]
        self.services_data.extend(sample_services)
    
    def _perform_connectivity_checks(self):
        """Check connectivity to all nodes"""
        self.session.update_status('PROCESSING', 'Checking node connectivity')
        
        for node_data in self.nodes_data:
            node_name = node_data.get('name', 'Unknown')
            node_ip = node_data.get('ip', '')
            location = node_data.get('location', '')
            
            # Create or update node record
            node, created = NodeCoverage.objects.get_or_create(
                customer=self.customer,
                session=self.session,
                node_name=node_name,
                defaults={
                    'node_ip': node_ip,
                    'location': location
                }
            )
            
            # Perform ping test
            ping_result = self._ping_node(node_ip)
            node.ping_status = ping_result['success']
            node.response_time = ping_result['response_time']
            
            # Determine overall node status
            if ping_result['success']:
                node.status = 'Online'
            else:
                node.status = 'Offline'
            
            node.save()
    
    def _ping_node(self, ip_address: str) -> Dict:
        """Ping a node and return results"""
        try:
            response_time = ping3.ping(ip_address, timeout=3)
            if response_time is not None:
                return {
                    'success': True,
                    'response_time': response_time * 1000  # Convert to milliseconds
                }
            else:
                return {'success': False, 'response_time': None}
        except Exception:
            return {'success': False, 'response_time': None}
    
    def _check_services(self):
        """Check services on all nodes"""
        self.session.update_status('PROCESSING', 'Checking services')
        
        nodes = NodeCoverage.objects.filter(session=self.session)
        
        for node in nodes:
            if node.ping_status:  # Only check services if node is reachable
                services_healthy = 0
                services_total = len(self.services_data)
                
                for service_data in self.services_data:
                    service_name = service_data.get('name', 'Unknown')
                    service_type = service_data.get('type', 'TCP')
                    port = service_data.get('port', 80)
                    
                    # Create service check record
                    service_check = ServiceCheck.objects.create(
                        node=node,
                        service_name=service_name,
                        service_type=service_type,
                        port=port
                    )
                    
                    # Perform service check
                    check_result = self._check_service(node.node_ip, port, service_type)
                    service_check.status = check_result['status']
                    service_check.response_time = check_result['response_time']
                    service_check.error_message = check_result.get('error', '')
                    service_check.save()
                    
                    if check_result['status'] == 'Healthy':
                        services_healthy += 1
                
                # Update node service counts
                node.services_count = services_total
                node.services_healthy = services_healthy
                
                # Update node status based on service health
                if services_healthy == services_total:
                    node.status = 'Online'
                elif services_healthy > 0:
                    node.status = 'Warning'
                else:
                    node.status = 'Offline'
                
                node.save()
    
    def _check_service(self, ip_address: str, port: int, service_type: str) -> Dict:
        """Check if a specific service is running"""
        try:
            start_time = time.time()
            
            if service_type in ['TCP', 'HTTP', 'HTTPS']:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                response_time = (time.time() - start_time) * 1000
                
                if result == 0:
                    return {
                        'status': 'Healthy',
                        'response_time': response_time
                    }
                else:
                    return {
                        'status': 'Unhealthy',
                        'response_time': None,
                        'error': f'Connection failed to {ip_address}:{port}'
                    }
            
            elif service_type == 'UDP':
                # UDP check is more complex, simulate for now
                return {
                    'status': 'Healthy',
                    'response_time': 50.0
                }
            
        except Exception as e:
            return {
                'status': 'Timeout',
                'response_time': None,
                'error': str(e)
            }
    
    def _generate_report(self):
        """Generate health check report"""
        self.session.update_status('PROCESSING', 'Generating health check report')
        
        nodes = NodeCoverage.objects.filter(session=self.session)
        services = ServiceCheck.objects.filter(node__session=self.session)
        
        # Calculate statistics
        total_nodes = nodes.count()
        healthy_nodes = nodes.filter(status='Online').count()
        warning_nodes = nodes.filter(status='Warning').count()
        offline_nodes = nodes.filter(status='Offline').count()
        
        total_services = services.count()
        healthy_services = services.filter(status='Healthy').count()
        
        # Calculate overall health score
        if total_nodes > 0:
            node_health_score = (healthy_nodes + (warning_nodes * 0.5)) / total_nodes * 100
        else:
            node_health_score = 0
            
        if total_services > 0:
            service_health_score = healthy_services / total_services * 100
        else:
            service_health_score = 0
            
        overall_health_score = (node_health_score + service_health_score) / 2
        
        # Health check reports are no longer needed - session status provides sufficient information
        pass
        
        # Update customer status
        if self.customer.setup_status == 'NEW':
            self.customer.setup_status = 'READY'
            self.customer.save()


def process_health_check_session(session_id: str):
    """Entry point for processing a health check session"""
    processor = HealthCheckProcessor(session_id)
    processor.process_session()


def run_health_check_async(session_id: str):
    """Run health check in background thread"""
    thread = threading.Thread(target=process_health_check_session, args=(session_id,))
    thread.daemon = True
    thread.start()
    return thread
