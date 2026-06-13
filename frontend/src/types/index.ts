// API Response Types
export interface UploadResponse {
  status: string;
  file_path: string;
  file_name: string;
  file_size: number;
  md5: string;
}

export interface AnalysisCreateResponse {
  id: string;
  file_path: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  created_at: string;
}

export interface Permission {
  permission: string;
  risk_level: string;
  description: string;
}

export interface FindingCard {
  type: string;
  category: string;
  risk_level: string;
  description: string;
  indicator?: string;
}

export interface URLFinding {
  url: string;
  domain: string;
  is_suspicious: boolean;
  reputation?: string;
}

export interface AnalysisReport {
  id?: string;
  status: string;
  file_path?: string;
  created_at?: string;
  apk_name: string;
  package_name: string;
  version_name: string;
  version_code: string;
  app_name: string;
  file_size: number;
  md5: string;
  sha256: string;
  components: {
    activities: string[];
    services: string[];
    broadcast_receivers: string[];
    content_providers: string[];
  };
  permissions: {
    all_permissions: string[];
    dangerous_list: string[];
    total_permissions: number;
    dangerous_permissions: number;
    risk_score: number;
  };
  urls_and_domains: {
    url_count: number;
    domain_count: number;
    suspicious_count: number;
    urls: string[];
    domains: string[];
    suspicious_urls: string[];
  };
  risk_assessment: {
    risk_score: number;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'safe';
    risk_factors: RiskFactor[];
  };
  findings: Finding[];
  report_json: {
    security_analyst: SecurityAnalyst;
  };
}

export interface RiskFactor {
  factor: string;
  severity: string;
  score: number;
  description: string;
}

export interface Finding {
  type: string;
  category: string;
  risk_level: string;
  description: string;
  indicator?: string;
  permission?: string;
}

export interface SecurityAnalyst {
  analyst_narrative: string;
  permission_explanations: PermissionExplanation[];
  risk_reasons: RiskReason[];
  executive_summary: ExecutiveSummary;
  recommendations: string[];
}

export interface PermissionExplanation {
  permission: string;
  risk: 'critical' | 'high' | 'medium' | 'low' | 'info';
  explanation: string;
}

export interface RiskReason {
  reason: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  indicator: string;
}

export interface ExecutiveSummary {
  risk_level: string;
  summary: string;
  recommendation: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  role: 'assistant';
  content: string;
}

// UI State Types
export interface AnalysisState {
  id: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  progress: number;
  error?: string;
}

export interface RiskScore {
  score: number;
  severity: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  color: string;
  icon: string;
}
