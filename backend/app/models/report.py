"""Fraud report model for user-submitted suspicious content."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FraudReport(Base):
    """Stores user-submitted fraud reports for admin review."""

    __tablename__ = "fraud_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # String instead of Enum for SQLite compatibility
    report_type = Column(String(30), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(500), nullable=True)
    # "pending" | "reviewing" | "confirmed_fraud" | "dismissed"
    status = Column(String(30), default="pending", nullable=False, index=True)
    admin_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(36), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="reports")

    def __repr__(self) -> str:
        return f"<FraudReport(id={self.id}, type={self.report_type}, status={self.status})>"
