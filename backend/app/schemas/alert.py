"""Alert-related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AlertResponse(BaseModel):
    """Schema for alert data in API responses."""

    id: str
    user_id: str
    alert_type: str
    title: str
    message: str
    scan_id: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertMarkRead(BaseModel):
    """Schema for marking alerts as read."""

    alert_ids: List[str]


class AlertListResponse(BaseModel):
    """Schema for alert list with unread count."""

    alerts: List[AlertResponse]
    total: int
    unread_count: int
