import { apiClient } from './client';
export const chatApi = {
    sendMessage: async (analysisId, message) => {
        const response = await apiClient.post(`/api/v1/chat`, {
            analysis_id: analysisId,
            message: message,
        });
        return response.data;
    },
    getChatHistory: async (analysisId) => {
        const response = await apiClient.get(`/api/v1/chat/${analysisId}`);
        return response.data;
    },
};
