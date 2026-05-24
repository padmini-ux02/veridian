"""Report service for managing user-submitted fraud reports."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.report import FraudReport
from app.models.user import User

logger = logging.getLogger("veridian.services.report")


class ReportService:
    """Service layer for fraud report CRUD operations."""

    @staticmethod
    def create_report(
        db: Session, user: User, report_type: str, title: str,
        content: str, description: Optional[str] = None,
        source: Optional[str] = None
    ) -> FraudReport:
        """Create a new fraud report submitted by a user."""
        report = FraudReport(
            user_id=user.id,
            report_type=report_type,
            title=title,
            content=content,
            description=description,
            source=source,
            status="pending",
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        logger.info(f"New fraud report created: {report.id} by {user.email}")
        return report

    @staticmethod
    def get_user_reports(
        db: Session, user_id: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Get paginated reports submitted by a specific user."""
        query = db.query(FraudReport).filter(FraudReport.user_id == user_id)
        total = query.count()
        total_pages = max((total + page_size - 1) // page_size, 1)
        offset = (page - 1) * page_size

        reports = (
            query.order_by(FraudReport.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {
            "reports": [ReportService._report_to_dict(r) for r in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @staticmethod
    def get_all_reports(
        db: Session, page: int = 1, page_size: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all reports (admin) with optional status filter."""
        query = db.query(FraudReport)

        if status:
            query = query.filter(FraudReport.status == status)

        total = query.count()
        total_pages = max((total + page_size - 1) // page_size, 1)
        offset = (page - 1) * page_size

        reports = (
            query.order_by(FraudReport.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # Enrich with reporter info
        report_list = []
        for report in reports:
            report_dict = ReportService._report_to_dict(report)
            user = db.query(User).filter(User.id == report.user_id).first()
            report_dict["reporter_username"] = user.username if user else "unknown"
            report_list.append(report_dict)

        return {
            "reports": report_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @staticmethod
    def update_report_status(
        db: Session, report_id: str, status: str,
        admin_notes: Optional[str], admin_id: str
    ) -> Optional[FraudReport]:
        """Update a report's status (admin action)."""
        report = db.query(FraudReport).filter(FraudReport.id == report_id).first()
        if not report:
            return None

        report.status = status
        report.admin_notes = admin_notes
        report.reviewed_by = admin_id
        report.reviewed_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        logger.info(f"Report {report_id} status updated to {status} by admin {admin_id}")
        return report

    @staticmethod
    def get_report_by_id(db: Session, report_id: str) -> Optional[Dict]:
        """Get a specific report by ID."""
        report = db.query(FraudReport).filter(FraudReport.id == report_id).first()
        if not report:
            return None
        
        report_dict = ReportService._report_to_dict(report)
        user = db.query(User).filter(User.id == report.user_id).first()
        report_dict["reporter_username"] = user.username if user else "unknown"
        return report_dict

    @staticmethod
    def get_report_stats(db: Session) -> Dict[str, int]:
        """Get report statistics for admin dashboard."""
        total = db.query(FraudReport).count()
        pending = db.query(FraudReport).filter(FraudReport.status == "pending").count()
        reviewing = db.query(FraudReport).filter(FraudReport.status == "reviewing").count()
        confirmed = db.query(FraudReport).filter(FraudReport.status == "confirmed_fraud").count()
        dismissed = db.query(FraudReport).filter(FraudReport.status == "dismissed").count()

        return {
            "total_reports": total,
            "pending": pending,
            "reviewing": reviewing,
            "confirmed_fraud": confirmed,
            "dismissed": dismissed,
        }

    @staticmethod
    def _report_to_dict(report: FraudReport) -> Dict[str, Any]:
        """Convert a FraudReport model to a dictionary."""
        return {
            "id": report.id,
            "user_id": report.user_id,
            "report_type": report.report_type,
            "title": report.title,
            "content": report.content,
            "description": report.description,
            "source": report.source,
            "status": report.status,
            "admin_notes": report.admin_notes,
            "reviewed_by": report.reviewed_by,
            "reviewed_at": report.reviewed_at.isoformat() if report.reviewed_at else None,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
