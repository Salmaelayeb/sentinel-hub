import { useMemo } from "react";
import { SecurityAlert } from "@/lib/security-data";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle, AlertCircle, Bell, Shield } from "lucide-react";
import { motion } from "framer-motion";

interface AlertsFeedProps {
  alerts: SecurityAlert[];
  onAcknowledge: (alertId: string) => void;
  isLoading?: boolean;
}

export function AlertsFeed({ alerts, onAcknowledge, isLoading }: AlertsFeedProps) {
  // Sort alerts by timestamp (newest first)
  const sortedAlerts = useMemo(() => {
    return [...alerts].sort((a, b) => {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
  }, [alerts]);

  // Separate unacknowledged and acknowledged alerts
  const unacknowledgedAlerts = useMemo(() => {
    return sortedAlerts.filter(a => !a.acknowledged);
  }, [sortedAlerts]);

  const acknowledgedAlerts = useMemo(() => {
    return sortedAlerts.filter(a => a.acknowledged).slice(0, 5); // Show only last 5
  }, [sortedAlerts]);

  // Get severity color and icon
  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'critical':
        return {
          color: 'text-red-600',
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/30',
          badgeBg: 'bg-red-500/20',
          badgeText: 'text-red-700',
          icon: AlertTriangle,
        };
      case 'high':
        return {
          color: 'text-orange-600',
          bgColor: 'bg-orange-500/10',
          borderColor: 'border-orange-500/30',
          badgeBg: 'bg-orange-500/20',
          badgeText: 'text-orange-700',
          icon: AlertTriangle,
        };
      case 'medium':
        return {
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-500/10',
          borderColor: 'border-yellow-500/30',
          badgeBg: 'bg-yellow-500/20',
          badgeText: 'text-yellow-700',
          icon: AlertCircle,
        };
      case 'low':
        return {
          color: 'text-blue-600',
          bgColor: 'bg-blue-500/10',
          borderColor: 'border-blue-500/30',
          badgeBg: 'bg-blue-500/20',
          badgeText: 'text-blue-700',
          icon: Bell,
        };
      default:
        return {
          color: 'text-gray-600',
          bgColor: 'bg-gray-500/10',
          borderColor: 'border-gray-500/30',
          badgeBg: 'bg-gray-500/20',
          badgeText: 'text-gray-700',
          icon: Shield,
        };
    }
  };

  // Get alert type icon
  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'intrusion':
        return '🚨';
      case 'vulnerability':
        return '🔓';
      case 'anomaly':
        return '⚠️';
      case 'compliance':
        return '📋';
      case 'policy_violation':
        return '🚫';
      case 'malware':
        return '🦠';
      case 'scan_complete':
        return '✅';
      default:
        return '📌';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-20 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="text-center py-8">
        <Shield className="h-12 w-12 mx-auto text-green-600 mb-2" />
        <p className="text-muted-foreground">No alerts at the moment</p>
        <p className="text-xs text-muted-foreground">Your system is secure</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Unacknowledged Alerts */}
      {unacknowledgedAlerts.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-red-600 uppercase tracking-wider">
            ⚠️ Action Required ({unacknowledgedAlerts.length})
          </h4>
          {unacknowledgedAlerts.map((alert) => {
            const style = getSeverityStyle(alert.severity);
            const IconComponent = style.icon;

            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-3 rounded-lg border ${style.bgColor} ${style.borderColor} transition-colors hover:border-opacity-100`}
              >
                <div className="flex items-start gap-2">
                  <IconComponent className={`h-4 w-4 mt-0.5 flex-shrink-0 ${style.color}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-foreground line-clamp-1">
                          {getAlertTypeIcon(alert.alertType)} {alert.alertType}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                          {alert.message}
                        </p>
                      </div>
                      <Badge className={`${style.badgeBg} ${style.badgeText} text-xs flex-shrink-0`}>
                        {alert.severity}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">{alert.source}</span>
                        <span className="text-xs text-muted-foreground">•</span>
                        <span className="text-xs text-muted-foreground">{formatTime(alert.timestamp)}</span>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onAcknowledge(alert.id)}
                        className="h-6 px-2 text-xs"
                      >
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Ack
                      </Button>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Acknowledged Alerts */}
      {acknowledgedAlerts.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            ✓ Acknowledged
          </h4>
          {acknowledgedAlerts.map((alert) => {
            const style = getSeverityStyle(alert.severity);
            const IconComponent = style.icon;

            return (
              <div
                key={alert.id}
                className="p-2 rounded-lg bg-muted/50 border border-border/50 opacity-75 text-xs"
              >
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-3 w-3 mt-0.5 flex-shrink-0 text-green-600" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {getAlertTypeIcon(alert.alertType)} {alert.message}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">{alert.source}</span>
                      <span className="text-xs text-muted-foreground">•</span>
                      <span className="text-xs text-muted-foreground">{formatTime(alert.timestamp)}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {unacknowledgedAlerts.length === 0 && acknowledgedAlerts.length === 0 && (
        <div className="text-center py-6">
          <Shield className="h-10 w-10 mx-auto text-green-600 mb-2" />
          <p className="text-sm text-muted-foreground">All alerts acknowledged</p>
        </div>
      )}
    </div>
  );
}