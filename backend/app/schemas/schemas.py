"""
Pydantic Schemas for FraudShield AI

This module provides type-safe request/response models for API endpoints.
Separates database models from API contracts for flexibility.

Schema Types:
1. CreateSchema: Input for POST requests (no id, no timestamps)
2. UpdateSchema: Input for PUT/PATCH (optional fields)
3. ResponseSchema: Output for GET requests (full data with relationships)

Design Principles:
- Strict validation using Pydantic v2
- Explicit field declarations for API contracts
- Nested schemas for relationships (without circular references)
- JSON serialization compatibility
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.models import (
    AnalysisStatus, ThreatType, FindingType, RiskLevel, Severity
)


# ============================================================================
# FINDING SCHEMAS - Individual security findings
# ============================================================================

class FindingCreateSchema(BaseModel):
    """Schema for creating a new finding via API"""
    
    finding_type: FindingType = Field(
        ...,
        description="Type of security finding"
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Finding category"
    )
    value: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Specific finding value"
    )
    risk_level: RiskLevel = Field(
        ...,
        description="Risk severity of finding"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description"
    )


class FindingUpdateSchema(BaseModel):
    """Schema for updating an existing finding"""
    
    finding_type: Optional[FindingType] = Field(
        None,
        description="Type of security finding"
    )
    category: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Finding category"
    )
    value: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Specific finding value"
    )
    risk_level: Optional[RiskLevel] = Field(
        None,
        description="Risk severity of finding"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description"
    )


class FindingResponseSchema(BaseModel):
    """Schema for returning a finding in API responses"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(
        ...,
        description="Finding ID"
    )
    analysis_id: int = Field(
        ...,
        description="Parent analysis ID"
    )
    finding_type: FindingType
    category: str
    value: str
    risk_level: RiskLevel
    description: Optional[str] = None
    created_at: datetime


# ============================================================================
# REPORT SCHEMAS - Security analysis reports
# ============================================================================

class ReportCreateSchema(BaseModel):
    """Schema for creating a report"""
    
    executive_summary: str = Field(
        ...,
        min_length=10,
        description="Executive summary for stakeholders"
    )
    threat_classification: str = Field(
        ...,
        min_length=10,
        description="Threat classification details"
    )
    recommendations: str = Field(
        ...,
        min_length=10,
        description="Security recommendations"
    )
    report_json: dict = Field(
        ...,
        description="Complete report as JSON"
    )


class ReportUpdateSchema(BaseModel):
    """Schema for updating a report"""
    
    executive_summary: Optional[str] = Field(
        None,
        min_length=10,
        description="Executive summary for stakeholders"
    )
    threat_classification: Optional[str] = Field(
        None,
        min_length=10,
        description="Threat classification details"
    )
    recommendations: Optional[str] = Field(
        None,
        min_length=10,
        description="Security recommendations"
    )
    report_json: Optional[dict] = Field(
        None,
        description="Complete report as JSON"
    )


class ReportResponseSchema(BaseModel):
    """Schema for returning a report"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    analysis_id: int
    executive_summary: str
    threat_classification: str
    recommendations: str
    report_json: dict
    created_at: datetime
    updated_at: datetime


# ============================================================================
# CHAT HISTORY SCHEMAS - RAG conversation history
# ============================================================================

class ChatHistoryCreateSchema(BaseModel):
    """Schema for creating a chat message"""
    
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question about analysis"
    )
    answer: str = Field(
        ...,
        min_length=1,
        description="AI-generated answer"
    )


class ChatHistoryUpdateSchema(BaseModel):
    """Schema for updating a chat message (typically not used)"""
    
    question: Optional[str] = Field(
        None,
        min_length=1,
        max_length=2000,
        description="User question about analysis"
    )
    answer: Optional[str] = Field(
        None,
        min_length=1,
        description="AI-generated answer"
    )


class ChatHistoryResponseSchema(BaseModel):
    """Schema for returning a chat message"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    analysis_id: int
    question: str
    answer: str
    created_at: datetime


# ============================================================================
# ANALYSIS SCHEMAS - APK analysis and scan results
# ============================================================================

class AnalysisCreateSchema(BaseModel):
    """
    Schema for initiating a new APK analysis.
    
    Called when user uploads APK file and analysis is queued.
    Only required fields: basic APK info and file reference.
    """
    
    apk_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original APK filename"
    )
    package_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        regex=r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)*$",
        description="Android package name (com.example.app)"
    )
    file_path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Full path to uploaded APK"
    )
    file_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 hash of APK"
    )


