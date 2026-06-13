import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AlertTriangle } from 'lucide-react';
export const LoadingSpinner = ({ size = 'md', text = 'Loading...', }) => {
    const sizeClass = {
        sm: 'w-4 h-4',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
    }[size];
    return (_jsxs("div", { className: "flex flex-col items-center justify-center gap-4", children: [_jsx("div", { className: `${sizeClass} animate-spin`, children: _jsx("div", { className: "w-full h-full border-4 border-cyber-border border-t-risk-critical rounded-full" }) }), text && _jsx("p", { className: "text-gray-400 text-sm", children: text })] }));
};
export const EmptyState = ({ title, description, icon, }) => {
    return (_jsxs("div", { className: "flex flex-col items-center justify-center py-12 px-4", children: [icon && _jsx("div", { className: "mb-4 text-gray-500", children: icon }), _jsx("h3", { className: "text-lg font-semibold text-white mb-2", children: title }), description && _jsx("p", { className: "text-gray-400 text-sm", children: description })] }));
};
export const ErrorState = ({ title, description, onRetry, }) => {
    return (_jsxs("div", { className: "flex flex-col items-center justify-center py-12 px-4", children: [_jsx(AlertTriangle, { className: "w-12 h-12 text-risk-critical mb-4" }), _jsx("h3", { className: "text-lg font-semibold text-white mb-2", children: title }), description && _jsx("p", { className: "text-gray-400 text-sm mb-4", children: description }), onRetry && (_jsx("button", { onClick: onRetry, className: "px-4 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors", children: "Retry" }))] }));
};
export const Badge = ({ label, severity, size = 'md' }) => {
    const colors = {
        critical: 'bg-risk-critical/20 text-risk-critical border-risk-critical',
        high: 'bg-risk-high/20 text-risk-high border-risk-high',
        medium: 'bg-risk-medium/20 text-risk-medium border-risk-medium',
        low: 'bg-risk-low/20 text-risk-low border-risk-low',
        safe: 'bg-risk-safe/20 text-risk-safe border-risk-safe',
        info: 'bg-blue-500/20 text-blue-400 border-blue-500',
    };
    const sizeClass = {
        sm: 'px-2 py-1 text-xs',
        md: 'px-3 py-1.5 text-sm',
        lg: 'px-4 py-2 text-base',
    }[size];
    return (_jsx("span", { className: `${colors[severity]} ${sizeClass} border rounded-full inline-block font-medium`, children: label }));
};
export const Card = ({ children, className = '', onClick }) => {
    return (_jsx("div", { onClick: onClick, className: `bg-cyber-card border border-cyber-border rounded-xl p-6 hover:border-cyber-border/80 transition-all shadow-cyber ${onClick ? 'cursor-pointer' : ''} ${className}`, children: children }));
};
export const Section = ({ title, description, children, className = '', }) => {
    return (_jsxs("div", { className: className, children: [_jsxs("div", { className: "mb-6", children: [_jsx("h2", { className: "text-2xl font-bold text-white mb-2", children: title }), description && _jsx("p", { className: "text-gray-400", children: description })] }), children] }));
};
