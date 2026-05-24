"""Database models package — exports all ORM models."""

from app.models.user import User
from app.models.scan import ScanResult
from app.models.report import FraudReport
from app.models.alert import Alert

__all__ = ["User", "ScanResult", "FraudReport", "Alert"]
