from rest_framework import serializers
from .models import (
    SecurityTool, Vulnerability, SecurityAlert, 
    ScanResult, NetworkHost, SecurityMetric
)


class SecurityToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityTool
        fields = '__all__'


class VulnerabilitySerializer(serializers.ModelSerializer):
    tool_name = serializers.CharField(source='tool.get_name_display', read_only=True)
    
    class Meta:
        model = Vulnerability
        fields = '__all__'


class SecurityAlertSerializer(serializers.ModelSerializer):
    tool_name = serializers.CharField(source='tool.get_name_display', read_only=True)
    
    class Meta:
        model = SecurityAlert
        fields = '__all__'


class ScanResultSerializer(serializers.ModelSerializer):
    tool_name = serializers.CharField(source='tool.get_name_display', read_only=True)
    
    class Meta:
        model = ScanResult
        fields = '__all__'


class NetworkHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkHost
        fields = '__all__'


class SecurityMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityMetric
        fields = '__all__'


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_vulnerabilities = serializers.IntegerField()
    critical_vulns = serializers.IntegerField()
    high_vulns = serializers.IntegerField()
    medium_vulns = serializers.IntegerField()
    low_vulns = serializers.IntegerField()
    active_tools = serializers.IntegerField()
    total_alerts = serializers.IntegerField()
    unacknowledged_alerts = serializers.IntegerField()
    hosts_discovered = serializers.IntegerField()
    last_scan_time = serializers.DateTimeField()
