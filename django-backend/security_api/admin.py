from django.contrib import admin
from .models import (
    SecurityTool, Vulnerability, SecurityAlert,
    ScanResult, NetworkHost, SecurityMetric ,ScanSchedule
)


@admin.register(SecurityTool)
class SecurityToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'last_scan', 'scan_count']
    list_filter = ['status', 'name']
    search_fields = ['name']
    readonly_fields = ('last_scan', 'scan_count', 'updated_at')


@admin.register(Vulnerability)
class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ['vuln_id', 'title', 'severity', 'status', 'affected_asset', 'discovered_at']
    list_filter = ['severity', 'status', 'tool']
    search_fields = ['title', 'description', 'cve_id', 'affected_asset']
    date_hierarchy = 'discovered_at'
    readonly_fields = ('discovered_at', 'updated_at')


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'severity', 'source', 'timestamp', 'acknowledged']
    list_filter = ['alert_type', 'severity', 'acknowledged', 'tool']
    search_fields = ['message', 'source']
    date_hierarchy = 'timestamp'
    actions = ['mark_acknowledged']
    def mark_acknowledged(self, request, queryset):
        queryset.update(acknowledged=True)
    mark_acknowledged.short_description = "Mark selected alerts as acknowledged"


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = ['tool', 'scan_type', 'target', 'start_time', 'status', 'vulnerabilities_found']
    list_filter = ['tool', 'status', 'scan_type']
    search_fields = ['target']
    date_hierarchy = 'start_time'
    readonly_fields = ('start_time', 'end_time', 'raw_output')


@admin.register(NetworkHost)
class NetworkHostAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'hostname', 'os_type', 'status', 'last_seen']
    list_filter = ['status', 'os_type']
    search_fields = ['ip_address', 'hostname']


@admin.register(SecurityMetric)
class SecurityMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'metric_name', 'value', 'timestamp']
    list_filter = ['metric_type', 'metric_name']
    date_hierarchy = 'timestamp'

@admin.register(ScanSchedule)
class ScanScheduleAdmin(admin.ModelAdmin):
    list_display = ('tool', 'target', 'frequency', 'is_active', 'last_run', 'next_run')
    list_filter = ('frequency', 'is_active', 'tool')
    search_fields = ('target',)