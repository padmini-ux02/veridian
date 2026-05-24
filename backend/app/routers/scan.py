"""Scan API routes for fraud detection operations."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.scan import ScanRequest
from app.services.scan_service import ScanService
from app.utils.security import get_current_user

logger = logging.getLogger("veridian.routers.scan")

router = APIRouter(prefix="/scan", tags=["Fraud Detection"])


@router.post("/analyze")
def analyze_content(
    scan_data: ScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze content for fraud detection.

    Supports SMS, email, and URL scanning with AI-powered analysis.
    Returns fraud probability, risk category, explanation, and feature importance.
    """
    try:
        result = ScanService.perform_scan(
            db=db,
            user=current_user,
            scan_type=scan_data.scan_type,
            content=scan_data.content,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Scan error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during fraud analysis",
        )


@router.get("/history")
def get_scan_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    scan_type: Optional[str] = Query(None, pattern=r"^(sms|email|url)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's scan history with pagination."""
    return ScanService.get_scan_history(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        scan_type=scan_type,
    )


@router.get("/stats")
def get_scan_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scan statistics for the authenticated user's dashboard."""
    return ScanService.get_user_stats(db=db, user_id=current_user.id)


@router.get("/{scan_id}")
def get_scan_detail(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed results for a specific scan."""
    result = ScanService.get_scan_by_id(db=db, scan_id=scan_id, user_id=current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan result not found",
        )
    return result
