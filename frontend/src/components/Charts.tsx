import React from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Finding } from '../types';

interface ChartData {
  name: string;
  value: number;
}

interface RiskDistributionChartProps {
  findings: Finding[];
}

export const RiskDistributionChart: React.FC<RiskDistributionChartProps> = ({ findings }) => {
  const data: ChartData[] = [
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
    return (
      <div className="w-full h-80 flex items-center justify-center text-gray-400">
        <p>No findings to display</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, value }) => `${name}: ${value}`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => value} />
      </PieChart>
    </ResponsiveContainer>
  );
};

interface FindingsBySeverityChartProps {
  findings: Finding[];
}

export const FindingsBySeverityChart: React.FC<FindingsBySeverityChartProps> = ({ findings }) => {
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

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a3142" />
        <XAxis dataKey="category" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1a1f2e',
            border: '1px solid #2a3142',
            borderRadius: '0.5rem',
          }}
          formatter={(value) => value}
        />
        <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

interface PermissionsRiskChartProps {
  permissions: string[];
  dangerousPermissions: string[];
}

export const PermissionsRiskChart: React.FC<PermissionsRiskChartProps> = ({
  permissions,
  dangerousPermissions,
}) => {
  const data = [
    {
      name: 'Permissions',
      total: permissions.length,
      dangerous: dangerousPermissions.length,
      safe: permissions.length - dangerousPermissions.length,
    },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#2a3142" />
        <XAxis type="number" stroke="#9ca3af" />
        <YAxis type="category" dataKey="name" stroke="#9ca3af" />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1a1f2e',
            border: '1px solid #2a3142',
            borderRadius: '0.5rem',
          }}
        />
        <Legend />
        <Bar dataKey="dangerous" fill="#dc2626" radius={[0, 8, 8, 0]} />
        <Bar dataKey="safe" fill="#10b981" radius={[0, 8, 8, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};
