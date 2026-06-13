import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Shield, Zap, BarChart3, Users } from 'lucide-react';
import { MainLayout, Card, Section } from '../components';
export const LandingPage = () => {
    const navigate = useNavigate();
    return (_jsxs(MainLayout, { children: [_jsx("section", { className: "min-h-screen bg-gradient-to-b from-cyber-darker via-cyber-dark to-cyber-darker flex items-center", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full", children: _jsxs("div", { className: "text-center space-y-8", children: [_jsxs("div", { children: [_jsxs("h1", { className: "text-5xl md:text-7xl font-bold text-white mb-6 leading-tight", children: ["Advanced APK", ' ', _jsx("span", { className: "text-transparent bg-clip-text bg-gradient-to-r from-risk-critical to-risk-high", children: "Security Analysis" })] }), _jsx("p", { className: "text-xl text-gray-400 max-w-2xl mx-auto", children: "Analyze Android applications for security vulnerabilities, malware indicators, and privacy risks using advanced AI-powered detection." })] }), _jsxs("div", { className: "flex flex-col sm:flex-row gap-4 justify-center pt-8", children: [_jsxs("button", { onClick: () => navigate('/scan'), className: "px-8 py-4 bg-gradient-to-r from-risk-critical to-risk-high text-white rounded-lg font-semibold hover:shadow-neon-red transition-all flex items-center justify-center gap-2", children: ["Analyze APK", _jsx(ArrowRight, { className: "w-5 h-5" })] }), _jsx("button", { className: "px-8 py-4 border border-cyber-border text-white rounded-lg font-semibold hover:border-cyber-border/50 transition-colors", children: "Learn More" })] })] }) }) }), _jsx("section", { className: "py-20 bg-cyber-dark", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: _jsx(Section, { title: "Comprehensive Security Analysis", description: "FraudShield AI provides detailed insights into every aspect of your APK", children: _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6", children: [
                                {
                                    icon: Shield,
                                    title: 'Permission Analysis',
                                    description: 'Identify dangerous permissions and their security implications',
                                },
                                {
                                    icon: Zap,
                                    title: 'Malware Detection',
                                    description: 'Advanced detection of malware signatures and suspicious behaviors',
                                },
                                {
                                    icon: BarChart3,
                                    title: 'Risk Scoring',
                                    description: 'Get a comprehensive risk score based on multiple factors',
                                },
                                {
                                    icon: Users,
                                    title: 'Privacy Analysis',
                                    description: 'Understand how your data is being accessed and transmitted',
                                },
                            ].map((feature, index) => (_jsxs(Card, { children: [_jsx(feature.icon, { className: "w-8 h-8 text-risk-critical mb-4" }), _jsx("h3", { className: "text-lg font-semibold text-white mb-2", children: feature.title }), _jsx("p", { className: "text-gray-400 text-sm", children: feature.description })] }, index))) }) }) }) }), _jsx("section", { className: "py-20 bg-cyber-darker", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: _jsx(Section, { title: "How It Works", description: "Simple, secure, and fast APK analysis", children: _jsx("div", { className: "grid grid-cols-1 md:grid-cols-4 gap-6", children: [
                                { number: '1', title: 'Upload', description: 'Select your APK file' },
                                { number: '2', title: 'Analyze', description: 'AI analyzes permissions & code' },
                                { number: '3', title: 'Review', description: 'Get detailed security report' },
                                { number: '4', title: 'Decide', description: 'Make informed decisions' },
                            ].map((step, index) => (_jsxs("div", { className: "relative", children: [_jsx(Card, { children: _jsxs("div", { className: "text-center", children: [_jsx("div", { className: "w-12 h-12 bg-gradient-to-br from-risk-critical to-risk-high rounded-full flex items-center justify-center mx-auto mb-4 text-lg font-bold text-white", children: step.number }), _jsx("h3", { className: "font-semibold text-white mb-2", children: step.title }), _jsx("p", { className: "text-gray-400 text-sm", children: step.description })] }) }), index < 3 && (_jsx("div", { className: "hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2", children: _jsx(ArrowRight, { className: "w-6 h-6 text-cyber-border" }) }))] }, index))) }) }) }) }), _jsx("section", { className: "py-20 bg-cyber-dark", children: _jsxs("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center", children: [_jsx("h2", { className: "text-4xl font-bold text-white mb-6", children: "Secure Your Android Ecosystem Today" }), _jsx("p", { className: "text-xl text-gray-400 mb-8 max-w-2xl mx-auto", children: "Join thousands of developers and security professionals who trust FraudShield AI for comprehensive APK security analysis." }), _jsxs("button", { onClick: () => navigate('/scan'), className: "px-8 py-4 bg-gradient-to-r from-risk-critical to-risk-high text-white rounded-lg font-semibold hover:shadow-neon-red transition-all inline-flex items-center gap-2", children: ["Get Started Free", _jsx(ArrowRight, { className: "w-5 h-5" })] })] }) })] }));
};
