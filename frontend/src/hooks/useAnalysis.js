import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisApi } from '../api/analysisApi';
export const useAnalysisStatus = (analysisId, enabled = true) => {
    return useQuery({
        queryKey: ['analysis', analysisId],
        queryFn: () => analysisApi.getAnalysisStatus(analysisId),
        enabled,
        refetchInterval: 3000,
        retry: 3,
    });
};
export const useAnalysisReport = (analysisId) => {
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
        mutationFn: (filePath) => analysisApi.createAnalysis(filePath),
        onSuccess: (data) => {
            queryClient.setQueryData(['analysis', data.id], data);
        },
    });
};
export const useRunAnalysis = () => {
    return useMutation({
        mutationFn: (analysisId) => analysisApi.runAnalysis(analysisId),
    });
};
