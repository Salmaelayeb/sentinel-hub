#!/usr/bin/env python
"""
Security tool integration scripts
Run this to manually trigger scans or integrate with external tools
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from security_api.models import SecurityTool, Vulnerability, SecurityAlert
from django.utils import timezone
import subprocess
import json


def initialize_security_tools():
    """Initialize all security tools in the database"""
    tools = [
        {'name': 'nmap', 'status': 'inactive'},
        {'name': 'zap', 'status': 'inactive'},
        {'name': 'openvas', 'status': 'inactive'},
        {'name': 'trivy', 'status': 'inactive'},
        {'name': 'tshark', 'status': 'inactive'},
        {'name': 'wazuh', 'status': 'inactive'},
    ]
    
    for tool_data in tools:
        tool, created = SecurityTool.objects.get_or_create(
            name=tool_data['name'],
            defaults={'status': tool_data['status']}
        )
        if created:
            print(f"Created tool: {tool.get_name_display()}")
        else:
            print(f"Tool already exists: {tool.get_name_display()}")


def run_nmap_scan_manual(target):
    """Manually run Nmap scan"""
    print(f"Running Nmap scan on {target}...")
    tool = SecurityTool.objects.get(name='nmap')
    tool.status = 'scanning'
    tool.save()
    
    try:
        result = subprocess.run(
            ['nmap', '-sV', target, '-oX', '-'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print("Scan completed!")
        print(result.stdout)
        
        tool.status = 'active'
        tool.last_scan = timezone.now()
        tool.scan_count += 1
        tool.save()
        
        # Create alert
        SecurityAlert.objects.create(
            alert_type='scan_complete',
            severity='low',
            message=f'Nmap scan completed for {target}',
            source='nmap_scanner',
            tool=tool
        )
        
    except Exception as e:
        print(f"Error: {e}")
        tool.status = 'error'
        tool.error_message = str(e)
        tool.save()


def generate_sample_data():
    """Generate sample vulnerabilities and alerts for testing"""
    print("Generating sample data...")
    
    tools = SecurityTool.objects.all()
    
    if not tools:
        print("No tools found. Run initialize_security_tools() first.")
        return
    
    # Sample vulnerabilities
    sample_vulns = [
        {
            'vuln_id': 'CVE-2024-0001',
            'title': 'SQL Injection in Login Form',
            'description': 'Unauthenticated SQL injection vulnerability in login endpoint',
            'severity': 'critical',
            'cvss_score': 9.8,
            'cve_id': 'CVE-2024-0001',
            'affected_asset': '192.168.1.100',
            'port': 443,
            'service': 'https',
            'tool': tools[1]  # ZAP
        },
        {
            'vuln_id': 'CVE-2024-0002',
            'title': 'Outdated OpenSSH Version',
            'description': 'Server running vulnerable OpenSSH version',
            'severity': 'high',
            'cvss_score': 7.5,
            'cve_id': 'CVE-2024-0002',
            'affected_asset': '192.168.1.101',
            'port': 22,
            'service': 'ssh',
            'tool': tools[0]  # Nmap
        },
        {
            'vuln_id': 'TRIVY-2024-0003',
            'title': 'Critical vulnerability in base image',
            'description': 'Container image contains critical vulnerabilities',
            'severity': 'critical',
            'cvss_score': 9.1,
            'affected_asset': 'nginx:latest',
            'tool': tools[3]  # Trivy
        },
    ]
    
    for vuln_data in sample_vulns:
        vuln, created = Vulnerability.objects.get_or_create(
            vuln_id=vuln_data['vuln_id'],
            defaults=vuln_data
        )
        if created:
            print(f"Created vulnerability: {vuln.title}")
    
    # Sample alerts
    sample_alerts = [
        {
            'alert_type': 'intrusion',
            'severity': 'high',
            'message': 'Multiple failed SSH login attempts detected',
            'source': 'wazuh',
            'source_ip': '203.0.113.42',
            'tool': tools[5]  # Wazuh
        },
        {
            'alert_type': 'vulnerability',
            'severity': 'critical',
            'message': 'New critical vulnerability discovered',
            'source': 'openvas',
            'tool': tools[2]  # OpenVAS
        },
    ]
    
    for alert_data in sample_alerts:
        alert = SecurityAlert.objects.create(**alert_data)
        print(f"Created alert: {alert.message}")
    
    print("Sample data generated successfully!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Security tool integration scripts')
    parser.add_argument('command', choices=['init', 'nmap', 'sample'], help='Command to execute')
    parser.add_argument('--target', help='Target for scan (IP or hostname)')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        initialize_security_tools()
    elif args.command == 'nmap':
        if not args.target:
            print("Error: --target is required for nmap command")
            sys.exit(1)
        run_nmap_scan_manual(args.target)
    elif args.command == 'sample':
        generate_sample_data()
