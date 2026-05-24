"""Tests for fraud detection scan endpoints and AI models."""

import pytest


class TestSMSScan:
    """Test SMS fraud detection."""

    def test_scan_spam_sms(self, client, auth_headers):
        """Test scanning a spam SMS message."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={
                "scan_type": "sms",
                "content": "Congratulations! You've won a $1,000 gift card! Click here to claim: http://bit.ly/free",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_fraud"] is True
        assert data["fraud_probability"] > 40
        assert data["risk_category"] in ("medium", "high", "critical")
        assert len(data["suspicious_keywords"]) > 0
        assert data["explanation"]

    def test_scan_legitimate_sms(self, client, auth_headers):
        """Test scanning a legitimate SMS message."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={
                "scan_type": "sms",
                "content": "Hey, are you coming to the meeting at 3pm today?",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fraud_probability"] < 50
        assert data["risk_category"] in ("low", "medium")

    def test_scan_empty_content(self, client, auth_headers):
        """Test scanning with empty content."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={"scan_type": "sms", "content": "   "},
        )
        assert response.status_code == 422


class TestEmailScan:
    """Test email fraud detection."""

    def test_scan_phishing_email(self, client, auth_headers):
        """Test scanning a phishing email."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={
                "scan_type": "email",
                "content": "Dear valued customer, your account has been suspended. Click here to verify your identity immediately or your account will be permanently closed.",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_fraud"] is True
        assert data["fraud_probability"] > 40
        assert data["explanation"]

    def test_scan_legitimate_email(self, client, auth_headers):
        """Test scanning a legitimate email."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={
                "scan_type": "email",
                "content": "Hi team, please find the quarterly report attached. Let me know if you have questions.",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fraud_probability"] < 50


class TestURLScan:
    """Test URL phishing detection."""

    def test_scan_phishing_url(self, client, auth_headers):
        """Test scanning a phishing URL."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={
                "scan_type": "url",
                "content": "http://secure-paypal-login.tk/verify/account",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_fraud"] is True
        assert data["fraud_probability"] > 40

    def test_scan_legitimate_url(self, client, auth_headers):
        """Test scanning a legitimate URL."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={
                "scan_type": "url",
                "content": "https://www.google.com/search?q=python",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["fraud_probability"] < 50

    def test_scan_invalid_type(self, client, auth_headers):
        """Test scanning with invalid scan type."""
        response = client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={"scan_type": "invalid", "content": "test content"},
        )
        assert response.status_code == 422


class TestScanHistory:
    """Test scan history endpoints."""

    def test_get_empty_history(self, client, auth_headers):
        """Test getting scan history when empty."""
        response = client.get("/api/v1/scan/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["scans"] == []

    def test_get_history_after_scan(self, client, auth_headers):
        """Test getting scan history after performing scans."""
        client.post(
            "/api/v1/scan/analyze",
            headers=auth_headers,
            json={"scan_type": "sms", "content": "Test message for history"},
        )

        response = client.get("/api/v1/scan/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["scans"]) == 1

    def test_get_scan_stats(self, client, auth_headers):
        """Test getting scan statistics."""
        response = client.get("/api/v1/scan/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_scans" in data
        assert "fraud_detected" in data
