"""URL Phishing Detection module.

Analyzes URLs for phishing indicators including:
- URL structure and length analysis
- Special character frequency
- Suspicious keyword detection
- TLD (top-level domain) reputation
- HTTPS validation
- IP address usage detection
- Domain entropy analysis
- Subdomain analysis
"""

import re
import math
import time
import logging
import os
import pickle
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger("veridian.ai.url")

# Suspicious TLDs commonly used in phishing
SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club",
    ".online", ".site", ".website", ".info", ".link", ".click",
    ".loan", ".win", ".racing", ".review", ".party", ".trade",
    ".bid", ".stream", ".download", ".accountant", ".science",
    ".work", ".date", ".faith", ".cricket",
}

# Trusted TLDs
TRUSTED_TLDS = {
    ".com", ".org", ".net", ".edu", ".gov", ".mil",
    ".co.uk", ".ac.uk", ".gov.uk", ".co.in", ".gov.in",
    ".co.jp", ".de", ".fr", ".ca", ".au", ".io",
}

# Known legitimate domains
LEGITIMATE_DOMAINS = {
    "google.com", "facebook.com", "amazon.com", "apple.com",
    "microsoft.com", "netflix.com", "paypal.com", "linkedin.com",
    "twitter.com", "github.com", "stackoverflow.com", "youtube.com",
    "instagram.com", "whatsapp.com", "wikipedia.org", "reddit.com",
    "yahoo.com", "outlook.com", "live.com", "office.com",
    "dropbox.com", "adobe.com", "zoom.us", "slack.com",
}

# Suspicious keywords in URLs
PHISHING_URL_KEYWORDS = [
    "login", "signin", "sign-in", "verify", "verification",
    "secure", "security", "account", "update", "confirm",
    "banking", "password", "credential", "authenticate",
    "wallet", "payment", "billing", "invoice", "suspend",
    "locked", "unlock", "restore", "recover", "alert",
    "notification", "warning", "urgent", "important",
    "free", "winner", "prize", "gift", "bonus",
    "paypal", "apple", "microsoft", "google", "amazon",
    "netflix", "facebook", "instagram", "whatsapp",
]

# Brand impersonation patterns
BRAND_IMPERSONATION = [
    r"(?i)(?:paypa[l1]|pay-pal|payp[a@]l)",
    r"(?i)(?:g[o0]{2}g[l1]e|go+gle)",
    r"(?i)(?:amaz[o0]n|amazn|amzon)",
    r"(?i)(?:app[l1]e|app1e)",
    r"(?i)(?:micr[o0]s[o0]ft|m1crosoft)",
    r"(?i)(?:faceb[o0]{2}k|faceb00k)",
    r"(?i)(?:netf[l1]ix|netfl1x)",
    r"(?i)(?:inst[a@]gr[a@]m)",
]


