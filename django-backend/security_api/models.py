from django.db import models
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class SecurityTool(models.Model):
    """Model for tracking security tool status"""
    TOOL_CHOICES = [
        ('nmap', 'Nmap'),
        ('zap', 'OWASP ZAP'),
        ('openvas', 'OpenVAS'),
        ('trivy', 'Trivy'),
        ('tshark', 'TShark'),
        ('wazuh', 'Wazuh'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('scanning', 'Scanning'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=50, choices=TOOL_CHOICES, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_scan = models.DateTimeField(null=True, blank=True)
    scan_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.status}"


class Vulnerability(models.Model):
    """Model for storing vulnerability findings"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Info'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    vuln_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    cvss_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    cve_id = models.CharField(max_length=50, blank=True, null=True)
    affected_asset = models.CharField(max_length=255)
    port = models.IntegerField(null=True, blank=True)
    service = models.CharField(max_length=100, blank=True, null=True)
    tool = models.ForeignKey(SecurityTool, on_delete=models.CASCADE, related_name='vulnerabilities')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    discovered_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    remediation = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-discovered_at', 'severity']
        indexes = [
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['discovered_at']),
        ]
    
    def __str__(self):
        return f"{self.vuln_id} - {self.title} ({self.severity})"


class SecurityAlert(models.Model):
    """Model for real-time security alerts"""
    ALERT_TYPE_CHOICES = [
        ('intrusion', 'Intrusion Attempt'),
        ('malware', 'Malware Detected'),
        ('vulnerability', 'New Vulnerability'),
        ('anomaly', 'Anomalous Behavior'),
        ('policy_violation', 'Policy Violation'),
        ('scan_complete', 'Scan Complete'),
    ]
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    source = models.CharField(max_length=100)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    destination_ip = models.GenericIPAddressField(null=True, blank=True)
    tool = models.ForeignKey(SecurityTool, on_delete=models.CASCADE, related_name='alerts')
    timestamp = models.DateTimeField(default=timezone.now)
    acknowledged = models.BooleanField(default=False)
    details = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['severity', 'acknowledged']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} - {self.severity} - {self.timestamp}"


class ScanResult(models.Model):
    """Model for storing complete scan results"""
    tool = models.ForeignKey(SecurityTool, on_delete=models.CASCADE, related_name='scan_results')
    scan_type = models.CharField(max_length=100)
    target = models.CharField(max_length=255)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='running')
    raw_output = models.TextField()
    parsed_data = models.JSONField(null=True, blank=True)
    vulnerabilities_found = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.tool.name} - {self.target} - {self.start_time}"


class NetworkHost(models.Model):
    """Model for tracking discovered network hosts"""
    ip_address = models.GenericIPAddressField(unique=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    os_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='up')
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(auto_now=True)
    open_ports = models.JSONField(default=list)
    services = models.JSONField(default=list)
    
    class Meta:
        ordering = ['ip_address']
    
    def __str__(self):
        return f"{self.ip_address} - {self.hostname or 'Unknown'}"


class SecurityMetric(models.Model):
    """Model for storing aggregated security metrics"""
    metric_type = models.CharField(max_length=50)
    metric_name = models.CharField(max_length=100)
    value = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
        ]
  
    def __str__(self):
        return f"{self.metric_name}: {self.value} - {self.timestamp}"

class ScanSchedule(models.Model):
    """Model for scheduling recurring scans"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('hourly', 'Every Hour'),
    ]
    
    tool = models.ForeignKey(SecurityTool, on_delete=models.CASCADE)
    target = models.CharField(max_length=255)
    scan_type = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tool.name} - {self.target} ({self.frequency})"