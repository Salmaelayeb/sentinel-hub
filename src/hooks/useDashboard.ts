import { useQuery } from '@tanstack/react-query';
import { securityApi } from '@/lib/api';

export interface DashboardStats {
  total_vulnerabilities: number;
  critical_vulns: number;
  high_vulns: number;
  medium_vulns: number;
  low_vulns: number;
  active_tools: number;
  total_alerts: number;
  unacknowledged_alerts: number;
  hosts_discovered: number;
  last_scan_time: string | null;
}

export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await securityApi.getDashboardStats();
      return response.data as DashboardStats;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};
