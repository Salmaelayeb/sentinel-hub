import { Card } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  severity?: "critical" | "high" | "medium" | "low" | "info";
}

export const MetricCard = ({ title, value, icon: Icon, trend, severity }: MetricCardProps) => {
  const getSeverityColor = () => {
    switch (severity) {
      case "critical": return "text-critical";
      case "high": return "text-high";
      case "medium": return "text-medium";
      case "low": return "text-low";
      case "info": return "text-info";
      default: return "text-primary";
    }
  };

  return (
    <Card className="p-6 border-border bg-card hover:bg-card/80 transition-colors glow-cyan">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground uppercase tracking-wider">{title}</p>
          <p className={`text-3xl font-bold ${getSeverityColor()}`}>{value}</p>
          {trend && (
            <p className={`text-xs ${trend.isPositive ? 'text-low' : 'text-critical'}`}>
              {trend.isPositive ? '↓' : '↑'} {trend.value}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-secondary ${getSeverityColor()}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </Card>
  );
};
