import { useQuery } from '@tanstack/react-query';
import { securityApi } from '@/lib/api';

export interface Vulnerability {
  id: number;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  cve_id?: string;
  affected_asset: string;
  description: string;
  tool: number;
  tool_name: string;
  discovered_at: string;
}

export const useVulnerabilities = () => {
  return useQuery({
    queryKey: ['vulnerabilities'],
    queryFn: async () => {
      const response = await securityApi.getVulnerabilities();
      return response.data.results as Vulnerability[];
    },
    refetchInterval: 30000,
  });
};
