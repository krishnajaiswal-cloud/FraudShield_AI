import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisApi } from '../api/analysisApi';


export const useAnalysisStatus = (analysisId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => analysisApi.getAnalysisStatus(analysisId),
    enabled,
    refetchInterval: 3000,
    retry: 3,
  });
};

export const useAnalysisReport = (analysisId: string) => {
  return useQuery({
    queryKey: ['report', analysisId],
    queryFn: () => analysisApi.getReport(analysisId),
    enabled: !!analysisId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export const useCreateAnalysis = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (filePath: string) => analysisApi.createAnalysis(filePath),
    onSuccess: (data) => {
      queryClient.setQueryData(['analysis', data.id], data);
    },
  });
};

export const useRunAnalysis = () => {
  return useMutation({
    mutationFn: (analysisId: string) => analysisApi.runAnalysis(analysisId),
  });
};
