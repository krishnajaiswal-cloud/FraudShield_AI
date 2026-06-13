import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React from 'react';
import { Shield, Menu, X, LogOut } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
export const Navbar = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = React.useState(false);
    const isHomePage = location.pathname === '/';
    return (_jsx("nav", { className: "bg-cyber-darker border-b border-cyber-border", children: _jsxs("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: [_jsxs("div", { className: "flex justify-between items-center h-16", children: [_jsxs(Link, { to: "/", className: "flex items-center gap-2 group", children: [_jsxs("div", { className: "relative", children: [_jsx(Shield, { className: "w-8 h-8 text-risk-critical" }), _jsx("div", { className: "absolute inset-0 bg-risk-critical/20 blur-lg group-hover:blur-xl transition-all" })] }), _jsx("span", { className: "font-bold text-xl text-white", children: "FraudShield AI" })] }), _jsx("div", { className: "hidden md:flex items-center gap-8", children: !isHomePage && (_jsxs(_Fragment, { children: [_jsx(Link, { to: "/scan", className: "text-gray-300 hover:text-white transition-colors", children: "Analyze" }), _jsxs("button", { onClick: () => navigate('/'), className: "flex items-center gap-2 text-gray-300 hover:text-white transition-colors", children: [_jsx(LogOut, { className: "w-4 h-4" }), "Home"] })] })) }), _jsx("button", { onClick: () => setIsOpen(!isOpen), className: "md:hidden text-gray-300 hover:text-white", children: isOpen ? _jsx(X, { className: "w-6 h-6" }) : _jsx(Menu, { className: "w-6 h-6" }) })] }), isOpen && (_jsx("div", { className: "md:hidden pb-4 space-y-2", children: !isHomePage && (_jsxs(_Fragment, { children: [_jsx(Link, { to: "/scan", className: "block px-4 py-2 text-gray-300 hover:text-white transition-colors", children: "Analyze" }), _jsx("button", { onClick: () => navigate('/'), className: "w-full text-left px-4 py-2 text-gray-300 hover:text-white transition-colors", children: "Home" })] })) }))] }) }));
};
