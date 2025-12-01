import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { securityApi } from '@/lib/api';
import { toast } from '@/hooks/use-toast';

export interface Tool {
  id: number;
  name: string;
  status: 'active' | 'inactive' | 'scanning' | 'error';
  description: string;
  last_scan?: string;
  config: any;
}

export const useTools = () => {
  return useQuery({
    queryKey: ['tools'],
    queryFn: async () => {
      const response = await securityApi.getTools();
      return response.data.results as Tool[];
    },
    refetchInterval: 15000,
  });
};

export const useStartScan = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (toolId: number) => securityApi.startScan(toolId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tools'] });
      toast({
        title: "Scan started",
        description: "The security scan has been initiated.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to start scan.",
        variant: "destructive",
      });
    },
  });
};

export const useStopScan = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (toolId: number) => securityApi.stopScan(toolId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tools'] });
      toast({
        title: "Scan stopped",
        description: "The security scan has been stopped.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to stop scan.",
        variant: "destructive",
      });
    },
  });
};
