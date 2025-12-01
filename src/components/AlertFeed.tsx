import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, Shield, Activity } from "lucide-react";
import { Alert, useAcknowledgeAlert } from "@/hooks/useAlerts";

interface AlertFeedProps {
  alerts: Alert[];
}

export const AlertFeed = ({ alerts }: AlertFeedProps) => {
  const { mutate: acknowledgeAlert } = useAcknowledgeAlert();
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
      case "high":
        return AlertCircle;
      case "medium":
        return Shield;
      default:
        return Activity;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "text-critical border-critical bg-critical/10";
      case "high": return "text-high border-high bg-high/10";
      case "medium": return "text-medium border-medium bg-medium/10";
      case "low": return "text-low border-low bg-low/10";
      case "info": return "text-info border-info bg-info/10";
      default: return "text-muted";
    }
  };

  return (
    <Card className="p-6 border-border bg-card h-full">
      <h2 className="text-xl font-bold mb-4 text-primary">Real-Time Alerts</h2>
      <ScrollArea className="h-[400px] pr-4">
        <div className="space-y-3">
          {alerts.map((alert) => {
            const Icon = getSeverityIcon(alert.severity);
            return (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)} transition-all hover:scale-[1.02] ${
                  alert.acknowledged ? 'opacity-50' : ''
                }`}
              >
                <div className="flex items-start gap-3">
                  <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-semibold text-sm">{alert.message}</p>
                      <Badge variant="outline" className="text-xs shrink-0">
                        {alert.severity}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between mt-1 text-xs text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <span className="font-mono">{alert.source}</span>
                        <span>•</span>
                        <Badge variant="outline" className="text-xs">
                          {alert.alert_type}
                        </Badge>
                      </div>
                      {!alert.acknowledged && (
                        <button
                          onClick={() => acknowledgeAlert(alert.id)}
                          className="text-primary hover:underline ml-2"
                        >
                          Acknowledge
                        </button>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(alert.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </Card>
  );
};
