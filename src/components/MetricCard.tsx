import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  variant?: 'default' | 'critical' | 'warning' | 'success' | 'info';
  className?: string;
}

const variantStyles = {
  default: {
    iconBg: 'bg-primary/10',
    iconColor: 'text-primary',
    glow: 'hover:shadow-glow-primary'
  },
  critical: {
    iconBg: 'bg-critical/10',
    iconColor: 'text-critical',
    glow: 'hover:shadow-glow-critical'
  },
  warning: {
    iconBg: 'bg-high/10',
    iconColor: 'text-high',
    glow: 'hover:shadow-[0_0_20px_hsl(var(--high)/0.3)]'
  },
  success: {
    iconBg: 'bg-low/10',
    iconColor: 'text-low',
    glow: 'hover:shadow-glow-success'
  },
  info: {
    iconBg: 'bg-info/10',
    iconColor: 'text-info',
    glow: 'hover:shadow-[0_0_20px_hsl(var(--info)/0.3)]'
  }
};

export function MetricCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  variant = 'default',
  className 
}: MetricCardProps) {
  const styles = variantStyles[variant];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn(
        "relative overflow-hidden rounded-lg border border-border bg-card p-6",
        "transition-all duration-300 card-glow",
        styles.glow,
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold font-mono tracking-tight text-foreground">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          )}
        </div>
        <div className={cn("rounded-lg p-3", styles.iconBg)}>
          <Icon className={cn("h-6 w-6", styles.iconColor)} />
        </div>
      </div>
      
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent to-primary/5 pointer-events-none" />
    </motion.div>
  );
}
