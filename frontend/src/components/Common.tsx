import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  text = 'Loading...',
}) => {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size];

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`${sizeClass} animate-spin`}>
        <div className="w-full h-full border-4 border-cyber-border border-t-risk-critical rounded-full" />
      </div>
      {text && <p className="text-gray-400 text-sm">{text}</p>}
    </div>
  );
};

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {icon && <div className="mb-4 text-gray-500">{icon}</div>}
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      {description && <p className="text-gray-400 text-sm">{description}</p>}
    </div>
  );
};

interface ErrorStateProps {
  title: string;
  description?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title,
  description,
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <AlertTriangle className="w-12 h-12 text-risk-critical mb-4" />
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      {description && <p className="text-gray-400 text-sm mb-4">{description}</p>}
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
};

interface BadgeProps {
  label: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'safe' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export const Badge: React.FC<BadgeProps> = ({ label, severity, size = 'md' }) => {
  const colors = {
    critical: 'bg-risk-critical/20 text-risk-critical border-risk-critical',
    high: 'bg-risk-high/20 text-risk-high border-risk-high',
    medium: 'bg-risk-medium/20 text-risk-medium border-risk-medium',
    low: 'bg-risk-low/20 text-risk-low border-risk-low',
    safe: 'bg-risk-safe/20 text-risk-safe border-risk-safe',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500',
  };

  const sizeClass = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }[size];

  return (
    <span className={`${colors[severity]} ${sizeClass} border rounded-full inline-block font-medium`}>
      {label}
    </span>
  );
};

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`bg-cyber-card border border-cyber-border rounded-xl p-6 hover:border-cyber-border/80 transition-all shadow-cyber ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
};

interface SectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export const Section: React.FC<SectionProps> = ({
  title,
  description,
  children,
  className = '',
}) => {
  return (
    <div className={className}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">{title}</h2>
        {description && <p className="text-gray-400">{description}</p>}
      </div>
      {children}
    </div>
  );
};
