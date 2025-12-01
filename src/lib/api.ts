import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const securityApi = {
  // Dashboard
  getDashboardStats: () => api.get('/dashboard/'),
  
  // Vulnerabilities
  getVulnerabilities: () => api.get('/vulnerabilities/'),
  getVulnerabilityById: (id: number) => api.get(`/vulnerabilities/${id}/`),
  getBySeverity: () => api.get('/vulnerabilities/by_severity/'),
  getRecentVulnerabilities: () => api.get('/vulnerabilities/recent/'),
  
  // Alerts
  getAlerts: () => api.get('/alerts/'),
  getUnacknowledgedAlerts: () => api.get('/alerts/unacknowledged/'),
  acknowledgeAlert: (id: number) => api.post(`/alerts/${id}/acknowledge/`),
  
  // Tools
  getTools: () => api.get('/tools/'),
  startScan: (id: number) => api.post(`/tools/${id}/start_scan/`),
  stopScan: (id: number) => api.post(`/tools/${id}/stop_scan/`),
  
  // Scan Results
  getScanResults: () => api.get('/scans/'),
  
  // Hosts
  getHosts: () => api.get('/hosts/'),
  
  // Metrics
  getMetrics: () => api.get('/metrics/'),
};