class URLPhishingDetector:
    """URL phishing detection using feature engineering and ML classification."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.lr_model: Optional[LogisticRegression] = None
        self.rf_model: Optional[RandomForestClassifier] = None
        self.is_trained = False
        self._initialize_models()

    def _initialize_models(self):
        """Initialize or load pre-trained models."""
        if self.model_path and os.path.exists(self.model_path):
            try:
                self._load_model(self.model_path)
                logger.info("Loaded pre-trained URL model from disk")
                return
            except Exception as e:
                logger.warning(f"Failed to load URL model: {e}")

        self._train_default_model()

    def _extract_url_features(self, url: str) -> Dict[str, float]:
        """Extract comprehensive numerical features from a URL."""
        features = {}

        # Ensure URL has scheme for parsing
        if not url.startswith(("http://", "https://")):
            url_parsed = urlparse("http://" + url)
        else:
            url_parsed = urlparse(url)

        domain = url_parsed.netloc.lower()
        path = url_parsed.path
        query = url_parsed.query

        # 1. Length features
        features["url_length"] = len(url)
        features["domain_length"] = len(domain)
        features["path_length"] = len(path)
        features["query_length"] = len(query)

        # 2. Character analysis
        features["dot_count"] = url.count(".")
        features["hyphen_count"] = url.count("-")
        features["underscore_count"] = url.count("_")
        features["slash_count"] = url.count("/")
        features["at_count"] = url.count("@")
        features["ampersand_count"] = url.count("&")
        features["equals_count"] = url.count("=")
        features["question_count"] = url.count("?")
        features["percent_count"] = url.count("%")
        features["tilde_count"] = url.count("~")

        # Special character ratio
        special_chars = sum(1 for c in url if not c.isalnum() and c not in ":/.")
        features["special_char_ratio"] = special_chars / max(len(url), 1)

        # Digit ratio in domain
        domain_digits = sum(1 for c in domain if c.isdigit())
        features["domain_digit_ratio"] = domain_digits / max(len(domain), 1)

        # 3. Protocol analysis
        features["is_https"] = 1.0 if url_parsed.scheme == "https" else 0.0

        # 4. IP address detection
        features["has_ip_address"] = 1.0 if re.search(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b", domain
        ) else 0.0

        # 5. Port usage
        domain_host = domain.split("@")[-1].split("/")[0]
        domain_suffix = domain_host.split(".", 1)[-1] if "." in domain_host else domain_host
        features["has_port"] = 1.0 if ":" in domain_suffix else 0.0
        try:
            if url_parsed.port and url_parsed.port not in (80, 443):
                features["has_port"] = 1.0
                features["unusual_port"] = 1.0
            else:
                features["unusual_port"] = 0.0
        except ValueError:
            features["unusual_port"] = 0.0

        # 6. Subdomain analysis
        domain_parts = domain.replace("www.", "").split(".")
        features["subdomain_count"] = max(len(domain_parts) - 2, 0)
        features["has_excessive_subdomains"] = 1.0 if features["subdomain_count"] > 2 else 0.0

        # 7. TLD analysis
        tld = "." + domain_parts[-1] if domain_parts else ""
        features["suspicious_tld"] = 1.0 if tld in SUSPICIOUS_TLDS else 0.0
        features["trusted_tld"] = 1.0 if tld in TRUSTED_TLDS else 0.0

        # 8. Domain reputation
        base_domain = ".".join(domain_parts[-2:]) if len(domain_parts) >= 2 else domain
        features["is_known_domain"] = 1.0 if base_domain in LEGITIMATE_DOMAINS else 0.0

        # 9. Phishing keyword count
        url_lower = url.lower()
        features["phishing_keyword_count"] = sum(
            1 for kw in PHISHING_URL_KEYWORDS if kw in url_lower
        )

        # 10. Brand impersonation
        features["brand_impersonation"] = sum(
            1 for pattern in BRAND_IMPERSONATION if re.search(pattern, url)
        )

        # 11. URL entropy
        if url:
            freq = Counter(url.lower())
            length = len(url)
            features["url_entropy"] = -sum(
                (c / length) * math.log2(c / length) for c in freq.values()
            )
        else:
            features["url_entropy"] = 0

        # 12. Domain entropy
        if domain:
            freq = Counter(domain.lower())
            length = len(domain)
            features["domain_entropy"] = -sum(
                (c / length) * math.log2(c / length) for c in freq.values()
            )
        else:
            features["domain_entropy"] = 0

        # 13. Path analysis
        features["path_has_double_slash"] = 1.0 if "//" in path else 0.0
        features["has_redirect"] = 1.0 if "redirect" in url_lower or "url=" in url_lower else 0.0

        # 14. Encoded characters
        features["encoded_char_count"] = len(re.findall(r"%[0-9a-fA-F]{2}", url))

        # 15. Shortened URL detection
        shorteners = ["bit.ly", "goo.gl", "tinyurl.com", "t.co", "is.gd", "ow.ly",
                       "cutt.ly", "rb.gy", "shorturl.at"]
        features["is_shortened"] = 1.0 if any(s in domain for s in shorteners) else 0.0

        return features

    def _calculate_rule_score(self, url: str, features: Dict[str, float]) -> Tuple[float, List[str]]:
        """Calculate rule-based phishing score."""
        score = 0.0
        indicators = []

        # Length indicators
        if features["url_length"] > 75:
            score += 5.0
            indicators.append("very_long_url")
        if features["url_length"] > 150:
            score += 5.0

        # No HTTPS
        if features["is_https"] == 0.0:
            score += 8.0
            indicators.append("no_https")

        # IP address usage
        if features["has_ip_address"] == 1.0:
            score += 15.0
            indicators.append("ip_address_in_url")

        # Suspicious TLD
        if features["suspicious_tld"] == 1.0:
            score += 12.0
            indicators.append("suspicious_tld")

        # Excessive subdomains
        if features["has_excessive_subdomains"] == 1.0:
            score += 8.0
            indicators.append("excessive_subdomains")

        # Phishing keywords
        if features["phishing_keyword_count"] > 0:
            score += features["phishing_keyword_count"] * 4.0
            indicators.append(f"phishing_keywords: {int(features['phishing_keyword_count'])}")

        # Brand impersonation
        if features["brand_impersonation"] > 0:
            score += features["brand_impersonation"] * 15.0
            indicators.append("brand_impersonation")

        # @ symbol in URL (can be used for credential harvesting)
        if features["at_count"] > 0:
            score += 10.0
            indicators.append("at_symbol_in_url")

        # High special character ratio
        if features["special_char_ratio"] > 0.3:
            score += 6.0
            indicators.append("high_special_chars")

        # Shortened URL
        if features["is_shortened"] == 1.0:
            score += 7.0
            indicators.append("shortened_url")

        # Unusual port
        if features["unusual_port"] == 1.0:
            score += 8.0
            indicators.append("unusual_port")

        # Redirect detection
        if features["has_redirect"] == 1.0:
            score += 6.0
            indicators.append("redirect_detected")

        # High domain digit ratio
        if features["domain_digit_ratio"] > 0.3:
            score += 5.0
            indicators.append("many_digits_in_domain")

        # Known domain bonus (reduce score)
        if features["is_known_domain"] == 1.0:
            score = max(score - 30.0, 0.0)
            indicators = [i for i in indicators if i != "suspicious_tld"]

        normalized = min(score / 60.0 * 100, 100.0)
        return normalized, indicators

    def _train_default_model(self):
        """Train with built-in URL dataset."""
        training_data = [
            # Phishing URLs
            ("http://secure-paypal-login.tk/verify/account", 1),
            ("http://192.168.1.1/login/microsoft/update.html", 1),
            ("http://www.gooogle-security.xyz/signin?redirect=true", 1),
            ("http://apple-id-verify.ml/confirm-identity", 1),
            ("http://amaz0n.customer.support.click/order/123", 1),
            ("http://netflix-billing.ga/update-payment", 1),
            ("https://login.microsoft.account.verify.tk/auth", 1),
            ("http://faceb00k-security-alert.club/verify", 1),
            ("http://banking-secure-login.online/verify/card", 1),
            ("http://www.paypal.com.secure.login.xyz/webscr", 1),
            ("http://bit.ly/free-prize-winner-2024", 1),
            ("http://192.168.0.1:8080/admin/steal-credentials.php", 1),
            ("http://google-doc-shared.site/document/edit", 1),
            ("http://instagram-verify.gq/confirm-account", 1),
            ("http://www.bank-of-america.security-update.top/login", 1),
            ("http://dropbox-file-share.cf/download/important", 1),
            ("http://whatsapp-update.ml/verify-number", 1),
            ("http://linkedin-invitation.xyz/accept?user=target", 1),
            ("http://microsoft-365-login.club/signin/oauth", 1),
            ("http://www.wells-fargo.secure.login.bid/online", 1),
            ("http://122.134.56.78/paypal/login.php", 1),
            ("http://secure.chase.com.verify.stream/account", 1),
            ("http://outlook-password-reset.download/recover", 1),
            ("http://icloud-find-device.party/locate?id=123", 1),
            ("http://zoom-meeting-join.tk/meeting/join", 1),

            # Legitimate URLs
            ("https://www.google.com/search?q=python+tutorial", 0),
            ("https://www.amazon.com/dp/B08N5WRWNW", 0),
            ("https://github.com/microsoft/vscode", 0),
            ("https://www.netflix.com/browse", 0),
            ("https://mail.google.com/mail/u/0/", 0),
            ("https://www.paypal.com/myaccount/summary", 0),
            ("https://www.linkedin.com/in/johndoe", 0),
            ("https://stackoverflow.com/questions/12345", 0),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0),
            ("https://en.wikipedia.org/wiki/Machine_learning", 0),
            ("https://www.apple.com/iphone-15-pro/", 0),
            ("https://www.microsoft.com/en-us/microsoft-365", 0),
            ("https://www.facebook.com/events/123456", 0),
            ("https://www.reddit.com/r/programming/", 0),
            ("https://www.nytimes.com/2024/01/15/technology", 0),
            ("https://docs.python.org/3/library/re.html", 0),
            ("https://www.instagram.com/natgeo/", 0),
            ("https://twitter.com/elonmusk/status/123", 0),
            ("https://www.dropbox.com/home", 0),
            ("https://zoom.us/j/1234567890", 0),
            ("https://www.bbc.com/news/technology-12345", 0),
            ("https://www.coursera.org/learn/machine-learning", 0),
            ("https://www.udemy.com/course/python-bootcamp/", 0),
            ("https://www.office.com/launch/word", 0),
            ("https://slack.com/workspace/myteam", 0),
        ]

        # Extract features for all URLs
        X = []
        y = []
        for url, label in training_data:
            features = self._extract_url_features(url)
            X.append(list(features.values()))
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        self.feature_names = list(self._extract_url_features(training_data[0][0]).keys())

        self.lr_model = LogisticRegression(
            C=1.0, max_iter=1000, class_weight="balanced", random_state=42
        )
        self.lr_model.fit(X, y)

        self.rf_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, class_weight="balanced", random_state=42
        )
        self.rf_model.fit(X, y)

        self.is_trained = True
        logger.info("URL phishing detection models trained successfully")

    def predict(self, url: str) -> Dict[str, Any]:
        """Analyze a URL for phishing indicators.

        Returns comprehensive analysis including safe/unsafe determination,
        risk score, explanation, and feature importance.
        """
        start = time.time()

        features = self._extract_url_features(url)
        rule_score, indicators = self._calculate_rule_score(url, features)

        # ML prediction
        ml_probability = 0.0
        if self.is_trained:
            X = np.array([list(features.values())])
            lr_prob = self.lr_model.predict_proba(X)[0][1] * 100
            rf_prob = self.rf_model.predict_proba(X)[0][1] * 100
            ml_probability = (lr_prob * 0.35) + (rf_prob * 0.35) + (rule_score * 0.3)
        else:
            ml_probability = rule_score

        fraud_probability = round(min(max(ml_probability, 0.0), 100.0), 2)

        if fraud_probability >= 80:
            risk_category = "critical"
        elif fraud_probability >= 60:
            risk_category = "high"
        elif fraud_probability >= 35:
            risk_category = "medium"
        else:
            risk_category = "low"

        is_fraud = fraud_probability >= 50
        is_safe = not is_fraud

        # Feature importance
        feature_importance = {
            "url_structure": round(min(
                features["url_length"] / 200 * 20 +
                features["special_char_ratio"] * 30, 25
            ), 2),
            "domain_reputation": round(
                features["suspicious_tld"] * 20 +
                (1 - features["is_known_domain"]) * 10 +
                features["brand_impersonation"] * 20, 2
            ),
            "security_protocol": round(
                (1 - features["is_https"]) * 15 +
                features["has_ip_address"] * 15, 2
            ),
            "phishing_indicators": round(min(
                features["phishing_keyword_count"] * 8, 20
            ), 2),
            "obfuscation": round(min(
                features["encoded_char_count"] * 5 +
                features["is_shortened"] * 10, 15
            ), 2),
        }

        total_imp = sum(feature_importance.values())
        if total_imp > 0:
            feature_importance = {
                k: round(v / total_imp * 100, 2) for k, v in feature_importance.items()
            }

        explanation = self._generate_explanation(
            url, fraud_probability, risk_category, features, indicators, is_safe
        )

        processing_time = int((time.time() - start) * 1000)

        return {
            "is_fraud": is_fraud,
            "is_safe": is_safe,
            "fraud_probability": fraud_probability,
            "risk_category": risk_category,
            "risk_score": fraud_probability,
            "explanation": explanation,
            "suspicious_keywords": indicators[:15],
            "feature_importance": feature_importance,
            "model_used": "URL Feature Engineering + LR + RF Ensemble",
            "processing_time_ms": processing_time,
        }

    def _generate_explanation(
        self, url: str, probability: float, risk_category: str,
        features: Dict, indicators: List[str], is_safe: bool
    ) -> str:
        """Generate human-readable URL analysis explanation."""
        parts = []

        status = "SAFE ✓" if is_safe else "UNSAFE ✗"
        if risk_category == "critical":
            parts.append(f"⚠️ {status} - CRITICAL RISK ({probability:.1f}%): This URL is highly likely a phishing attempt.")
        elif risk_category == "high":
            parts.append(f"🔴 {status} - HIGH RISK ({probability:.1f}%): This URL shows strong phishing indicators.")
        elif risk_category == "medium":
            parts.append(f"🟡 {status} - MEDIUM RISK ({probability:.1f}%): This URL has some suspicious characteristics.")
        else:
            parts.append(f"🟢 {status} - LOW RISK ({probability:.1f}%): This URL appears to be safe.")

        if features["is_https"] == 0.0:
            parts.append("• ⚠️ No HTTPS encryption — data transmitted insecurely.")

        if features["has_ip_address"] == 1.0:
            parts.append("• Uses IP address instead of domain name (common in phishing).")

        if features["suspicious_tld"] == 1.0:
            parts.append("• Uses a suspicious top-level domain commonly associated with phishing.")

        if features["has_excessive_subdomains"] == 1.0:
            parts.append(f"• Excessive subdomain depth ({int(features['subdomain_count'])} levels).")

        if features["phishing_keyword_count"] > 0:
            parts.append(f"• Contains {int(features['phishing_keyword_count'])} phishing-related keyword(s) in URL.")

        if features["brand_impersonation"] > 0:
            parts.append("• ⚠️ Appears to impersonate a well-known brand (typosquatting).")

        if features["is_shortened"] == 1.0:
            parts.append("• URL is shortened, hiding the actual destination.")

        if features["at_count"] > 0:
            parts.append("• Contains '@' symbol which can be used to deceive users about the actual domain.")

        if features["url_length"] > 100:
            parts.append(f"• Unusually long URL ({int(features['url_length'])} characters).")

        if features["is_known_domain"] == 1.0:
            parts.append("• ✓ Domain belongs to a known, legitimate service.")

        return "\n".join(parts)

    def save_model(self, path: str):
        """Save trained models to disk."""
        model_data = {
            "lr_model": self.lr_model,
            "rf_model": self.rf_model,
            "feature_names": getattr(self, "feature_names", []),
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    def _load_model(self, path: str):
        """Load pre-trained models from disk."""
        with open(path, "rb") as f:
            model_data = pickle.load(f)
        self.lr_model = model_data["lr_model"]
        self.rf_model = model_data["rf_model"]
        self.feature_names = model_data.get("feature_names", [])
        self.is_trained = True
