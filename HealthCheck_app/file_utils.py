"""
Customer File Management Utilities
Enhanced file management functions for Health Check application
"""

import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Customer, HealthCheckFile


def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file for duplicate detection"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None


def find_duplicate_files(customer, file_type=None):
    """Find duplicate files for a customer based on file hash"""
    from collections import defaultdict
    
    # Get all files for customer
    files_query = HealthCheckFile.objects.filter(customer=customer)
    if file_type:
        files_query = files_query.filter(file_type=file_type)
    
    files = files_query.order_by('uploaded_at')
    
    # Group files by their hash
    hash_groups = defaultdict(list)
    
    for file_obj in files:
        if file_obj.file_path and Path(file_obj.file_path).exists():
            file_hash = calculate_file_hash(file_obj.file_path)
            if file_hash:
                hash_groups[file_hash].append(file_obj)
    
    # Return groups that have duplicates
    duplicates = {}
    for file_hash, file_list in hash_groups.items():
        if len(file_list) > 1:
            duplicates[file_hash] = file_list
    
    return duplicates


def cleanup_old_files(customer, file_type=None, days_old=30):
    """Clean up old files older than specified days"""
    cutoff_date = timezone.now() - timedelta(days=days_old)
    
    files_query = HealthCheckFile.objects.filter(
        customer=customer,
        uploaded_at__lt=cutoff_date
    )
    
    if file_type:
        files_query = files_query.filter(file_type=file_type)
    
    old_files = files_query.order_by('uploaded_at')
    
    cleaned_up = []
    for file_obj in old_files:
        try:
            # Don't auto-delete TRACKER_GENERATED files - they're important
            if file_obj.file_type == 'TRACKER_GENERATED':
                continue
                
            if file_obj.file_path and Path(file_obj.file_path).exists():
                Path(file_obj.file_path).unlink()
                print(f"🗑️ Deleted old file: {file_obj.stored_filename}")
            
            file_obj.delete()
            cleaned_up.append(file_obj.stored_filename)
        except Exception as e:
            print(f"⚠️ Error cleaning up {file_obj.stored_filename}: {e}")
    
    return cleaned_up


def verify_file_integrity(customer):
    """Verify that all database file records have corresponding physical files"""
    files = HealthCheckFile.objects.filter(customer=customer)
    
    missing_files = []
    orphaned_files = []
    
    for file_obj in files:
        if file_obj.file_path:
            if not Path(file_obj.file_path).exists():
                missing_files.append({
                    'id': file_obj.id,
                    'filename': file_obj.stored_filename,
                    'path': file_obj.file_path,
                    'type': file_obj.file_type
                })
    
    return {
        'missing_files': missing_files,
        'missing_count': len(missing_files)
    }


def get_directory_size(directory_path):
    """Calculate total size of a directory and its subdirectories"""
    total_size = 0
    file_count = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
                    file_count += 1
    except Exception as e:
        print(f"Error calculating directory size for {directory_path}: {e}")
    
    return {
        'size_bytes': total_size,
        'size_mb': round(total_size / (1024 * 1024), 2),
        'file_count': file_count
    }


def get_customer_directory_stats(customer):
    """Get comprehensive statistics about a customer's file directory"""
    from ..views import SCRIPT_DIR
    
    customer_name = customer.name.replace(" ", "_").replace("/", "_").replace(".", "_")
    customer_base_dir = SCRIPT_DIR / "customer_files" / customer_name
    
    stats = {
        'customer_name': customer.name,
        'network_name': customer.network_name,
        'directory_exists': customer_base_dir.exists(),
        'total_size': 0,
        'total_files': 0,
        'folders': {}
    }
    
    if not customer_base_dir.exists():
        return stats
    
    # Check if it's network-specific
    if customer.network_name and customer.network_name.strip():
        network_name = customer.network_name.replace(" ", "_").replace("/", "_").replace(".", "_")
        customer_dir = customer_base_dir / network_name
    else:
        customer_dir = customer_base_dir
    
    if customer_dir.exists():
        overall_stats = get_directory_size(customer_dir)
        stats['total_size'] = overall_stats['size_mb']
        stats['total_files'] = overall_stats['file_count']
        
        # Get stats for each subfolder
        folder_names = ['host_files', 'tec_reports', 'generated_trackers', 'old_trackers', 'inventory_files']
        
        for folder_name in folder_names:
            folder_path = customer_dir / folder_name
            if folder_path.exists():
                folder_stats = get_directory_size(folder_path)
                stats['folders'][folder_name] = folder_stats
            else:
                stats['folders'][folder_name] = {'size_bytes': 0, 'size_mb': 0, 'file_count': 0}
    
    return stats


