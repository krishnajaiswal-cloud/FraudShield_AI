import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart3, MessageCircle, Home, ChevronRight } from 'lucide-react';
export const DashboardNav = ({ currentPage = 'dashboard' }) => {
    const { analysisId } = useParams();
    const navigate = useNavigate();
    if (!analysisId)
        return null;
    return (_jsx("div", { className: "bg-cyber-darker border-b border-cyber-border", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: _jsxs("div", { className: "flex items-center gap-8 h-16 overflow-x-auto", children: [_jsxs("button", { onClick: () => navigate('/'), className: "flex items-center gap-2 text-gray-400 hover:text-white transition-colors whitespace-nowrap", children: [_jsx(Home, { className: "w-4 h-4" }), _jsx("span", { className: "text-sm", children: "Home" })] }), _jsx(ChevronRight, { className: "w-4 h-4 text-gray-600 flex-shrink-0" }), _jsxs("button", { onClick: () => navigate(`/dashboard/${analysisId}`), className: `flex items-center gap-2 whitespace-nowrap pb-4 border-b-2 transition-colors ${currentPage === 'dashboard'
                            ? 'text-white border-risk-critical'
                            : 'text-gray-400 hover:text-white border-transparent'}`, children: [_jsx(BarChart3, { className: "w-4 h-4" }), _jsx("span", { className: "text-sm", children: "Dashboard" })] }), _jsxs("button", { onClick: () => navigate(`/chat/${analysisId}`), className: `flex items-center gap-2 whitespace-nowrap pb-4 border-b-2 transition-colors ${currentPage === 'chat'
                            ? 'text-white border-risk-critical'
                            : 'text-gray-400 hover:text-white border-transparent'}`, children: [_jsx(MessageCircle, { className: "w-4 h-4" }), _jsx("span", { className: "text-sm", children: "Chat with AI" })] })] }) }) }));
};
