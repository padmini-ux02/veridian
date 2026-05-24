"""Dashboard API routes for user alerts and notification management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertMarkRead
from app.utils.security import get_current_user

logger = logging.getLogger("veridian.routers.dashboard")

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/alerts")
def get_user_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's alerts/notifications."""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)

    if unread_only:
        query = query.filter(Alert.is_read == False)

    total = query.count()
    unread_count = (
        db.query(Alert)
        .filter(Alert.user_id == current_user.id, Alert.is_read == False)
        .count()
    )

    total_pages = max((total + page_size - 1) // page_size, 1)
    offset = (page - 1) * page_size

    alerts = (
        query.order_by(Alert.created_at.desc())
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
        "unread_count": unread_count,
    }


@router.put("/alerts/mark-read")
def mark_alerts_read(
    data: AlertMarkRead,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark specified alerts as read."""
    updated_count = (
        db.query(Alert)
        .filter(
            Alert.id.in_(data.alert_ids),
            Alert.user_id == current_user.id,
        )
        .update({Alert.is_read: True}, synchronize_session="fetch")
    )
    db.commit()

    return {"message": f"{updated_count} alert(s) marked as read"}


@router.put("/alerts/mark-all-read")
def mark_all_alerts_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all of the user's alerts as read."""
    updated_count = (
        db.query(Alert)
        .filter(
            Alert.user_id == current_user.id,
            Alert.is_read == False,
        )
        .update({Alert.is_read: True}, synchronize_session="fetch")
    )
    db.commit()

    return {"message": f"{updated_count} alert(s) marked as read"}
