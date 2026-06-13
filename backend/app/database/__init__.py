"""
Database package for FraudShield AI

Provides database connection, session management, and ORM models.
"""
from app.database.database import (
    Base,
    engine,
    SessionLocal,
    init_db,
    drop_db,
    get_db,
    get_engine,
)
from app.database.session import SessionManager, session_manager
from app.database.models import (
    Analysis, Finding, Report, ChatHistory,
    AnalysisStatus, ThreatType, SeverityLevel, TimestampMixin
)
from app.database.schemas import (
    AnalysisCreateSchema, AnalysisResponseSchema, AnalysisDetailResponseSchema,
    FindingCreateSchema, FindingResponseSchema,
    ReportCreateSchema, ReportResponseSchema,
    ChatHistoryCreateSchema, ChatHistoryResponseSchema,
    AnalysisListResponseSchema, FindingListResponseSchema,
    ChatHistoryListResponseSchema, RunAnalysisResponseSchema
)
from app.database.crud import (
    AnalysisCRUD, FindingCRUD, ReportCRUD, ChatHistoryCRUD, AnalyticsCRUD
)

__all__ = [
    # Database management
    "Base",
    "engine",
    "SessionLocal",
    "init_db",
    "drop_db",
    "get_db",
    "get_engine",
    "SessionManager",
    "session_manager",
    # Models
    "Analysis",
    "Finding",
    "Report",
    "ChatHistory",
    "AnalysisStatus",
    "ThreatType",
    "SeverityLevel",
    "TimestampMixin",
    # Schemas
    "AnalysisCreateSchema",
    "AnalysisResponseSchema",
    "AnalysisDetailResponseSchema",
    "FindingCreateSchema",
    "FindingResponseSchema",
    "ReportCreateSchema",
    "ReportResponseSchema",
    "ChatHistoryCreateSchema",
    "ChatHistoryResponseSchema",
    "AnalysisListResponseSchema",
    "FindingListResponseSchema",
    "ChatHistoryListResponseSchema",
    "RunAnalysisResponseSchema",
    # CRUD operations
    "AnalysisCRUD",
    "FindingCRUD",
    "ReportCRUD",
    "ChatHistoryCRUD",
    "AnalyticsCRUD",
]


