"""Report-related Pydantic schemas for fraud reporting."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Schema for creating a new fraud report."""

    report_type: str = Field(..., pattern=r"^(sms|email|url|other)$")
    title: str = Field(..., min_length=5, max_length=300)
    content: str = Field(..., min_length=10, max_length=10000)
    description: Optional[str] = Field(None, max_length=5000)
    source: Optional[str] = Field(None, max_length=500)


class ReportUpdate(BaseModel):
    """Schema for admin to update report status."""

    status: str = Field(..., pattern=r"^(pending|reviewing|confirmed_fraud|dismissed)$")
    admin_notes: Optional[str] = Field(None, max_length=5000)


class ReportResponse(BaseModel):
    """Schema for report data in API responses."""

    id: str
    user_id: str
    report_type: str
    title: str
    content: str
    description: Optional[str] = None
    source: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reporter_username: Optional[str] = None

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Schema for paginated report list."""

    reports: List[ReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
