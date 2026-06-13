"""
APK Analysis Endpoints

Endpoints for managing APK analysis workflow:
- POST /api/v1/analysis - Create analysis record
- POST /api/v1/analysis/{analysis_id}/run - Execute analysis
- GET /api/v1/analysis/{analysis_id} - Get analysis details
- GET /api/v1/analysis - List analyses
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from typing import Optional
from sqlalchemy.orm import Session
import logging
import os

from app.database.database import SessionLocal
from app.database.crud import AnalysisCRUD
from app.database.models import AnalysisStatus, Analysis
from app.database.schemas import (
    AnalysisCreateSchema, AnalysisResponseSchema, AnalysisDetailResponseSchema,
    AnalysisListResponseSchema, RunAnalysisResponseSchema
)
from app.services.analysis_service import AnalysisService
from app.core.exceptions import ValidationException, DatabaseException, ResourceNotFoundException
from app.agents.apk_inspector import APKAnalysisError
from app.agents.risk_scorer import risk_scorer

logger = logging.getLogger(__name__)
router = APIRouter()


def get_db():
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Service instance (singleton)
analysis_service = AnalysisService()


@router.post("/analysis", response_model=AnalysisResponseSchema, tags=["Analysis"], status_code=status.HTTP_201_CREATED)
def create_analysis(
    analysis_request: AnalysisCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new analysis record for an APK file.
    
    This endpoint initializes an analysis record with status=PENDING.
    Use POST /api/v1/analysis/{analysis_id}/run to execute the actual analysis.
    
    Args:
        analysis_request: Analysis creation request with APK details
        db: Database session
        
    Returns:
        AnalysisResponseSchema: Created analysis record
        
    Raises:
        HTTPException 400: If file_hash already analyzed
        HTTPException 500: If database error occurs
        
    Example:
        POST /api/v1/analysis
        {
            "apk_name": "facebook.apk",
            "package_name": "com.facebook.katana",
            "file_path": "./storage/uploads/facebook.apk",
            "file_hash": "abc123...",
            "version_name": "4.5.0",
            "version_code": "450"
        }
    """
    try:
        # Provide defaults for optional fields from frontend
        apk_name = analysis_request.apk_name or os.path.basename(analysis_request.file_path)
        package_name = analysis_request.package_name or "unknown.package"
        file_hash = analysis_request.file_hash or "PENDING_EXTRACTION"
        
        logger.info(f"Creating analysis record for {apk_name}")
        
        # Check for duplicate file_hash (skip if pending extraction)
        if file_hash != "PENDING_EXTRACTION":
            existing = AnalysisCRUD.get_by_file_hash(db, file_hash)
            if existing:
                logger.warning(f"APK {file_hash} already analyzed: {existing.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"APK already analyzed. Use analysis ID: {existing.id}"
                )
        
        # Create analysis record
        analysis = AnalysisCRUD.create(
            db,
            file_hash=file_hash,
            apk_name=apk_name,
            package_name=package_name,
            file_path=analysis_request.file_path,
            md5_hash=analysis_request.md5_hash,
            version_name=analysis_request.version_name,
            version_code=analysis_request.version_code,
            app_name=analysis_request.app_name,
            file_size=analysis_request.file_size
        )
        
        logger.info(f"Analysis record created: {analysis.id}")
        return analysis
        
    except HTTPException:
        raise
    except DatabaseException as e:
        logger.error(f"Database error creating analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create analysis record"
        )


