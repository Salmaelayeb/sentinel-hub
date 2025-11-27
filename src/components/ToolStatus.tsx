import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

interface Tool {
  name: string;
  status: "active" | "idle" | "error";
  lastScan: string;
  findings: number;
}

interface ToolStatusProps {
  tools: Tool[];
}

export const ToolStatus = ({ tools }: ToolStatusProps) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return <CheckCircle2 className="h-4 w-4 text-low" />;
      case "idle": return <Clock className="h-4 w-4 text-medium" />;
      case "error": return <XCircle className="h-4 w-4 text-critical" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-low/20 text-low border-low";
      case "idle": return "bg-medium/20 text-medium border-medium";
      case "error": return "bg-critical/20 text-critical border-critical";
      default: return "";
    }
  };

  return (
    <Card className="p-6 border-border bg-card">
      <h2 className="text-xl font-bold mb-4 text-primary">Security Tools Status</h2>
      <div className="grid grid-cols-2 gap-4">
        {tools.map((tool) => (
          <div key={tool.name} className="p-4 rounded-lg bg-secondary border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">{tool.name}</span>
              {getStatusIcon(tool.status)}
            </div>
            <div className="space-y-1 text-xs text-muted-foreground">
              <p>Last scan: {tool.lastScan}</p>
              <p>Findings: <span className="text-foreground font-bold">{tool.findings}</span></p>
            </div>
            <Badge variant="outline" className={`mt-2 text-xs ${getStatusColor(tool.status)}`}>
              {tool.status}
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  );
};
