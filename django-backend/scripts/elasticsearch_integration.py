#!/usr/bin/env python
"""
Elasticsearch integration for centralized log storage and analysis
"""
import os
import sys
import django
from datetime import datetime
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from elasticsearch import Elasticsearch
from django.conf import settings


class ElasticsearchClient:
    """Client for interacting with Elasticsearch"""
    
    def __init__(self):
        es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost:9200')
        self.es = Elasticsearch([f'http://{es_host}'])
        self.index_prefix = 'security-'
    
    def create_indices(self):
        """Create Elasticsearch indices for different data types"""
        indices = {
            'vulnerabilities': {
                'mappings': {
                    'properties': {
                        'vuln_id': {'type': 'keyword'},
                        'title': {'type': 'text'},
                        'description': {'type': 'text'},
                        'severity': {'type': 'keyword'},
                        'cvss_score': {'type': 'float'},
                        'cve_id': {'type': 'keyword'},
                        'affected_asset': {'type': 'keyword'},
                        'tool': {'type': 'keyword'},
                        'discovered_at': {'type': 'date'},
                        'status': {'type': 'keyword'}
                    }
                }
            },
            'alerts': {
                'mappings': {
                    'properties': {
                        'alert_type': {'type': 'keyword'},
                        'severity': {'type': 'keyword'},
                        'message': {'type': 'text'},
                        'source': {'type': 'keyword'},
                        'source_ip': {'type': 'ip'},
                        'destination_ip': {'type': 'ip'},
                        'tool': {'type': 'keyword'},
                        'timestamp': {'type': 'date'}
                    }
                }
            },
            'scan_results': {
                'mappings': {
                    'properties': {
                        'tool': {'type': 'keyword'},
                        'scan_type': {'type': 'keyword'},
                        'target': {'type': 'keyword'},
                        'start_time': {'type': 'date'},
                        'end_time': {'type': 'date'},
                        'status': {'type': 'keyword'},
                        'vulnerabilities_found': {'type': 'integer'},
                        'raw_output': {'type': 'text'}
                    }
                }
            },
            'network_traffic': {
                'mappings': {
                    'properties': {
                        'timestamp': {'type': 'date'},
                        'source_ip': {'type': 'ip'},
                        'destination_ip': {'type': 'ip'},
                        'source_port': {'type': 'integer'},
                        'destination_port': {'type': 'integer'},
                        'protocol': {'type': 'keyword'},
                        'packet_size': {'type': 'integer'},
                        'flags': {'type': 'keyword'}
                    }
                }
            }
        }
        
        for index_name, index_body in indices.items():
            full_index = f'{self.index_prefix}{index_name}'
            if not self.es.indices.exists(index=full_index):
                self.es.indices.create(index=full_index, body=index_body)
                print(f'Created index: {full_index}')
            else:
                print(f'Index already exists: {full_index}')
    
    def index_vulnerability(self, vulnerability):
        """Index a vulnerability to Elasticsearch"""
        doc = {
            'vuln_id': vulnerability.vuln_id,
            'title': vulnerability.title,
            'description': vulnerability.description,
            'severity': vulnerability.severity,
            'cvss_score': float(vulnerability.cvss_score) if vulnerability.cvss_score else None,
            'cve_id': vulnerability.cve_id,
            'affected_asset': vulnerability.affected_asset,
            'tool': vulnerability.tool.name,
            'discovered_at': vulnerability.discovered_at.isoformat(),
            'status': vulnerability.status
        }
        
        self.es.index(
            index=f'{self.index_prefix}vulnerabilities',
            id=vulnerability.id,
            document=doc
        )
        print(f'Indexed vulnerability: {vulnerability.vuln_id}')
    
    def index_alert(self, alert):
        """Index a security alert to Elasticsearch"""
        doc = {
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'message': alert.message,
            'source': alert.source,
            'source_ip': alert.source_ip,
            'destination_ip': alert.destination_ip,
            'tool': alert.tool.name,
            'timestamp': alert.timestamp.isoformat()
        }
        
        self.es.index(
            index=f'{self.index_prefix}alerts',
            id=alert.id,
            document=doc
        )
        print(f'Indexed alert: {alert.message}')
    
    def index_scan_result(self, scan_result):
        """Index scan result to Elasticsearch"""
        doc = {
            'tool': scan_result.tool.name,
            'scan_type': scan_result.scan_type,
            'target': scan_result.target,
            'start_time': scan_result.start_time.isoformat(),
            'end_time': scan_result.end_time.isoformat() if scan_result.end_time else None,
            'status': scan_result.status,
            'vulnerabilities_found': scan_result.vulnerabilities_found,
            'raw_output': scan_result.raw_output[:10000]  # Limit size
        }
        
        self.es.index(
            index=f'{self.index_prefix}scan_results',
            id=scan_result.id,
            document=doc
        )
        print(f'Indexed scan result: {scan_result.id}')
    
    def index_network_traffic(self, packet_data):
        """Index network traffic data from Wireshark/TShark"""
        self.es.index(
            index=f'{self.index_prefix}network_traffic',
            document=packet_data
        )
    
    def search_vulnerabilities(self, query, severity=None, limit=100):
        """Search vulnerabilities in Elasticsearch"""
        body = {
            'query': {
                'bool': {
                    'must': [
                        {'match': {'description': query}}
                    ]
                }
            },
            'size': limit,
            'sort': [{'discovered_at': {'order': 'desc'}}]
        }
        
        if severity:
            body['query']['bool']['filter'] = [{'term': {'severity': severity}}]
        
        results = self.es.search(index=f'{self.index_prefix}vulnerabilities', body=body)
        return results['hits']['hits']
    
    def get_vulnerability_stats(self):
        """Get aggregated vulnerability statistics"""
        body = {
            'size': 0,
            'aggs': {
                'by_severity': {
                    'terms': {'field': 'severity'}
                },
                'by_tool': {
                    'terms': {'field': 'tool'}
                },
                'by_status': {
                    'terms': {'field': 'status'}
                }
            }
        }
        
        results = self.es.search(index=f'{self.index_prefix}vulnerabilities', body=body)
        return results['aggregations']


def sync_all_to_elasticsearch():
    """Sync all existing data from Django DB to Elasticsearch"""
    from security_api.models import Vulnerability, SecurityAlert, ScanResult
    
    es_client = ElasticsearchClient()
    es_client.create_indices()
    
    # Sync vulnerabilities
    print("\nSyncing vulnerabilities...")
    for vuln in Vulnerability.objects.all():
        es_client.index_vulnerability(vuln)
    
    # Sync alerts
    print("\nSyncing alerts...")
    for alert in SecurityAlert.objects.all():
        es_client.index_alert(alert)
    
    # Sync scan results
    print("\nSyncing scan results...")
    for scan in ScanResult.objects.all():
        es_client.index_scan_result(scan)
    
    print("\n✓ All data synced to Elasticsearch!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Elasticsearch integration')
    parser.add_argument('command', choices=['create', 'sync', 'stats'], help='Command to execute')
    
    args = parser.parse_args()
    
    es_client = ElasticsearchClient()
    
    if args.command == 'create':
        es_client.create_indices()
    elif args.command == 'sync':
        sync_all_to_elasticsearch()
    elif args.command == 'stats':
        stats = es_client.get_vulnerability_stats()
        print("\nVulnerability Statistics:")
        print(json.dumps(stats, indent=2))
