"""
Pydantic Schemas for FraudShield AI

Defines request/response schemas with validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

# Generic type variable for paginated responses
T = TypeVar('T')


# Enums
class AnalysisStatusSchema(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class ThreatTypeSchema(str, Enum):
    MALWARE = "malware"
    SPYWARE = "spyware"
    TROJAN = "trojan"
    ADWARE = "adware"
    RANSOMWARE = "ransomware"
    PUP = "pup"
    SUSPICIOUS = "suspicious"
    CLEAN = "clean"


class SeverityLevelSchema(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# Finding Schemas
class FindingCreateSchema(BaseModel):
    """Schema for creating findings"""
    finding_type: str
    category: str
    value: str
    risk_level: SeverityLevelSchema = SeverityLevelSchema.INFO
    risk_score: Optional[float] = None
    description: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class FindingUpdateSchema(BaseModel):
    """Schema for updating findings"""
    risk_level: Optional[SeverityLevelSchema] = None
    description: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class FindingResponseSchema(BaseModel):
    """Schema for finding responses"""
    id: int
    analysis_id: int
    finding_type: str
    category: str
    value: str
    risk_level: SeverityLevelSchema
    risk_score: Optional[float] = None
    description: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Security Analyst Schemas
class PermissionExplanationSchema(BaseModel):
    """Schema for permission explanation from security analyst"""
    permission: str = Field(..., description="Android permission name")
    risk: str = Field(..., description="Risk level: critical, high, medium, low, or info")
    explanation: str = Field(..., description="Plain-English explanation of permission risk")


class RiskReasonSchema(BaseModel):
    """Schema for risk reason from security analyst"""
    severity: str = Field(..., description="Severity level: critical, high, medium, low, or info")
    reason: str = Field(..., description="Explanation of the risk")
    indicator: str = Field(..., description="The specific finding that triggered this risk")


class PrioritizedRiskFactorSchema(BaseModel):
    """Schema for prioritized risk factor from security analyst"""
    factor: str = Field(..., description="Risk factor name")
    severity: str = Field(..., description="Severity level: critical, high, medium, low, or info")
    reason: Optional[str] = Field(None, description="Explanation of why this is a risk")


class SecurityAnalystSchema(BaseModel):
    """Schema for security analyst assessment section of report"""
    analyst_narrative: str = Field(default="", description="Professional 3-5 paragraph security assessment")
    user_friendly_summary: str = Field(default="", description="Plain-English summary of key security concerns")
    security_assessment: str = Field(default="", description="Security recommendation based on analysis")
    permission_explanations: List[PermissionExplanationSchema] = Field(default_factory=list, description="Explanations of requested permissions")
    risk_reasons: List[RiskReasonSchema] = Field(default_factory=list, description="Detailed reasons for detected risks")
    prioritized_risk_factors: List[PrioritizedRiskFactorSchema] = Field(default_factory=list, description="Risk factors sorted by severity")
    recommendation_list: List[str] = Field(default_factory=list, description="Actionable recommendations for the user")


# Report Schemas
class ReportCreateSchema(BaseModel):
    """Schema for creating reports"""
    executive_summary: Optional[str] = None
    threat_classification: Optional[str] = None
    recommendations: Optional[str] = None
    report_json: Dict[str, Any]


class ReportUpdateSchema(BaseModel):
    """Schema for updating reports"""
    executive_summary: Optional[str] = None
    threat_classification: Optional[str] = None
    recommendations: Optional[str] = None
    report_json: Optional[Dict[str, Any]] = None


class ReportResponseSchema(BaseModel):
    """Schema for report responses"""
    id: int
    analysis_id: int
    executive_summary: Optional[str] = None
    threat_classification: Optional[str] = None
    recommendations: Optional[str] = None
    report_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Analysis Schemas
class AnalysisCreateSchema(BaseModel):
    """Schema for creating analysis records"""
    file_path: str
    apk_name: Optional[str] = None
    package_name: Optional[str] = None
    file_hash: Optional[str] = None
    md5_hash: Optional[str] = None
    version_name: Optional[str] = None
    version_code: Optional[str] = None
    app_name: Optional[str] = None
    file_size: Optional[int] = None


class AnalysisUpdateSchema(BaseModel):
    """Schema for updating analysis records"""
    status: Optional[AnalysisStatusSchema] = None
    threat_type: Optional[ThreatTypeSchema] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    severity: Optional[SeverityLevelSchema] = None
    error_message: Optional[str] = None
    version_name: Optional[str] = None
    version_code: Optional[str] = None
    app_name: Optional[str] = None
    file_size: Optional[int] = None


class AnalysisResponseSchema(BaseModel):
    """Schema for analysis responses"""
    id: int
    apk_name: str
    package_name: str
    file_path: str
    file_hash: str
    md5_hash: Optional[str] = None
    version_name: Optional[str] = None
    version_code: Optional[str] = None
    app_name: Optional[str] = None
    file_size: Optional[int] = None
    status: AnalysisStatusSchema
    threat_type: Optional[ThreatTypeSchema] = None
    risk_score: float
    severity: SeverityLevelSchema
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetailResponseSchema(BaseModel):
    """Schema for detailed analysis responses with relationships"""
    id: int
    apk_name: str
    package_name: str
    file_path: str
    file_hash: str
    md5_hash: Optional[str] = None
    version_name: Optional[str] = None
    version_code: Optional[str] = None
    app_name: Optional[str] = None
    file_size: Optional[int] = None
    status: AnalysisStatusSchema
    threat_type: Optional[ThreatTypeSchema] = None
    risk_score: float
    severity: SeverityLevelSchema
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    findings: List[FindingResponseSchema] = []
    report: Optional[ReportResponseSchema] = None

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryCreateSchema(BaseModel):
    """Schema for creating chat history"""
    question: str
    answer: str


class ChatHistoryResponseSchema(BaseModel):
    """Schema for chat history responses"""
    id: int
    analysis_id: int
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Pagination
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


class AnalysisListResponseSchema(BaseModel):
    """Schema for paginated analysis list"""
    items: List[AnalysisResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class FindingListResponseSchema(BaseModel):
    """Schema for paginated findings list"""
    items: List[FindingResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class ChatHistoryListResponseSchema(BaseModel):
    """Schema for paginated chat history list"""
    items: List[ChatHistoryResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


# Error Response
class ErrorResponseSchema(BaseModel):
    """Schema for error responses"""
    status_code: int
    detail: str
    error_type: str
    timestamp: datetime


# Analysis Statistics
class AnalysisStatsSchema(BaseModel):
    """Schema for analysis statistics"""
    total_analyses: int
    pending: int
    processing: int
    completed: int
    failed: int
    quarantined: int
    average_risk_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int


class FindingsSummarySchema(BaseModel):
    """Schema for findings summary"""
    total_findings: int
    by_category: Dict[str, int]
    by_risk_level: Dict[str, int]
    top_categories: List[Dict[str, Any]]


# Run Analysis Response
class RunAnalysisResponseSchema(BaseModel):
    """Schema for run analysis response"""
    analysis_id: int
    status: AnalysisStatusSchema
    message: str
