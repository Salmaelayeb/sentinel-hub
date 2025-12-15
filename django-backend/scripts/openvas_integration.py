#!/usr/bin/env python
"""
OpenVAS integration for comprehensive vulnerability scanning
"""
import os
import sys
import django
from gvm.connections import UnixSocketConnection, TLSConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from security_api.models import SecurityTool, Vulnerability, ScanResult, SecurityAlert
from django.utils import timezone


class OpenVASScanner:
    """OpenVAS integration for vulnerability scanning"""
    
    def __init__(self, host='localhost', port=9390, username='admin', password='admin'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.tool = SecurityTool.objects.get_or_create(name='openvas')[0]
    
    def scan_target(self, target, scan_config='Full and fast'):
        """
        Perform OpenVAS vulnerability scan
        
        Args:
            target: IP address or hostname to scan
            scan_config: Scan configuration name
        """
        print(f"Starting OpenVAS scan on {target}...")
        
        self.tool.status = 'scanning'
        self.tool.save()
        
        try:
            # Connect to OpenVAS
            connection = TLSConnection(hostname=self.host, port=self.port)
            transform = EtreeTransform()
            
            with Gmp(connection, transform=transform) as gmp:
                # Authenticate
                gmp.authenticate(self.username, self.password)
                
                 # Create target
                target_name = f"target_{int(time.time())}"
                target_response = gmp.create_target(
                    name=target_name,
                    hosts=target
                )

                target_id = target_response.get('id')
                if not target_id:
                    raise Exception("Failed to create target")

                # Get scan config
                configs = gmp.get_scan_configs()
                config_id = None
                for config in configs.findall('config'):
                    if config.find('name').text == scan_config:
                        config_id = config.get('id')
                        break

                if not config_id:
                    config_id = configs.find('config').get('id')

                # Get scanner
                scanners = gmp.get_scanners()
                scanner_id = scanners.find('scanner').get('id')

                # Create task
                task_response = gmp.create_task(
                    name=task_name,
                    config_id=config_id,
                    target_id=target_id,
                    scanner_id=scanner_id
                )

                                
                # Start the task
                gmp.start_task(task_id)
                
                # Wait for completion
                print("Waiting for scan to complete...")
                self._wait_for_completion(gmp, task_id)
                
                # Get results
                print("Retrieving results...")
                results = gmp.get_results(task_id=task_id)
                
                # Process results
                vuln_count = self._process_results(results, target)
                
                # Save scan result
                scan_result = ScanResult.objects.create(
                    tool=self.tool,
                    scan_type='openvas_full',
                    target=target,
                    start_time=timezone.now(),
                    end_time=timezone.now(),
                    status='completed',
                    raw_output=str(results),
                    vulnerabilities_found=vuln_count
                )
                
                # Update tool status
                self.tool.status = 'active'
                self.tool.last_scan = timezone.now()
                self.tool.scan_count += 1
                self.tool.save()
                
                # Create completion alert
                SecurityAlert.objects.create(
                    alert_type='scan_complete',
                    severity='low',
                    message=f'OpenVAS scan completed for {target}. Found {vuln_count} vulnerabilities.',
                    source='openvas_scanner',
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
    
    def _wait_for_completion(self, gmp, task_id, timeout=3600):
        """Wait for task to complete"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Scan timeout")
            
            task = gmp.get_task(task_id)
            status = task.find('.//status').text
            progress = task.find('.//progress').text
            
            print(f"Status: {status} - Progress: {progress}%")
            
            if status == 'Done':
                break
            elif status in ['Stopped', 'Interrupted']:
                raise Exception(f"Scan {status}")
            
            time.sleep(30)
    
    def _process_results(self, results, target):
        """Process OpenVAS results and create vulnerability records"""
        severity_map = {
            'High': 'high',
            'Medium': 'medium',
            'Low': 'low',
            'Log': 'info'
        }
        
        vuln_count = 0
        
        for result in results.findall('.//result'):
            threat = result.find('threat').text
            
            if threat in ['High', 'Medium', 'Low']:
                name = result.find('name').text
                description = result.find('description').text or ''
                nvt = result.find('nvt')
                cvss = result.find('severity').text
                
                # Get CVE if available
                cve_id = None
                refs = nvt.findall('.//ref')
                for ref in refs:
                    if ref.get('type') == 'cve':
                        cve_id = ref.get('id')
                        break
                
                vuln_id = f"OPENVAS-{nvt.get('oid')}-{hash(target) % 10000}"
                
                # Create vulnerability
                vuln, created = Vulnerability.objects.get_or_create(
                    vuln_id=vuln_id,
                    defaults={
                        'title': name,
                        'description': description[:1000],
                        'severity': severity_map.get(threat, 'low'),
                        'cvss_score': float(cvss) if cvss and cvss != '' else None,
                        'cve_id': cve_id,
                        'affected_asset': target,
                        'tool': self.tool
                    }
                )
                
                if created:
                    vuln_count += 1
                    print(f"  - {name} ({threat})")
        
        return vuln_count


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenVAS vulnerability scanner')
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('--host', default='localhost', help='OpenVAS host')
    parser.add_argument('--port', type=int, default=9390, help='OpenVAS port')
    parser.add_argument('--username', default='admin', help='OpenVAS username')
    parser.add_argument('--password', default='admin', help='OpenVAS password')
    
    args = parser.parse_args()
    
    scanner = OpenVASScanner(args.host, args.port, args.username, args.password)
    scanner.scan_target(args.target)
