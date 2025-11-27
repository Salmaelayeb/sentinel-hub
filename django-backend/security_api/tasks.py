"""
Celery tasks for automated security tool execution
"""
from celery import shared_task
from django.utils import timezone
import subprocess
import json
from .models import SecurityTool, Vulnerability, SecurityAlert, ScanResult


@shared_task
def run_nmap_scan(target, scan_type='basic'):
    """Execute Nmap scan"""
    tool = SecurityTool.objects.get(name='nmap')
    tool.status = 'scanning'
    tool.save()
    
    try:
        # Nmap command example
        if scan_type == 'basic':
            cmd = ['nmap', '-sV', '-O', target, '-oX', '-']
        elif scan_type == 'aggressive':
            cmd = ['nmap', '-A', target, '-oX', '-']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Save scan result
        scan = ScanResult.objects.create(
            tool=tool,
            scan_type=scan_type,
            target=target,
            end_time=timezone.now(),
            status='completed',
            raw_output=result.stdout
        )
        
        tool.status = 'active'
        tool.last_scan = timezone.now()
        tool.scan_count += 1
        tool.save()
        
        return {'status': 'success', 'scan_id': scan.id}
        
    except Exception as e:
        tool.status = 'error'
        tool.error_message = str(e)
        tool.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def run_zap_scan(target_url):
    """Execute OWASP ZAP scan"""
    tool = SecurityTool.objects.get(name='zap')
    tool.status = 'scanning'
    tool.save()
    
    try:
        # ZAP API call example
        # This is a simplified version, actual implementation would use ZAP API
        cmd = ['zap-cli', 'quick-scan', '--self-contained', target_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        scan = ScanResult.objects.create(
            tool=tool,
            scan_type='web_vulnerability',
            target=target_url,
            end_time=timezone.now(),
            status='completed',
            raw_output=result.stdout
        )
        
        tool.status = 'active'
        tool.last_scan = timezone.now()
        tool.scan_count += 1
        tool.save()
        
        return {'status': 'success', 'scan_id': scan.id}
        
    except Exception as e:
        tool.status = 'error'
        tool.error_message = str(e)
        tool.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def run_trivy_scan(image_name):
    """Execute Trivy container scan"""
    tool = SecurityTool.objects.get(name='trivy')
    tool.status = 'scanning'
    tool.save()
    
    try:
        cmd = ['trivy', 'image', '--format', 'json', image_name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        scan = ScanResult.objects.create(
            tool=tool,
            scan_type='container_scan',
            target=image_name,
            end_time=timezone.now(),
            status='completed',
            raw_output=result.stdout
        )
        
        # Parse Trivy JSON output and create vulnerabilities
        try:
            trivy_data = json.loads(result.stdout)
            vuln_count = 0
            for result_item in trivy_data.get('Results', []):
                for vuln in result_item.get('Vulnerabilities', []):
                    Vulnerability.objects.create(
                        vuln_id=f"TRIVY-{vuln.get('VulnerabilityID')}",
                        title=vuln.get('Title', 'Unknown'),
                        description=vuln.get('Description', ''),
                        severity=vuln.get('Severity', 'unknown').lower(),
                        cvss_score=vuln.get('CVSS', {}).get('nvd', {}).get('V3Score'),
                        cve_id=vuln.get('VulnerabilityID'),
                        affected_asset=image_name,
                        tool=tool
                    )
                    vuln_count += 1
            
            scan.vulnerabilities_found = vuln_count
            scan.save()
            
        except json.JSONDecodeError:
            pass
        
        tool.status = 'active'
        tool.last_scan = timezone.now()
        tool.scan_count += 1
        tool.save()
        
        return {'status': 'success', 'scan_id': scan.id}
        
    except Exception as e:
        tool.status = 'error'
        tool.error_message = str(e)
        tool.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def aggregate_daily_metrics():
    """Aggregate security metrics daily"""
    from .models import SecurityMetric
    
    # Count vulnerabilities by severity
    from django.db.models import Count
    vuln_counts = Vulnerability.objects.filter(status='open').values('severity').annotate(count=Count('id'))
    
    for item in vuln_counts:
        SecurityMetric.objects.create(
            metric_type='vulnerability',
            metric_name=f'open_{item["severity"]}_vulnerabilities',
            value=item['count']
        )
    
    # Count total alerts
    alert_count = SecurityAlert.objects.filter(acknowledged=False).count()
    SecurityMetric.objects.create(
        metric_type='alert',
        metric_name='unacknowledged_alerts',
        value=alert_count
    )
    
    return {'status': 'metrics_aggregated'}
