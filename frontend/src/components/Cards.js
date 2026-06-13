import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AlertTriangle, AlertCircle, Info, CheckCircle, Shield } from 'lucide-react';
import { Badge, Card } from './Common';
import { getRiskColor } from '../utils/risk';
export const RiskScoreCard = ({ score, severity }) => {
    const colors = {
        critical: 'from-risk-critical to-risk-critical/60',
        high: 'from-risk-high to-risk-high/60',
        medium: 'from-risk-medium to-risk-medium/60',
        low: 'from-risk-low to-risk-low/60',
        safe: 'from-risk-safe to-risk-safe/60',
    };
    const icons = {
        critical: AlertTriangle,
        high: AlertCircle,
        medium: AlertCircle,
        low: Info,
        safe: CheckCircle,
    };
    const Icon = icons[severity];
    return (_jsxs(Card, { className: "relative overflow-hidden", children: [_jsx("div", { className: `absolute inset-0 bg-gradient-to-br ${colors[severity]} opacity-5` }), _jsxs("div", { className: "relative", children: [_jsxs("div", { className: "flex items-center justify-between mb-4", children: [_jsx("h3", { className: "text-lg font-semibold text-white", children: "Risk Score" }), _jsx(Icon, { className: `w-6 h-6 text-${severity === 'critical' ? 'risk-critical' : severity === 'high' ? 'risk-high' : severity === 'medium' ? 'risk-medium' : severity === 'low' ? 'risk-low' : 'risk-safe'}` })] }), _jsxs("div", { className: "mb-4", children: [_jsx("div", { className: "text-5xl font-bold text-white mb-2", children: score }), _jsx(Badge, { label: severity.charAt(0).toUpperCase() + severity.slice(1), severity: severity, size: "lg" })] }), _jsx("div", { className: "w-full bg-cyber-darker rounded-full h-2 overflow-hidden", children: _jsx("div", { className: `h-full bg-gradient-to-r ${colors[severity]}`, style: { width: `${score}%` } }) })] })] }));
};
export const FindingCard = ({ finding, onClick }) => {
    return (_jsx(Card, { onClick: onClick, children: _jsxs("div", { className: "flex items-start justify-between gap-4", children: [_jsxs("div", { children: [_jsx("h4", { className: "font-semibold text-white mb-1", children: finding.type }), _jsx("p", { className: "text-sm text-gray-400 mb-3", children: finding.description }), _jsxs("div", { className: "flex items-center gap-2 flex-wrap", children: [_jsx(Badge, { label: finding.category, severity: finding.risk_level, size: "sm" }), finding.indicator && (_jsx("span", { className: "text-xs text-gray-400 bg-cyber-darker px-2 py-1 rounded", children: finding.indicator }))] })] }), _jsx("div", { className: `px-3 py-1 rounded-lg text-sm font-medium flex-shrink-0 ${getRiskColor(finding.risk_level)}`, children: finding.risk_level })] }) }));
};
export const PermissionCard = ({ permission }) => {
    return (_jsx(Card, { children: _jsx("div", { className: "flex items-start justify-between gap-4", children: _jsxs("div", { className: "flex-1", children: [_jsx("h4", { className: "font-semibold text-white mb-2", children: permission.permission.split('.').pop() }), _jsx("p", { className: "text-sm text-gray-400 mb-4", children: permission.explanation }), _jsx("div", { className: "flex items-center gap-2", children: _jsx(Badge, { label: permission.risk, severity: permission.risk, size: "sm" }) })] }) }) }));
};
export const URLCard = ({ url, isSuspicious }) => {
    return (_jsx(Card, { children: _jsx("div", { className: "flex items-start justify-between gap-4", children: _jsxs("div", { className: "flex-1 break-all", children: [_jsx("h4", { className: "font-mono text-sm text-blue-400 mb-2", children: url }), isSuspicious && (_jsx(Badge, { label: "Suspicious", severity: "high", size: "sm" }))] }) }) }));
};
export const RiskReasonCard = ({ reason }) => {
    return (_jsx(Card, { children: _jsxs("div", { className: "flex gap-4", children: [_jsx("div", { className: `flex-shrink-0 w-1 rounded-full bg-gradient-to-b ${reason.severity === 'critical'
                        ? 'from-risk-critical to-risk-critical/50'
                        : reason.severity === 'high'
                            ? 'from-risk-high to-risk-high/50'
                            : reason.severity === 'medium'
                                ? 'from-risk-medium to-risk-medium/50'
                                : reason.severity === 'low'
                                    ? 'from-risk-low to-risk-low/50'
                                    : 'from-blue-500 to-blue-500/50'}` }), _jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 mb-2", children: [_jsx("h4", { className: "font-semibold text-white", children: reason.reason }), _jsx(Badge, { label: reason.severity, severity: reason.severity, size: "sm" })] }), reason.indicator && (_jsx("p", { className: "text-sm text-gray-400", children: reason.indicator }))] })] }) }));
};
export const SecurityAnalystCard = ({ title, content, }) => {
    return (_jsxs(Card, { children: [_jsxs("div", { className: "mb-4 flex items-center gap-2", children: [_jsx(Shield, { className: "w-5 h-5 text-risk-critical" }), _jsx("h3", { className: "text-lg font-semibold text-white", children: title })] }), Array.isArray(content) ? (_jsx("ul", { className: "space-y-2", children: content.map((item, index) => (_jsxs("li", { className: "text-gray-300 flex items-start gap-2", children: [_jsx("span", { className: "text-risk-critical mt-1 flex-shrink-0", children: "\u2022" }), _jsx("span", { children: item })] }, index))) })) : (_jsx("p", { className: "text-gray-300 leading-relaxed", children: content }))] }));
};
