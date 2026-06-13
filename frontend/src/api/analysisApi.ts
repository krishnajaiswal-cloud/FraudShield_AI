import { apiClient } from './client';
import { AnalysisCreateResponse, AnalysisReport } from '../types';

export const analysisApi = {
  createAnalysis: async (filePath: string) => {
    const response = await apiClient.post<AnalysisCreateResponse>(
      '/api/v1/analysis',
      { file_path: filePath }
    );
    return response.data;
  },

  runAnalysis: async (analysisId: string) => {
    const response = await apiClient.post(
      `/api/v1/analysis/${analysisId}/run`,
      {}
    );
    return response.data;
  },

  getAnalysisStatus: async (analysisId: string) => {
    const response = await apiClient.get<AnalysisReport>(
      `/api/v1/analysis/${analysisId}`
    );
    return response.data;
  },

  getReport: async (analysisId: string) => {
    const response = await apiClient.get<AnalysisReport>(
      `/api/v1/analysis/${analysisId}`
    );
    return response.data;
  },
};
