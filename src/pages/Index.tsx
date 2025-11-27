import { Shield, AlertTriangle, Activity, Network, Database, Lock } from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { VulnerabilityTable } from "@/components/VulnerabilityTable";
import { AlertFeed } from "@/components/AlertFeed";
import { ToolStatus } from "@/components/ToolStatus";

const Index = () => {
  // Mock data for demonstration
  const metrics = [
    {
      title: "Critical Vulnerabilities",
      value: 7,
      icon: AlertTriangle,
      trend: { value: "2 from last scan", isPositive: false },
      severity: "critical" as const,
    },
    {
      title: "Active Threats",
      value: 23,
      icon: Shield,
      trend: { value: "5 from yesterday", isPositive: false },
      severity: "high" as const,
    },
    {
      title: "Systems Monitored",
      value: 156,
      icon: Network,
      severity: "info" as const,
    },
    {
      title: "Security Score",
      value: "72%",
      icon: Lock,
      trend: { value: "3% from last week", isPositive: true },
      severity: "medium" as const,
    },
  ];

  const vulnerabilities = [
    {
      id: "CVE-2024-1234",
      name: "SQL Injection in Login Form",
      severity: "critical" as const,
      tool: "OWASP ZAP",
      target: "webapp.example.com",
      cvss: 9.8,
      status: "open" as const,
    },
    {
      id: "CVE-2024-5678",
      name: "Outdated OpenSSL Version",
      severity: "high" as const,
      tool: "OpenVAS",
      target: "10.0.1.45",
      cvss: 8.2,
      status: "investigating" as const,
    },
    {
      id: "CVE-2024-9012",
      name: "Container Image Vulnerability",
      severity: "high" as const,
      tool: "Trivy",
      target: "nginx:latest",
      cvss: 7.5,
      status: "open" as const,
    },
    {
      id: "NMAP-001",
      name: "Open Port 22 (SSH)",
      severity: "medium" as const,
      tool: "Nmap",
      target: "10.0.1.67",
      cvss: 5.3,
      status: "investigating" as const,
    },
    {
      id: "CVE-2024-3456",
      name: "XSS in Search Parameter",
      severity: "medium" as const,
      tool: "OWASP ZAP",
      target: "api.example.com",
      cvss: 6.1,
      status: "resolved" as const,
    },
  ];

  const alerts = [
    {
      id: "1",
      title: "Brute force attack detected on SSH port",
      timestamp: "2 minutes ago",
      severity: "critical" as const,
      source: "Wazuh SIEM",
    },
    {
      id: "2",
      title: "New vulnerability discovered in production server",
      timestamp: "15 minutes ago",
      severity: "high" as const,
      source: "OpenVAS",
    },
    {
      id: "3",
      title: "Suspicious network traffic pattern detected",
      timestamp: "32 minutes ago",
      severity: "medium" as const,
      source: "Wireshark",
    },
    {
      id: "4",
      title: "Security scan completed successfully",
      timestamp: "1 hour ago",
      severity: "info" as const,
      source: "Nmap",
    },
    {
      id: "5",
      title: "Container image updated with patches",
      timestamp: "2 hours ago",
      severity: "low" as const,
      source: "Trivy",
    },
    {
      id: "6",
      title: "Multiple failed login attempts",
      timestamp: "3 hours ago",
      severity: "high" as const,
      source: "Wazuh SIEM",
    },
  ];

  const tools = [
    { name: "Wazuh SIEM", status: "active" as const, lastScan: "Live", findings: 23 },
    { name: "OpenVAS", status: "active" as const, lastScan: "10 min ago", findings: 12 },
    { name: "OWASP ZAP", status: "idle" as const, lastScan: "1 hour ago", findings: 8 },
    { name: "Nmap", status: "active" as const, lastScan: "5 min ago", findings: 45 },
    { name: "Trivy", status: "idle" as const, lastScan: "30 min ago", findings: 6 },
    { name: "Wireshark", status: "active" as const, lastScan: "Live", findings: 156 },
  ];

  return (
    <div className="min-h-screen cyber-gradient p-6">
      <div className="max-w-[1600px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-primary mb-2 flex items-center gap-3">
              <Activity className="h-8 w-8" />
              Security Operations Center
            </h1>
            <p className="text-muted-foreground">
              Integrated monitoring platform for automated security analysis
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="pulse-glow">
              <Database className="h-5 w-5 text-primary" />
            </div>
            <span className="text-sm text-muted-foreground">ELK Stack Connected</span>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Vulnerability Table - spans 2 columns */}
          <div className="lg:col-span-2">
            <VulnerabilityTable vulnerabilities={vulnerabilities} />
          </div>

          {/* Alert Feed - spans 1 column */}
          <div className="lg:col-span-1">
            <AlertFeed alerts={alerts} />
          </div>
        </div>

        {/* Tool Status */}
        <ToolStatus tools={tools} />
      </div>
    </div>
  );
};

export default Index;
