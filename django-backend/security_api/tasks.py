"""
Celery tasks for automated security tool execution
"""
import os
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import subprocess
import json

from .models import (
    ScanSchedule, SecurityTool, Vulnerability, 
    SecurityAlert, ScanResult
)

logger = logging.getLogger(__name__)


@shared_task
def execute_tool_scan(tool_name, target, scan_type, scan_result_id):
    """
    Execute a security tool scan
    This is the main task that routes to specific tool implementations
    
    Args:
        tool_name: Name of the tool (nmap, zap, openvas, etc.)
        target: Target to scan
        scan_type: Type of scan
        scan_result_id: ID of ScanResult to update
    """
    logger.info(f"Starting {tool_name} scan on {target}")
    
    try:
        scan_result = ScanResult.objects.get(id=scan_result_id)
        tool = SecurityTool.objects.get(name=tool_name)
        
        # Update status
        scan_result.status = 'running'
        scan_result.save()
        
        tool.status = 'scanning'
        tool.save()
        
        # Route to specific tool handler
        if tool_name == 'nmap':
            result = run_nmap_scan.delay(target, scan_type)
        elif tool_name == 'zap':
            result = run_zap_scan.delay(target)
        elif tool_name == 'trivy':
            result = run_trivy_scan.delay(target)
        else:
            raise ValueError(f"Unsupported tool: {tool_name}")
        
        logger.info(f"Successfully queued {tool_name} scan")
        return {'status': 'success', 'tool': tool_name, 'target': target}
        
    except Exception as e:
        logger.error(f"Error in execute_tool_scan: {e}", exc_info=True)
        
        if scan_result_id:
            try:
                scan_result = ScanResult.objects.get(id=scan_result_id)
                scan_result.status = 'failed'
                scan_result.end_time = timezone.now()
                scan_result.raw_output = str(e)
                scan_result.save()
            except:
                pass
        
        return {'status': 'error', 'message': str(e)}


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
        else:
            cmd = ['nmap', '-sV', target, '-oX', '-']
        
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
        
        logger.info(f"Nmap scan completed for {target}")
        return {'status': 'success', 'scan_id': scan.id}
        
    except Exception as e:
        logger.error(f"Nmap scan failed: {e}", exc_info=True)
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
        # ZAP API call example (simplified)
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
        
        logger.info(f"ZAP scan completed for {target_url}")
        return {'status': 'success', 'scan_id': scan.id}
        
    except Exception as e:
        logger.error(f"ZAP scan failed: {e}", exc_info=True)
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
        
        # Parse Trivy JSON output
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
            logger.warning("Could not parse Trivy JSON output")
        
        tool.status = 'active'
        tool.last_scan = timezone.now()
        tool.scan_count += 1
        tool.save()
        
        logger.info(f"Trivy scan completed for {image_name}")
        return {'status': 'success', 'scan_id': scan.id}
        
    except Exception as e:
        logger.error(f"Trivy scan failed: {e}", exc_info=True)
        tool.status = 'error'
        tool.error_message = str(e)
        tool.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def trigger_scheduled_scans():
    """
    Celery Beat task that runs every minute to check for scheduled scans
    """
    current_time = timezone.now()
    
    # Check for daily scans
    daily_scans = ScanSchedule.objects.filter(
        frequency='daily',
        is_active=True
    )
    
    for schedule in daily_scans:
        if schedule.last_run is None or \
           (current_time - schedule.last_run).days >= 1:
            logger.info(f"Triggering scheduled scan: {schedule.tool.name} on {schedule.target}")
            
            scan_result = ScanResult.objects.create(
                tool=schedule.tool,
                target=schedule.target,
                scan_type=schedule.scan_type,
                status='queued'
            )
            
            execute_tool_scan.delay(
                schedule.tool.name,
                schedule.target,
                schedule.scan_type,
                scan_result.id
            )
            
            schedule.last_run = current_time
            schedule.next_run = current_time + timedelta(days=1)
            schedule.save()


@shared_task
def trigger_hourly_scans():
    """Trigger hourly scans"""
    current_time = timezone.now()
    
    hourly_scans = ScanSchedule.objects.filter(
        frequency='hourly',
        is_active=True
    )
    
    for schedule in hourly_scans:
        if schedule.last_run is None or \
           (current_time - schedule.last_run).seconds >= 3600:
            
            logger.info(f"Triggering hourly scan: {schedule.tool.name}")
            
            scan_result = ScanResult.objects.create(
                tool=schedule.tool,
                target=schedule.target,
                scan_type=schedule.scan_type,
                status='queued'
            )
            
            execute_tool_scan.delay(
                schedule.tool.name,
                schedule.target,
                schedule.scan_type,
                scan_result.id
            )
            
            schedule.last_run = current_time
            schedule.next_run = current_time + timedelta(hours=1)
            schedule.save()


@shared_task
def aggregate_daily_metrics():
    """Aggregate security metrics daily"""
    from .models import SecurityMetric
    from django.db.models import Count
    
    # Count vulnerabilities by severity
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
    
    logger.info("Daily metrics aggregated")
    return {'status': 'metrics_aggregated'}