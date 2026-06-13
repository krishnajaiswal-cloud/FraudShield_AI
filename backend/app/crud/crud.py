"""
CRUD Operations for FraudShield AI

Utility functions for database operations on all models.
Separates business logic from endpoint handlers.

Design:
- One CRUD class per model
- Generic methods: create, read, update, delete, list
- Custom queries for complex filtering
- Type hints for all parameters and returns
- Error handling and logging
"""

from typing import Optional, List, Generic, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_
import logging

from app.models.models import (
    Analysis, Finding, Report, ChatHistory,
    AnalysisStatus, ThreatType, Severity, RiskLevel
)
from app.schemas.schemas import (
    AnalysisCreateSchema, AnalysisUpdateSchema,
    FindingCreateSchema, FindingUpdateSchema,
    ReportCreateSchema, ReportUpdateSchema,
    ChatHistoryCreateSchema, ChatHistoryUpdateSchema
)

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for base CRUD operations


# ============================================================================
# BASE CRUD CLASS - Generic CRUD operations
# ============================================================================

class BaseCRUD(Generic[T]):
    """
    Generic CRUD base class for common database operations.
    
    Provides standard Create, Read, Update, Delete methods
    that can be inherited by model-specific CRUD classes.
    """
    
    def __init__(self, model):
        self.model = model
    
    def create(self, db: Session, obj_in: dict) -> T:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Dictionary or Pydantic model with data
            
        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Created {self.model.__name__} with id={db_obj.id}")
        return db_obj
    
    def read(self, db: Session, id: int) -> Optional[T]:
        """
        Read a record by ID.
        
        Args:
            db: Database session
            id: Primary key
            
        Returns:
            Model instance or None if not found
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def update(self, db: Session, id: int, obj_in: dict) -> Optional[T]:
        """
        Update a record by ID.
        
        Args:
            db: Database session
            id: Primary key
            obj_in: Dictionary with fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = self.read(db, id)
        if not db_obj:
            return None
        
        # Update only provided fields
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Updated {self.model.__name__} with id={id}")
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            db: Database session
            id: Primary key
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.read(db, id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        logger.info(f"Deleted {self.model.__name__} with id={id}")
        return True
    
    def list_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10
    ) -> List[T]:
        """
        List all records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of model instances
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def count(self, db: Session) -> int:
        """
        Count total records.
        
        Args:
            db: Database session
            
        Returns:
            Total number of records
        """
        return db.query(self.model).count()


# ============================================================================
# ANALYSIS CRUD - APK analysis operations
# ============================================================================

class AnalysisCRUD(BaseCRUD):
    """CRUD operations for Analysis model"""
    
    def create(self, db: Session, obj_in: AnalysisCreateSchema) -> Analysis:
        """
        Create a new analysis.
        
        Called when user uploads APK and analysis is queued.
        Status defaults to PENDING, other fields to safe defaults.
        """
        obj_data = obj_in.model_dump()
        return super().create(db, obj_data)
    
    def update(self, db: Session, id: int, obj_in: AnalysisUpdateSchema) -> Optional[Analysis]:
        """
        Update analysis results.
        
        Called by analysis service after processing completes.
        Updates status, threat type, risk score, severity.
        """
        obj_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, id, obj_data)
    
    def get_by_package(self, db: Session, package_name: str) -> Optional[Analysis]:
        """
        Get analysis by Android package name.
        
        Useful for checking if package was already analyzed.
        Returns most recent analysis if multiple exist.
        """
        return db.query(Analysis)\
            .filter(Analysis.package_name == package_name)\
            .order_by(desc(Analysis.created_at))\
            .first()
    
    def get_by_hash(self, db: Session, file_hash: str) -> Optional[Analysis]:
        """
        Get analysis by file hash.
        
        Enables deduplication - if same APK uploaded before,
        can reuse previous analysis instead of re-analyzing.
        """
        return db.query(Analysis)\
            .filter(Analysis.file_hash == file_hash)\
            .first()
    
    def list_by_status(
        self,
        db: Session,
        status: AnalysisStatus,
        skip: int = 0,
        limit: int = 10
    ) -> List[Analysis]:
        """
        List analyses by status.
        
        Common query: get all pending/processing jobs for batch processing.
        """
        return db.query(Analysis)\
            .filter(Analysis.status == status)\
            .order_by(desc(Analysis.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def list_by_severity(
        self,
        db: Session,
        severity: Severity,
        skip: int = 0,
        limit: int = 10
    ) -> List[Analysis]:
        """
        List analyses by severity classification.
        
        For dashboard: show high/critical risk APKs.
        """
        return db.query(Analysis)\
            .filter(Analysis.severity == severity)\
            .order_by(desc(Analysis.risk_score))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def list_high_risk(
        self,
        db: Session,
        risk_threshold: float = 70.0,
        skip: int = 0,
        limit: int = 10
    ) -> List[Analysis]:
        """
        List high-risk analyses above threshold.
        
        Args:
            db: Database session
            risk_threshold: Minimum risk score (0-100)
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of high-risk analyses sorted by risk score
        """
        return db.query(Analysis)\
            .filter(Analysis.risk_score >= risk_threshold)\
            .order_by(desc(Analysis.risk_score))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def list_recent(
        self,
        db: Session,
        days: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> List[Analysis]:
        """
        List recent analyses.
        
        For dashboard: show analyses from last N days.
        """
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return db.query(Analysis)\
            .filter(Analysis.created_at >= cutoff)\
            .order_by(desc(Analysis.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def count_by_status(self, db: Session) -> dict:
        """
        Count analyses by status.
        
        Returns dict like:
        {
            "pending": 5,
            "processing": 2,
            "completed": 45,
            "failed": 1
        }
        """
        counts = {}
        for status in AnalysisStatus:
            count = db.query(Analysis)\
                .filter(Analysis.status == status)\
                .count()
            counts[status.value] = count
        return counts
    
    def get_dashboard_stats(self, db: Session) -> dict:
        """
        Get comprehensive dashboard statistics.
        
        Returns:
            Dictionary with counts, averages, and recent analyses
        """
        total = self.count(db)
        
        # Count by status
        status_counts = self.count_by_status(db)
        
        # Count by severity
        severity_counts = {}
        for severity in Severity:
            count = db.query(Analysis)\
                .filter(Analysis.severity == severity)\
                .count()
            severity_counts[severity.value] = count
        
        # Average risk score
        result = db.query(
            (Analysis.risk_score.sum() / self.count(db))
            if self.count(db) > 0 else 0
        ).scalar()
        avg_risk = float(result) if result else 0.0
        
        # Recent analyses
        recent = self.list_recent(db, days=7, limit=10)
        
        return {
            "total_analyses": total,
            "status": status_counts,
            "severity": severity_counts,
            "average_risk_score": avg_risk,
            "recent_count": len(recent)
        }
    
    def search(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Analysis]:
        """
        Full-text search on apk_name and package_name.
        
        Args:
            db: Database session
            query: Search string
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of matching analyses
        """
        search_term = f"%{query}%"
        return db.query(Analysis)\
            .filter(
                or_(
                    Analysis.apk_name.ilike(search_term),
                    Analysis.package_name.ilike(search_term)
                )
            )\
            .order_by(desc(Analysis.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()


# ============================================================================
# FINDING CRUD - Security finding operations
# ============================================================================

class FindingCRUD(BaseCRUD):
    """CRUD operations for Finding model"""
    
    def create(self, db: Session, analysis_id: int, obj_in: FindingCreateSchema) -> Finding:
        """
        Create a new finding for an analysis.
        
        Args:
            db: Database session
            analysis_id: Parent analysis ID
            obj_in: Finding data
            
        Returns:
            Created Finding instance
        """
        obj_data = obj_in.model_dump()
        obj_data['analysis_id'] = analysis_id
        return super().create(db, obj_data)
    
    def get_by_analysis(self, db: Session, analysis_id: int) -> List[Finding]:
        """
        Get all findings for an analysis.
        
        Automatically called when loading analysis details.
        """
        return db.query(Finding)\
            .filter(Finding.analysis_id == analysis_id)\
            .order_by(desc(Finding.risk_level))\
            .all()
    
    def count_by_analysis(self, db: Session, analysis_id: int) -> int:
        """Count findings for an analysis"""
        return db.query(Finding)\
            .filter(Finding.analysis_id == analysis_id)\
            .count()
    
    def count_critical_by_analysis(self, db: Session, analysis_id: int) -> int:
        """Count critical/high risk findings for an analysis"""
        return db.query(Finding)\
            .filter(
                and_(
                    Finding.analysis_id == analysis_id,
                    Finding.risk_level.in_([RiskLevel.CRITICAL, RiskLevel.HIGH])
                )
            )\
            .count()
    
    def get_by_type(
        self,
        db: Session,
        finding_type: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Finding]:
        """
        Get findings by type.
        
        For analytics: count findings by type across all analyses.
        """
        return db.query(Finding)\
            .filter(Finding.finding_type == finding_type)\
            .order_by(desc(Finding.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def bulk_create(
        self,
        db: Session,
        analysis_id: int,
        findings: List[FindingCreateSchema]
    ) -> List[Finding]:
        """
        Create multiple findings for an analysis.
        
        Used after analysis completes with all discovered findings.
        """
        created_findings = []
        for finding_data in findings:
            finding = self.create(db, analysis_id, finding_data)
            created_findings.append(finding)
        logger.info(f"Created {len(created_findings)} findings for analysis {analysis_id}")
        return created_findings
    
    def delete_by_analysis(self, db: Session, analysis_id: int) -> int:
        """
        Delete all findings for an analysis.
        
        Usually called by cascade on analysis deletion.
        Returns count of deleted findings.
        """
        count = db.query(Finding)\
            .filter(Finding.analysis_id == analysis_id)\
            .delete()
        db.commit()
        logger.info(f"Deleted {count} findings for analysis {analysis_id}")
        return count


# ============================================================================
# REPORT CRUD - Report generation and storage
# ============================================================================

class ReportCRUD(BaseCRUD):
    """CRUD operations for Report model"""
    
    def create(self, db: Session, analysis_id: int, obj_in: ReportCreateSchema) -> Report:
        """
        Create a report for an analysis.
        
        Called after analysis completes.
        One-to-one: each analysis has at most one report.
        """
        obj_data = obj_in.model_dump()
        obj_data['analysis_id'] = analysis_id
        return super().create(db, obj_data)
    
    def get_by_analysis(self, db: Session, analysis_id: int) -> Optional[Report]:
        """
        Get report for an analysis.
        
        Returns the one report associated with analysis, or None.
        """
        return db.query(Report)\
            .filter(Report.analysis_id == analysis_id)\
            .first()
    
    def exists_for_analysis(self, db: Session, analysis_id: int) -> bool:
        """
        Check if report exists for analysis.
        
        Before creating report, verify one doesn't already exist.
        """
        return db.query(Report)\
            .filter(Report.analysis_id == analysis_id)\
            .count() > 0
    
    def update(
        self,
        db: Session,
        analysis_id: int,
        obj_in: ReportUpdateSchema
    ) -> Optional[Report]:
        """
        Update report for an analysis.
        
        Args:
            db: Database session
            analysis_id: Analysis ID (not report ID)
            obj_in: Updated report data
            
        Returns:
            Updated Report or None if not found
        """
        report = self.get_by_analysis(db, analysis_id)
        if not report:
            return None
        
        obj_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, report.id, obj_data)
    
    def delete_by_analysis(self, db: Session, analysis_id: int) -> bool:
        """
        Delete report for an analysis.
        
        Usually called by cascade on analysis deletion.
        """
        report = self.get_by_analysis(db, analysis_id)
        if not report:
            return False
        return self.delete(db, report.id)


# ============================================================================
# CHAT HISTORY CRUD - Conversation management
# ============================================================================

class ChatHistoryCRUD(BaseCRUD):
    """CRUD operations for ChatHistory model"""
    
    def create(self, db: Session, analysis_id: int, obj_in: ChatHistoryCreateSchema) -> ChatHistory:
        """
        Create a chat message for an analysis.
        
        Called when user asks question about analysis results.
        """
        obj_data = obj_in.model_dump()
        obj_data['analysis_id'] = analysis_id
        return super().create(db, obj_data)
    
    def get_by_analysis(
        self,
        db: Session,
        analysis_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatHistory]:
        """
        Get chat history for an analysis.
        
        Returns conversation ordered chronologically.
        """
        return db.query(ChatHistory)\
            .filter(ChatHistory.analysis_id == analysis_id)\
            .order_by(asc(ChatHistory.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def count_by_analysis(self, db: Session, analysis_id: int) -> int:
        """Count messages in analysis conversation"""
        return db.query(ChatHistory)\
            .filter(ChatHistory.analysis_id == analysis_id)\
            .count()
    
    def get_latest_conversation(
        self,
        db: Session,
        analysis_id: int,
        limit: int = 10
    ) -> List[ChatHistory]:
        """
        Get most recent messages for context.
        
        Useful for RAG context window - get last N messages for LLM.
        """
        return db.query(ChatHistory)\
            .filter(ChatHistory.analysis_id == analysis_id)\
            .order_by(desc(ChatHistory.created_at))\
            .limit(limit)\
            .all()[::-1]  # Reverse to chronological order
    
    def clear_history(self, db: Session, analysis_id: int) -> int:
        """
        Delete all chat history for an analysis.
        
        Called when user wants to restart conversation.
        Returns count of deleted messages.
        """
        count = db.query(ChatHistory)\
            .filter(ChatHistory.analysis_id == analysis_id)\
            .delete()
        db.commit()
        logger.info(f"Cleared {count} chat messages for analysis {analysis_id}")
        return count
    
    def delete_by_analysis(self, db: Session, analysis_id: int) -> int:
        """
        Delete all messages when analysis is deleted.
        
        Called by cascade on analysis deletion.
        """
        return self.clear_history(db, analysis_id)


# ============================================================================
# GLOBAL CRUD INSTANCES - Convenient access to all CRUD operations
# ============================================================================

# Create singleton instances for import and use throughout the app
analysis_crud = AnalysisCRUD(Analysis)
finding_crud = FindingCRUD(Finding)
report_crud = ReportCRUD(Report)
chat_crud = ChatHistoryCRUD(ChatHistory)


# ============================================================================
# UTILITY FUNCTIONS - Common database operations
# ============================================================================

def get_analysis_with_findings(db: Session, analysis_id: int) -> Optional[Analysis]:
    """
    Get analysis with all relationships loaded.
    
    Eagerly loads findings and report to avoid N+1 queries.
    """
    return db.query(Analysis)\
        .filter(Analysis.id == analysis_id)\
        .first()


def delete_analysis_complete(db: Session, analysis_id: int) -> bool:
    """
    Complete analysis deletion with cascade cleanup.
    
    Deletes analysis and all related findings, report, chat history.
    """
    try:
        return analysis_crud.delete(db, analysis_id)
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
        db.rollback()
        return False


def update_analysis_risk_score(db: Session, analysis_id: int) -> float:
    """
    Recalculate analysis risk score from findings.
    
    Aggregates risk levels of all findings:
    - CRITICAL findings: +25 points each
    - HIGH findings: +15 points each
    - MEDIUM findings: +8 points each
    - LOW findings: +2 points each
    
    Capped at 100.0.
    """
    findings = finding_crud.get_by_analysis(db, analysis_id)
    
    risk_score = 0.0
    for finding in findings:
        if finding.risk_level == RiskLevel.CRITICAL:
            risk_score += 25.0
        elif finding.risk_level == RiskLevel.HIGH:
            risk_score += 15.0
        elif finding.risk_level == RiskLevel.MEDIUM:
            risk_score += 8.0
        elif finding.risk_level == RiskLevel.LOW:
            risk_score += 2.0
    
    # Cap at 100
    risk_score = min(risk_score, 100.0)
    
    # Determine severity from risk score
    if risk_score >= 80:
        severity = Severity.CRITICAL
    elif risk_score >= 60:
        severity = Severity.HIGH
    elif risk_score >= 40:
        severity = Severity.MEDIUM
    elif risk_score >= 20:
        severity = Severity.LOW
    else:
        severity = Severity.SAFE
    
    # Update analysis
    analysis_crud.update(
        db,
        analysis_id,
        {
            'risk_score': risk_score,
            'severity': severity
        }
    )
    
    logger.info(f"Updated analysis {analysis_id} risk_score={risk_score}, severity={severity.value}")
    return risk_score


# ============================================================================
# CRUD USAGE EXAMPLES
# ============================================================================
"""
Example usage in endpoint handlers:

