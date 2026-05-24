"""Scan-related Pydantic schemas for fraud detection requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ScanRequest(BaseModel):
    """Schema for submitting content for fraud detection scanning."""

    scan_type: str = Field(..., pattern=r"^(sms|email|url)$")
    content: str = Field(..., min_length=1, max_length=10000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Strip whitespace and ensure content is not empty after sanitization."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Content cannot be empty or only whitespace")
        return cleaned


class ScanResponse(BaseModel):
    """Schema for fraud detection scan results."""

    id: str
    scan_type: str
    input_content: str
    is_fraud: bool
    fraud_probability: float = Field(..., ge=0.0, le=100.0)
    risk_category: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    explanation: str
    suspicious_keywords: List[str] = []
    feature_importance: Dict[str, float] = {}
    model_used: str
    processing_time_ms: int
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class ScanHistoryResponse(BaseModel):
    """Schema for paginated scan history."""

    scans: List[ScanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScanStatsResponse(BaseModel):
    """Schema for scan statistics."""

    total_scans: int
    fraud_detected: int
    safe_detected: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    sms_scans: int
    email_scans: int
    url_scans: int
    average_risk_score: float
    scans_by_date: List[Dict[str, Any]] = []
