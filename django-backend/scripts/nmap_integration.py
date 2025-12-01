#!/usr/bin/env python
"""
Nmap integration for network scanning and host discovery
"""
import os
import sys
import django
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from security_api.models import SecurityTool, Vulnerability, NetworkHost, ScanResult, SecurityAlert
from django.utils import timezone


class NmapScanner:
    """Nmap integration for network scanning"""
    
    def __init__(self):
        self.tool = SecurityTool.objects.get_or_create(name='nmap')[0]
    
    def scan_network(self, target, scan_type='basic'):
        """
        Perform network scan using Nmap
        
        Args:
            target: IP address, range, or network (e.g., "192.168.1.0/24")
            scan_type: Type of scan - basic, aggressive, stealth, vuln
        """
        print(f"Starting Nmap {scan_type} scan on {target}...")
        
        self.tool.status = 'scanning'
        self.tool.save()
        
        # Define scan commands
        scan_commands = {
            'basic': ['nmap', '-sV', '-O', target, '-oX', '-'],
            'aggressive': ['nmap', '-A', '-T4', target, '-oX', '-'],
            'stealth': ['nmap', '-sS', '-sV', target, '-oX', '-'],
            'vuln': ['nmap', '-sV', '--script=vuln', target, '-oX', '-']
        }
        
        try:
            # Execute Nmap scan
            result = subprocess.run(
                scan_commands.get(scan_type, scan_commands['basic']),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                raise Exception(f"Nmap scan failed: {result.stderr}")
            
            # Save raw scan result
            scan_result = ScanResult.objects.create(
                tool=self.tool,
                scan_type=scan_type,
                target=target,
                start_time=timezone.now(),
                end_time=timezone.now(),
                status='completed',
                raw_output=result.stdout
            )
            
            # Parse XML output
            vulnerabilities_found = self._parse_nmap_output(result.stdout, target)
            scan_result.vulnerabilities_found = vulnerabilities_found
            scan_result.save()
            
            # Update tool status
            self.tool.status = 'active'
            self.tool.last_scan = timezone.now()
            self.tool.scan_count += 1
            self.tool.save()
            
            # Create completion alert
            SecurityAlert.objects.create(
                alert_type='scan_complete',
                severity='low',
                message=f'Nmap {scan_type} scan completed for {target}. Found {vulnerabilities_found} issues.',
                source='nmap_scanner',
                tool=self.tool
            )
            
            print(f"✓ Scan completed. Found {vulnerabilities_found} vulnerabilities.")
            return scan_result
            
        except subprocess.TimeoutExpired:
            self.tool.status = 'error'
            self.tool.error_message = 'Scan timeout'
            self.tool.save()
            print("✗ Scan timed out")
            return None
            
        except Exception as e:
            self.tool.status = 'error'
            self.tool.error_message = str(e)
            self.tool.save()
            print(f"✗ Scan error: {e}")
            return None
    
    def _parse_nmap_output(self, xml_output, target):
        """Parse Nmap XML output and create vulnerability records"""
        vuln_count = 0
        
        try:
            root = ET.fromstring(xml_output)
            
            # Parse hosts
            for host in root.findall('host'):
                # Get host information
                address = host.find('address')
                if address is not None:
                    ip_address = address.get('addr')
                    
                    # Get hostname
                    hostname = None
                    hostnames = host.find('hostnames')
                    if hostnames is not None:
                        hostname_elem = hostnames.find('hostname')
                        if hostname_elem is not None:
                            hostname = hostname_elem.get('name')
                    
                    # Get OS information
                    os_type = None
                    os_match = host.find('.//osmatch')
                    if os_match is not None:
                        os_type = os_match.get('name')
                    
                    # Get status
                    status_elem = host.find('status')
                    status = status_elem.get('state') if status_elem is not None else 'unknown'
                    
                    # Create or update network host
                    network_host, created = NetworkHost.objects.update_or_create(
                        ip_address=ip_address,
                        defaults={
                            'hostname': hostname,
                            'os_type': os_type,
                            'status': status
                        }
                    )
                    
                    # Parse ports and services
                    ports_data = []
                    services_data = []
                    
                    ports = host.find('ports')
                    if ports is not None:
                        for port in ports.findall('port'):
                            port_id = port.get('portid')
                            protocol = port.get('protocol')
                            
                            state = port.find('state')
                            port_state = state.get('state') if state is not None else 'unknown'
                            
                            service = port.find('service')
                            if service is not None:
                                service_name = service.get('name', 'unknown')
                                service_version = service.get('version', '')
                                
                                ports_data.append({
                                    'port': port_id,
                                    'protocol': protocol,
                                    'state': port_state
                                })
                                
                                services_data.append({
                                    'port': port_id,
                                    'service': service_name,
                                    'version': service_version
                                })
                                
                                # Check for potential vulnerabilities
                                if port_state == 'open':
                                    # Check for known vulnerable services
                                    if self._is_vulnerable_service(service_name, service_version):
                                        vuln_id = f"NMAP-{ip_address}-{port_id}"
                                        
                                        Vulnerability.objects.get_or_create(
                                            vuln_id=vuln_id,
                                            defaults={
                                                'title': f'Potentially vulnerable service on port {port_id}',
                                                'description': f'Service {service_name} {service_version} detected on {ip_address}:{port_id}',
                                                'severity': 'medium',
                                                'affected_asset': ip_address,
                                                'port': int(port_id),
                                                'service': service_name,
                                                'tool': self.tool
                                            }
                                        )
                                        vuln_count += 1
                    
                    # Update host with ports and services
                    network_host.open_ports = ports_data
                    network_host.services = services_data
                    network_host.save()
            
            # Parse script results (vulnerability scan)
            for script in root.findall('.//script'):
                script_id = script.get('id')
                script_output = script.get('output', '')
                
                if 'vuln' in script_id or 'CVE' in script_output:
                    # Extract CVE information
                    import re
                    cve_pattern = r'CVE-\d{4}-\d{4,7}'
                    cves = re.findall(cve_pattern, script_output)
                    
                    for cve in cves:
                        vuln_id = f"NMAP-{cve}-{target}"
                        
                        Vulnerability.objects.get_or_create(
                            vuln_id=vuln_id,
                            defaults={
                                'title': f'Vulnerability detected: {cve}',
                                'description': script_output[:500],
                                'severity': 'high',
                                'cve_id': cve,
                                'affected_asset': target,
                                'tool': self.tool
                            }
                        )
                        vuln_count += 1
        
        except ET.ParseError as e:
            print(f"Error parsing Nmap XML: {e}")
        
        return vuln_count
    
    def _is_vulnerable_service(self, service_name, version):
        """Check if a service version is known to be vulnerable"""
        vulnerable_services = {
            'ssh': ['OpenSSH 7.4', 'OpenSSH 7.3'],
            'ftp': ['vsftpd 2.3.4'],
            'http': ['Apache 2.4.49', 'nginx 1.10.0'],
            'smb': ['Samba 3.6.3', 'Samba 4.5.0']
        }
        
        if service_name.lower() in vulnerable_services:
            for vuln_version in vulnerable_services[service_name.lower()]:
                if vuln_version in version:
                    return True
        
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Nmap network scanner')
    parser.add_argument('target', help='Target IP, range, or network (e.g., 192.168.1.0/24)')
    parser.add_argument('--scan-type', choices=['basic', 'aggressive', 'stealth', 'vuln'], 
                       default='basic', help='Type of scan to perform')
    
    args = parser.parse_args()
    
    scanner = NmapScanner()
    scanner.scan_network(args.target, args.scan_type)
