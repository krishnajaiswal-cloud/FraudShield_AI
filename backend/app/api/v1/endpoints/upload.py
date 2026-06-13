"""
APK file upload endpoint
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", tags=["Upload"])
async def upload_apk(
    file: UploadFile = File(...),
    metadata: Optional[str] = None
):
    """
    Upload an APK file for analysis
    
    Args:
        file: APK file to upload (.apk)
        metadata: Optional JSON metadata about the upload
        
    Returns:
        Upload status and file ID
        
    Response Example:
        {
            "file_id": "550e8400-e29b-41d4-a716-446655440000",
            "filename": "app.apk",
            "size_bytes": 5242880,
            "upload_timestamp": "2024-01-15T10:30:45Z",
            "status": "received"
        }
    """
    try:
        # Validate file type
        if not file.filename.endswith(".apk"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .apk files are allowed"
            )
        
        # Get file size
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        from app.core.config import settings
        if file_size > settings.APK_MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum of {settings.APK_MAX_FILE_SIZE} bytes"
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate file ID
        import uuid
        file_id = str(uuid.uuid4())
        
        # Save file
        file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"APK file uploaded: {file_id} - {file.filename} ({file_size} bytes)")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "size_bytes": file_size,
            "upload_timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "received"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )


@router.get("/upload/{file_id}", tags=["Upload"])
async def get_upload_status(file_id: str):
    """
    Get upload status and metadata
    
    Args:
        file_id: File ID from upload
        
    Returns:
        Upload status and metadata
    """
    # TODO: Implement database lookup for upload status
    return {
        "file_id": file_id,
        "status": "received",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
