from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from .models import (
    SecurityTool, Vulnerability, SecurityAlert, 
    ScanResult, NetworkHost, SecurityMetric ,ScanSchedule
)
from .serializers import (
    SecurityToolSerializer, VulnerabilitySerializer,
    SecurityAlertSerializer, ScanResultSerializer,
    NetworkHostSerializer, SecurityMetricSerializer,
    DashboardStatsSerializer ,ScanScheduleSerializer
)
from .tasks import execute_tool_scan 

class ScanScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing scan schedules"""
    queryset = ScanSchedule.objects.all()
    serializer_class = ScanScheduleSerializer 
    filterset_fields = ['tool', 'is_active', 'frequency']
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Enable/disable a schedule"""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        return Response({
            'message': f"Schedule {'activated' if schedule.is_active else 'deactivated'}",
            'is_active': schedule.is_active
        })
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Trigger a scheduled scan immediately"""
        schedule = self.get_object()
        
        scan_result = ScanResult.objects.create(
            tool=schedule.tool,
            target=schedule.target,
            scan_type=schedule.scan_type,
            status='pending'
        )
        
        execute_tool_scan.delay(
            schedule.tool.name,
            schedule.target,
            schedule.scan_type,
            scan_result.id
        )
        
        return Response({
            'message': 'Scan triggered immediately',
            'scan_result_id': scan_result.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def active_schedules(self, request):
        """Get all active schedules"""
        schedules = ScanSchedule.objects.filter(is_active=True)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
class SecurityToolViewSet(viewsets.ModelViewSet):
    """API endpoint for security tools"""
    queryset = SecurityTool.objects.all()
    serializer_class = SecurityToolSerializer
    
    @action(detail=True, methods=['post'])
    def start_scan(self, request, pk=None):
        """Trigger a scan for a specific tool"""
        tool = self.get_object()
        target = request.data.get('target', '')
        scan_type = request.data.get('scan_type', 'basic')
        tool.status = 'scanning'
        tool.save()
        
        if not target:
            return Response(
                {'error': 'Target is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
         # Create ScanResult record
        scan_result = ScanResult.objects.create(
            tool=tool,
            target=target,
            scan_type=scan_type,
            status='queued',
            start_time=timezone.now())
    
        tool.status = 'scanning'
        tool.save()
    
    # Trigger Celery task
        execute_tool_scan.delay(tool.name, target, scan_type, scan_result.id)
    
        return Response({
            'status': 'scan_started',
            'tool': tool.name,
            'scan_result_id': scan_result.id,
            'message': f'{tool.get_name_display()} scan initiated on {target}'
    })
    
    @action(detail=True, methods=['post'])
    def stop_scan(self, request, pk=None):
        """Stop a running scan"""
        tool = self.get_object()
        tool.status = 'active'
        tool.save()
        
        return Response({
            'status': 'scan_stopped',
            'tool': tool.name
        })


class VulnerabilityViewSet(viewsets.ModelViewSet):
    """API endpoint for vulnerabilities"""
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_fields = ['severity', 'status', 'tool']
    search_fields = ['title', 'description', 'cve_id', 'affected_asset']
    
    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Get vulnerability counts by severity"""
        counts = Vulnerability.objects.filter(status='open').values('severity').annotate(count=Count('id'))
        return Response(counts)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent vulnerabilities (last 24 hours)"""
        last_24h = timezone.now() - timezone.timedelta(hours=24)
        recent_vulns = Vulnerability.objects.filter(discovered_at__gte=last_24h)
        serializer = self.get_serializer(recent_vulns, many=True)
        return Response(serializer.data)


class SecurityAlertViewSet(viewsets.ModelViewSet):
    """API endpoint for security alerts"""
    queryset = SecurityAlert.objects.all()
    serializer_class = SecurityAlertSerializer
    filterset_fields = ['severity', 'alert_type', 'acknowledged', 'tool']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.acknowledged = True
        alert.save()
        return Response({'status': 'acknowledged'})
    
    @action(detail=False, methods=['get'])
    def unacknowledged(self, request):
        """Get all unacknowledged alerts"""
        alerts = SecurityAlert.objects.filter(acknowledged=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class ScanResultViewSet(viewsets.ModelViewSet):
    """API endpoint for scan results"""
    queryset = ScanResult.objects.all()
    serializer_class = ScanResultSerializer
    filterset_fields = ['tool', 'status', 'scan_type']


class NetworkHostViewSet(viewsets.ModelViewSet):
    """API endpoint for network hosts"""
    queryset = NetworkHost.objects.all()
    serializer_class = NetworkHostSerializer
    filterset_fields = ['status']
    search_fields = ['ip_address', 'hostname']


class SecurityMetricViewSet(viewsets.ModelViewSet):
    """API endpoint for security metrics"""
    queryset = SecurityMetric.objects.all()
    serializer_class = SecurityMetricSerializer
    filterset_fields = ['metric_type', 'metric_name']


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard statistics"""
    
    def list(self, request):
        """Get comprehensive dashboard statistics"""
        # Vulnerability counts
        vuln_counts = Vulnerability.objects.filter(status='open').values('severity').annotate(count=Count('id'))
        vuln_dict = {item['severity']: item['count'] for item in vuln_counts}
        
        # Tool status
        active_tools = SecurityTool.objects.filter(status='active').count()
        
        # Alert counts
        total_alerts = SecurityAlert.objects.count()
        unack_alerts = SecurityAlert.objects.filter(acknowledged=False).count()
        
        # Host count
        hosts = NetworkHost.objects.count()
        
        # Last scan time
        last_scan = SecurityTool.objects.filter(last_scan__isnull=False).order_by('-last_scan').first()
        
        stats = {
            'total_vulnerabilities': Vulnerability.objects.filter(status='open').count(),
            'critical_vulns': vuln_dict.get('critical', 0),
            'high_vulns': vuln_dict.get('high', 0),
            'medium_vulns': vuln_dict.get('medium', 0),
            'low_vulns': vuln_dict.get('low', 0),
            'active_tools': active_tools,
            'total_alerts': total_alerts,
            'unacknowledged_alerts': unack_alerts,
            'hosts_discovered': hosts,
            'last_scan_time': last_scan.last_scan if last_scan else None
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
