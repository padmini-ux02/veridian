"""Scan result database model for storing fraud detection outcomes."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ScanResult(Base):
    """Stores the result of each fraud detection scan."""

    __tablename__ = "scan_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # String instead of Enum for SQLite compatibility ("sms" | "email" | "url")
    scan_type = Column(String(20), nullable=False, index=True)
    input_content = Column(Text, nullable=False)
    is_fraud = Column(Integer, default=0, nullable=False)
    fraud_probability = Column(Float, default=0.0, nullable=False)
    # String instead of Enum for SQLite ("low" | "medium" | "high" | "critical")
    risk_category = Column(String(20), default="low", nullable=False, index=True)
    risk_score = Column(Float, default=0.0, nullable=False)
    explanation = Column(Text, nullable=True)
    suspicious_keywords = Column(Text, nullable=True)  # JSON string
    feature_importance = Column(Text, nullable=True)   # JSON string
    model_used = Column(String(100), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="scans")

    def __repr__(self) -> str:
        return (
            f"<ScanResult(id={self.id}, type={self.scan_type}, "
            f"fraud={self.is_fraud}, risk={self.risk_category})>"
        )
