// ============================================================
// FILE: components/ToolCard.tsx
// ============================================================

import { useState } from "react";
import { SecurityTool } from "@/lib/security-data";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Play, Square, AlertCircle, CheckCircle, Zap } from "lucide-react";
import { motion } from "framer-motion";

interface ToolCardProps {
  tool: SecurityTool;
  onStartScan: (toolId: string, target: string, scanType: string) => void;
  onStopScan: (toolId: string) => void;
  isLoading?: boolean;
}

export function ToolCard({ tool, onStartScan, onStopScan, isLoading = false }: ToolCardProps) {
  const [target, setTarget] = useState("");
  const [scanType, setScanType] = useState(tool.scanTypes?.[0] || "standard");
  const [showForm, setShowForm] = useState(false);

 

  // Status checks - SIMPLIFIED
  const isScanning = tool.status === "scanning";
  const isActive = tool.status === "active";
  const canStartScan = isActive && !isScanning && !isLoading;

  const handleStartScan = (e: React.MouseEvent) => {
    e.preventDefault();

    if (!target.trim()) {
      alert("Please enter a target");
      return;
    }


    onStartScan(tool.id, target, scanType);
    setTarget("");
    setShowForm(false);
  };

  const handleStopScan = (e: React.MouseEvent) => {
    e.preventDefault();
    onStopScan(tool.id);
    setShowForm(false);
  };

  const handleShowForm = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowForm(true);
  };

  const handleCancelForm = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowForm(false);
  };

  const getPlaceholder = () => {
    switch (tool.name) {
      case "nmap":
        return "Target: 192.168.1.0/24 or example.com";
      case "openvas":
        return "Target IP: 192.168.1.50";
      case "trivy":
        return "Image name: nginx:latest";
      case "zap":
        return "Target URL: http://localhost:8000";
      case "wireshark":
        return "Interface: eth0";
      case "wazuh":
        return "Agent name or ID";
      default:
        return "Enter target";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="p-4 hover:shadow-lg transition-shadow">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <tool.icon className="h-5 w-5 text-primary" />
            <h3 className="font-semibold text-foreground text-sm">
              {tool.displayName}
            </h3>
          </div>

          {/* Status Badge */}
          <Badge
            variant="outline"
            className={`text-xs whitespace-nowrap ${
              isScanning
                ? "bg-yellow-500/10 text-yellow-700 border-yellow-500/30 animate-pulse"
                : isActive
                  ? "bg-green-500/10 text-green-700 border-green-500/30"
                  : "bg-red-500/10 text-red-700 border-red-500/30"
            }`}
          >
            {isScanning && <Zap className="h-3 w-3 mr-1 animate-spin" />}
            {isActive && !isScanning && (
              <CheckCircle className="h-3 w-3 mr-1" />
            )}
            {!isActive && !isScanning && (
              <AlertCircle className="h-3 w-3 mr-1" />
            )}
            <span className="capitalize">{tool.status}</span>
          </Badge>
        </div>

        {/* Description */}
        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
          {tool.description}
        </p>

        {/* Last Scan Info */}
        {tool.lastScan && (
          <p className="text-xs text-muted-foreground mb-3">
            Last scan: {new Date(tool.lastScan).toLocaleDateString()}
          </p>
        )}

        {/* Main Action - SHOW/HIDE BASED ON STATUS */}
        {isScanning ? (
          // Show STOP button when scanning
          <Button
            onClick={handleStopScan}
            variant="destructive"
            size="sm"
            className="w-full text-xs"
            disabled={isLoading}
          >
            <Square className="h-4 w-4 mr-2" />
            Stop Scan
          </Button>
        ) : !showForm ? (
          // Show START button (if not showing form)
          <Button
            onClick={handleShowForm}
            disabled={!canStartScan}
            size="sm"
            className="w-full text-xs"
          >
            <Play className="h-4 w-4 mr-2" />
            {isActive ? "Start Scan" : "Tool Not Available"}
          </Button>
        ) : (
          // Show FORM (if showForm is true)
          <div className="space-y-2">
            {/* Target Input */}
            <Input
              placeholder={getPlaceholder()}
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              disabled={isLoading}
              className="text-xs h-8"
              autoFocus
            />

            {/* Scan Type Select */}
            {tool.scanTypes && tool.scanTypes.length > 0 && (
              <Select
                value={scanType}
                onValueChange={setScanType}
                disabled={isLoading}
              >
                <SelectTrigger className="text-xs h-8">
                  <SelectValue placeholder="Scan type" />
                </SelectTrigger>
                <SelectContent>
                  {tool.scanTypes.map((type) => (
                    <SelectItem key={type} value={type} className="text-xs">
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                onClick={handleStartScan}
                disabled={!target.trim() || isLoading}
                size="sm"
                className="flex-1 text-xs h-8"
              >
                <Play className="h-3 w-3 mr-1" />
                Start
              </Button>
              <Button
                onClick={handleCancelForm}
                variant="outline"
                size="sm"
                disabled={isLoading}
                className="flex-1 text-xs h-8"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

       
      </Card>
    </motion.div>
  );
}