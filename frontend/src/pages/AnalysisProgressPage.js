import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import { MainLayout, Card, LoadingSpinner, ErrorState, Section } from '../components';
import { useAnalysisStatus } from '../hooks/useAnalysis';
export const AnalysisProgressPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { data, isLoading, error } = useAnalysisStatus(id || '', !!id);
    useEffect(() => {
        if (data && data.status === 'completed') {
            // Redirect to dashboard when analysis is complete
            const timer = setTimeout(() => {
                navigate(`/dashboard/${id}`);
            }, 1000);
            return () => clearTimeout(timer);
        }
        return;
    }, [data, id, navigate]);
    if (!id) {
        return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12", children: _jsx(ErrorState, { title: "Invalid Analysis ID", description: "No analysis ID provided" }) }) }));
    }
    if (error) {
        return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12", children: _jsx(ErrorState, { title: "Error Loading Analysis", description: error instanceof Error ? error.message : 'Unknown error occurred', onRetry: () => window.location.reload() }) }) }));
    }
    return (_jsx(MainLayout, { children: _jsx("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12", children: _jsx(Section, { title: "Analysis Progress", children: _jsxs("div", { className: "space-y-8", children: [_jsx(Card, { children: _jsx("div", { className: "text-center space-y-8", children: isLoading ? (_jsxs(_Fragment, { children: [_jsx(LoadingSpinner, { size: "lg" }), _jsxs("div", { children: [_jsx("h3", { className: "text-xl font-semibold text-white mb-2", children: "Analyzing Your APK" }), _jsx("p", { className: "text-gray-400", children: "Our security AI is scanning your application for vulnerabilities..." })] })] })) : data ? (_jsx(_Fragment, { children: data.status === 'completed' ? (_jsxs(_Fragment, { children: [_jsx(CheckCircle2, { className: "w-16 h-16 text-risk-safe mx-auto" }), _jsxs("div", { children: [_jsx("h3", { className: "text-xl font-semibold text-white mb-2", children: "Analysis Complete!" }), _jsx("p", { className: "text-gray-400", children: "Redirecting to your security report..." })] })] })) : data.status === 'failed' ? (_jsxs(_Fragment, { children: [_jsx(AlertCircle, { className: "w-16 h-16 text-risk-critical mx-auto" }), _jsxs("div", { children: [_jsx("h3", { className: "text-xl font-semibold text-white mb-2", children: "Analysis Failed" }), _jsx("p", { className: "text-gray-400", children: "An error occurred while analyzing your APK. Please try again." })] }), _jsx("button", { onClick: () => navigate('/scan'), className: "px-6 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors", children: "Try Again" })] })) : (_jsxs(_Fragment, { children: [_jsx(LoadingSpinner, { size: "lg" }), _jsxs("div", { children: [_jsx("h3", { className: "text-xl font-semibold text-white mb-2", children: "Processing..." }), _jsxs("p", { className: "text-gray-400", children: ["Status: ", data.status] })] })] })) })) : null }) }), _jsxs(Card, { children: [_jsx("h3", { className: "font-semibold text-white mb-4", children: "Analysis Details" }), _jsxs("div", { className: "space-y-3 text-sm", children: [_jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-400", children: "Analysis ID" }), _jsx("span", { className: "text-white font-mono", children: id })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-400", children: "Status" }), _jsx("span", { className: "text-white capitalize", children: data?.status || 'Unknown' })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-400", children: "File Path" }), _jsx("span", { className: "text-white font-mono text-xs truncate", children: data?.file_path || 'N/A' })] }), _jsxs("div", { className: "flex justify-between", children: [_jsx("span", { className: "text-gray-400", children: "Created" }), _jsx("span", { className: "text-white", children: data?.created_at ? new Date(data.created_at).toLocaleString() : 'N/A' })] })] })] }), _jsxs(Card, { children: [_jsx("h3", { className: "font-semibold text-white mb-4", children: "Analysis Steps" }), _jsx("div", { className: "space-y-3", children: [
                                        { step: 'Uploading', completed: true },
                                        { step: 'Extracting', completed: data?.status !== 'pending' },
                                        { step: 'Analyzing', completed: data?.status === 'completed' || data?.status === 'analyzing' },
                                        { step: 'Generating Report', completed: data?.status === 'completed' },
                                    ].map((item, index) => (_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: `w-2 h-2 rounded-full ${item.completed ? 'bg-risk-safe' : 'bg-gray-600'}` }), _jsx("span", { className: item.completed ? 'text-white' : 'text-gray-400', children: item.step })] }, index))) })] })] }) }) }) }));
};
