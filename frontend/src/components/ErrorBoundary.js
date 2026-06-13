import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Card } from './Common';
export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }
    render() {
        if (this.state.hasError) {
            return (_jsx("div", { className: "min-h-screen bg-cyber-dark flex items-center justify-center px-4", children: _jsxs(Card, { className: "max-w-md", children: [_jsxs("div", { className: "flex items-center gap-4 mb-4", children: [_jsx(AlertTriangle, { className: "w-8 h-8 text-risk-critical flex-shrink-0" }), _jsx("h1", { className: "text-2xl font-bold text-white", children: "Something went wrong" })] }), _jsx("p", { className: "text-gray-400 mb-6", children: this.state.error?.message || 'An unexpected error occurred' }), _jsx("button", { onClick: () => window.location.reload(), className: "w-full px-4 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors", children: "Reload Page" })] }) }));
        }
        return this.props.children;
    }
}
