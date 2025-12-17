#!/usr/bin/env python
"""
Wazuh integration for SIEM and intrusion detection
Fetches real alerts from Wazuh API - NO mock data
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from security_api.models import SecurityTool, SecurityAlert, Vulnerability
from django.utils import timezone


class WazuhClient:
    """Wazuh API client for fetching real security alerts"""
    
    def __init__(self):
        self.api_url = os.environ.get('WAZUH_API_URL', 'https://localhost:55000')
        self.username = os.environ.get('WAZUH_API_USER', 'wazuh-wui')
        self.password = os.environ.get('WAZUH_API_PASSWORD', '')
        self.verify_ssl = os.environ.get('WAZUH_VERIFY_SSL', 'false').lower() == 'true'
        self.token = None
        self.tool = SecurityTool.objects.get_or_create(
            name='wazuh',
            defaults={'status': 'inactive'}
        )[0]
    
    def authenticate(self):
        """Authenticate with Wazuh API and get JWT token"""
        try:
            response = requests.post(
                f"{self.api_url}/security/user/authenticate",
                auth=(self.username, self.password),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('data', {}).get('token')
                print("✓ Authenticated with Wazuh API")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            self.tool.status = 'error'
            self.tool.error_message = str(e)
            self.tool.save()
            return False
    
    def _make_request(self, endpoint, method='GET', params=None):
        """Make authenticated request to Wazuh API"""
        if not self.token:
            if not self.authenticate():
                return None
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(
                    url, 
                    headers=headers, 
                    params=params,
                    verify=self.verify_ssl,
                    timeout=60
                )
            else:
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=params,
                    verify=self.verify_ssl,
                    timeout=60
                )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expired, re-authenticate
                self.token = None
                return self._make_request(endpoint, method, params)
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def get_alerts(self, limit=100, level_min=7):
        """
        Fetch recent alerts from Wazuh
        
        Args:
            limit: Maximum number of alerts to fetch
            level_min: Minimum alert level (1-15, 7+ for significant alerts)
        """
        print(f"Fetching alerts from Wazuh (min level: {level_min})...")
        
        # Get alerts from the last 24 hours
        params = {
            'limit': limit,
            'sort': '-timestamp',
            'q': f'rule.level>={level_min}'
        }
        
        result = self._make_request('/alerts', params=params)
        
        if result and 'data' in result:
            alerts = result['data'].get('affected_items', [])
            print(f"✓ Retrieved {len(alerts)} alerts from Wazuh")
            return alerts
        
        return []
    
    def get_agents(self):
        """Get list of Wazuh agents"""
        result = self._make_request('/agents')
        
        if result and 'data' in result:
            return result['data'].get('affected_items', [])
        
        return []
    
    def get_agent_vulnerabilities(self, agent_id):
        """Get vulnerabilities detected on a specific agent"""
        result = self._make_request(f'/vulnerability/{agent_id}')
        
        if result and 'data' in result:
            return result['data'].get('affected_items', [])
        
        return []
    
    def sync_alerts(self, hours_back=24):
        """
        Sync Wazuh alerts to Django SecurityAlert model
        Fetches REAL alerts only - no mock data
        """
        print(f"Syncing Wazuh alerts from last {hours_back} hours...")
        
        self.tool.status = 'scanning'
        self.tool.save()
        
        try:
            alerts = self.get_alerts(limit=500, level_min=5)
            
            if not alerts:
                print("No alerts retrieved from Wazuh")
                self.tool.status = 'active'
                self.tool.save()
                return 0
            
            created_count = 0
            
            for alert in alerts:
                # Map Wazuh severity levels to our model
                wazuh_level = alert.get('rule', {}).get('level', 0)
                severity = self._map_severity(wazuh_level)
                
                # Map Wazuh groups to alert types
                groups = alert.get('rule', {}).get('groups', [])
                alert_type = self._map_alert_type(groups)
                
                # Get source information
                agent = alert.get('agent', {})
                source = agent.get('name', 'unknown')
                source_ip = alert.get('data', {}).get('srcip') or agent.get('ip')
                dest_ip = alert.get('data', {}).get('dstip')
                
                # Unique identifier based on Wazuh alert ID
                wazuh_id = alert.get('id', str(hash(json.dumps(alert, default=str))))
                
                # Check if alert already exists
                existing = SecurityAlert.objects.filter(
                    details__wazuh_id=wazuh_id
                ).exists()
                
                if not existing:
                    SecurityAlert.objects.create(
                        alert_type=alert_type,
                        severity=severity,
                        message=alert.get('rule', {}).get('description', 'Wazuh alert'),
                        source=source,
                        source_ip=source_ip,
                        destination_ip=dest_ip,
                        tool=self.tool,
                        timestamp=self._parse_timestamp(alert.get('timestamp')),
                        details={
                            'wazuh_id': wazuh_id,
                            'rule_id': alert.get('rule', {}).get('id'),
                            'rule_level': wazuh_level,
                            'groups': groups,
                            'full_log': alert.get('full_log', '')[:1000]
                        }
                    )
                    created_count += 1
            
            # Update tool status
            self.tool.status = 'active'
            self.tool.last_scan = timezone.now()
            self.tool.scan_count += 1
            self.tool.save()
            
            print(f"✓ Created {created_count} new alerts in database")
            return created_count
            
        except Exception as e:
            print(f"✗ Sync error: {e}")
            self.tool.status = 'error'
            self.tool.error_message = str(e)
            self.tool.save()
            return 0
    
    def sync_vulnerabilities(self):
        """
        Sync vulnerabilities from all Wazuh agents
        REAL data only from Wazuh vulnerability detector
        """
        print("Syncing vulnerabilities from Wazuh agents...")
        
        agents = self.get_agents()
        vuln_count = 0
        
        for agent in agents:
            agent_id = agent.get('id')
            agent_name = agent.get('name', 'unknown')
            
            vulns = self.get_agent_vulnerabilities(agent_id)
            
            for vuln in vulns:
                cve_id = vuln.get('cve')
                if not cve_id:
                    continue
                
                vuln_id = f"WAZUH-{cve_id}-{agent_id}"
                
                # Map CVSS to severity
                cvss = vuln.get('cvss2_score') or vuln.get('cvss3_score')
                severity = self._cvss_to_severity(cvss)
                
                Vulnerability.objects.get_or_create(
                    vuln_id=vuln_id,
                    defaults={
                        'title': vuln.get('title', cve_id),
                        'description': vuln.get('rationale', '')[:1000],
                        'severity': severity,
                        'cvss_score': cvss,
                        'cve_id': cve_id,
                        'affected_asset': f"{agent_name} ({agent.get('ip', 'unknown')})",
                        'tool': self.tool,
                        'service': vuln.get('name'),
                        'remediation': vuln.get('reference', '')
                    }
                )
                vuln_count += 1
        
        print(f"✓ Synced {vuln_count} vulnerabilities from Wazuh")
        return vuln_count
    
    def _map_severity(self, level):
        """Map Wazuh level (1-15) to our severity levels"""
        if level >= 12:
            return 'critical'
        elif level >= 9:
            return 'high'
        elif level >= 6:
            return 'medium'
        else:
            return 'low'
    
    def _map_alert_type(self, groups):
        """Map Wazuh groups to alert types"""
        groups_lower = [g.lower() for g in groups]
        
        if any(g in groups_lower for g in ['intrusion_detection', 'ids', 'attack']):
            return 'intrusion'
        elif any(g in groups_lower for g in ['malware', 'virus', 'trojan']):
            return 'malware'
        elif any(g in groups_lower for g in ['vulnerability', 'cve']):
            return 'vulnerability'
        elif any(g in groups_lower for g in ['policy', 'pci_dss', 'gdpr', 'hipaa']):
            return 'policy_violation'
        elif any(g in groups_lower for g in ['anomaly', 'suspicious']):
            return 'anomaly'
        else:
            return 'intrusion'
    
    def _cvss_to_severity(self, cvss):
        """Convert CVSS score to severity level"""
        if cvss is None:
            return 'medium'
        
        cvss = float(cvss)
        if cvss >= 9.0:
            return 'critical'
        elif cvss >= 7.0:
            return 'high'
        elif cvss >= 4.0:
            return 'medium'
        else:
            return 'low'
    
    def _parse_timestamp(self, timestamp_str):
        """Parse Wazuh timestamp to datetime"""
        if not timestamp_str:
            return timezone.now()
        
        try:
            # Wazuh format: 2024-01-15T10:30:00.000+0000
            dt = datetime.fromisoformat(timestamp_str.replace('+0000', '+00:00'))
            return dt
        except:
            return timezone.now()
    
    def check_connection(self):
        """Verify connection to Wazuh API"""
        print("Testing Wazuh API connection...")
        
        if self.authenticate():
            result = self._make_request('/manager/status')
            if result:
                print(f"✓ Wazuh Manager status: {result.get('data', {})}")
                self.tool.status = 'active'
                self.tool.save()
                return True
        
        print("✗ Failed to connect to Wazuh")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Wazuh SIEM integration')
    parser.add_argument('--sync-alerts', action='store_true', help='Sync alerts from Wazuh')
    parser.add_argument('--sync-vulns', action='store_true', help='Sync vulnerabilities from Wazuh')
    parser.add_argument('--check', action='store_true', help='Check Wazuh connection')
    parser.add_argument('--hours', type=int, default=24, help='Hours of data to sync')
    
    args = parser.parse_args()
    
    client = WazuhClient()
    
    if args.check:
        client.check_connection()
    elif args.sync_alerts:
        client.sync_alerts(hours_back=args.hours)
    elif args.sync_vulns:
        client.sync_vulnerabilities()
    else:
        # Default: sync both
        client.sync_alerts()
        client.sync_vulnerabilities()
