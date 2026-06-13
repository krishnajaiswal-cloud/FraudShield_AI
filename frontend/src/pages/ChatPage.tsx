import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MainLayout, ChatWindow, LoadingSpinner, ErrorState } from '../components';
import { useSendMessage, useChatHistory } from '../hooks/useChat';
import { ChatMessage } from '../types';

export const ChatPage: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const { data: chatHistory, isLoading: isLoadingHistory } = useChatHistory(analysisId || '');
  const sendMessage = useSendMessage();
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Load chat history
  useEffect(() => {
    if (chatHistory) {
      setMessages(chatHistory);
    }
  }, [chatHistory]);

  const handleSendMessage = async (message: string) => {
    if (!analysisId) return;

    // Add user message to local state
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await sendMessage.mutateAsync({
        analysisId,
        message,
      });

      // Add assistant response to local state
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.content,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Optionally show error message to user
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I failed to process your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  if (!analysisId) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <ErrorState
            title="Invalid Analysis ID"
            description="No analysis ID provided"
          />
        </div>
      </MainLayout>
    );
  }

  if (isLoadingHistory) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex items-center justify-center min-h-[60vh]">
          <LoadingSpinner size="lg" text="Loading chat..." />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="h-screen bg-cyber-darker">
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={sendMessage.isPending}
        />
      </div>
    </MainLayout>
  );
};
