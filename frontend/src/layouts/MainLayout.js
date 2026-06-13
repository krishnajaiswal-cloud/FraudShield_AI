import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Navbar } from './Navbar';
import { Footer } from './Footer';
export const MainLayout = ({ children }) => {
    return (_jsxs("div", { className: "flex flex-col min-h-screen bg-cyber-dark", children: [_jsx(Navbar, {}), _jsx("main", { className: "flex-1", children: children }), _jsx(Footer, {})] }));
};