class AnalysisUpdateSchema(BaseModel):
    """
    Schema for updating analysis results after processing.
    
    Called by backend service after analysis completes.
    Updates status, threat type, risk score, etc.
    """
    
    status: Optional[AnalysisStatus] = Field(
        None,
        description="Current analysis status"
    )
    threat_type: Optional[ThreatType] = Field(
        None,
        description="Detected threat type if any"
    )
    risk_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Risk score 0-100"
    )
    severity: Optional[Severity] = Field(
        None,
        description="Overall severity classification"
    )


class AnalysisResponseSchema(BaseModel):
    """
    Schema for returning full analysis with all relationships.
    
    This is the complete object returned to API clients.
    Includes findings, report, and chat history.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Analysis ID")
    apk_name: str
    package_name: str
    file_path: str
    file_hash: str
    status: AnalysisStatus
    threat_type: Optional[ThreatType] = None
    risk_score: float
    severity: Severity
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships (without chat_history to avoid bloat)
    findings: List[FindingResponseSchema] = Field(
        default_factory=list,
        description="All findings for this APK"
    )
    report: Optional[ReportResponseSchema] = Field(
        None,
        description="Generated security report"
    )


class AnalysisDetailResponseSchema(AnalysisResponseSchema):
    """
    Extended response schema with full chat history.
    
    Used for detailed analysis view that includes conversation.
    """
    
    chat_history: List[ChatHistoryResponseSchema] = Field(
        default_factory=list,
        description="Chat conversation about this analysis"
    )


class AnalysisListResponseSchema(BaseModel):
    """
    Lightweight schema for list endpoints.
    
    Returns only essential fields without nested relationships
    to avoid excessive data transfer and N+1 queries.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    apk_name: str
    package_name: str
    status: AnalysisStatus
    threat_type: Optional[ThreatType] = None
    risk_score: float
    severity: Severity
    created_at: datetime
    updated_at: datetime
    
    # Stats without loading all relationships
    findings_count: int = Field(
        default=0,
        description="Number of findings (computed)"
    )


# ============================================================================
# BULK/SUMMARY SCHEMAS - For dashboard and analytics
# ============================================================================

class AnalysisSummarySchema(BaseModel):
    """Summary statistics for a single analysis"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    apk_name: str
    package_name: str
    status: AnalysisStatus
    risk_score: float
    severity: Severity
    findings_count: int = 0
    created_at: datetime


class DashboardStatsSchema(BaseModel):
    """Dashboard statistics and metrics"""
    
    total_analyses: int = Field(default=0, description="Total APKs analyzed")
    pending_count: int = Field(default=0, description="Pending analyses")
    completed_count: int = Field(default=0, description="Completed analyses")
    failed_count: int = Field(default=0, description="Failed analyses")
    critical_count: int = Field(default=0, description="Critical severity APKs")
    high_count: int = Field(default=0, description="High severity APKs")
    average_risk_score: float = Field(default=0.0, description="Average risk score")
    recent_analyses: List[AnalysisSummarySchema] = Field(
        default_factory=list,
        description="Last 10 analyses"
    )


# ============================================================================
# VALIDATION SCHEMAS - For common request/response patterns
# ============================================================================

class PaginationParamsSchema(BaseModel):
    """Query parameters for paginated list endpoints"""
    
    skip: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum records to return"
    )


class PaginatedResponseSchema(BaseModel):
    """Generic paginated response wrapper"""
    
    total: int = Field(..., description="Total records")
    skip: int = Field(..., description="Records skipped")
    limit: int = Field(..., description="Records returned")
    items: List[dict] = Field(..., description="Paginated items")


class ErrorResponseSchema(BaseModel):
    """Standard error response format"""
    
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SCHEMA DESIGN NOTES
# ============================================================================
"""
1. SEPARATION OF CONCERNS:
   - CreateSchema: Only input fields (no id/timestamps)
   - UpdateSchema: Optional fields for partial updates
   - ResponseSchema: All fields including relationships
   - ListSchema: Lightweight version without relationships

2. VALIDATION:
   - Min/max length constraints
   - Regex patterns for Android package names
   - Range validation (0-100 for risk_score)
   - Required fields with ... marker

3. RELATIONSHIPS:
   - Nested schemas to represent database relationships
   - Circular references avoided with flat responses
   - Optional fields for nullable relationships

4. PERFORMANCE:
   - ListSchema without full relationships prevents N+1 queries
   - Separate DetailSchema for full data when needed
   - DashboardStats schema for aggregated queries

5. API CONTRACTS:
   - from_attributes=True enables ORM model conversion
   - ConfigDict defines schema behavior
   - Type hints ensure IDE support and validation

6. BACKWARDS COMPATIBILITY:
   - Field descriptions help API documentation
   - Default values for optional fields
   - Version-friendly design for future changes
"""
