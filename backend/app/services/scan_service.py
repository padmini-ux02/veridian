"""Scan service orchestrating fraud detection across all content types."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.email_detector import EmailFraudDetector
from app.ai.explainer import FraudExplainer
from app.ai.sms_detector import SMSFraudDetector
from app.ai.url_detector import URLPhishingDetector
from app.models.alert import Alert
from app.models.scan import ScanResult
from app.models.user import User

logger = logging.getLogger("veridian.services.scan")

# Initialize AI modules as singletons
_sms_detector: Optional[SMSFraudDetector] = None
_email_detector: Optional[EmailFraudDetector] = None
_url_detector: Optional[URLPhishingDetector] = None
_explainer: Optional[FraudExplainer] = None


def get_sms_detector() -> SMSFraudDetector:
    global _sms_detector
    if _sms_detector is None:
        _sms_detector = SMSFraudDetector()
    return _sms_detector


def get_email_detector() -> EmailFraudDetector:
    global _email_detector
    if _email_detector is None:
        _email_detector = EmailFraudDetector()
    return _email_detector


def get_url_detector() -> URLPhishingDetector:
    global _url_detector
    if _url_detector is None:
        _url_detector = URLPhishingDetector()
    return _url_detector


def get_explainer() -> FraudExplainer:
    global _explainer
    if _explainer is None:
        _explainer = FraudExplainer()
    return _explainer


class ScanService:
    """Service layer for fraud detection scanning operations."""

    @staticmethod
    def perform_scan(
        db: Session, user: User, scan_type: str, content: str
    ) -> Dict[str, Any]:
        """Perform a fraud detection scan on the given content.

        Args:
            db: Database session
            user: Current authenticated user
            scan_type: Type of scan ('sms', 'email', 'url')
            content: The content to analyze

        Returns:
            Complete scan result with AI analysis

        Raises:
            ValueError: If scan_type is invalid
        """
        # Run appropriate detector
        if scan_type == "sms":
            detector = get_sms_detector()
            prediction = detector.predict(content)
        elif scan_type == "email":
            detector = get_email_detector()
            prediction = detector.predict(content)
        elif scan_type == "url":
            detector = get_url_detector()
            prediction = detector.predict(content)
        else:
            raise ValueError(f"Invalid scan type: {scan_type}")

        # Get detailed explanation
        explainer = get_explainer()
        full_explanation = explainer.generate_full_explanation(
            scan_type, content, prediction
        )

        # Store scan result in database
        scan_result = ScanResult(
            user_id=user.id,
            scan_type=scan_type,
            input_content=content[:5000],  # Limit stored content
            is_fraud=1 if prediction["is_fraud"] else 0,
            fraud_probability=prediction["fraud_probability"],
            risk_category=prediction["risk_category"],
            risk_score=prediction["risk_score"],
            explanation=prediction["explanation"],
            suspicious_keywords=json.dumps(prediction["suspicious_keywords"]),
            feature_importance=json.dumps(prediction["feature_importance"]),
            model_used=prediction["model_used"],
            processing_time_ms=prediction["processing_time_ms"],
        )

        db.add(scan_result)

        # Create alert for high/critical risk
        if prediction["risk_category"] in ("high", "critical"):
            alert = Alert(
                user_id=user.id,
                alert_type="high_risk" if prediction["risk_category"] == "high" else "critical",
                title=f"High-Risk {scan_type.upper()} Detected",
                message=(
                    f"A {scan_type} scan detected {prediction['risk_category']} risk content "
                    f"with {prediction['fraud_probability']:.1f}% fraud probability."
                ),
                scan_id=scan_result.id,
            )
            db.add(alert)

        db.commit()
        db.refresh(scan_result)

        logger.info(
            f"Scan completed: type={scan_type}, risk={prediction['risk_category']}, "
            f"prob={prediction['fraud_probability']:.1f}%, user={user.email}"
        )

        return {
            "id": scan_result.id,
            "scan_type": scan_type,
            "input_content": content,
            "is_fraud": bool(prediction["is_fraud"]),
            "fraud_probability": float(prediction["fraud_probability"]),
            "risk_category": str(prediction["risk_category"]),
            "risk_score": float(prediction["risk_score"]),
            "explanation": str(prediction["explanation"]),
            "suspicious_keywords": [str(k) for k in prediction["suspicious_keywords"]],
            "feature_importance": {str(k): float(v) for k, v in prediction["feature_importance"].items()},
            "model_used": str(prediction["model_used"]),
            "processing_time_ms": int(prediction["processing_time_ms"]),
            "created_at": scan_result.created_at.isoformat(),
            "detailed_explanation": full_explanation,
        }

    @staticmethod
    def get_scan_history(
        db: Session, user_id: str, page: int = 1, page_size: int = 20,
        scan_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated scan history for a user.

        Args:
            db: Database session
            user_id: The user's ID
            page: Page number (1-indexed)
            page_size: Number of results per page
            scan_type: Optional filter by scan type

        Returns:
            Dictionary with scans list and pagination info
        """
        query = db.query(ScanResult).filter(ScanResult.user_id == user_id)

        if scan_type:
            query = query.filter(ScanResult.scan_type == scan_type)

        total = query.count()
        total_pages = max((total + page_size - 1) // page_size, 1)
        offset = (page - 1) * page_size

        scans = (
            query.order_by(ScanResult.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        scan_list = []
        for scan in scans:
            scan_list.append({
                "id": scan.id,
                "scan_type": scan.scan_type,
                "input_content": scan.input_content[:200] + "..." if len(scan.input_content) > 200 else scan.input_content,
                "is_fraud": bool(scan.is_fraud),
                "fraud_probability": scan.fraud_probability,
                "risk_category": scan.risk_category,
                "risk_score": scan.risk_score,
                "explanation": scan.explanation or "",
                "suspicious_keywords": json.loads(scan.suspicious_keywords) if scan.suspicious_keywords else [],
                "feature_importance": json.loads(scan.feature_importance) if scan.feature_importance else {},
                "model_used": scan.model_used or "",
                "processing_time_ms": scan.processing_time_ms or 0,
                "created_at": scan.created_at.isoformat(),
            })

        return {
            "scans": scan_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @staticmethod
    def get_scan_by_id(db: Session, scan_id: str, user_id: str) -> Optional[Dict]:
        """Get a specific scan result by ID."""
        scan = (
            db.query(ScanResult)
            .filter(ScanResult.id == scan_id, ScanResult.user_id == user_id)
            .first()
        )

        if not scan:
            return None

        return {
            "id": scan.id,
            "scan_type": scan.scan_type,
            "input_content": scan.input_content,
            "is_fraud": bool(scan.is_fraud),
            "fraud_probability": scan.fraud_probability,
            "risk_category": scan.risk_category,
            "risk_score": scan.risk_score,
            "explanation": scan.explanation or "",
            "suspicious_keywords": json.loads(scan.suspicious_keywords) if scan.suspicious_keywords else [],
            "feature_importance": json.loads(scan.feature_importance) if scan.feature_importance else {},
            "model_used": scan.model_used or "",
            "processing_time_ms": scan.processing_time_ms or 0,
            "created_at": scan.created_at.isoformat(),
        }

    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """Get scan statistics for a specific user."""
        base_query = db.query(ScanResult).filter(ScanResult.user_id == user_id)

        total_scans = base_query.count()
        fraud_detected = base_query.filter(ScanResult.is_fraud == 1).count()
        safe_detected = total_scans - fraud_detected

        high_risk = base_query.filter(
            ScanResult.risk_category.in_(["high", "critical"])
        ).count()
        medium_risk = base_query.filter(ScanResult.risk_category == "medium").count()
        low_risk = base_query.filter(ScanResult.risk_category == "low").count()

        sms_scans = base_query.filter(ScanResult.scan_type == "sms").count()
        email_scans = base_query.filter(ScanResult.scan_type == "email").count()
        url_scans = base_query.filter(ScanResult.scan_type == "url").count()

        avg_risk = base_query.with_entities(
            func.avg(ScanResult.risk_score)
        ).scalar() or 0.0

        # Scans by date (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_scans = (
            db.query(
                func.date(ScanResult.created_at).label("date"),
                func.count(ScanResult.id).label("count"),
                func.sum(ScanResult.is_fraud).label("fraud_count"),
            )
            .filter(
                ScanResult.user_id == user_id,
                ScanResult.created_at >= thirty_days_ago,
            )
            .group_by(func.date(ScanResult.created_at))
            .order_by(func.date(ScanResult.created_at))
            .all()
        )

        scans_by_date = [
            {
                "date": str(row.date),
                "total": row.count,
                "fraud": int(row.fraud_count or 0),
            }
            for row in daily_scans
        ]

        return {
            "total_scans": total_scans,
            "fraud_detected": fraud_detected,
            "safe_detected": safe_detected,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "sms_scans": sms_scans,
            "email_scans": email_scans,
            "url_scans": url_scans,
            "average_risk_score": round(float(avg_risk), 2),
            "scans_by_date": scans_by_date,
        }

    @staticmethod
    def get_admin_stats(db: Session) -> Dict[str, Any]:
        """Get global scan statistics for admin dashboard."""
        total_scans = db.query(ScanResult).count()
        fraud_detected = db.query(ScanResult).filter(ScanResult.is_fraud == 1).count()
        safe_detected = total_scans - fraud_detected
        total_users = db.query(User).count()

        high_risk = db.query(ScanResult).filter(
            ScanResult.risk_category.in_(["high", "critical"])
        ).count()
        medium_risk = db.query(ScanResult).filter(
            ScanResult.risk_category == "medium"
        ).count()
        low_risk = db.query(ScanResult).filter(
            ScanResult.risk_category == "low"
        ).count()

        sms_scans = db.query(ScanResult).filter(ScanResult.scan_type == "sms").count()
        email_scans = db.query(ScanResult).filter(ScanResult.scan_type == "email").count()
        url_scans = db.query(ScanResult).filter(ScanResult.scan_type == "url").count()

        avg_risk = db.query(func.avg(ScanResult.risk_score)).scalar() or 0.0

        # Fraud trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_stats = (
            db.query(
                func.date(ScanResult.created_at).label("date"),
                func.count(ScanResult.id).label("total"),
                func.sum(ScanResult.is_fraud).label("fraud"),
            )
            .filter(ScanResult.created_at >= thirty_days_ago)
            .group_by(func.date(ScanResult.created_at))
            .order_by(func.date(ScanResult.created_at))
            .all()
        )

        fraud_trends = [
            {
                "date": str(row.date),
                "total": row.total,
                "fraud": int(row.fraud or 0),
                "safe": row.total - int(row.fraud or 0),
            }
            for row in daily_stats
        ]

        # Recent scans
        recent_scans = (
            db.query(ScanResult)
            .order_by(ScanResult.created_at.desc())
            .limit(10)
            .all()
        )

        recent_list = [
            {
                "id": s.id,
                "scan_type": s.scan_type,
                "risk_category": s.risk_category,
                "fraud_probability": s.fraud_probability,
                "created_at": s.created_at.isoformat(),
            }
            for s in recent_scans
        ]

        return {
            "total_users": total_users,
            "total_scans": total_scans,
            "fraud_detected": fraud_detected,
            "safe_detected": safe_detected,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "sms_scans": sms_scans,
            "email_scans": email_scans,
            "url_scans": url_scans,
            "average_risk_score": round(float(avg_risk), 2),
            "fraud_trends": fraud_trends,
            "recent_scans": recent_list,
        }
