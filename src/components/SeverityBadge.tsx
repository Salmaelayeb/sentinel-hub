import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const severityConfig = {
  critical: {
    bg: 'bg-critical/20',
    text: 'text-critical',
    border: 'border-critical/30',
    dot: 'bg-critical'
  },
  high: {
    bg: 'bg-high/20',
    text: 'text-high',
    border: 'border-high/30',
    dot: 'bg-high'
  },
  medium: {
    bg: 'bg-medium/20',
    text: 'text-medium',
    border: 'border-medium/30',
    dot: 'bg-medium'
  },
  low: {
    bg: 'bg-low/20',
    text: 'text-low',
    border: 'border-low/30',
    dot: 'bg-low'
  },
  info: {
    bg: 'bg-info/20',
    text: 'text-info',
    border: 'border-info/30',
    dot: 'bg-info'
  }
};

const sizeConfig = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
  lg: 'text-base px-3 py-1.5'
};

export function SeverityBadge({ severity, className, size = 'sm' }: SeverityBadgeProps) {
  const config = severityConfig[severity];
  
  return (
    <span 
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-mono uppercase tracking-wider",
        config.bg,
        config.text,
        config.border,
        sizeConfig[size],
        className
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full animate-pulse", config.dot)} />
      {severity}
    </span>
  );
}
