import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart3, MessageCircle, Home, ChevronRight } from 'lucide-react';

interface DashboardNavProps {
  currentPage?: 'dashboard' | 'chat';
}

export const DashboardNav: React.FC<DashboardNavProps> = ({ currentPage = 'dashboard' }) => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();

  if (!analysisId) return null;

  return (
    <div className="bg-cyber-darker border-b border-cyber-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-8 h-16 overflow-x-auto">
          {/* Home */}
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors whitespace-nowrap"
          >
            <Home className="w-4 h-4" />
            <span className="text-sm">Home</span>
          </button>

          <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />

          {/* Dashboard */}
          <button
            onClick={() => navigate(`/dashboard/${analysisId}`)}
            className={`flex items-center gap-2 whitespace-nowrap pb-4 border-b-2 transition-colors ${
              currentPage === 'dashboard'
                ? 'text-white border-risk-critical'
                : 'text-gray-400 hover:text-white border-transparent'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span className="text-sm">Dashboard</span>
          </button>

          {/* Chat */}
          <button
            onClick={() => navigate(`/chat/${analysisId}`)}
            className={`flex items-center gap-2 whitespace-nowrap pb-4 border-b-2 transition-colors ${
              currentPage === 'chat'
                ? 'text-white border-risk-critical'
                : 'text-gray-400 hover:text-white border-transparent'
            }`}
          >
            <MessageCircle className="w-4 h-4" />
            <span className="text-sm">Chat with AI</span>
          </button>
        </div>
      </div>
    </div>
  );
};
