import { useMemo } from "react";
import { DashboardHeader } from "@/components/DashboardHeader";
import { MetricCard } from "@/components/MetricCard";
import { ToolCard } from "@/components/ToolCard";
import { AlertsFeed } from "@/components/AlertFeed";
import { VulnerabilityCharts } from "@/components/VulnerabilityCharts";
import { VulnerabilitiesTable } from "@/components/VulnerabilityTable";
import { 
  useDashboardStats,
  useSecurityTools,
  useAlerts,
  useVulnerabilities,
  useAcknowledgeAlert,
  useStartScan,
  useStopScan,
} from "@/hooks/useSecurityData";

import {
  transformTool,
  transformVulnerability,
  transformAlert,
  transformDashboardStats,
  fallbackTools,
  fallbackVulnerabilities,
  fallbackAlerts,
  mockDashboardStats,
} from "@/lib/security-data";
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Server, 
  Bug,
  Radar,
  Wifi,
  WifiOff
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import heroBg from "@/assets/hero-bg.jpg";

export default function Dashboard() {
  // ============================================================
  // API Data Hooks
  // ============================================================
  
  const { 
    data: apiStats, 
    isLoading: statsLoading, 
    isError: statsError 
  } = useDashboardStats();
  
  const { 
    data: apiTools, 
    isLoading: toolsLoading, 
    isError: toolsError 
  } = useSecurityTools();
  
  const { 
    data: apiAlerts, 
    isLoading: alertsLoading, 
    isError: alertsError 
  } = useAlerts();
  
  const { 
    data: apiVulnerabilities, 
    isLoading: vulnsLoading, 
    isError: vulnsError 
  } = useVulnerabilities();
  
  const acknowledgeAlert = useAcknowledgeAlert();
  const startScan = useStartScan();
  const stopScan = useStopScan();

  // ============================================================
  // Connection Status
  // ============================================================
  
  const isConnected = apiStats !== null && apiStats !== undefined && !statsError;

  // ============================================================
  // Data Transformation & Fallback Logic
  // ============================================================
  
  const stats = useMemo(() => {
    if (apiStats && apiStats.total_vulnerabilities !== undefined) {
      return transformDashboardStats(apiStats);
    }
    return mockDashboardStats;
  }, [apiStats]);

  const tools = useMemo(() => {
    if (apiTools && Array.isArray(apiTools) && apiTools.length > 0) {
      return apiTools.map(transformTool);
    }
    return fallbackTools;
  }, [apiTools]);

  const alerts = useMemo(() => {
    if (apiAlerts && Array.isArray(apiAlerts) && apiAlerts.length > 0) {
      return apiAlerts.map(transformAlert);
    }
    return fallbackAlerts;
  }, [apiAlerts]);

  const vulnerabilities = useMemo(() => {
    if (apiVulnerabilities && Array.isArray(apiVulnerabilities) && apiVulnerabilities.length > 0) {
      return apiVulnerabilities.map(transformVulnerability);
    }
    return fallbackVulnerabilities;
  }, [apiVulnerabilities]);

  // ============================================================
  // Chart Data Computation
  // ============================================================
  
  const severityChartData = useMemo(() => [
    { name: 'Critical', value: stats.criticalCount, color: 'hsl(0, 72%, 51%)' },
    { name: 'High', value: stats.highCount, color: 'hsl(25, 95%, 53%)' },
    { name: 'Medium', value: stats.mediumCount, color: 'hsl(45, 93%, 47%)' },
    { name: 'Low', value: stats.lowCount, color: 'hsl(142, 71%, 45%)' }
  ], [stats]);

  const toolChartData = useMemo(() => {
    // Group vulnerabilities by tool
    const toolCounts: Record<string, number> = {};
    vulnerabilities.forEach(v => {
      const toolName = v.tool;
      toolCounts[toolName] = (toolCounts[toolName] || 0) + 1;
    });
    
    return Object.entries(toolCounts).map(([name, count]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      vulnerabilities: count
    }));
  }, [vulnerabilities]);

  // Trend data: vulnerabilities by date and severity
  const trendData = useMemo(() => {
    const days: { date: string; critical: number; high: number; medium: number; low: number }[] = [];
    
    // Last 7 days
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      // Count vulnerabilities discovered on this date
      const dayVulns = vulnerabilities.filter(v => {
        const vulnDate = new Date(v.discoveredAt);
        return vulnDate.toDateString() === date.toDateString();
      });
      
      days.push({
        date: dateStr,
        critical: dayVulns.filter(v => v.severity === 'critical').length,
        high: dayVulns.filter(v => v.severity === 'high').length,
        medium: dayVulns.filter(v => v.severity === 'medium').length,
        low: dayVulns.filter(v => v.severity === 'low').length,
      });
    }
    return days;
  }, [vulnerabilities]);

  // ============================================================
  // Event Handlers
  // ============================================================
  
  const handleAcknowledgeAlert = (alertId: string) => {
    if (isConnected) {
      acknowledgeAlert.mutate(Number(alertId));
    }
  };

  const handleStartScan = (toolId: string, target: string, scanType: string) => {
    if (isConnected) {
      startScan.mutate({ toolId: Number(toolId), target, scanType });
    }
  };

  const handleStopScan = (toolId: string) => {
    if (isConnected) {
      stopScan.mutate(Number(toolId));
    }
  };

  // ============================================================
  // Computed Values
  // ============================================================
  
  const unacknowledgedCount = alerts.filter(a => !a.acknowledged).length;

  // ============================================================
  // Render
  // ============================================================
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <DashboardHeader alertCount={unacknowledgedCount} />
      
      {/* Hero Section with Background */}
      <div className="relative overflow-hidden border-b border-border">
        <div 
          className="absolute inset-0 opacity-30"
          style={{ 
            backgroundImage: `url(${heroBg})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/50 via-background/80 to-background" />
        
        <div className="relative container py-8 px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Title Section */}
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl md:text-3xl font-bold text-foreground">
                Security Operations <span className="text-primary">Dashboard</span>
              </h2>
              <Badge 
                variant={isConnected ? "default" : "secondary"}
                className={isConnected ? "bg-green-500/20 text-green-700 border-green-500/30" : "bg-muted text-muted-foreground"}
              >
                {isConnected ? (
                  <><Wifi className="h-3 w-3 mr-1" /> Live</>
                ) : (
                  <><WifiOff className="h-3 w-3 mr-1" /></>
                )}
              </Badge>
            </div>
            
            {/* Subtitle */}
            <p className="text-muted-foreground max-w-2xl">
              {isConnected 
                ? `Real-time monitoring connected  - ${stats.totalVulnerabilities} vulnerabilities detected`
                : ''}
            </p>
          </motion.div>

          {/* Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <MetricCard
              title="Total Vulnerabilities"
              value={stats.totalVulnerabilities}
              icon={Bug}
              variant="default"
              isLoading={statsLoading}
            />
            <MetricCard
              title="Critical Issues"
              value={stats.criticalCount}
              subtitle="Requires immediate action"
              icon={AlertTriangle}
              variant="critical"
              isLoading={statsLoading}
            />
            <MetricCard
              title="Active Alerts"
              value={unacknowledgedCount}
              icon={Activity}
              variant="warning"
              isLoading={alertsLoading}
            />
            <MetricCard
              title="Tools Online"
              value={`${tools.filter(t => t.status === 'active').length}/${tools.length}`}
              icon={Server}
              variant="success"
              isLoading={toolsLoading}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container py-8 px-4">
        <Tabs defaultValue="overview" className="space-y-6">
          {/* Tab Navigation */}
          <TabsList className="bg-secondary/50 border border-border">
            <TabsTrigger value="overview" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              <Shield className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="tools" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              <Radar className="mr-2 h-4 w-4" />
              Security Tools
            </TabsTrigger>
            <TabsTrigger value="vulnerabilities" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              <Bug className="mr-2 h-4 w-4" />
              Vulnerabilities
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Charts - 2 columns */}
              <div className="lg:col-span-2">
                <VulnerabilityCharts
                  severityData={severityChartData}
                  toolData={toolChartData.length > 0 ? toolChartData : [
                    { name: 'Nmap', vulnerabilities: 0 },
                    { name: 'OWASP ZAP', vulnerabilities: 0 },
                    { name: 'Trivy', vulnerabilities: 0 },
                  ]}
                  trendData={trendData}
                />
              </div>

              {/* Alerts Feed - 1 column */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-foreground">Recent Alerts</h3>
                  <span className="text-xs text-muted-foreground font-mono">
                    {unacknowledgedCount} unread
                  </span>
                </div>
                <div className="rounded-lg border border-border bg-card p-4 max-h-[600px] overflow-y-auto">
                  <AlertsFeed 
                    alerts={alerts} 
                    onAcknowledge={handleAcknowledgeAlert}
                    isLoading={alertsLoading}
                  />
                </div>
              </div>
            </div>

            {/* Recent Vulnerabilities Table */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground">Recent Vulnerabilities</h3>
              <VulnerabilitiesTable vulnerabilities={vulnerabilities} isLoading={vulnsLoading} />
            </div>
          </TabsContent>

          {/* Tools Tab */}
          <TabsContent value="tools" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-foreground">Security Tools</h3>
                <p className="text-sm text-muted-foreground">
                  Launch scans and manage your security toolkit
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tools.map((tool) => (
                <ToolCard 
                  key={tool.id} 
                  tool={tool}
                  onStartScan={handleStartScan}
                  onStopScan={handleStopScan}
                  isLoading={toolsLoading}
                />
              ))}
            </div>
          </TabsContent>

          {/* Vulnerabilities Tab */}
          <TabsContent value="vulnerabilities" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-foreground">All Vulnerabilities</h3>
                <p className="text-sm text-muted-foreground">
                  {vulnerabilities.length} vulnerabilities found across all tools
                </p>
              </div>
            </div>
            
            <VulnerabilitiesTable vulnerabilities={vulnerabilities} isLoading={vulnsLoading} />
            
            <VulnerabilityCharts
              severityData={severityChartData}
              toolData={toolChartData.length > 0 ? toolChartData : [
                { name: 'Nmap', vulnerabilities: 0 },
                { name: 'OWASP ZAP', vulnerabilities: 0 },
              ]}
              trendData={trendData}
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50 py-6">
        <div className="container px-4 text-center">
          <p className="text-sm text-muted-foreground">
            SentinelHub Security Operations Center • 
            <span className="font-mono ml-2">
              {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}
            </span>
            {isConnected && <span className="ml-2 text-green-600">● Connected </span>}
          </p>
        </div>
      </footer>
    </div>
  );
}