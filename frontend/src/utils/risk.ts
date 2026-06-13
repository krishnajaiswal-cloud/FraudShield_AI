import { RiskScore } from '../types';

export const getRiskScore = (score: number): RiskScore => {
  if (score >= 80) {
    return {
      score,
      severity: 'critical',
      color: 'bg-risk-critical',
      icon: 'AlertTriangle',
    };
  } else if (score >= 60) {
    return {
      score,
      severity: 'high',
      color: 'bg-risk-high',
      icon: 'AlertCircle',
    };
  } else if (score >= 40) {
    return {
      score,
      severity: 'medium',
      color: 'bg-risk-medium',
      icon: 'AlertOctagon',
    };
  } else if (score >= 20) {
    return {
      score,
      severity: 'low',
      color: 'bg-risk-low',
      icon: 'Info',
    };
  } else {
    return {
      score,
      severity: 'safe',
      color: 'bg-risk-safe',
      icon: 'Shield',
    };
  }
};

export const getRiskColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-risk-critical bg-risk-critical/10';
    case 'high':
      return 'text-risk-high bg-risk-high/10';
    case 'medium':
      return 'text-risk-medium bg-risk-medium/10';
    case 'low':
      return 'text-risk-low bg-risk-low/10';
    case 'safe':
      return 'text-risk-safe bg-risk-safe/10';
    default:
      return 'text-gray-500 bg-gray-500/10';
  }
};

export const getRiskBadgeColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-risk-critical/20 text-risk-critical border-risk-critical';
    case 'high':
      return 'bg-risk-high/20 text-risk-high border-risk-high';
    case 'medium':
      return 'bg-risk-medium/20 text-risk-medium border-risk-medium';
    case 'low':
      return 'bg-risk-low/20 text-risk-low border-risk-low';
    case 'safe':
      return 'bg-risk-safe/20 text-risk-safe border-risk-safe';
    default:
      return 'bg-gray-500/20 text-gray-500 border-gray-500';
  }
};

export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};
