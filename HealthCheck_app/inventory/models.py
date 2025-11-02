"""
Inventory models for HealthCheck application

This module defines the database models for inventory-related data.
"""

from django.db import models
from django.utils import timezone


class InventoryRecord(models.Model):
    """
    Model to store inventory records from remote inventory CSV files
    """
    customer_name = models.CharField(max_length=100, db_index=True)
    hc_id = models.IntegerField()
    node_ip = models.GenericIPAddressField()
    location = models.CharField(max_length=200)
    user_label = models.CharField(max_length=200)
    shelf_type = models.CharField(max_length=100)
    mnemonic = models.CharField(max_length=50)
    report_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['customer_name', 'hc_id', 'mnemonic', 'report_date']
        indexes = [
            models.Index(fields=['customer_name', 'report_date']),
            models.Index(fields=['hc_id']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.hc_id} - {self.mnemonic}"


class InventoryFile(models.Model):
    """
    Model to track inventory files uploaded/processed
    """
    customer_name = models.CharField(max_length=100, db_index=True)
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    records_count = models.IntegerField(default=0)
    processed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['customer_name', 'filename']
    
    def __str__(self):
        return f"{self.customer_name} - {self.filename}"
