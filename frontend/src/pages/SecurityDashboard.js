import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Package, AlertTriangle, Database, Globe } from 'lucide-react';
import { MainLayout, Card, Section, LoadingSpinner, ErrorState, RiskScoreCard, FindingCard, PermissionCard, URLCard, RiskReasonCard, SecurityAnalystCard, RiskDistributionChart, FindingsBySeverityChart, PermissionsRiskChart, Badge, } from '../components';
import { useAnalysisReport } from '../hooks/useAnalysis';
import { formatBytes } from '../utils/risk';
export const SecurityDashboard = () => {
    const { analysisId } = useParams();
    const { data: report, isLoading, error } = useAnalysisReport(analysisId || '');
    const [filterSeverity, setFilterSeverity] = useState(null);
    const filteredFindings = useMemo(() => {
        if (!report?.findings)
            return [];
        if (!filterSeverity)
            return report.findings;
        return report.findings.filter(f => f.risk_level === filterSeverity);
    }, [report?.findings, filterSeverity]);
    if (isLoading) {
        return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex items-center justify-center min-h-[60vh]", children: _jsx(LoadingSpinner, { size: "lg", text: "Loading security report..." }) }) }));
    }
    if (error || !report) {
        return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12", children: _jsx(ErrorState, { title: "Failed to Load Report", description: error instanceof Error ? error.message : 'Unknown error occurred' }) }) }));
    }
    const riskScore = report.risk_assessment.risk_score;
    const severity = report.risk_assessment.severity;
    return (_jsx(MainLayout, { children: _jsxs("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12", children: [_jsx(Section, { title: "APK Information", children: _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6", children: [
                            { label: 'App Name', value: report.app_name },
                            { label: 'Package Name', value: report.package_name },
                            { label: 'Version', value: `${report.version_name} (${report.version_code})` },
                            { label: 'File Size', value: formatBytes(report.file_size) },
                        ].map((item, index) => (_jsx(Card, { children: _jsxs("div", { className: "text-center", children: [_jsx("p", { className: "text-gray-400 text-sm mb-2", children: item.label }), _jsx("p", { className: "text-white font-semibold break-words", children: item.value })] }) }, index))) }) }), _jsx(Section, { title: "Security Assessment", children: _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-6", children: [_jsx("div", { className: "lg:col-span-1", children: _jsx(RiskScoreCard, { score: riskScore, severity: severity }) }), _jsx("div", { className: "lg:col-span-2 grid grid-cols-2 gap-4", children: [
                                    {
                                        icon: AlertTriangle,
                                        label: 'Total Findings',
                                        value: report.findings?.length || 0,
                                    },
                                    {
                                        icon: Database,
                                        label: 'Dangerous Permissions',
                                        value: report.permissions.dangerous_permissions,
                                    },
                                    {
                                        icon: Globe,
                                        label: 'Extracted URLs',
                                        value: report.urls_and_domains.url_count,
                                    },
                                    {
                                        icon: Package,
                                        label: 'Components Found',
                                        value: (report.components.activities?.length || 0) +
                                            (report.components.services?.length || 0) +
                                            (report.components.broadcast_receivers?.length || 0) +
                                            (report.components.content_providers?.length || 0),
                                    },
                                ].map((stat, index) => {
                                    const Icon = stat.icon;
                                    return (_jsx(Card, { children: _jsxs("div", { className: "flex items-center gap-4", children: [_jsx(Icon, { className: "w-8 h-8 text-risk-critical flex-shrink-0" }), _jsxs("div", { children: [_jsx("p", { className: "text-gray-400 text-sm", children: stat.label }), _jsx("p", { className: "text-2xl font-bold text-white", children: stat.value })] })] }) }, index));
                                }) })] }) }), _jsx(Section, { title: "Security Analytics", children: _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs(Card, { children: [_jsx("h3", { className: "text-lg font-semibold text-white mb-4", children: "Risk Distribution" }), _jsx(RiskDistributionChart, { findings: report.findings || [] })] }), _jsxs(Card, { children: [_jsx("h3", { className: "text-lg font-semibold text-white mb-4", children: "Findings by Severity" }), _jsx(FindingsBySeverityChart, { findings: report.findings || [] })] }), _jsxs(Card, { className: "lg:col-span-2", children: [_jsx("h3", { className: "text-lg font-semibold text-white mb-4", children: "Permission Risk Analysis" }), _jsx(PermissionsRiskChart, { permissions: report.permissions.all_permissions, dangerousPermissions: report.permissions.dangerous_list })] })] }) }), _jsx(Section, { title: "Security Findings", children: _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex flex-wrap gap-2", children: [['critical', 'high', 'medium', 'low', 'info'].map((severity_filter) => (_jsx("button", { onClick: () => setFilterSeverity(filterSeverity === severity_filter ? null : severity_filter), className: `px-4 py-2 rounded-lg transition-colors capitalize ${filterSeverity === severity_filter
                                            ? 'bg-risk-critical text-white'
                                            : 'bg-cyber-card text-gray-300 hover:bg-cyber-border'}`, children: severity_filter }, severity_filter))), filterSeverity && (_jsx("button", { onClick: () => setFilterSeverity(null), className: "px-4 py-2 rounded-lg bg-cyber-card text-gray-300 hover:bg-cyber-border transition-colors", children: "Clear" }))] }), _jsx("div", { className: "space-y-4", children: filteredFindings.length > 0 ? (filteredFindings.map((finding, index) => (_jsx(FindingCard, { finding: finding }, index)))) : (_jsx(Card, { children: _jsx("p", { className: "text-center text-gray-400 py-8", children: "No findings for this filter" }) })) })] }) }), report.report_json?.security_analyst?.permission_explanations &&
                    report.report_json.security_analyst.permission_explanations.length > 0 && (_jsx(Section, { title: "Permission Analysis", children: _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6", children: report.report_json.security_analyst.permission_explanations.map((perm, index) => (_jsx(PermissionCard, { permission: perm }, index))) }) })), report.urls_and_domains?.urls &&
                    report.urls_and_domains.urls.length > 0 && (_jsx(Section, { title: "URL Analysis", children: _jsx("div", { className: "space-y-4", children: report.urls_and_domains.urls.map((url, index) => (_jsx(URLCard, { url: url, isSuspicious: report.urls_and_domains.suspicious_urls?.includes(url) || false }, index))) }) })), report.report_json?.security_analyst && (_jsx(Section, { title: "Security Analyst Assessment", className: "bg-gradient-to-br from-cyber-card/40 to-cyber-darker/40 rounded-xl p-6 border border-cyber-border", children: _jsxs("div", { className: "space-y-6", children: [_jsx(SecurityAnalystCard, { title: "Security Assessment", content: report.report_json.security_analyst.analyst_narrative }), report.report_json.security_analyst.executive_summary && (_jsx(Card, { children: _jsxs("div", { className: "space-y-4", children: [_jsx("h3", { className: "text-lg font-semibold text-white", children: "Executive Summary" }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { children: [_jsx("p", { className: "text-gray-400 text-sm mb-1", children: "Risk Level" }), _jsx(Badge, { label: report.report_json.security_analyst.executive_summary.risk_level, severity: report.report_json.security_analyst.executive_summary.risk_level.toLowerCase(), size: "lg" })] }), _jsxs("div", { children: [_jsx("p", { className: "text-gray-400 text-sm mb-1", children: "Summary" }), _jsx("p", { className: "text-white", children: report.report_json.security_analyst.executive_summary.summary })] }), _jsxs("div", { children: [_jsx("p", { className: "text-gray-400 text-sm mb-1", children: "Recommendation" }), _jsx("p", { className: "text-white", children: report.report_json.security_analyst.executive_summary.recommendation })] })] })] }) })), report.report_json.security_analyst.risk_reasons &&
                                report.report_json.security_analyst.risk_reasons.length > 0 && (_jsxs("div", { children: [_jsx("h3", { className: "text-lg font-semibold text-white mb-4", children: "Risk Reasons" }), _jsx("div", { className: "space-y-4", children: report.report_json.security_analyst.risk_reasons.map((reason, index) => (_jsx(RiskReasonCard, { reason: reason }, index))) })] })), report.report_json.security_analyst.recommendations &&
                                report.report_json.security_analyst.recommendations.length > 0 && (_jsx(SecurityAnalystCard, { title: "Recommendations", content: report.report_json.security_analyst.recommendations }))] }) }))] }) }));
};
