import { Shield, AlertTriangle, Activity, Network, Database, Lock } from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { VulnerabilityTable } from "@/components/VulnerabilityTable";
import { AlertFeed } from "@/components/AlertFeed";
import { ToolStatus } from "@/components/ToolStatus";
import { useDashboard } from "@/hooks/useDashboard";
import { useVulnerabilities } from "@/hooks/useVulnerabilities";
import { useAlerts } from "@/hooks/useAlerts";
import { useTools } from "@/hooks/useTools";

const Index = () => {
  const { data: dashboardStats, isLoading: isDashboardLoading } = useDashboard();
  const { data: vulnerabilities = [], isLoading: isVulnerabilitiesLoading } = useVulnerabilities();
  const { data: alerts = [], isLoading: isAlertsLoading } = useAlerts();
  const { data: tools = [], isLoading: isToolsLoading } = useTools();

  // Metrics based on real data
  const metrics = [
    {
      title: "Critical Vulnerabilities",
      value: dashboardStats?.critical_vulns || 0,
      icon: AlertTriangle,
      trend: { value: `${dashboardStats?.total_vulnerabilities || 0} total`, isPositive: false },
      severity: "critical" as const,
    },
    {
      title: "Active Threats",
      value: dashboardStats?.high_vulns || 0,
      icon: Shield,
      trend: { value: `${dashboardStats?.unacknowledged_alerts || 0} unacknowledged`, isPositive: false },
      severity: "high" as const,
    },
    {
      title: "Systems Monitored",
      value: dashboardStats?.hosts_discovered || 0,
      icon: Network,
      severity: "info" as const,
    },
    {
      title: "Active Tools",
      value: dashboardStats?.active_tools || 0,
      icon: Lock,
      trend: { value: `${tools.length} configured`, isPositive: true },
      severity: "medium" as const,
    },
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
            {isVulnerabilitiesLoading ? (
              <div className="glass-effect rounded-lg p-8 text-center">
                <p className="text-muted-foreground">Loading vulnerabilities...</p>
              </div>
            ) : (
              <VulnerabilityTable vulnerabilities={vulnerabilities} />
            )}
          </div>

          {/* Alert Feed - spans 1 column */}
          <div className="lg:col-span-1">
            {isAlertsLoading ? (
              <div className="glass-effect rounded-lg p-8 text-center">
                <p className="text-muted-foreground">Loading alerts...</p>
              </div>
            ) : (
              <AlertFeed alerts={alerts} />
            )}
          </div>
        </div>

        {/* Tool Status */}
        {isToolsLoading ? (
          <div className="glass-effect rounded-lg p-8 text-center">
            <p className="text-muted-foreground">Loading tools...</p>
          </div>
        ) : (
          <ToolStatus tools={tools} />
        )}
      </div>
    </div>
  );
};

export default Index;
