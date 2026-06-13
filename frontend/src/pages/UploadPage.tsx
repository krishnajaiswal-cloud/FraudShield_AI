import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { MainLayout, FileUpload, ErrorState } from '../components';
import { useUploadAPK } from '../hooks/useUpload';
import { useCreateAnalysis, useRunAnalysis } from '../hooks/useAnalysis';

export const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string>();
  const [isCreatingAnalysis, setIsCreatingAnalysis] = useState(false);

  const uploadAPK = useUploadAPK();
  const createAnalysis = useCreateAnalysis();
  const runAnalysis = useRunAnalysis();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setUploadError(undefined);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select an APK file');
      return;
    }

    try {
      setUploadError(undefined);
      const uploadResult = await uploadAPK.mutateAsync(selectedFile);

      // Create analysis record
      setIsCreatingAnalysis(true);
      const analysisResult = await createAnalysis.mutateAsync(uploadResult.file_path);

      // Run analysis
      await runAnalysis.mutateAsync(analysisResult.id);

      // Redirect to analysis progress page
      navigate(`/analysis/${analysisResult.id}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to upload APK';
      setUploadError(message);
    } finally {
      setIsCreatingAnalysis(false);
    }
  };

  const isLoading = uploadAPK.isPending || isCreatingAnalysis;

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">Upload APK for Analysis</h1>
          <p className="text-gray-400">
            Select an Android APK file to analyze for security vulnerabilities and risks
          </p>
        </div>

        {uploadError && (
          <div className="mb-8">
            <ErrorState
              title="Upload Failed"
              description={uploadError}
              onRetry={() => {
                setUploadError(undefined);
                setSelectedFile(null);
              }}
            />
          </div>
        )}

        <div className="space-y-8">
          <FileUpload
            onFileSelect={handleFileSelect}
            error={uploadAPK.error ? 'Failed to upload file' : undefined}
          />

          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isLoading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-risk-critical to-risk-high text-white rounded-lg font-semibold hover:shadow-neon-red transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
              {isLoading ? 'Uploading...' : 'Upload and Analyze'}
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 border border-cyber-border text-white rounded-lg font-semibold hover:border-cyber-border/50 transition-colors"
            >
              Cancel
            </button>
          </div>

          <div className="bg-cyber-card border border-cyber-border rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">About APK Analysis</h3>
            <ul className="space-y-3 text-gray-400 text-sm">
              <li className="flex items-start gap-3">
                <span className="text-risk-critical mt-1 flex-shrink-0">•</span>
                <span>Analyzes Android manifest for permissions</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-risk-critical mt-1 flex-shrink-0">•</span>
                <span>Extracts embedded URLs and domains</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-risk-critical mt-1 flex-shrink-0">•</span>
                <span>Detects suspicious components and behaviors</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-risk-critical mt-1 flex-shrink-0">•</span>
                <span>Generates comprehensive security report</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};
