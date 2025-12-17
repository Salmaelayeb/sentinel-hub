import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Clock, Play, Square, Activity } from "lucide-react";
import { Tool, useStartScan, useStopScan } from "@/hooks/useTools";

interface ToolStatusProps {
  tools: Tool[];
}

export const ToolStatus = ({ tools }: ToolStatusProps) => {
  const { mutate: startScan } = useStartScan();
  const { mutate: stopScan } = useStopScan();
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return <CheckCircle2 className="h-4 w-4 text-low" />;
      case "scanning": return <Activity className="h-4 w-4 text-info animate-pulse" />;
      case "inactive": return <Clock className="h-4 w-4 text-medium" />;
      case "error": return <XCircle className="h-4 w-4 text-critical" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-low/20 text-low border-low";
      case "scanning": return "bg-info/20 text-info border-info";
      case "inactive": return "bg-medium/20 text-medium border-medium";
      case "error": return "bg-critical/20 text-critical border-critical";
      default: return "";
    }
  };

  return (
    <Card className="p-6 border-border bg-card">
      <h2 className="text-xl font-bold mb-4 text-primary">Security Tools Status</h2>
      <div className="grid grid-cols-2 gap-4">
        {tools.map((tool) => (
          <div key={tool.id} className="p-4 rounded-lg bg-secondary border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">{tool.name}</span>
              {getStatusIcon(tool.status)}
            </div>
            <div className="space-y-1 text-xs text-muted-foreground mb-2">
              <p>Last scan: {tool.last_scan ? new Date(tool.last_scan).toLocaleString() : 'Never'}</p>
            </div>
            <div className="flex items-center justify-between">
              <Badge variant="outline" className={`text-xs ${getStatusColor(tool.status)}`}>
                {tool.status}
              </Badge>
              {tool.status === 'scanning' ? (
                <button
                  onClick={() => stopScan(tool.id)}
                  className="text-xs px-2 py-1 rounded bg-destructive/20 text-destructive hover:bg-destructive/30 flex items-center gap-1"
                >
                  <Square className="h-3 w-3" />
                  Stop
                </button>
              ) : (
                <button
                  onClick={() => startScan({ toolId: tool.id, target: 'localhost', scanType: 'basic' })}
                  className="text-xs px-2 py-1 rounded bg-primary/20 text-primary hover:bg-primary/30 flex items-center gap-1"
                  disabled={tool.status === 'error'}
                >
                  <Play className="h-3 w-3" />
                  Start
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
