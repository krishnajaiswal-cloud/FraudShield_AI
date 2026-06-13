import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
export const ChatWindow = ({ messages, onSendMessage, isLoading = false, }) => {
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim() || isSending)
            return;
        setIsSending(true);
        try {
            await onSendMessage(input);
            setInput('');
        }
        finally {
            setIsSending(false);
        }
    };
    return (_jsxs("div", { className: "flex flex-col h-screen bg-cyber-darker", children: [_jsx("div", { className: "flex-1 overflow-y-auto p-4 space-y-4", children: messages.length === 0 ? (_jsx("div", { className: "flex items-center justify-center h-full text-gray-400", children: _jsx("p", { children: "No messages yet. Start a conversation!" }) })) : (_jsxs(_Fragment, { children: [messages.map((message, index) => (_jsx("div", { className: `flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`, children: _jsx("div", { className: `max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${message.role === 'user'
                                    ? 'bg-risk-critical text-white'
                                    : 'bg-cyber-card border border-cyber-border text-gray-300'}`, children: _jsx("p", { className: "text-sm leading-relaxed", children: message.content }) }) }, index))), isLoading && (_jsx("div", { className: "flex justify-start", children: _jsx("div", { className: "bg-cyber-card border border-cyber-border text-gray-300 px-4 py-2 rounded-lg", children: _jsx("p", { className: "text-sm", children: "Analyzing..." }) }) })), _jsx("div", { ref: messagesEndRef })] })) }), _jsx("div", { className: "border-t border-cyber-border p-4 bg-cyber-darker", children: _jsxs("form", { onSubmit: handleSendMessage, className: "flex gap-3", children: [_jsx("input", { type: "text", value: input, onChange: (e) => setInput(e.target.value), placeholder: "Ask a question about the APK...", disabled: isSending || isLoading, className: "flex-1 px-4 py-2 bg-cyber-card border border-cyber-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-risk-critical disabled:opacity-50" }), _jsx("button", { type: "submit", disabled: isSending || isLoading || !input.trim(), className: "px-4 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2", children: isSending || isLoading ? (_jsx(Loader2, { className: "w-4 h-4 animate-spin" })) : (_jsx(Send, { className: "w-4 h-4" })) })] }) })] }));
};
