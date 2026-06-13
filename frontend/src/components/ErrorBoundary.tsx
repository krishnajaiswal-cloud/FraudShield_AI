import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Card } from './Common';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-cyber-dark flex items-center justify-center px-4">
          <Card className="max-w-md">
            <div className="flex items-center gap-4 mb-4">
              <AlertTriangle className="w-8 h-8 text-risk-critical flex-shrink-0" />
              <h1 className="text-2xl font-bold text-white">Something went wrong</h1>
            </div>
            <p className="text-gray-400 mb-6">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors"
            >
              Reload Page
            </button>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
