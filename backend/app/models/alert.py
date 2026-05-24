"""Alert model for real-time fraud notifications."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    """Real-time alert notifications for fraud detection events."""

    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # String instead of Enum for SQLite compatibility
    # "warning" | "high_risk" | "critical" | "info"
    alert_type = Column(String(30), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    scan_id = Column(String(36), nullable=True, index=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type}, read={self.is_read})>"
