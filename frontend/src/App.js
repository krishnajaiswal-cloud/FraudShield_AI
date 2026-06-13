import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components';
import { LandingPage, UploadPage, AnalysisProgressPage, SecurityDashboard, ChatPage, } from './pages';
export const App = () => {
    return (_jsx(ErrorBoundary, { children: _jsx(Router, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(LandingPage, {}) }), _jsx(Route, { path: "/scan", element: _jsx(UploadPage, {}) }), _jsx(Route, { path: "/analysis/:id", element: _jsx(AnalysisProgressPage, {}) }), _jsx(Route, { path: "/dashboard/:analysisId", element: _jsx(SecurityDashboard, {}) }), _jsx(Route, { path: "/chat/:analysisId", element: _jsx(ChatPage, {}) }), _jsx(Route, { path: "*", element: _jsx(Navigate, { to: "/", replace: true }) })] }) }) }));
};
