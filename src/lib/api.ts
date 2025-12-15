const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    console.error('API fetch error:', error);
    return { 
      data: null, 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
}

// Types matching Django backend models
export interface DjangoSecurityTool {
  id: number;
  name: string;
  status: 'active' | 'inactive' | 'scanning' | 'error';
  last_scan?: string;
  scan_count: number;
  error_message?: string;
  updated_at: string;
}

export interface DjangoVulnerability {
  id: number;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'in_progress' | 'resolved' | 'false_positive';
  affected_asset: string;
  description: string;
  cve_id?: string;
  cvss_score?: string;
  tool: number | string;
  tool_name?: string;
  created_at?: string;
  discovered_at: string;
  updated_at: string;
  vuln_id: string;
  port?: number;
  service?: string;
}

export interface DjangoSecurityAlert {
  id: number;
  alert_type: 'intrusion' | 'vulnerability' | 'anomaly' | 'compliance' | 'policy_violation' | 'malware' | 'scan_complete';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
  source: string;
  acknowledged: boolean;
  tool: number | string;
  timestamp?: string;
  created_at?: string;
}

export interface DjangoDashboardStats {
  total_vulnerabilities: number;
  critical_vulns: number;
  high_vulns: number;
  medium_vulns: number;
  low_vulns: number;
  active_tools: number;
  total_alerts: number;
  unacknowledged_alerts: number;
  hosts_discovered: number;
  last_scan_time: string | null;
}

export interface DjangoVulnerabilityTrend {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface DjangoScanResult {
  id: number;
  tool: number | string;
  target: string;
  scan_type: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  start_time: string;
  end_time?: string;
  result_data?: Record<string, unknown>;
  findings_count?: number;
  vulnerabilities_found?: number;
}

// Helper function to extract results from paginated response
function extractResults<T>(response: any): T[] {
  if (response && typeof response === 'object' && 'results' in response) {
    return response.results as T[];
  }
  if (Array.isArray(response)) {
    return response;
  }
  return [];
}

// API Service functions
export const securityApi = {
  // Dashboard
  getDashboardStats: () => 
    fetchApi<DjangoDashboardStats>('/dashboard/'),

  // Vulnerabilities
  getVulnerabilities: async () => {
    const { data, error } = await fetchApi<any>('/vulnerabilities/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoVulnerability>(data);
    return { data: results, error: null };
  },
  
  getVulnerabilityById: (id: number) => 
    fetchApi<DjangoVulnerability>(`/vulnerabilities/${id}/`),
  
  getVulnerabilitiesBySeverity: async () => {
    const { data, error } = await fetchApi<any>('/vulnerabilities/by_severity/');
    if (error) return { data: null, error };
    const results = extractResults<{ severity: string; count: number }>(data);
    return { data: results, error: null };
  },
  
  getRecentVulnerabilities: async () => {
    const { data, error } = await fetchApi<any>('/vulnerabilities/recent/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoVulnerability>(data);
    return { data: results, error: null };
  },
  
  getVulnerabilityTrend: async () => {
    const { data, error } = await fetchApi<any>('/vulnerabilities/trend/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoVulnerabilityTrend>(data);
    return { data: results, error: null };
  },

  // Alerts
  getAlerts: async () => {
    const { data, error } = await fetchApi<any>('/alerts/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoSecurityAlert>(data);
    return { data: results, error: null };
  },
  
  getUnacknowledgedAlerts: async () => {
    const { data, error } = await fetchApi<any>('/alerts/unacknowledged/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoSecurityAlert>(data);
    return { data: results, error: null };
  },
  
  acknowledgeAlert: (id: number) => 
    fetchApi<DjangoSecurityAlert>(`/alerts/${id}/acknowledge/`, { method: 'POST' }),

  // Security Tools
  getTools: async () => {
    const { data, error } = await fetchApi<any>('/tools/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoSecurityTool>(data);
    return { data: results, error: null };
  },
  
  getToolById: (id: number) => 
    fetchApi<DjangoSecurityTool>(`/tools/${id}/`),
  
  startScan: (toolId: number, target: string, scanType: string) => 
    fetchApi<{ status: string; tool: string; message: string; scan_result_id?: number }>(`/tools/${toolId}/start_scan/`, {
      method: 'POST',
      body: JSON.stringify({ target, scan_type: scanType }),
    }),
  
  stopScan: (toolId: number) => 
    fetchApi<{ message: string }>(`/tools/${toolId}/stop_scan/`, { method: 'POST' }),

  // Scan Results
  getScans: async () => {
    const { data, error } = await fetchApi<any>('/scans/');
    if (error) return { data: null, error };
    const results = extractResults<DjangoScanResult>(data);
    return { data: results, error: null };
  },
  
  getScanById: (id: number) => 
    fetchApi<DjangoScanResult>(`/scans/${id}/`),

  // Hosts
  getHosts: async () => {
    const { data, error } = await fetchApi<any>('/hosts/');
    if (error) return { data: null, error };
    const results = extractResults<{ id: number; ip_address: string; hostname?: string; status: string }>(data);
    return { data: results, error: null };
  },

  // Metrics
  getMetrics: async () => {
    const { data, error } = await fetchApi<any>('/metrics/');
    if (error) return { data: null, error };
    const results = extractResults<{ name: string; value: number; timestamp: string }>(data);
    return { data: results, error: null };
  },
};

export default securityApi;