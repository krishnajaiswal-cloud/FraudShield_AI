import React, { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Package, AlertTriangle, Database, Globe } from 'lucide-react';
import {
  MainLayout,
  Card,
  Section,
  LoadingSpinner,
  ErrorState,
  RiskScoreCard,
  FindingCard,
  PermissionCard,
  URLCard,
  RiskReasonCard,
  SecurityAnalystCard,
  RiskDistributionChart,
  FindingsBySeverityChart,
  PermissionsRiskChart,
  Badge,
} from '../components';
import { useAnalysisReport } from '../hooks/useAnalysis';
import { formatBytes } from '../utils/risk';

export const SecurityDashboard: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const { data: report, isLoading, error } = useAnalysisReport(analysisId || '');
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);

  const filteredFindings = useMemo(() => {
    if (!report?.findings) return [];
    if (!filterSeverity) return report.findings;
    return report.findings.filter(f => f.risk_level === filterSeverity);
  }, [report?.findings, filterSeverity]);

  if (isLoading) {
    return (
      <MainLayout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex items-center justify-center min-h-[60vh]">
          <LoadingSpinner size="lg" text="Loading security report..." />
        </div>
      </MainLayout>
    );
  }

  if (error || !report) {
    return (
      <MainLayout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <ErrorState
            title="Failed to Load Report"
            description={error instanceof Error ? error.message : 'Unknown error occurred'}
          />
        </div>
      </MainLayout>
    );
  }

  const riskScore = report.risk_assessment.risk_score;
  const severity = report.risk_assessment.severity;

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        {/* APK Information */}
        <Section title="APK Information">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'App Name', value: report.app_name },
              { label: 'Package Name', value: report.package_name },
              { label: 'Version', value: `${report.version_name} (${report.version_code})` },
              { label: 'File Size', value: formatBytes(report.file_size) },
            ].map((item, index) => (
              <Card key={index}>
                <div className="text-center">
                  <p className="text-gray-400 text-sm mb-2">{item.label}</p>
                  <p className="text-white font-semibold break-words">{item.value}</p>
                </div>
              </Card>
            ))}
          </div>
        </Section>

        {/* Risk Score */}
        <Section title="Security Assessment">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <RiskScoreCard score={riskScore} severity={severity} />
            </div>

            {/* Overview Cards */}
            <div className="lg:col-span-2 grid grid-cols-2 gap-4">
              {[
                {
                  icon: AlertTriangle,
                  label: 'Total Findings',
                  value: report.findings?.length || 0,
                },
                {
                  icon: Database,
                  label: 'Dangerous Permissions',
                  value: report.permissions.dangerous_permissions,
                },
                {
                  icon: Globe,
                  label: 'Extracted URLs',
                  value: report.urls_and_domains.url_count,
                },
                {
                  icon: Package,
                  label: 'Components Found',
                  value:
                    (report.components.activities?.length || 0) +
                    (report.components.services?.length || 0) +
                    (report.components.broadcast_receivers?.length || 0) +
                    (report.components.content_providers?.length || 0),
                },
              ].map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <Card key={index}>
                    <div className="flex items-center gap-4">
                      <Icon className="w-8 h-8 text-risk-critical flex-shrink-0" />
                      <div>
                        <p className="text-gray-400 text-sm">{stat.label}</p>
                        <p className="text-2xl font-bold text-white">{stat.value}</p>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </Section>

        {/* Charts Section */}
        <Section title="Security Analytics">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
              <RiskDistributionChart findings={report.findings || []} />
            </Card>

            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">Findings by Severity</h3>
              <FindingsBySeverityChart findings={report.findings || []} />
            </Card>

            <Card className="lg:col-span-2">
              <h3 className="text-lg font-semibold text-white mb-4">Permission Risk Analysis</h3>
              <PermissionsRiskChart
                permissions={report.permissions.all_permissions}
                dangerousPermissions={report.permissions.dangerous_list}
              />
            </Card>
          </div>
        </Section>

        {/* Findings Section */}
        <Section title="Security Findings">
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {['critical', 'high', 'medium', 'low', 'info'].map((severity_filter) => (
                <button
                  key={severity_filter}
                  onClick={() =>
                    setFilterSeverity(
                      filterSeverity === severity_filter ? null : severity_filter
                    )
                  }
                  className={`px-4 py-2 rounded-lg transition-colors capitalize ${
                    filterSeverity === severity_filter
                      ? 'bg-risk-critical text-white'
                      : 'bg-cyber-card text-gray-300 hover:bg-cyber-border'
                  }`}
                >
                  {severity_filter}
                </button>
              ))}
              {filterSeverity && (
                <button
                  onClick={() => setFilterSeverity(null)}
                  className="px-4 py-2 rounded-lg bg-cyber-card text-gray-300 hover:bg-cyber-border transition-colors"
                >
                  Clear
                </button>
              )}
            </div>

            <div className="space-y-4">
              {filteredFindings.length > 0 ? (
                filteredFindings.map((finding, index) => (
                  <FindingCard key={index} finding={finding} />
                ))
              ) : (
                <Card>
                  <p className="text-center text-gray-400 py-8">
                    No findings for this filter
                  </p>
                </Card>
              )}
            </div>
          </div>
        </Section>

        {/* Permissions Section */}
        {report.report_json?.security_analyst?.permission_explanations &&
          report.report_json.security_analyst.permission_explanations.length > 0 && (
            <Section title="Permission Analysis">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {report.report_json.security_analyst.permission_explanations.map(
                  (perm, index) => (
                    <PermissionCard key={index} permission={perm} />
                  )
                )}
              </div>
            </Section>
          )}

        {/* URLs Section */}
        {report.urls_and_domains?.urls &&
          report.urls_and_domains.urls.length > 0 && (
            <Section title="URL Analysis">
              <div className="space-y-4">
                {report.urls_and_domains.urls.map((url, index) => (
                  <URLCard
                    key={index}
                    url={url}
                    isSuspicious={report.urls_and_domains.suspicious_urls?.includes(url) || false}
                  />
                ))}
              </div>
            </Section>
          )}

        {/* Security Analyst Section */}
        {report.report_json?.security_analyst && (
          <Section
            title="Security Analyst Assessment"
            className="bg-gradient-to-br from-cyber-card/40 to-cyber-darker/40 rounded-xl p-6 border border-cyber-border"
          >
            <div className="space-y-6">
              {/* Analyst Narrative */}
              <SecurityAnalystCard
                title="Security Assessment"
                content={report.report_json.security_analyst.analyst_narrative}
              />

              {/* Executive Summary */}
              {report.report_json.security_analyst.executive_summary && (
                <Card>
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">Executive Summary</h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Risk Level</p>
                        <Badge
                          label={report.report_json.security_analyst.executive_summary.risk_level}
                          severity={report.report_json.security_analyst.executive_summary.risk_level.toLowerCase() as any}
                          size="lg"
                        />
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Summary</p>
                        <p className="text-white">
                          {report.report_json.security_analyst.executive_summary.summary}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Recommendation</p>
                        <p className="text-white">
                          {report.report_json.security_analyst.executive_summary.recommendation}
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>
              )}

              {/* Risk Reasons */}
              {report.report_json.security_analyst.risk_reasons &&
                report.report_json.security_analyst.risk_reasons.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-4">Risk Reasons</h3>
                    <div className="space-y-4">
                      {report.report_json.security_analyst.risk_reasons.map((reason, index) => (
                        <RiskReasonCard key={index} reason={reason} />
                      ))}
                    </div>
                  </div>
                )}

              {/* Recommendations */}
              {report.report_json.security_analyst.recommendations &&
                report.report_json.security_analyst.recommendations.length > 0 && (
                  <SecurityAnalystCard
                    title="Recommendations"
                    content={report.report_json.security_analyst.recommendations}
                  />
                )}
            </div>
          </Section>
        )}
      </div>
    </MainLayout>
  );
};
