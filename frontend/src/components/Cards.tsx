import React from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle, Shield } from 'lucide-react';
import { Badge, Card } from './Common';
import { getRiskColor } from '../utils/risk';
import { Finding, PermissionExplanation, RiskReason } from '../types';

interface RiskScoreCardProps {
  score: number;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'safe';
}

export const RiskScoreCard: React.FC<RiskScoreCardProps> = ({ score, severity }) => {
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

  return (
    <Card className="relative overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${colors[severity]} opacity-5`} />
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Risk Score</h3>
          <Icon className={`w-6 h-6 text-${severity === 'critical' ? 'risk-critical' : severity === 'high' ? 'risk-high' : severity === 'medium' ? 'risk-medium' : severity === 'low' ? 'risk-low' : 'risk-safe'}`} />
        </div>
        <div className="mb-4">
          <div className="text-5xl font-bold text-white mb-2">{score}</div>
          <Badge label={severity.charAt(0).toUpperCase() + severity.slice(1)} severity={severity} size="lg" />
        </div>
        <div className="w-full bg-cyber-darker rounded-full h-2 overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${colors[severity]}`}
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    </Card>
  );
};

interface FindingCardProps {
  finding: Finding;
  onClick?: () => void;
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding, onClick }) => {
  return (
    <Card onClick={onClick}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h4 className="font-semibold text-white mb-1">{finding.type}</h4>
          <p className="text-sm text-gray-400 mb-3">{finding.description}</p>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge label={finding.category} severity={finding.risk_level as any} size="sm" />
            {finding.indicator && (
              <span className="text-xs text-gray-400 bg-cyber-darker px-2 py-1 rounded">
                {finding.indicator}
              </span>
            )}
          </div>
        </div>
        <div className={`px-3 py-1 rounded-lg text-sm font-medium flex-shrink-0 ${getRiskColor(
          finding.risk_level
        )}`}>
          {finding.risk_level}
        </div>
      </div>
    </Card>
  );
};

interface PermissionCardProps {
  permission: PermissionExplanation;
}

export const PermissionCard: React.FC<PermissionCardProps> = ({ permission }) => {
  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h4 className="font-semibold text-white mb-2">
            {permission.permission.split('.').pop()}
          </h4>
          <p className="text-sm text-gray-400 mb-4">{permission.explanation}</p>
          <div className="flex items-center gap-2">
            <Badge label={permission.risk} severity={permission.risk as any} size="sm" />
          </div>
        </div>
      </div>
    </Card>
  );
};

interface URLCardProps {
  url: string;
  isSuspicious: boolean;
}

export const URLCard: React.FC<URLCardProps> = ({ url, isSuspicious }) => {
  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 break-all">
          <h4 className="font-mono text-sm text-blue-400 mb-2">{url}</h4>
          {isSuspicious && (
            <Badge label="Suspicious" severity="high" size="sm" />
          )}
        </div>
      </div>
    </Card>
  );
};

interface RiskReasonCardProps {
  reason: RiskReason;
}

export const RiskReasonCard: React.FC<RiskReasonCardProps> = ({ reason }) => {
  return (
    <Card>
      <div className="flex gap-4">
        <div className={`flex-shrink-0 w-1 rounded-full bg-gradient-to-b ${
          reason.severity === 'critical'
            ? 'from-risk-critical to-risk-critical/50'
            : reason.severity === 'high'
            ? 'from-risk-high to-risk-high/50'
            : reason.severity === 'medium'
            ? 'from-risk-medium to-risk-medium/50'
            : reason.severity === 'low'
            ? 'from-risk-low to-risk-low/50'
            : 'from-blue-500 to-blue-500/50'
        }`} />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-semibold text-white">{reason.reason}</h4>
            <Badge label={reason.severity} severity={reason.severity as any} size="sm" />
          </div>
          {reason.indicator && (
            <p className="text-sm text-gray-400">{reason.indicator}</p>
          )}
        </div>
      </div>
    </Card>
  );
};

interface SecurityAnalystCardProps {
  title: string;
  content: string | string[];
}

export const SecurityAnalystCard: React.FC<SecurityAnalystCardProps> = ({
  title,
  content,
}) => {
  return (
    <Card>
      <div className="mb-4 flex items-center gap-2">
        <Shield className="w-5 h-5 text-risk-critical" />
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      {Array.isArray(content) ? (
        <ul className="space-y-2">
          {content.map((item, index) => (
            <li key={index} className="text-gray-300 flex items-start gap-2">
              <span className="text-risk-critical mt-1 flex-shrink-0">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-300 leading-relaxed">{content}</p>
      )}
    </Card>
  );
};
