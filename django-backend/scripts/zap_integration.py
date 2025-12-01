#!/usr/bin/env python
"""
OWASP ZAP integration for web application security scanning
"""
import os
import sys
import django
import requests
import time
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from security_api.models import SecurityTool, Vulnerability, ScanResult, SecurityAlert
from django.utils import timezone


class ZAPScanner:
    """OWASP ZAP integration for web security scanning"""
    
    def __init__(self, zap_api_url='http://localhost:8080', api_key=None):
        self.zap_url = zap_api_url
        self.api_key = api_key
        self.tool = SecurityTool.objects.get_or_create(name='zap')[0]
    
    def scan_website(self, target_url, scan_type='quick'):
        """
        Perform web application security scan
        
        Args:
            target_url: URL to scan (e.g., http://example.com)
            scan_type: Type of scan - quick, full, api
        """
        print(f"Starting ZAP {scan_type} scan on {target_url}...")
        
        self.tool.status = 'scanning'
        self.tool.save()
        
        try:
            # Start ZAP session
            self._access_url(target_url)
            
            # Spider the site
            print("Spidering target...")
            spider_scan_id = self._spider(target_url)
            self._wait_for_spider(spider_scan_id)
            
            # Active scan
            if scan_type in ['full', 'api']:
                print("Running active scan...")
                scan_id = self._active_scan(target_url)
                self._wait_for_scan(scan_id)
            
            # Get alerts
            print("Retrieving vulnerabilities...")
            alerts = self._get_alerts(target_url)
            
            # Save scan result
            scan_result = ScanResult.objects.create(
                tool=self.tool,
                scan_type=scan_type,
                target=target_url,
                start_time=timezone.now(),
                end_time=timezone.now(),
                status='completed',
                raw_output=str(alerts),
                vulnerabilities_found=len(alerts)
            )
            
            # Process alerts and create vulnerabilities
            vuln_count = self._process_alerts(alerts, target_url)
            
            # Update tool status
            self.tool.status = 'active'
            self.tool.last_scan = timezone.now()
            self.tool.scan_count += 1
            self.tool.save()
            
            # Create completion alert
            SecurityAlert.objects.create(
                alert_type='scan_complete',
                severity='low',
                message=f'ZAP {scan_type} scan completed for {target_url}. Found {vuln_count} vulnerabilities.',
                source='zap_scanner',
                tool=self.tool
            )
            
            print(f"✓ Scan completed. Found {vuln_count} vulnerabilities.")
            return scan_result
            
        except Exception as e:
            print(f"✗ Scan error: {e}")
            self.tool.status = 'error'
            self.tool.error_message = str(e)
            self.tool.save()
            return None
    
    def _make_request(self, endpoint, params=None):
        """Make request to ZAP API"""
        if params is None:
            params = {}
        
        if self.api_key:
            params['apikey'] = self.api_key
        
        url = f"{self.zap_url}{endpoint}"
        response = requests.get(url, params=params)
        return response.json()
    
    def _access_url(self, url):
        """Access target URL through ZAP"""
        self._make_request('/JSON/core/action/accessUrl/', {'url': url})
    
    def _spider(self, url):
        """Start spider scan"""
        result = self._make_request('/JSON/spider/action/scan/', {'url': url})
        return result.get('scan')
    
    def _wait_for_spider(self, scan_id, timeout=300):
        """Wait for spider to complete"""
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Spider scan timeout")
            
            result = self._make_request('/JSON/spider/view/status/', {'scanId': scan_id})
            status = int(result.get('status', 0))
            
            if status >= 100:
                print("Spider completed")
                break
            
            print(f"Spider progress: {status}%")
            time.sleep(5)
    
    def _active_scan(self, url):
        """Start active scan"""
        result = self._make_request('/JSON/ascan/action/scan/', {'url': url})
        return result.get('scan')
    
    def _wait_for_scan(self, scan_id, timeout=600):
        """Wait for active scan to complete"""
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Active scan timeout")
            
            result = self._make_request('/JSON/ascan/view/status/', {'scanId': scan_id})
            status = int(result.get('status', 0))
            
            if status >= 100:
                print("Active scan completed")
                break
            
            print(f"Scan progress: {status}%")
            time.sleep(10)
    
    def _get_alerts(self, base_url):
        """Get alerts from ZAP"""
        result = self._make_request('/JSON/core/view/alerts/', {'baseurl': base_url})
        return result.get('alerts', [])
    
    def _process_alerts(self, alerts, target_url):
        """Process ZAP alerts and create vulnerability records"""
        severity_map = {
            '3': 'critical',
            '2': 'high',
            '1': 'medium',
            '0': 'low'
        }
        
        vuln_count = 0
        
        for alert in alerts:
            alert_id = alert.get('alert', 'Unknown')
            risk = alert.get('risk', '0')
            severity = severity_map.get(risk, 'low')
            
            vuln_id = f"ZAP-{alert.get('pluginId', 'UNKNOWN')}-{hash(target_url + alert_id) % 10000}"
            
            # Create or update vulnerability
            vuln, created = Vulnerability.objects.get_or_create(
                vuln_id=vuln_id,
                defaults={
                    'title': alert.get('alert', 'Unknown vulnerability'),
                    'description': alert.get('description', ''),
                    'severity': severity,
                    'affected_asset': target_url,
                    'tool': self.tool,
                    'remediation': alert.get('solution', '')
                }
            )
            
            if created:
                vuln_count += 1
                print(f"  - {alert.get('alert')} ({severity})")
        
        return vuln_count


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OWASP ZAP web scanner')
    parser.add_argument('target', help='Target URL (e.g., http://example.com)')
    parser.add_argument('--scan-type', choices=['quick', 'full', 'api'], 
                       default='quick', help='Type of scan to perform')
    parser.add_argument('--zap-url', default='http://localhost:8080', 
                       help='ZAP API URL')
    parser.add_argument('--api-key', help='ZAP API key')
    
    args = parser.parse_args()
    
    scanner = ZAPScanner(args.zap_url, args.api_key)
    scanner.scan_website(args.target, args.scan_type)
