import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components';
import {
  LandingPage,
  UploadPage,
  AnalysisProgressPage,
  SecurityDashboard,
  ChatPage,
} from './pages';

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/scan" element={<UploadPage />} />
          <Route path="/analysis/:id" element={<AnalysisProgressPage />} />
          <Route path="/dashboard/:analysisId" element={<SecurityDashboard />} />
          <Route path="/chat/:analysisId" element={<ChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};
