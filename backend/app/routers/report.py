"""Report API routes for user-submitted fraud reports."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate
from app.services.report_service import ReportService
from app.utils.security import get_current_admin, get_current_user

logger = logging.getLogger("veridian.routers.report")

router = APIRouter(prefix="/reports", tags=["Fraud Reports"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new fraud report."""
    report = ReportService.create_report(
        db=db,
        user=current_user,
        report_type=report_data.report_type,
        title=report_data.title,
        content=report_data.content,
        description=report_data.description,
        source=report_data.source,
    )
    return ReportService._report_to_dict(report)


@router.get("/my-reports")
def get_my_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's submitted reports."""
    return ReportService.get_user_reports(
        db=db, user_id=current_user.id, page=page, page_size=page_size
    )


@router.get("/{report_id}")
def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific report by ID."""
    report = ReportService.get_report_by_id(db=db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    # Users can only view their own reports (unless admin)
    if report["user_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return report
