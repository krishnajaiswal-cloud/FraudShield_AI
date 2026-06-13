import { jsx as _jsx } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MainLayout, ChatWindow, LoadingSpinner, ErrorState } from '../components';
import { useSendMessage, useChatHistory } from '../hooks/useChat';
export const ChatPage = () => {
    const { analysisId } = useParams();
    const { data: chatHistory, isLoading: isLoadingHistory } = useChatHistory(analysisId || '');
    const sendMessage = useSendMessage();
    const [messages, setMessages] = useState([]);
    // Load chat history
    useEffect(() => {
        if (chatHistory) {
            setMessages(chatHistory);
        }
    }, [chatHistory]);
    const handleSendMessage = async (message) => {
        if (!analysisId)
            return;
        // Add user message to local state
        const userMessage = {
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
            const assistantMessage = {
                role: 'assistant',
                content: response.content,
                timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, assistantMessage]);
        }
        catch (error) {
            console.error('Failed to send message:', error);
            // Optionally show error message to user
            const errorMessage = {
                role: 'assistant',
                content: 'Sorry, I failed to process your request. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, errorMessage]);
        }
    };
    if (!analysisId) {
        return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12", children: _jsx(ErrorState, { title: "Invalid Analysis ID", description: "No analysis ID provided" }) }) }));
    }
    if (isLoadingHistory) {
        return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex items-center justify-center min-h-[60vh]", children: _jsx(LoadingSpinner, { size: "lg", text: "Loading chat..." }) }) }));
    }
    return (_jsx(MainLayout, { children: _jsx("div", { className: "h-screen bg-cyber-darker", children: _jsx(ChatWindow, { messages: messages, onSendMessage: handleSendMessage, isLoading: sendMessage.isPending }) }) }));
};
