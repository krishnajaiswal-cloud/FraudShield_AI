"""
CRUD Operations for FraudShield AI

Provides database operations for all models with proper error handling.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import desc, and_

from app.database.models import (
    Analysis, Finding, Report, ChatHistory,
    AnalysisStatus, ThreatType, SeverityLevel
)
from app.core.exceptions import DatabaseException, ResourceNotFoundException

logger = logging.getLogger(__name__)


class AnalysisCRUD:
    """CRUD operations for Analysis model"""

    @staticmethod
    def create(db: Session, file_hash: str, apk_name: str, package_name: str, 
               file_path: str, **kwargs) -> Analysis:
        """
        Create new analysis record.
        Checks for duplicate file_hash to prevent re-analysis.
        
        Args:
            db: Database session
            file_hash: SHA256 hash of APK file
            apk_name: APK filename
            package_name: Android package name
            file_path: Path to APK file on disk
            **kwargs: Additional fields (version_name, version_code, app_name, file_size, etc.)
            
        Returns:
            Analysis: Created analysis record
            
        Raises:
            DatabaseException: If duplicate hash found or database error occurs
        """
        try:
            # Check for duplicate (skip if pending extraction)
            if file_hash != "PENDING_EXTRACTION":
                existing = db.query(Analysis).filter(Analysis.file_hash == file_hash).first()
                if existing:
                    logger.warning(f"APK with hash {file_hash} already analyzed: {existing.id}")
                    raise DatabaseException(
                        f"APK file already analyzed (ID: {existing.id}). Use existing analysis."
                    )
            
            # Create new record
            analysis = Analysis(
                apk_name=apk_name,
                package_name=package_name,
                file_path=file_path,
                file_hash=file_hash,
                status=AnalysisStatus.PENDING,
                **kwargs
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
            logger.info(f"Created analysis record: {analysis.id} for {package_name}")
            return analysis
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating analysis: {e}")
            raise DatabaseException(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating analysis: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(db: Session, analysis_id: int) -> Analysis:
        """Get analysis by ID with all relationships"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ResourceNotFoundException("Analysis", analysis_id)
            return analysis
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching analysis: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_by_file_hash(db: Session, file_hash: str) -> Optional[Analysis]:
        """Get analysis by file hash"""
        try:
            return db.query(Analysis).filter(Analysis.file_hash == file_hash).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching analysis by hash: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 50,
                 status: Optional[str] = None, severity: Optional[str] = None,
                 package_name: Optional[str] = None) -> tuple[List[Analysis], int]:
        """
        List analyses with optional filters and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            status: Filter by analysis status
            severity: Filter by severity level
            package_name: Filter by package name (partial match)
            
        Returns:
            Tuple of (analyses list, total count)
        """
        try:
            query = db.query(Analysis)
            
            # Apply filters
            if status:
                query = query.filter(Analysis.status == AnalysisStatus[status.upper()])
            if severity:
                query = query.filter(Analysis.severity == SeverityLevel[severity.upper()])
            if package_name:
                query = query.filter(Analysis.package_name.ilike(f"%{package_name}%"))
            
            total = query.count()
            analyses = query.order_by(desc(Analysis.created_at)).offset(skip).limit(limit).all()
            
            return analyses, total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing analyses: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def update(db: Session, analysis_id: int, **kwargs) -> Analysis:
        """
        Update analysis record.
        
        Args:
            db: Database session
            analysis_id: Analysis ID to update
            **kwargs: Fields to update (status, threat_type, risk_score, severity, error_message, etc.)
            
        Returns:
            Analysis: Updated analysis record
            
        Raises:
            ResourceNotFoundException: If analysis not found
            DatabaseException: If database error occurs
        """
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ResourceNotFoundException("Analysis", analysis_id)
            
            # Update only provided fields
            for key, value in kwargs.items():
                if value is not None and hasattr(analysis, key):
                    setattr(analysis, key, value)
            
            analysis.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(analysis)
            
            logger.info(f"Updated analysis: {analysis_id}")
            return analysis
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error updating analysis: {e}")
            raise DatabaseException(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating analysis: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def delete(db: Session, analysis_id: int) -> bool:
        """Delete analysis and cascade delete findings, reports, chat history"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ResourceNotFoundException("Analysis", analysis_id)
            
            db.delete(analysis)
            db.commit()
            
            logger.info(f"Deleted analysis: {analysis_id}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting analysis: {e}")
            raise DatabaseException(f"Database error: {str(e)}")


class FindingCRUD:
    """CRUD operations for Finding model"""

    @staticmethod
    def create(db: Session, analysis_id: int, finding_type: str, category: str,
               value: str, **kwargs) -> Finding:
        """Create new finding record"""
        try:
            # Verify parent analysis exists
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ResourceNotFoundException("Analysis", analysis_id)
            
            finding = Finding(
                analysis_id=analysis_id,
                finding_type=finding_type,
                category=category,
                value=value,
                **kwargs
            )
            db.add(finding)
            db.commit()
            db.refresh(finding)
            
            logger.debug(f"Created finding: {finding.id} for analysis {analysis_id}")
            return finding
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating finding: {e}")
            raise DatabaseException(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating finding: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(db: Session, finding_id: int) -> Finding:
        """Get finding by ID"""
        try:
            finding = db.query(Finding).filter(Finding.id == finding_id).first()
            if not finding:
                raise ResourceNotFoundException("Finding", finding_id)
            return finding
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching finding: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def list_by_analysis(db: Session, analysis_id: int, skip: int = 0, limit: int = 100,
                         category: Optional[str] = None,
                         risk_level: Optional[str] = None) -> tuple[List[Finding], int]:
        """List findings for an analysis with optional filters"""
        try:
            query = db.query(Finding).filter(Finding.analysis_id == analysis_id)
            
            if category:
                query = query.filter(Finding.category == category)
            if risk_level:
                query = query.filter(Finding.risk_level == SeverityLevel[risk_level.upper()])
            
            total = query.count()
            findings = query.order_by(desc(Finding.created_at)).offset(skip).limit(limit).all()
            
            return findings, total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing findings: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def delete(db: Session, finding_id: int) -> bool:
        """Delete finding"""
        try:
            finding = db.query(Finding).filter(Finding.id == finding_id).first()
            if not finding:
                raise ResourceNotFoundException("Finding", finding_id)
            
            db.delete(finding)
            db.commit()
            
            logger.debug(f"Deleted finding: {finding_id}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting finding: {e}")
            raise DatabaseException(f"Database error: {str(e)}")


class ReportCRUD:
    """CRUD operations for Report model"""

    @staticmethod
    def create(db: Session, analysis_id: int, report_json: Dict[str, Any], **kwargs) -> Report:
        """Create new report record"""
        try:
            # Check for unique constraint
            existing = db.query(Report).filter(Report.analysis_id == analysis_id).first()
            if existing:
                raise DatabaseException(f"Report already exists for analysis {analysis_id}")
            
            report = Report(
                analysis_id=analysis_id,
                report_json=report_json,
                **kwargs
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            
            logger.info(f"Created report: {report.id} for analysis {analysis_id}")
            return report
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating report: {e}")
            raise DatabaseException(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating report: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(db: Session, report_id: int) -> Report:
        """Get report by ID"""
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ResourceNotFoundException("Report", report_id)
            return report
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching report: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_by_analysis_id(db: Session, analysis_id: int) -> Optional[Report]:
        """Get report for an analysis"""
        try:
            return db.query(Report).filter(Report.analysis_id == analysis_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching report: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def update(db: Session, report_id: int, **kwargs) -> Report:
        """Update report record"""
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ResourceNotFoundException("Report", report_id)
            
            for key, value in kwargs.items():
                if value is not None and hasattr(report, key):
                    setattr(report, key, value)
            
            report.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(report)
            
            logger.info(f"Updated report: {report_id}")
            return report
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating report: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def delete(db: Session, report_id: int) -> bool:
        """Delete report"""
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ResourceNotFoundException("Report", report_id)
            
            db.delete(report)
            db.commit()
            
            logger.info(f"Deleted report: {report_id}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting report: {e}")
            raise DatabaseException(f"Database error: {str(e)}")


class ChatHistoryCRUD:
    """CRUD operations for ChatHistory model"""

    @staticmethod
    def create(db: Session, analysis_id: int, question: str, answer: str) -> ChatHistory:
        """Create new chat history record"""
        try:
            chat = ChatHistory(
                analysis_id=analysis_id,
                question=question,
                answer=answer
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
            
            logger.debug(f"Created chat history: {chat.id} for analysis {analysis_id}")
            return chat
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating chat history: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_by_id(db: Session, chat_id: int) -> ChatHistory:
        """Get chat history by ID"""
        try:
            chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
            if not chat:
                raise ResourceNotFoundException("ChatHistory", chat_id)
            return chat
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching chat history: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def list_by_analysis(db: Session, analysis_id: int, skip: int = 0, limit: int = 50) -> tuple[List[ChatHistory], int]:
        """List chat history for an analysis"""
        try:
            query = db.query(ChatHistory).filter(ChatHistory.analysis_id == analysis_id)
            total = query.count()
            chats = query.order_by(desc(ChatHistory.created_at)).offset(skip).limit(limit).all()
            return chats, total
        except SQLAlchemyError as e:
            logger.error(f"Database error listing chat history: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def delete(db: Session, chat_id: int) -> bool:
        """Delete chat history entry"""
        try:
            chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
            if not chat:
                raise ResourceNotFoundException("ChatHistory", chat_id)
            
            db.delete(chat)
            db.commit()
            
            logger.debug(f"Deleted chat history: {chat_id}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting chat history: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def clear_analysis_history(db: Session, analysis_id: int) -> int:
        """Delete all chat history for an analysis"""
        try:
            count = db.query(ChatHistory).filter(ChatHistory.analysis_id == analysis_id).delete()
            db.commit()
            
            logger.info(f"Cleared {count} chat history entries for analysis {analysis_id}")
            return count
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error clearing chat history: {e}")
            raise DatabaseException(f"Database error: {str(e)}")


class AnalyticsCRUD:
    """Analytics queries for dashboard and reporting"""

    @staticmethod
    def get_analysis_stats(db: Session) -> Dict[str, Any]:
        """Get analysis statistics"""
        try:
            total = db.query(Analysis).count()
            pending = db.query(Analysis).filter(Analysis.status == AnalysisStatus.PENDING).count()
            processing = db.query(Analysis).filter(Analysis.status == AnalysisStatus.PROCESSING).count()
            completed = db.query(Analysis).filter(Analysis.status == AnalysisStatus.COMPLETED).count()
            failed = db.query(Analysis).filter(Analysis.status == AnalysisStatus.FAILED).count()
            quarantined = db.query(Analysis).filter(Analysis.status == AnalysisStatus.QUARANTINED).count()
            
            # Calculate average risk score
            avg_result = db.query(Analysis).filter(
                Analysis.status == AnalysisStatus.COMPLETED
            ).first()
            
            avg_risk = 0.0
            if avg_result:
                from sqlalchemy import func
                avg_risk = db.query(func.avg(Analysis.risk_score)).filter(
                    Analysis.status == AnalysisStatus.COMPLETED
                ).scalar() or 0.0
            
            # Count by severity
            critical = db.query(Analysis).filter(Analysis.severity == SeverityLevel.CRITICAL).count()
            high = db.query(Analysis).filter(Analysis.severity == SeverityLevel.HIGH).count()
            medium = db.query(Analysis).filter(Analysis.severity == SeverityLevel.MEDIUM).count()
            low = db.query(Analysis).filter(Analysis.severity == SeverityLevel.LOW).count()
            info = db.query(Analysis).filter(Analysis.severity == SeverityLevel.INFO).count()
            
            return {
                'total_analyses': total,
                'pending': pending,
                'processing': processing,
                'completed': completed,
                'failed': failed,
                'quarantined': quarantined,
                'average_risk_score': float(avg_risk),
                'critical_count': critical,
                'high_count': high,
                'medium_count': medium,
                'low_count': low,
                'info_count': info,
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting stats: {e}")
            raise DatabaseException(f"Database error: {str(e)}")

    @staticmethod
    def get_findings_summary(db: Session, analysis_id: Optional[int] = None) -> Dict[str, Any]:
        """Get findings summary"""
        try:
            query = db.query(Finding)
            if analysis_id:
                query = query.filter(Finding.analysis_id == analysis_id)
            
            total = query.count()
            
            # Group by category
            from sqlalchemy import func
            by_category = {}
            category_results = db.query(Finding.category, func.count(Finding.id)).group_by(Finding.category).all()
            for cat, count in category_results:
                by_category[cat] = count
            
            # Group by risk level
            by_risk = {}
            risk_results = db.query(Finding.risk_level, func.count(Finding.id)).group_by(Finding.risk_level).all()
            for risk, count in risk_results:
                by_risk[risk.value if hasattr(risk, 'value') else str(risk)] = count
            
            return {
                'total_findings': total,
                'by_category': by_category,
                'by_risk_level': by_risk,
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting findings summary: {e}")
            raise DatabaseException(f"Database error: {str(e)}")