def archive_old_customer_files(customer, archive_days=90):
    """Archive old files to a separate archive directory"""
    from ..views import SCRIPT_DIR
    
    customer_name = customer.name.replace(" ", "_").replace("/", "_").replace(".", "_")
    customer_dir = SCRIPT_DIR / "customer_files" / customer_name
    archive_dir = SCRIPT_DIR / "customer_files" / "_archived" / customer_name
    
    if not customer_dir.exists():
        return {'archived_files': [], 'error': 'Customer directory not found'}
    
    # Create archive directory
    os.makedirs(archive_dir, exist_ok=True)
    
    cutoff_date = timezone.now() - timedelta(days=archive_days)
    archived_files = []
    
    try:
        # Find old files
        for root, dirs, files in os.walk(customer_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    # Check file modification time
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
                    
                    if mod_time < cutoff_date:
                        # Create corresponding archive path
                        rel_path = file_path.relative_to(customer_dir)
                        archive_path = archive_dir / rel_path
                        
                        # Create directory structure in archive
                        os.makedirs(archive_path.parent, exist_ok=True)
                        
                        # Move file to archive
                        shutil.move(str(file_path), str(archive_path))
                        archived_files.append({
                            'original_path': str(file_path),
                            'archive_path': str(archive_path),
                            'filename': file,
                            'mod_time': mod_time.isoformat()
                        })
                        
                except Exception as e:
                    print(f"Error archiving {file_path}: {e}")
                    continue
        
        return {
            'archived_files': archived_files,
            'archive_count': len(archived_files),
            'archive_directory': str(archive_dir)
        }
        
    except Exception as e:
        return {'archived_files': [], 'error': str(e)}


def cleanup_empty_directories(base_directory):
    """Remove empty directories recursively"""
    removed_dirs = []
    
    try:
        for root, dirs, files in os.walk(base_directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    # Try to remove directory if it's empty
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        removed_dirs.append(dir_path)
                        print(f"🗑️ Removed empty directory: {dir_path}")
                except OSError:
                    # Directory not empty, skip
                    continue
    except Exception as e:
        print(f"Error during cleanup: {e}")
    
    return removed_dirs


def generate_file_management_report(customer=None):
    """Generate a comprehensive file management report"""
    from ..views import SCRIPT_DIR
    
    report = {
        'generated_at': timezone.now().isoformat(),
        'customers': [],
        'summary': {
            'total_customers': 0,
            'total_files': 0,
            'total_size_mb': 0,
            'total_directories': 0
        }
    }
    
    if customer:
        customers = [customer]
    else:
        customers = Customer.objects.filter(is_deleted=False)
    
    for customer in customers:
        customer_stats = get_customer_directory_stats(customer)
        integrity_check = verify_file_integrity(customer)
        
        customer_report = {
            'customer_info': {
                'id': customer.id,
                'name': customer.name,
                'network_name': customer.network_name,
                'network_type': customer.network_type,
                'setup_status': customer.setup_status,
                'created_at': customer.created_at.isoformat()
            },
            'directory_stats': customer_stats,
            'integrity_check': integrity_check,
            'database_files': HealthCheckFile.objects.filter(customer=customer).count()
        }
        
        report['customers'].append(customer_report)
        
        # Update summary
        report['summary']['total_files'] += customer_stats['total_files']
        report['summary']['total_size_mb'] += customer_stats['total_size']
    
    report['summary']['total_customers'] = len(customers)
    report['summary']['total_directories'] = len([c for c in report['customers'] if c['directory_stats']['directory_exists']])
    
    return report