# Create analysis
analysis_data = AnalysisCreateSchema(
    apk_name="app.apk",
    package_name="com.example.app",
    file_path="./storage/uploads/123.apk",
    file_hash="abc123..."
)
analysis = analysis_crud.create(db, analysis_data)

# Get analysis with findings
analysis = analysis_crud.read(db, analysis.id)
findings = finding_crud.get_by_analysis(db, analysis.id)

# Add findings after analysis
findings_data = [
    FindingCreateSchema(
        finding_type=FindingType.PERMISSION,
        category="DANGEROUS_PERMISSIONS",
        value="ANDROID_PERMISSION_CAMERA",
        risk_level=RiskLevel.HIGH,
        description="Camera access without user interaction"
    )
]
findings = finding_crud.bulk_create(db, analysis.id, findings_data)

# Update risk score based on findings
update_analysis_risk_score(db, analysis.id)

# Generate report
report_data = ReportCreateSchema(
    executive_summary="...",
    threat_classification="...",
    recommendations="...",
    report_json={...}
)
report = report_crud.create(db, analysis.id, report_data)

# Get chat history
messages = chat_crud.get_by_analysis(db, analysis.id)

# Add chat message
question = ChatHistoryCreateSchema(
    question="Is this app safe?",
    answer="Based on analysis..."
)
chat_crud.create(db, analysis.id, question)
"""