@router.post("/analysis/{analysis_id}/run", response_model=RunAnalysisResponseSchema, tags=["Analysis"])
def run_analysis(
    analysis_id: int,
    background: bool = Query(False, description="Run analysis in background"),
    db: Session = Depends(get_db)
):
    """
    Execute APK analysis workflow.
    
    Triggers the APK Inspector analysis pipeline:
    1. Load APK file
    2. Extract metadata, permissions, components
    3. Extract URLs and domains
    4. Analyze for threats
    5. Create findings and report
    
    Status Flow:
        PENDING → PROCESSING → COMPLETED (on success)
        PENDING → PROCESSING → FAILED (on error)
    
    Args:
        analysis_id: Analysis record ID
        background: If False (default), wait for completion. If True, return immediately.
        db: Database session
        
    Returns:
        RunAnalysisResponseSchema: Analysis result with status
        
    Raises:
        HTTPException 404: If analysis not found
        HTTPException 400: If APK file not found or analysis failed
        HTTPException 500: If unexpected error occurs
        
    Example:
        POST /api/v1/analysis/123/run
        Response:
        {
            "analysis_id": 123,
            "status": "completed",
            "message": "Analysis completed. Found 45 findings."
        }
    """
    try:
        logger.info(f"Running analysis: {analysis_id}")
        
        # Get analysis record
        analysis = AnalysisCRUD.get_by_id(db, analysis_id)
        
        # Verify APK file exists
        if not os.path.exists(analysis.file_path):
            error_msg = f"APK file not found: {analysis.file_path}"
            logger.error(error_msg)
            AnalysisCRUD.update(db, analysis_id, status=AnalysisStatus.FAILED, error_message=error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Execute analysis
        result = analysis_service.analyze_apk(db, analysis_id, analysis.file_path)
        
        logger.info(f"Analysis completed: {analysis_id}")
        
        return {
            "analysis_id": result['analysis_id'],
            "status": result['status'],
            "message": result['message']
        }
        
    except ResourceNotFoundException as e:
        logger.error(f"Analysis not found: {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ValidationException, APKAnalysisError) as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseException as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )


@router.get("/analysis/{analysis_id}", response_model=AnalysisDetailResponseSchema, tags=["Analysis"])
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete analysis details with findings and report.
    
    Returns analysis metadata, all findings, and the generated report.
    
    Args:
        analysis_id: Analysis record ID
        db: Database session
        
    Returns:
        AnalysisDetailResponseSchema: Complete analysis with findings
        
    Raises:
        HTTPException 404: If analysis not found
        HTTPException 500: If database error occurs
        
    Example:
        GET /api/v1/analysis/123
        Response:
        {
            "id": 123,
            "package_name": "com.facebook.katana",
            "status": "completed",
            "risk_score": 0.65,
            "severity": "high",
            "findings": [...],
            "report": {...}
        }
    """
    try:
        logger.info(f"Fetching analysis details: {analysis_id}")
        
        detail = analysis_service.get_analysis_detail(db, analysis_id)
        
        analysis = detail['analysis']
        findings = detail['findings']
        report = detail['report']
        
        return AnalysisDetailResponseSchema(
            id=analysis.id,
            apk_name=analysis.apk_name,
            package_name=analysis.package_name,
            file_path=analysis.file_path,
            file_hash=analysis.file_hash,
            md5_hash=analysis.md5_hash,
            version_name=analysis.version_name,
            version_code=analysis.version_code,
            app_name=analysis.app_name,
            file_size=analysis.file_size,
            status=analysis.status,
            threat_type=analysis.threat_type,
            risk_score=analysis.risk_score,
            severity=analysis.severity,
            error_message=analysis.error_message,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
            findings=[
                {
                    'id': f.id,
                    'analysis_id': f.analysis_id,
                    'finding_type': f.finding_type,
                    'category': f.category,
                    'value': f.value,
                    'risk_level': f.risk_level,
                    'risk_score': f.risk_score,
                    'description': f.description,
                    'extra_data': f.extra_data,
                    'created_at': f.created_at,
                    'updated_at': f.updated_at
                } for f in findings
            ],
            report={
                'id': report.id,
                'analysis_id': report.analysis_id,
                'executive_summary': report.executive_summary,
                'threat_classification': report.threat_classification,
                'recommendations': report.recommendations,
                'report_json': report.report_json,
                'created_at': report.created_at,
                'updated_at': report.updated_at
            } if report else None
        )
        
    except ResourceNotFoundException as e:
        logger.error(f"Analysis not found: {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analysis"
        )


@router.get("/analysis", response_model=AnalysisListResponseSchema, tags=["Analysis"])
def list_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    analysis_status: Optional[str] = Query(None, description="Filter by status: pending, processing, completed, failed, quarantined"),
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low, info"),
    package_name: Optional[str] = Query(None, description="Filter by package name (partial match)"),
    db: Session = Depends(get_db)
):
    """
    List analyses with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return (1-100)
        analysis_status: Filter by analysis status
        severity: Filter by severity level
        package_name: Filter by package name (partial match)
        db: Database session
        
    Returns:
        AnalysisListResponseSchema: Paginated list of analyses
        
    Raises:
        HTTPException 500: If database error occurs
        
    Example:
        GET /api/v1/analysis?analysis_status=completed&severity=high&limit=20
    """
    try:
        logger.info(f"Listing analyses: skip={skip}, limit={limit}")
        
        analyses, total = AnalysisCRUD.list_all(
            db,
            skip=skip,
            limit=limit,
            status=analysis_status,
            severity=severity,
            package_name=package_name
        )
        
        total_pages = (total + limit - 1) // limit
        
        return AnalysisListResponseSchema(
            items=[
                AnalysisResponseSchema(
                    id=a.id,
                    apk_name=a.apk_name,
                    package_name=a.package_name,
                    file_path=a.file_path,
                    file_hash=a.file_hash,
                    md5_hash=a.md5_hash,
                    version_name=a.version_name,
                    version_code=a.version_code,
                    app_name=a.app_name,
                    file_size=a.file_size,
                    status=a.status,
                    threat_type=a.threat_type,
                    risk_score=a.risk_score,
                    severity=a.severity,
                    error_message=a.error_message,
                    created_at=a.created_at,
                    updated_at=a.updated_at
                ) for a in analyses
            ],
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=total_pages
        )
        
    except DatabaseException as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing analyses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list analyses"
        )

        
        return {
            "analysis_id": analysis_id,
            "file_id": file_id,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "estimated_duration_seconds": 60
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create analysis task"
        )


@router.post("/analysis/{analysis_id}/score", tags=["Analysis"])
def score_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Calculate risk score for analysis findings
    
    Analyzes all findings from APK inspection and generates:
    - Risk score (0-100)
    - Severity level (low/medium/high/critical)
    - Detailed risk factors with explanations
    - Executive summary
    
    Args:
        analysis_id: ID of analysis to score
        
    Returns:
        Risk assessment with score, severity, and factors
    """
    logger.info(f"Calculating risk score for analysis: {analysis_id}")
    
    try:
        # Get analysis record
        analysis = AnalysisCRUD.get_by_id(db, analysis_id)
        if not analysis:
            logger.warning(f"Analysis not found: {analysis_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        # Check if analysis has findings
        if not analysis.findings:
            logger.warning(f"Analysis has no findings: {analysis_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Analysis has no findings to score. Run analysis first."
            )
        
        # Prepare findings data for risk scorer
        apk_findings = {
            "permissions": [],
            "urls": [],
            "domains": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "providers": []
        }
        
        # Extract findings by type
        for finding in analysis.findings:
            finding_type = finding.finding_type
            category = finding.category
            value = finding.value
            
            if finding_type == "permission":
                apk_findings["permissions"].append(value)
            elif finding_type == "url":
                apk_findings["urls"].append({
                    "url": value,
                    "risk_score": finding.risk_score or 0.0
                })
            elif finding_type == "domain":
                apk_findings["domains"].append(value)
            elif finding_type == "activity":
                apk_findings["activities"].append(value)
            elif finding_type == "service":
                apk_findings["services"].append(value)
            elif finding_type == "receiver":
                apk_findings["receivers"].append(value)
            elif finding_type == "provider":
                apk_findings["providers"].append(value)
        
        logger.info(f"Extracted findings: {len(analysis.findings)} total")
        
        # Calculate risk score
        risk_assessment = risk_scorer.score_apk(apk_findings)
        logger.info(
            f"Risk assessment calculated: score={risk_assessment.risk_score}, "
            f"severity={risk_assessment.severity.value}"
        )
        
        # Update analysis with risk score
        try:
            analysis.risk_score = risk_assessment.risk_score / 100.0  # Normalize to 0-1 for DB
            analysis.severity = risk_assessment.severity.value
            db.commit()
            logger.info(f"Analysis {analysis_id} updated with risk score")
        except Exception as e:
            logger.error(f"Failed to update analysis with risk score: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store risk score"
            )
        
        # Return assessment
        return risk_assessment.to_dict()
        
    except HTTPException:
        raise
    except ResourceNotFoundException as e:
        logger.error(f"Resource not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during risk scoring: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate risk score"
        )


# Helper function to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
