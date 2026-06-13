import { apiClient } from './client';
import { ChatResponse, ChatMessage } from '../types';

export const chatApi = {
  sendMessage: async (analysisId: string, message: string) => {
    const response = await apiClient.post<ChatResponse>(
      `/api/v1/chat`,
      {
        analysis_id: analysisId,
        message: message,
      }
    );
    return response.data;
  },

  getChatHistory: async (analysisId: string) => {
    const response = await apiClient.get<ChatMessage[]>(
      `/api/v1/chat/${analysisId}`
    );
    return response.data;
  },
};
