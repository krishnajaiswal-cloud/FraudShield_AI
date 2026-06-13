import React from 'react';
import { Share2, Copy, Download } from 'lucide-react';
import { Card } from './Common';

interface ShareExportProps {
  analysisId: string;
  onExport?: () => void;
}

export const ShareExport: React.FC<ShareExportProps> = ({ analysisId, onExport }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopyLink = () => {
    const link = `${window.location.origin}/dashboard/${analysisId}`;
    navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card>
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h3 className="font-semibold text-white mb-1">Share Analysis</h3>
          <p className="text-gray-400 text-sm">Export or share your security report</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyLink}
            className="flex items-center gap-2 px-3 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors"
            title="Copy link to clipboard"
          >
            <Copy className="w-4 h-4" />
            {copied ? 'Copied!' : 'Copy Link'}
          </button>
          <button
            onClick={onExport}
            className="flex items-center gap-2 px-3 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors"
            title="Export as PDF"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            className="flex items-center gap-2 px-3 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors"
            title="Share analysis"
          >
            <Share2 className="w-4 h-4" />
            Share
          </button>
        </div>
      </div>
    </Card>
  );
};
