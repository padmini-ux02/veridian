"""Tests for AI model validation and accuracy."""

import pytest

from app.ai.sms_detector import SMSFraudDetector
from app.ai.email_detector import EmailFraudDetector
from app.ai.url_detector import URLPhishingDetector
from app.ai.chat_assistant import ChatAssistant
from app.ai.explainer import FraudExplainer


class TestSMSDetector:
    """Test SMS fraud detection model."""

    @pytest.fixture
    def detector(self):
        return SMSFraudDetector()

    def test_spam_detection(self, detector):
        """Test that known spam is detected."""
        result = detector.predict("You've won $1000! Claim now at http://prize.tk")
        assert result["fraud_probability"] > 30
        assert result["is_fraud"] is True or result["risk_category"] in ("medium", "high", "critical")

    def test_legitimate_detection(self, detector):
        """Test that legitimate messages are not flagged."""
        result = detector.predict("Hey, want to grab lunch today?")
        assert result["fraud_probability"] < 50
        assert result["risk_category"] in ("low", "medium")

    def test_financial_scam(self, detector):
        """Test financial scam detection."""
        result = detector.predict("Send $500 via Western Union to claim your prize of $50,000")
        assert result["fraud_probability"] > 40
        assert len(result["suspicious_keywords"]) > 0

    def test_output_structure(self, detector):
        """Test that output has all required fields."""
        result = detector.predict("Test message")
        required_fields = [
            "is_fraud", "fraud_probability", "risk_category",
            "risk_score", "explanation", "suspicious_keywords",
            "feature_importance", "model_used", "processing_time_ms",
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_probability_range(self, detector):
        """Test that probability is within valid range."""
        result = detector.predict("Any test message")
        assert 0 <= result["fraud_probability"] <= 100
        assert 0 <= result["risk_score"] <= 100


class TestEmailDetector:
    """Test email fraud detection model."""

    @pytest.fixture
    def detector(self):
        return EmailFraudDetector()

    def test_phishing_detection(self, detector):
        """Test phishing email detection."""
        result = detector.predict(
            "Your account has been suspended. Verify immediately at http://verify.tk"
        )
        assert result["fraud_probability"] > 30

    def test_legitimate_email(self, detector):
        """Test legitimate email detection."""
        result = detector.predict(
            "Hi team, the meeting has been moved to 3pm tomorrow."
        )
        assert result["fraud_probability"] < 50

    def test_output_structure(self, detector):
        """Test output has required fields."""
        result = detector.predict("Test email content")
        assert "is_fraud" in result
        assert "explanation" in result
        assert "feature_importance" in result


class TestURLDetector:
    """Test URL phishing detection model."""

    @pytest.fixture
    def detector(self):
        return URLPhishingDetector()

    def test_phishing_url(self, detector):
        """Test phishing URL detection."""
        result = detector.predict("http://paypal-login.tk/verify")
        assert result["fraud_probability"] > 30

    def test_legitimate_url(self, detector):
        """Test legitimate URL detection."""
        result = detector.predict("https://www.google.com")
        assert result["fraud_probability"] < 50

    def test_ip_url(self, detector):
        """Test URL with IP address."""
        result = detector.predict("http://192.168.1.1/login")
        assert result["fraud_probability"] > 20

    def test_safe_unsafe_flag(self, detector):
        """Test safe/unsafe flag consistency."""
        result = detector.predict("http://malicious.tk/steal")
        assert "is_safe" in result
        assert result["is_safe"] != result["is_fraud"]


class TestChatAssistant:
    """Test AI chat assistant."""

    @pytest.fixture
    def assistant(self):
        return ChatAssistant()

    def test_scam_identification_query(self, assistant):
        """Test query about identifying scams."""
        result = assistant.chat("How can I identify scam messages?")
        assert result["intent"] == "identify_scam"
        assert len(result["response"]) > 100

    def test_danger_explanation(self, assistant):
        """Test danger explanation without context."""
        result = assistant.chat("Why is this message dangerous?")
        assert result["intent"] == "why_dangerous"
        assert result["has_context"] is False

    def test_general_help(self, assistant):
        """Test general help query."""
        result = assistant.chat("Hello, how can you help me?")
        assert result["intent"] == "general_help"
        assert "Veridian" in result["response"]

    def test_with_scan_context(self, assistant):
        """Test response with scan context."""
        context = {
            "risk_category": "high",
            "fraud_probability": 85.5,
            "scan_type": "sms",
            "suspicious_keywords": ["claim", "prize", "URL: http://fake.tk"],
            "feature_importance": {"spam_keywords": 40, "urgency_indicators": 30},
        }
        result = assistant.chat("Why is this message dangerous?", scan_context=context)
        assert result["has_context"] is True
        assert "85.5" in result["response"]


class TestExplainer:
    """Test explainable AI module."""

    @pytest.fixture
    def explainer(self):
        return FraudExplainer()

    def test_full_explanation(self, explainer):
        """Test comprehensive explanation generation."""
        prediction = {
            "risk_category": "high",
            "fraud_probability": 78.5,
            "feature_importance": {"spam_keywords": 35, "urgency_indicators": 25, "url_presence": 20},
            "suspicious_keywords": ["free", "click here", "win"],
        }
        result = explainer.generate_full_explanation("sms", "Win free prizes!", prediction)
        assert "summary" in result
        assert "risk_factors" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_risk_factor_analysis(self, explainer):
        """Test risk factor ranking."""
        features = {"spam_keywords": 40, "urgency_indicators": 20, "url_presence": 5}
        factors = explainer._analyze_risk_factors(features)
        assert len(factors) > 0
        assert factors[0]["importance"] >= factors[-1]["importance"]
