import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import securityApi, { 
  DjangoDashboardStats, 
  DjangoVulnerability, 
  DjangoSecurityAlert, 
  DjangoSecurityTool,
  DjangoScanResult
} from '@/lib/api';
import { toast } from 'sonner';

// Query keys for cache management
export const queryKeys = {
  dashboard: ['dashboard'] as const,
  vulnerabilities: ['vulnerabilities'] as const,
  vulnerabilitiesBySeverity: ['vulnerabilities', 'by-severity'] as const,
  recentVulnerabilities: ['vulnerabilities', 'recent'] as const,
  alerts: ['alerts'] as const,
  unacknowledgedAlerts: ['alerts', 'unacknowledged'] as const,
  tools: ['tools'] as const,
  scans: ['scans'] as const,
  hosts: ['hosts'] as const,
  metrics: ['metrics'] as const,
};

// Dashboard stats hook
export function useDashboardStats() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: async () => {
      const { data, error } = await securityApi.getDashboardStats();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 30000,
    retry: 3,
  });
}

// Vulnerabilities hooks
export function useVulnerabilities() {
  return useQuery({
    queryKey: queryKeys.vulnerabilities,
    queryFn: async () => {
      const { data, error } = await securityApi.getVulnerabilities();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 60000,
    retry: 3,
  });
}

export function useVulnerabilitiesBySeverity() {
  return useQuery({
    queryKey: queryKeys.vulnerabilitiesBySeverity,
    queryFn: async () => {
      const { data, error } = await securityApi.getVulnerabilitiesBySeverity();
      if (error) throw new Error(error);
      return data;
    },
  });
}

export function useRecentVulnerabilities() {
  return useQuery({
    queryKey: queryKeys.recentVulnerabilities,
    queryFn: async () => {
      const { data, error } = await securityApi.getRecentVulnerabilities();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 30000,
  });
}

export function useVulnerabilityTrend() {
  return useQuery({
    queryKey: ['vulnerabilities', 'trend'] as const,
    queryFn: async () => {
      const { data, error } = await securityApi.getVulnerabilityTrend();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 60000,
  });
}

// Alerts hooks
export function useAlerts() {
  return useQuery({
    queryKey: queryKeys.alerts,
    queryFn: async () => {
      const { data, error } = await securityApi.getAlerts();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 15000,
    retry: 3,
  });
}

export function useUnacknowledgedAlerts() {
  return useQuery({
    queryKey: queryKeys.unacknowledgedAlerts,
    queryFn: async () => {
      const { data, error } = await securityApi.getUnacknowledgedAlerts();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 15000,
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (alertId: number) => {
      const { data, error } = await securityApi.acknowledgeAlert(alertId);
      if (error) throw new Error(error);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alerts });
      queryClient.invalidateQueries({ queryKey: queryKeys.unacknowledgedAlerts });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
      toast.success('Alert acknowledged');
    },
    onError: (error) => {
      toast.error('Failed to acknowledge alert', { description: error.message });
    },
  });
}

// Security Tools hooks
export function useSecurityTools() {
  return useQuery({
    queryKey: queryKeys.tools,
    queryFn: async () => {
      const { data, error } = await securityApi.getTools();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 30000,
    retry: 3,
  });
}

export function useStartScan() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ toolId, target, scanType }: { toolId: number; target: string; scanType: string }) => {
      const { data, error } = await securityApi.startScan(toolId, target, scanType);
      if (error) throw new Error(error);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tools });
      queryClient.invalidateQueries({ queryKey: queryKeys.scans });
      toast.success('Scan started', { description: data?.message });
    },
    onError: (error) => {
      toast.error('Failed to start scan', { description: error.message });
    },
  });
}

export function useStopScan() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (toolId: number) => {
      const { data, error } = await securityApi.stopScan(toolId);
      if (error) throw new Error(error);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tools });
      queryClient.invalidateQueries({ queryKey: queryKeys.scans });
      toast.info('Scan stopped');
    },
    onError: (error) => {
      toast.error('Failed to stop scan', { description: error.message });
    },
  });
}

// Scans hooks
export function useScans() {
  return useQuery({
    queryKey: queryKeys.scans,
    queryFn: async () => {
      const { data, error } = await securityApi.getScans();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 10000,
    retry: 3,
  });
}

// Hosts hook
export function useHosts() {
  return useQuery({
    queryKey: queryKeys.hosts,
    queryFn: async () => {
      const { data, error } = await securityApi.getHosts();
      if (error) throw new Error(error);
      return data;
    },
  });
}

// Metrics hook
export function useMetrics() {
  return useQuery({
    queryKey: queryKeys.metrics,
    queryFn: async () => {
      const { data, error } = await securityApi.getMetrics();
      if (error) throw new Error(error);
      return data;
    },
    refetchInterval: 60000,
  });
}
