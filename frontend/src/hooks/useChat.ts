import { useQuery, useMutation } from '@tanstack/react-query';
import { chatApi } from '../api/chatApi';

export const useChatHistory = (analysisId: string) => {
  return useQuery({
    queryKey: ['chat', analysisId],
    queryFn: () => chatApi.getChatHistory(analysisId),
    enabled: !!analysisId,
  });
};

export const useSendMessage = () => {
  return useMutation({
    mutationFn: ({ analysisId, message }: { analysisId: string; message: string }) =>
      chatApi.sendMessage(analysisId, message),
  });
};
