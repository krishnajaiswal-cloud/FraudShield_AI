import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-cyber-darker border-t border-cyber-border mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-semibold text-white mb-4">FraudShield AI</h3>
            <p className="text-gray-400 text-sm">
              Advanced APK security analysis powered by AI
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-4">Features</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Permission Analysis</li>
              <li>URL Extraction</li>
              <li>Risk Scoring</li>
              <li>Security Reports</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-4">Security</h3>
            <p className="text-gray-400 text-sm">
              Your APK files are analyzed securely and never stored
            </p>
          </div>
        </div>
        <div className="border-t border-cyber-border mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2024 FraudShield AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
