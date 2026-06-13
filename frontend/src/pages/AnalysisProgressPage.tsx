import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import { MainLayout, Card, LoadingSpinner, ErrorState, Section } from '../components';
import { useAnalysisStatus } from '../hooks/useAnalysis';

export const AnalysisProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, isLoading, error } = useAnalysisStatus(id || '', !!id);

  useEffect(() => {
    if (data && data.status === 'completed') {
      // Redirect to dashboard when analysis is complete
      const timer = setTimeout(() => {
        navigate(`/dashboard/${id}`);
      }, 1000);
      return () => clearTimeout(timer);
    }
    return;
  }, [data, id, navigate]);

  if (!id) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <ErrorState
            title="Invalid Analysis ID"
            description="No analysis ID provided"
          />
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <ErrorState
            title="Error Loading Analysis"
            description={error instanceof Error ? error.message : 'Unknown error occurred'}
            onRetry={() => window.location.reload()}
          />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Section title="Analysis Progress">
          <div className="space-y-8">
            {/* Progress Card */}
            <Card>
              <div className="text-center space-y-8">
                {isLoading ? (
                  <>
                    <LoadingSpinner size="lg" />
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2">
                        Analyzing Your APK
                      </h3>
                      <p className="text-gray-400">
                        Our security AI is scanning your application for vulnerabilities...
                      </p>
                    </div>
                  </>
                ) : data ? (
                  <>
                    {data.status === 'completed' ? (
                      <>
                        <CheckCircle2 className="w-16 h-16 text-risk-safe mx-auto" />
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-2">
                            Analysis Complete!
                          </h3>
                          <p className="text-gray-400">
                            Redirecting to your security report...
                          </p>
                        </div>
                      </>
                    ) : data.status === 'failed' ? (
                      <>
                        <AlertCircle className="w-16 h-16 text-risk-critical mx-auto" />
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-2">
                            Analysis Failed
                          </h3>
                          <p className="text-gray-400">
                            An error occurred while analyzing your APK. Please try again.
                          </p>
                        </div>
                        <button
                          onClick={() => navigate('/scan')}
                          className="px-6 py-2 bg-risk-critical text-white rounded-lg hover:bg-risk-critical/90 transition-colors"
                        >
                          Try Again
                        </button>
                      </>
                    ) : (
                      <>
                        <LoadingSpinner size="lg" />
                        <div>
                          <h3 className="text-xl font-semibold text-white mb-2">
                            Processing...
                          </h3>
                          <p className="text-gray-400">
                            Status: {data.status}
                          </p>
                        </div>
                      </>
                    )}
                  </>
                ) : null}
              </div>
            </Card>

            {/* Analysis Details */}
            <Card>
              <h3 className="font-semibold text-white mb-4">Analysis Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Analysis ID</span>
                  <span className="text-white font-mono">{id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Status</span>
                  <span className="text-white capitalize">{data?.status || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">File Path</span>
                  <span className="text-white font-mono text-xs truncate">
                    {data?.file_path || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Created</span>
                  <span className="text-white">
                    {data?.created_at ? new Date(data.created_at).toLocaleString() : 'N/A'}
                  </span>
                </div>
              </div>
            </Card>

            {/* Progress Steps */}
            <Card>
              <h3 className="font-semibold text-white mb-4">Analysis Steps</h3>
              <div className="space-y-3">
                {[
                  { step: 'Uploading', completed: true },
                  { step: 'Extracting', completed: data?.status !== 'pending' },
                  { step: 'Analyzing', completed: data?.status === 'completed' || data?.status === 'analyzing' },
                  { step: 'Generating Report', completed: data?.status === 'completed' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        item.completed ? 'bg-risk-safe' : 'bg-gray-600'
                      }`}
                    />
                    <span className={item.completed ? 'text-white' : 'text-gray-400'}>
                      {item.step}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </Section>
      </div>
    </MainLayout>
  );
};
