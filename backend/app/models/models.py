"""
SQLAlchemy ORM Models for FraudShield AI

This module defines all database models with proper relationships,
indexing, and cascade behavior for the fraud detection system.

Key Design Decisions:
1. BaseModel mixin for automatic timestamp management
2. Foreign key constraints with CASCADE delete for data integrity
3. Indexes on frequently queried columns for performance
4. String enums for status/type fields for type safety
5. JSON fields for flexible data storage (report_json)
6. Relationship lazy loading set to 'select' for explicit loading
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    ForeignKey, Index, Enum, JSON, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import enum

from app.database.database import Base


# ============================================================================
# ENUMS - Type-safe status and category definitions
# ============================================================================

class AnalysisStatus(str, enum.Enum):
    """Analysis processing status lifecycle"""
    PENDING = "pending"           # Queued, waiting for processing
    PROCESSING = "processing"     # Currently analyzing APK
    COMPLETED = "completed"       # Analysis finished successfully
    FAILED = "failed"             # Analysis encountered error
    CANCELLED = "cancelled"       # User cancelled analysis


class ThreatType(str, enum.Enum):
    """Classification of detected threats"""
    MALWARE = "malware"
    SPYWARE = "spyware"
    ADWARE = "adware"
    RANSOMWARE = "ransomware"
    TROJAN = "trojan"
    EXPLOIT = "exploit"
    PUA = "pua"  # Potentially Unwanted Application
    SUSPICIOUS = "suspicious"
    BENIGN = "benign"


class FindingType(str, enum.Enum):
    """Granular categorization of security findings"""
    PERMISSION = "permission"           # Dangerous permission usage
    API_MISUSE = "api_misuse"          # Incorrect API usage patterns
    BEHAVIOR = "behavior"               # Suspicious behavioral pattern
    CRYPTO = "crypto"                   # Cryptographic anomalies
    NETWORK = "network"                 # Suspicious network activities
    DATAFLOW = "dataflow"               # Unsafe data flow
    OBFUSCATION = "obfuscation"        # Code obfuscation detected
    NATIVE_CODE = "native_code"        # Native code execution
    REFLECTION = "reflection"           # Dynamic reflection usage


class RiskLevel(str, enum.Enum):
    """Risk severity for individual findings"""
    CRITICAL = "critical"  # Immediate threat
    HIGH = "high"          # Significant threat
    MEDIUM = "medium"      # Moderate threat
    LOW = "low"            # Minor issue
    INFO = "info"          # Informational only


class Severity(str, enum.Enum):
    """Overall APK severity classification"""
    CRITICAL = "critical"  # Dangerous - block immediately
    HIGH = "high"          # Very concerning
    MEDIUM = "medium"      # Requires review
    LOW = "low"            # Monitor
    SAFE = "safe"          # No threats detected


# ============================================================================
# BASE MIXIN - Reusable timestamp columns for audit trails
# ============================================================================

class TimestampMixin:
    """
    Mixin providing automatic created_at and updated_at timestamps.
    
    Every model uses this to maintain audit trails for compliance
    and debugging. Timestamps are automatically set/updated by the database.
    """
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,  # Index for filtering by date range
        doc="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Timestamp when record was last modified"
    )


# ============================================================================
# MODEL 1: ANALYSIS - Core entity for each APK scan
# ============================================================================

class Analysis(Base, TimestampMixin):
    """
    Represents a single APK analysis job.
    
    Root entity for all related findings, reports, and chat history.
    One Analysis can have multiple Findings, one Report, and many ChatHistory entries.
    
    Relationships:
    - findings: 1-to-Many with Finding (CASCADE delete)
    - report: 1-to-1 with Report (CASCADE delete)  
    - chat_history: 1-to-Many with ChatHistory (CASCADE delete)
    
    Indexes:
    - status + updated_at: For dashboard queries (show recent pending/processing)
    - risk_score: For sorting by threat level
    - created_at: For audit trails and time-range queries
    """
    
    __tablename__ = "analysis"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # APK Metadata
    apk_name = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Original APK filename"
    )
    
    package_name = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Android package name (com.example.app)"
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        unique=True,
        doc="Full path to uploaded APK file in storage"
    )
    
    file_hash = Column(
        String(64),  # SHA-256 hash
        nullable=False,
        unique=True,
        index=True,
        doc="SHA-256 hash for deduplication and cache lookups"
    )
    
    # Analysis Status
    status = Column(
        Enum(AnalysisStatus),
        default=AnalysisStatus.PENDING,
        nullable=False,
        index=True,
        doc="Current analysis processing status"
    )
    
    # Analysis Results
    threat_type = Column(
        Enum(ThreatType),
        default=ThreatType.BENIGN,
        nullable=True,
        doc="Primary threat classification if found"
    )
    
    risk_score = Column(
        Float,
        default=0.0,
        nullable=False,
        index=True,
        doc="Numerical risk score 0.0-100.0 for ranking"
    )
    
    severity = Column(
        Enum(Severity),
        default=Severity.SAFE,
        nullable=False,
        index=True,
        doc="Overall severity classification"
    )
    
    # Relationships (lazy='select' requires explicit loading)
    findings: List['Finding'] = relationship(
        "Finding",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select",
        doc="All security findings for this APK"
    )
    
    report: Optional['Report'] = relationship(
        "Report",
        back_populates="analysis",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
        doc="Generated security report"
    )
    
    chat_history: List['ChatHistory'] = relationship(
        "ChatHistory",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select",
        doc="RAG chat conversation about this analysis"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_analysis_status_updated", "status", "updated_at"),
        Index("idx_analysis_risk_severity", "risk_score", "severity"),
        Index("idx_analysis_package", "package_name"),
    )
    
    @hybrid_property
    def is_high_risk(self) -> bool:
        """Convenience property for filtering high-risk APKs"""
        return self.risk_score >= 70.0
    
    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, apk_name={self.apk_name}, severity={self.severity})>"


# ============================================================================
# MODEL 2: FINDING - Individual security issues discovered in APK
# ============================================================================

class Finding(Base, TimestampMixin):
    """
    Represents a single security finding within an analysis.
    
    Findings are granular security issues with specific evidence
    (permissions, API misuse, behavioral patterns, etc).
    
    Multiple findings are aggregated to determine overall risk_score.
    
    Relationships:
    - analysis: Many-to-1 with Analysis (parent)
    
    Indexes:
    - (analysis_id, risk_level): For counting findings by severity per APK
    - finding_type: For statistical analysis
    - created_at: For audit trails
    """
    
    __tablename__ = "finding"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    analysis_id = Column(
        Integer,
        ForeignKey("analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to parent analysis"
    )
    
    # Finding Classification
    finding_type = Column(
        Enum(FindingType),
        nullable=False,
        index=True,
        doc="Categorization of finding type"
    )
    
    category = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Specific category (e.g., 'DANGEROUS_PERMISSIONS', 'NETWORK_EXFILTRATION')"
    )
    
    value = Column(
        String(255),
        nullable=False,
        doc="Specific finding value (e.g., 'ANDROID_PERMISSION_CAMERA')"
    )
    
    risk_level = Column(
        Enum(RiskLevel),
        nullable=False,
        index=True,
        doc="Severity of this individual finding"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Human-readable description of the security issue"
    )
    
    # Relationship to parent analysis
    analysis: 'Analysis' = relationship(
        "Analysis",
        back_populates="findings",
        lazy="select",
        doc="Parent analysis this finding belongs to"
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_finding_analysis_risk", "analysis_id", "risk_level"),
        Index("idx_finding_type_category", "finding_type", "category"),
    )
    
    def __repr__(self) -> str:
        return f"<Finding(id={self.id}, type={self.finding_type}, risk={self.risk_level})>"


# ============================================================================
# MODEL 3: REPORT - Comprehensive security analysis report
# ============================================================================

class Report(Base, TimestampMixin):
    """
    Represents a generated security report for an analysis.
    
    One-to-one relationship with Analysis.
    Contains executive summary, threat classification, recommendations,
    and full JSON report for archival/compliance.
    
    Relationships:
    - analysis: 1-to-1 with Analysis (parent)
    
    Indexes:
    - created_at: For report generation audit trails
    """
    
    __tablename__ = "report"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key (UNIQUE for 1-to-1 relationship)
    analysis_id = Column(
        Integer,
        ForeignKey("analysis.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        doc="Reference to analysis (one report per analysis)"
    )
    
    # Report Content
    executive_summary = Column(
        Text,
        nullable=False,
        doc="High-level summary of findings for stakeholders"
    )
    
    threat_classification = Column(
        Text,
        nullable=False,
        doc="Detailed threat classification and categorization"
    )
    
    recommendations = Column(
        Text,
        nullable=False,
        doc="Security recommendations and remediation steps"
    )
    
    # Full JSON for compliance/archival
    report_json = Column(
        JSON,
        nullable=False,
        doc="Complete report as JSON for storage and compliance"
    )
    
    # Relationship to parent analysis
    analysis: 'Analysis' = relationship(
        "Analysis",
        back_populates="report",
        lazy="select",
        doc="Associated analysis"
    )
    
    __table_args__ = (
        Index("idx_report_analysis", "analysis_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, analysis_id={self.analysis_id})>"


# ============================================================================
# MODEL 4: CHAT_HISTORY - RAG conversation history for analysis insights
# ============================================================================

class ChatHistory(Base, TimestampMixin):
    """
    Stores conversation history for RAG (Retrieval-Augmented Generation).
    
    Users can ask questions about the analysis and get AI-powered
    answers grounded in the findings and report.
    
    Each message is stored for context and audit trails.
    
    Relationships:
    - analysis: Many-to-1 with Analysis (parent)
    
    Indexes:
    - (analysis_id, created_at): For retrieving conversation history
    """
    
    __tablename__ = "chat_history"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    analysis_id = Column(
        Integer,
        ForeignKey("analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to analysis being discussed"
    )
    
    # Conversation Content
    question = Column(
        Text,
        nullable=False,
        doc="User question about the analysis"
    )
    
    answer = Column(
        Text,
        nullable=False,
        doc="AI-generated answer grounded in analysis findings"
    )
    
    # Relationship to parent analysis
    analysis: 'Analysis' = relationship(
        "Analysis",
        back_populates="chat_history",
        lazy="select",
        doc="Associated analysis"
    )
    
    __table_args__ = (
        Index("idx_chat_analysis_created", "analysis_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, analysis_id={self.analysis_id})>"


# ============================================================================
# SUMMARY OF DESIGN DECISIONS
# ============================================================================
"""
1. CASCADE DELETE:
   - Finding → Analysis: Deleting analysis deletes all findings (orphan protection)
   - Report → Analysis: One report per analysis, cascade ensures cleanup
   - ChatHistory → Analysis: Clear conversation when analysis is deleted

2. INDEXES:
   - analysis(status, updated_at): Dashboard "recent pending" queries
   - analysis(risk_score): Sorting by threat level
   - finding(analysis_id, risk_level): Count findings by severity
   - chat_history(analysis_id, created_at): Load conversation in order

3. FOREIGN KEYS:
   - ON DELETE CASCADE: Maintain referential integrity, prevent orphaned records
   - Nullable=False: Enforce that every finding/report belongs to analysis

4. RELATIONSHIPS:
   - lazy='select': Explicit loading prevents N+1 queries
   - back_populates: Bidirectional sync between parent/child
   - uselist=False: Report has one-to-one relationship

5. ENUMS:
   - Type-safe status fields (AnalysisStatus, ThreatType, etc.)
   - Prevents invalid states at database level
   - Can be easily updated without migrations

6. JSON Field:
   - report_json: Flexible schema for full report archival
   - Allows storing additional analysis metadata
   - Enables historical comparisons

7. Timestamps:
   - Automatic created_at/updated_at on all records
   - Indexed for efficient time-range queries
   - Enables audit trails and SLA tracking
"""
