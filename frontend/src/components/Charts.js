import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
export const RiskDistributionChart = ({ findings }) => {
    const data = [
        {
            name: 'Critical',
            value: findings.filter(f => f.risk_level === 'critical').length,
        },
        {
            name: 'High',
            value: findings.filter(f => f.risk_level === 'high').length,
        },
        {
            name: 'Medium',
            value: findings.filter(f => f.risk_level === 'medium').length,
        },
        {
            name: 'Low',
            value: findings.filter(f => f.risk_level === 'low').length,
        },
    ].filter(item => item.value > 0);
    const COLORS = ['#dc2626', '#ef5350', '#f59e0b', '#3b82f6'];
    if (data.length === 0) {
        return (_jsx("div", { className: "w-full h-80 flex items-center justify-center text-gray-400", children: _jsx("p", { children: "No findings to display" }) }));
    }
    return (_jsx(ResponsiveContainer, { width: "100%", height: 300, children: _jsxs(PieChart, { children: [_jsx(Pie, { data: data, cx: "50%", cy: "50%", labelLine: false, label: ({ name, value }) => `${name}: ${value}`, outerRadius: 100, fill: "#8884d8", dataKey: "value", children: data.map((_, index) => (_jsx(Cell, { fill: COLORS[index % COLORS.length] }, `cell-${index}`))) }), _jsx(Tooltip, { formatter: (value) => value })] }) }));
};
export const FindingsBySeverityChart = ({ findings }) => {
    const data = [
        {
            category: 'Critical',
            count: findings.filter(f => f.risk_level === 'critical').length,
        },
        {
            category: 'High',
            count: findings.filter(f => f.risk_level === 'high').length,
        },
        {
            category: 'Medium',
            count: findings.filter(f => f.risk_level === 'medium').length,
        },
        {
            category: 'Low',
            count: findings.filter(f => f.risk_level === 'low').length,
        },
    ];
    return (_jsx(ResponsiveContainer, { width: "100%", height: 300, children: _jsxs(BarChart, { data: data, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#2a3142" }), _jsx(XAxis, { dataKey: "category", stroke: "#9ca3af" }), _jsx(YAxis, { stroke: "#9ca3af" }), _jsx(Tooltip, { contentStyle: {
                        backgroundColor: '#1a1f2e',
                        border: '1px solid #2a3142',
                        borderRadius: '0.5rem',
                    }, formatter: (value) => value }), _jsx(Bar, { dataKey: "count", fill: "#3b82f6", radius: [8, 8, 0, 0] })] }) }));
};
export const PermissionsRiskChart = ({ permissions, dangerousPermissions, }) => {
    const data = [
        {
            name: 'Permissions',
            total: permissions.length,
            dangerous: dangerousPermissions.length,
            safe: permissions.length - dangerousPermissions.length,
        },
    ];
    return (_jsx(ResponsiveContainer, { width: "100%", height: 300, children: _jsxs(BarChart, { data: data, layout: "vertical", children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "#2a3142" }), _jsx(XAxis, { type: "number", stroke: "#9ca3af" }), _jsx(YAxis, { type: "category", dataKey: "name", stroke: "#9ca3af" }), _jsx(Tooltip, { contentStyle: {
                        backgroundColor: '#1a1f2e',
                        border: '1px solid #2a3142',
                        borderRadius: '0.5rem',
                    } }), _jsx(Legend, {}), _jsx(Bar, { dataKey: "dangerous", fill: "#dc2626", radius: [0, 8, 8, 0] }), _jsx(Bar, { dataKey: "safe", fill: "#10b981", radius: [0, 8, 8, 0] })] }) }));
};
