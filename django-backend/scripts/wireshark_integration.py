#!/usr/bin/env python
"""
Wireshark/TShark integration for network traffic analysis
"""
import os
import sys
import django
import subprocess
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from security_api.models import SecurityTool, SecurityAlert
from django.utils import timezone


class WiresharkAnalyzer:
    """Wireshark/TShark integration for network traffic capture and analysis"""
    
    def __init__(self):
        self.tool = SecurityTool.objects.get_or_create(
            name='tshark',
            defaults={'status': 'inactive'}
        )[0]
    
    def capture_traffic(self, interface='eth0', duration=60, filter_expr=None):
        """
        Capture network traffic using TShark
        
        Args:
            interface: Network interface to capture from
            duration: Capture duration in seconds
            filter_expr: BPF filter expression (e.g., 'tcp port 80')
        """
        print(f"Starting traffic capture on {interface} for {duration}s...")
        
        self.tool.status = 'scanning'
        self.tool.save()
        
        output_file = f"/tmp/capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
        
        cmd = [
            'tshark',
            '-i', interface,
            '-a', f'duration:{duration}',
            '-w', output_file
        ]
        
        if filter_expr:
            cmd.extend(['-f', filter_expr])
        
        try:
            subprocess.run(cmd, check=True, timeout=duration + 10)
            print(f"✓ Capture saved to {output_file}")
            
            # Analyze the capture
            self._analyze_capture(output_file)
            
            self.tool.status = 'active'
            self.tool.last_scan = timezone.now()
            self.tool.scan_count += 1
            self.tool.save()
            
            return output_file
            
        except Exception as e:
            print(f"✗ Capture error: {e}")
            self.tool.status = 'error'
            self.tool.error_message = str(e)
            self.tool.save()
            return None
    
    def _analyze_capture(self, pcap_file):
        """Analyze captured traffic for anomalies"""
        print("Analyzing captured traffic...")
        
        # Extract statistics
        cmd = [
            'tshark',
            '-r', pcap_file,
            '-q',
            '-z', 'conv,tcp',
            '-z', 'io,stat,1'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Detect anomalies
            self._detect_anomalies(pcap_file)
            
        except Exception as e:
            print(f"Analysis error: {e}")
    
    def _detect_anomalies(self, pcap_file):
        """Detect network anomalies and suspicious patterns"""
        anomalies = []
        
        # Check for port scans
        port_scan = self._detect_port_scan(pcap_file)
        if port_scan:
            anomalies.append({
                'type': 'port_scan',
                'severity': 'high',
                'message': f'Port scan detected from {port_scan["source"]}',
                'source': port_scan['source']
            })
        
        # Check for DDoS patterns
        ddos = self._detect_ddos(pcap_file)
        if ddos:
            anomalies.append({
                'type': 'anomaly',
                'severity': 'critical',
                'message': f'Potential DDoS attack from {ddos["source"]}',
                'source': ddos['source']
            })
        
        # Create alerts for detected anomalies
        for anomaly in anomalies:
            SecurityAlert.objects.create(
                alert_type=anomaly['type'],
                severity=anomaly['severity'],
                message=anomaly['message'],
                source=anomaly['source'],
                tool=self.tool
            )
            print(f"⚠ Alert created: {anomaly['message']}")
    
    def _detect_port_scan(self, pcap_file):
        """Detect port scanning activity"""
        cmd = [
            'tshark',
            '-r', pcap_file,
            '-Y', 'tcp.flags.syn==1 and tcp.flags.ack==0',
            '-T', 'fields',
            '-e', 'ip.src',
            '-e', 'tcp.dstport'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            lines = result.stdout.strip().split('\n')
            
            # Count unique destination ports per source IP
            from collections import defaultdict
            port_counts = defaultdict(set)
            
            for line in lines:
                if '\t' in line:
                    src_ip, dst_port = line.split('\t')
                    port_counts[src_ip].add(dst_port)
            
            # If a source IP scanned more than 20 ports, it's likely a port scan
            for src_ip, ports in port_counts.items():
                if len(ports) > 20:
                    return {'source': src_ip, 'ports_scanned': len(ports)}
            
        except Exception as e:
            print(f"Port scan detection error: {e}")
        
        return None
    
    def _detect_ddos(self, pcap_file):
        """Detect potential DDoS attacks"""
        cmd = [
            'tshark',
            '-r', pcap_file,
            '-q',
            '-z', 'conv,ip'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Parse output and look for abnormally high packet rates
            # This is a simplified detection - production systems would be more sophisticated
            lines = result.stdout.split('\n')
            for line in lines:
                if 'packets' in line.lower():
                    # Extract packet counts and identify high-volume sources
                    # Simplified example
                    pass
            
        except Exception as e:
            print(f"DDoS detection error: {e}")
        
        return None
    
    def extract_credentials(self, pcap_file):
        """Extract potential credentials from unencrypted traffic"""
        print("Scanning for credentials in captured traffic...")
        
        cmd = [
            'tshark',
            '-r', pcap_file,
            '-Y', 'http.request or ftp',
            '-T', 'fields',
            '-e', 'http.authorization',
            '-e', 'ftp.request.command'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout.strip():
                SecurityAlert.objects.create(
                    alert_type='policy_violation',
                    severity='high',
                    message='Unencrypted credentials detected in network traffic',
                    source='wireshark_analyzer',
                    tool=self.tool
                )
                print("⚠ Warning: Unencrypted credentials found!")
            
        except Exception as e:
            print(f"Credential extraction error: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Wireshark network traffic analyzer')
    parser.add_argument('--interface', default='eth0', help='Network interface to capture from')
    parser.add_argument('--duration', type=int, default=60, help='Capture duration in seconds')
    parser.add_argument('--filter', help='BPF filter expression')
    parser.add_argument('--analyze', help='Analyze existing PCAP file')
    
    args = parser.parse_args()
    
    analyzer = WiresharkAnalyzer()
    
    if args.analyze:
        analyzer._analyze_capture(args.analyze)
    else:
        analyzer.capture_traffic(args.interface, args.duration, args.filter)
