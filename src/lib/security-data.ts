import { 
  Shield, 
  Radar, 
  Bug, 
  Container, 
  Network, 
  Eye,
  LucideIcon
} from "lucide-react";
import { DjangoSecurityTool, DjangoVulnerability, DjangoSecurityAlert, DjangoDashboardStats } from "./api";

// Icon mapping for tools
const toolIconMap: Record<string, LucideIcon> = {
  nmap: Radar,
  zap: Bug,
  openvas: Shield,
  trivy: Container,
  wazuh: Eye,
  wireshark: Network,
  tshark: Network,
};

const toolScanTypes: Record<string, string[]> = {
  nmap: ["basic", "full", "stealth", "aggressive"],
  zap: ["spider", "active", "passive", "ajax"],
  openvas: ["full", "fast", "discovery"],
  trivy: ["image", "filesystem", "config"],
  wazuh: ["realtime", "scheduled"],
  wireshark: ["capture", "analyze"],
};

const toolCategories: Record<string, 'network' | 'web' | 'container' | 'siem'> = {
  nmap: 'network',
  zap: 'web',
  openvas: 'network',
  trivy: 'container',
  wazuh: 'siem',
  wireshark: 'network',
};

const toolDisplayNames: Record<string, string> = {
  nmap: 'Nmap',
  zap: 'OWASP ZAP',
  openvas: 'OpenVAS',
  trivy: 'Trivy',
  wazuh: 'Wazuh',
  wireshark: 'Wireshark/TShark',
};

export interface SecurityTool {
  id: string;
  name: string;
  displayName: string;
  description: string;
  status: 'active' | 'inactive' | 'scanning' | 'error';
  icon: LucideIcon;
  scanTypes: string[];
  lastScan?: string;
  category: 'network' | 'web' | 'container' | 'siem';
}

export interface Vulnerability {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'in_progress' | 'resolved' | 'false_positive';
  affectedAsset: string;
  description: string;
  cveId?: string;
  tool: string;
  discoveredAt: string;
  cvssScore?: string;
  port?: number;
  service?: string;
}

export interface SecurityAlert {
  id: string;
  alertType: 'intrusion' | 'vulnerability' | 'anomaly' | 'compliance' | 'policy_violation' | 'malware' | 'scan_complete';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
  source: string;
  acknowledged: boolean;
  tool: string;
  timestamp: string;
}

export interface DashboardStats {
  totalVulnerabilities: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  activeAlerts: number;
  activeScans: number;
  toolsOnline: number;
  totalTools: number;
}

// Transform functions from Django API response to frontend types
export function transformTool(djangoTool: DjangoSecurityTool): SecurityTool {
  const name = djangoTool.name.toLowerCase();
  return {
    id: String(djangoTool.id),
    name: name,
    displayName: toolDisplayNames[name] || djangoTool.name,
    description: `${name.toUpperCase()} - Status: ${djangoTool.status}`,
    status: djangoTool.status,
    icon: toolIconMap[name] || Shield,
    scanTypes: toolScanTypes[name] || ['default'],
    lastScan: djangoTool.last_scan,
    category: toolCategories[name] || 'network',
  };
}

export function transformVulnerability(djangoVuln: DjangoVulnerability): Vulnerability {
  return {
    id: String(djangoVuln.id),
    title: djangoVuln.title,
    severity: djangoVuln.severity,
    status: djangoVuln.status,
    affectedAsset: djangoVuln.affected_asset,
    description: djangoVuln.description,
    cveId: djangoVuln.cve_id,
    tool: djangoVuln.tool_name || String(djangoVuln.tool),
    discoveredAt: djangoVuln.discovered_at,
    cvssScore: djangoVuln.cvss_score,
    port: djangoVuln.port,
    service: djangoVuln.service,
  };
}

export function transformAlert(djangoAlert: DjangoSecurityAlert): SecurityAlert {
  return {
    id: String(djangoAlert.id),
    alertType: djangoAlert.alert_type,
    severity: djangoAlert.severity,
    message: djangoAlert.message,
    source: djangoAlert.source,
    acknowledged: djangoAlert.acknowledged,
    tool: String(djangoAlert.tool),
    timestamp: djangoAlert.created_at || djangoAlert.timestamp || new Date().toISOString(),
  };
}

export function transformDashboardStats(djangoStats: DjangoDashboardStats): DashboardStats {
  return {
    totalVulnerabilities: djangoStats.total_vulnerabilities,
    criticalCount: djangoStats.critical_vulns,
    highCount: djangoStats.high_vulns,
    mediumCount: djangoStats.medium_vulns,
    lowCount: djangoStats.low_vulns,
    activeAlerts: djangoStats.unacknowledged_alerts,
    activeScans: 0,
    toolsOnline: djangoStats.active_tools,
    totalTools: 6,
  };
}

// Fallback mock data for when API is unavailable
export const mockDashboardStats: DashboardStats = {
  totalVulnerabilities: 0,
  criticalCount: 0,
  highCount: 0,
  mediumCount: 0,
  lowCount: 0,
  activeAlerts: 0,
  activeScans: 0,
  toolsOnline: 0,
  totalTools: 6,
};

export const fallbackTools: SecurityTool[] = [
  {
    id: "1",
    name: "nmap",
    displayName: "Nmap",
    description: "Network discovery and security auditing tool",
    status: "active",
    icon: Radar,
    scanTypes: ["basic", "full", "stealth", "aggressive"],
    lastScan: new Date().toISOString(),
    category: "network"
  },
  {
    id: "2",
    name: "zap",
    displayName: "OWASP ZAP",
    description: "Web application security scanner",
    status: "active",
    icon: Bug,
    scanTypes: ["spider", "active", "passive", "ajax"],
    category: "web"
  },
  {
    id: "3",
    name: "openvas",
    displayName: "OpenVAS",
    description: "Comprehensive vulnerability assessment",
    status: "active",
    icon: Shield,
    scanTypes: ["full", "fast", "discovery"],
    category: "network"
  },
  {
    id: "4",
    name: "trivy",
    displayName: "Trivy",
    description: "Container and filesystem security scanner",
    status: "active",
    icon: Container,
    scanTypes: ["image", "filesystem", "config"],
    category: "container"
  },
  {
    id: "5",
    name: "wazuh",
    displayName: "Wazuh",
    description: "SIEM and intrusion detection system",
    status: "active",
    icon: Eye,
    scanTypes: ["realtime", "scheduled"],
    category: "siem"
  },
  {
    id: "6",
    name: "wireshark",
    displayName: "Wireshark/TShark",
    description: "Network protocol analyzer",
    status: "active",
    icon: Network,
    scanTypes: ["capture", "analyze"],
    category: "network"
  }
];

export const fallbackVulnerabilities: Vulnerability[] = [];

export const fallbackAlerts: SecurityAlert[] = [];