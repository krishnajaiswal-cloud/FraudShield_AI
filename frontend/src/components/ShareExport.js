import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { Share2, Copy, Download } from 'lucide-react';
import { Card } from './Common';
export const ShareExport = ({ analysisId, onExport }) => {
    const [copied, setCopied] = React.useState(false);
    const handleCopyLink = () => {
        const link = `${window.location.origin}/dashboard/${analysisId}`;
        navigator.clipboard.writeText(link);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    return (_jsx(Card, { children: _jsxs("div", { className: "flex items-center justify-between gap-4 flex-wrap", children: [_jsxs("div", { children: [_jsx("h3", { className: "font-semibold text-white mb-1", children: "Share Analysis" }), _jsx("p", { className: "text-gray-400 text-sm", children: "Export or share your security report" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsxs("button", { onClick: handleCopyLink, className: "flex items-center gap-2 px-3 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors", title: "Copy link to clipboard", children: [_jsx(Copy, { className: "w-4 h-4" }), copied ? 'Copied!' : 'Copy Link'] }), _jsxs("button", { onClick: onExport, className: "flex items-center gap-2 px-3 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors", title: "Export as PDF", children: [_jsx(Download, { className: "w-4 h-4" }), "Export"] }), _jsxs("button", { className: "flex items-center gap-2 px-3 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors", title: "Share analysis", children: [_jsx(Share2, { className: "w-4 h-4" }), "Share"] })] })] }) }));
};
