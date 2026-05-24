"""Admin API routes for user management, report review, and system analytics."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.user import User
from app.schemas.report import ReportUpdate
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.report_service import ReportService
from app.services.scan_service import ScanService
from app.utils.security import get_current_admin

logger = logging.getLogger("veridian.routers.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def get_admin_dashboard(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get comprehensive admin dashboard statistics."""
    scan_stats = ScanService.get_admin_stats(db)
    report_stats = ReportService.get_report_stats(db)

    return {
        **scan_stats,
        "reports": report_stats,
    }


@router.get("/users")
def get_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get all registered users with pagination."""
    users, total = AuthService.get_all_users(
        db, skip=(page - 1) * page_size, limit=page_size
    )
    total_pages = max((total + page_size - 1) // page_size, 1)

    return {
        "users": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.put("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: str,
    is_active: bool = Query(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Activate or deactivate a user account."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account status",
        )

    user = AuthService.toggle_user_status(db, user_id, is_active)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "message": f"User {'activated' if is_active else 'deactivated'} successfully",
        "user": UserResponse.model_validate(user),
    }


@router.get("/reports")
def get_all_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(
        None, alias="status",
        pattern=r"^(pending|reviewing|confirmed_fraud|dismissed)$"
    ),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get all fraud reports with optional status filtering."""
    return ReportService.get_all_reports(
        db=db, page=page, page_size=page_size, status=status_filter
    )


@router.put("/reports/{report_id}")
def update_report(
    report_id: str,
    update_data: ReportUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update a report's status and add admin notes."""
    report = ReportService.update_report_status(
        db=db,
        report_id=report_id,
        status=update_data.status,
        admin_notes=update_data.admin_notes,
        admin_id=admin.id,
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return ReportService._report_to_dict(report)


@router.get("/alerts")
def get_all_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get all system alerts (admin monitoring)."""
    total = db.query(Alert).count()
    total_pages = max((total + page_size - 1) // page_size, 1)
    offset = (page - 1) * page_size

    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "alerts": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "alert_type": a.alert_type,
                "title": a.title,
                "message": a.message,
                "scan_id": a.scan_id,
                "is_read": a.is_read,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ],
        "total": total,
        "page": page,
        "total_pages": total_pages,
    }
