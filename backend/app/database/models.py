"""
Database Models for FraudShield AI

Defines all SQLAlchemy ORM models with relationships, enums, and audit trails.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON, Index
from sqlalchemy.orm import relationship

# Import Base from database.py to use the same metadata registry
from app.database.database import Base


class TimestampMixin:
    """Mixin for audit trail timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AnalysisStatus(str, Enum):
    """Analysis workflow status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class ThreatType(str, Enum):
    """Threat classification"""
    MALWARE = "malware"
    SPYWARE = "spyware"
    TROJAN = "trojan"
    ADWARE = "adware"
    RANSOMWARE = "ransomware"
    PUP = "pup"  # Potentially Unwanted Program
    SUSPICIOUS = "suspicious"
    CLEAN = "clean"


class SeverityLevel(str, Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Analysis(Base, TimestampMixin):
    """
    APK Analysis record - main entity for analysis workflow
    
    Stores analysis metadata and status information.
    References the uploaded APK file and links to findings and reports.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    apk_name = Column(String(255), nullable=False)
    package_name = Column(String(255), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA256
    md5_hash = Column(String(32), nullable=True)
    
    # Analysis metadata
    version_name = Column(String(50), nullable=True)
    version_code = Column(String(50), nullable=True)
    app_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    
    # Analysis results
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False, index=True)
    threat_type = Column(SQLEnum(ThreatType), nullable=True)
    risk_score = Column(Float, default=0.0, nullable=False)  # 0.0-1.0
    severity = Column(SQLEnum(SeverityLevel), default=SeverityLevel.INFO, nullable=False, index=True)
    
    # Error tracking
    error_message = Column(String(1024), nullable=True)
    
    # Relationships
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    report = relationship("Report", uselist=False, back_populates="analysis", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="analysis", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_analysis_status_created', 'status', 'created_at'),
        Index('idx_analysis_package_severity', 'package_name', 'severity'),
    )


class Finding(Base, TimestampMixin):
    """
    Individual finding from APK analysis
    
    Stores specific security findings, permissions, URLs, and other artifacts
    extracted during APK analysis.
    """
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Finding metadata
    finding_type = Column(String(50), nullable=False)  # permission, url, activity, etc.
    category = Column(String(100), nullable=False, index=True)  # CONTACTS, CAMERA, INTERNET, etc.
    value = Column(String(1024), nullable=False)  # The actual value (permission name, URL, etc.)
    
    # Risk information
    risk_level = Column(SQLEnum(SeverityLevel), default=SeverityLevel.INFO, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=True)  # 0.0-1.0 for URLs
    
    # Additional info
    description = Column(String(1024), nullable=True)
    extra_data = Column(JSON, nullable=True)  # Store additional structured data
    
    # Relationships
    analysis = relationship("Analysis", back_populates="findings")
    
    __table_args__ = (
        Index('idx_finding_analysis_category', 'analysis_id', 'category'),
    )


class Report(Base, TimestampMixin):
    """
    Comprehensive analysis report
    
    Generates after analysis completion with summary, recommendations,
    and detailed threat classification.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Report content
    executive_summary = Column(String(2048), nullable=True)
    threat_classification = Column(String(500), nullable=True)
    recommendations = Column(String(2048), nullable=True)
    
    # Full report as JSON
    report_json = Column(JSON, nullable=False)  # Complete structured report
    
    # Relationships
    analysis = relationship("Analysis", back_populates="report")


class ChatHistory(Base, TimestampMixin):
    """
    Chat history for RAG (Retrieval Augmented Generation) queries
    
    Stores Q&A pairs for analysis-specific conversational AI.
    """
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chat content
    question = Column(String(2048), nullable=False)
    answer = Column(String(4096), nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="chat_history")
    
    __table_args__ = (
        Index('idx_chat_analysis_created', 'analysis_id', 'created_at'),
    )
