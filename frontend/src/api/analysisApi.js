import { apiClient } from './client';
export const analysisApi = {
    createAnalysis: async (filePath) => {
        const response = await apiClient.post('/api/v1/analysis', { file_path: filePath });
        return response.data;
    },
    runAnalysis: async (analysisId) => {
        const response = await apiClient.post(`/api/v1/analysis/${analysisId}/run`, {});
        return response.data;
    },
    getAnalysisStatus: async (analysisId) => {
        const response = await apiClient.get(`/api/v1/analysis/${analysisId}`);
        return response.data;
    },
    getReport: async (analysisId) => {
        const response = await apiClient.get(`/api/v1/analysis/${analysisId}`);
        return response.data;
    },
};
