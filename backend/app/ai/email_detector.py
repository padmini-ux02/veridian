"""Email Fraud Detection module for phishing, spam, and social engineering attacks.

Analyzes email content for:
- Phishing language patterns
- Urgency/pressure tactics
- Suspicious sender patterns
- Social engineering indicators
- Malicious link detection
"""

import re
import math
import time
import logging
import os
import pickle
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger("veridian.ai.email")

# Phishing language indicators
PHISHING_PATTERNS = [
    r"(?i)(?:verify|confirm|update|validate)\s+(?:your|the|account)\s+(?:account|identity|information|details|password)",
    r"(?i)(?:your\s+account\s+(?:has\s+been|is|will\s+be))\s+(?:suspended|locked|compromised|restricted|limited|closed)",
    r"(?i)(?:click\s+(?:here|the\s+link|below|this))\s+(?:to|and)\s+(?:verify|confirm|update|restore|unlock)",
    r"(?i)(?:unauthorized|suspicious|unusual)\s+(?:activity|login|access|transaction|sign[- ]?in)",
    r"(?i)(?:reset|change|update)\s+(?:your\s+)?password\s+(?:now|immediately|within)",
    r"(?i)(?:we\s+(?:have\s+)?noticed|we\s+detected|we\s+found)\s+(?:suspicious|unusual|unauthorized)",
    r"(?i)(?:failure\s+to\s+(?:comply|verify|respond|update))\s+(?:will|may)\s+(?:result|lead)",
    r"(?i)(?:dear\s+(?:valued\s+)?(?:customer|user|member|account\s+holder|client))",
    r"(?i)(?:your\s+(?:email|mailbox|inbox)\s+(?:is\s+)?(?:full|quota|storage|exceeded))",
    r"(?i)(?:payment\s+(?:failed|declined|rejected|problem|issue))",
    r"(?i)(?:refund|compensation|reimbursement)\s+(?:of|for|amount)",
    r"(?i)(?:security\s+(?:alert|warning|notice|update|breach))",
]

URGENCY_PHRASES = [
    r"(?i)(?:within\s+\d+\s+(?:hours?|minutes?|days?))",
    r"(?i)(?:immediately|urgent(?:ly)?|right\s+(?:now|away))",
    r"(?i)(?:act\s+(?:now|fast|quickly|immediately))",
    r"(?i)(?:time[- ]?sensitive|time[- ]?limited)",
    r"(?i)(?:last\s+(?:chance|warning|notice|reminder))",
    r"(?i)(?:expire|expiring|expires|expiration)\s+(?:today|soon|tonight|tomorrow)",
    r"(?i)(?:don'?t\s+(?:delay|wait|ignore|miss))",
    r"(?i)(?:as\s+soon\s+as\s+possible|asap)",
    r"(?i)(?:respond|reply|act|call)\s+(?:before|by|within)",
]

SOCIAL_ENGINEERING_PATTERNS = [
    r"(?i)(?:i\s+am\s+(?:a|the)\s+(?:prince|king|queen|minister|general|officer|banker|lawyer))",
    r"(?i)(?:inheritance|beneficiary|next\s+of\s+kin|unclaimed\s+funds)",
    r"(?i)(?:confidential|private|secret)\s+(?:matter|business|transaction|deal)",
    r"(?i)(?:(?:million|billion)\s+(?:dollars?|pounds?|euros?))",
    r"(?i)(?:transfer\s+(?:fee|cost|charge))",
    r"(?i)(?:help\s+me\s+(?:transfer|move|distribute))",
    r"(?i)(?:i\s+need\s+(?:your|a\s+trusted)\s+(?:help|assistance|partner))",
    r"(?i)(?:business\s+(?:proposal|opportunity|venture|deal))",
    r"(?i)(?:you\s+(?:have\s+been|are)\s+(?:selected|chosen|nominated|awarded))",
]

SUSPICIOUS_SENDER_PATTERNS = [
    r"(?i)(?:noreply|no-reply|donotreply|do-not-reply)",
    r"(?i)(?:admin|support|security|helpdesk|service)@(?!(?:google|microsoft|apple|amazon|paypal)\.com)",
    r"@.*\.(?:tk|ml|ga|cf|gq|xyz|top|club|online|site|website|info)\b",
    r"(?i)(?:notification|alert|warning|update)@",
]


class EmailFraudDetector:
    """Email fraud detection using NLP patterns and ML classification."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.lr_model: Optional[LogisticRegression] = None
        self.rf_model: Optional[RandomForestClassifier] = None
        self.is_trained = False
        self._initialize_models()

    def _initialize_models(self):
        """Initialize or load pre-trained models."""
        if self.model_path and os.path.exists(self.model_path):
            try:
                self._load_model(self.model_path)
                logger.info("Loaded pre-trained email model from disk")
                return
            except Exception as e:
                logger.warning(f"Failed to load email model: {e}")

        self._train_default_model()

    def _preprocess_email(self, text: str) -> str:
        """Clean and normalize email content."""
        text = text.lower().strip()
        text = re.sub(r"http\S+|www\.\S+", " URL_LINK ", text)
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " EMAIL_ADDR ", text)
        text = re.sub(r"<[^>]+>", " ", text)  # Remove HTML tags
        text = re.sub(r"&[a-zA-Z]+;", " ", text)  # Remove HTML entities
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive features from email content."""
        features = {}

        # Basic text statistics
        features["char_count"] = len(text)
        words = text.split()
        features["word_count"] = len(words)
        features["avg_word_length"] = np.mean([len(w) for w in words]) if words else 0
        features["sentence_count"] = max(len(re.split(r'[.!?]+', text)), 1)

        # Pattern counts
        features["phishing_pattern_count"] = sum(
            1 for p in PHISHING_PATTERNS if re.search(p, text)
        )
        features["urgency_phrase_count"] = sum(
            1 for p in URGENCY_PHRASES if re.search(p, text)
        )
        features["social_engineering_count"] = sum(
            1 for p in SOCIAL_ENGINEERING_PATTERNS if re.search(p, text)
        )
        features["suspicious_sender_count"] = sum(
            1 for p in SUSPICIOUS_SENDER_PATTERNS if re.search(p, text)
        )

        # Link analysis
        urls = re.findall(r"http\S+|www\.\S+", text)
        features["url_count"] = len(urls)
        features["has_shortened_url"] = int(any(
            re.search(r"(?:bit\.ly|goo\.gl|tinyurl|t\.co|is\.gd|ow\.ly)", url)
            for url in urls
        ))

        # Suspicious domain in URLs
        features["suspicious_tld_count"] = sum(
            1 for url in urls
            if re.search(r"\.(?:tk|ml|ga|cf|gq|xyz|top|club|online|site)\b", url)
        )

        # Formatting cues
        features["uppercase_ratio"] = (
            sum(1 for c in text if c.isupper()) / max(len(text), 1)
        )
        features["exclamation_count"] = text.count("!")
        features["html_tag_count"] = len(re.findall(r"<[^>]+>", text))

        # Money and financial references
        features["money_reference_count"] = len(
            re.findall(r"\$\s*[\d,]+(?:\.\d{2})?|\d+\s*(?:dollars?|usd|gbp|eur|pounds?)", text, re.I)
        )

        # Personal data requests
        features["personal_data_request"] = int(bool(re.search(
            r"(?i)(?:ssn|social\s+security|credit\s+card|bank\s+account|routing|password|pin|cvv|date\s+of\s+birth)",
            text,
        )))

        return features

    def _calculate_rule_score(self, text: str) -> Tuple[float, List[str]]:
        """Calculate rule-based phishing score."""
        score = 0.0
        indicators = []

        for pattern in PHISHING_PATTERNS:
            match = re.search(pattern, text)
            if match:
                score += 6.0
                indicators.append(f"phishing: {match.group()[:60]}")

        for pattern in URGENCY_PHRASES:
            match = re.search(pattern, text)
            if match:
                score += 4.0
                indicators.append(f"urgency: {match.group()[:40]}")

        for pattern in SOCIAL_ENGINEERING_PATTERNS:
            match = re.search(pattern, text)
            if match:
                score += 7.0
                indicators.append(f"social_engineering: {match.group()[:50]}")

        for pattern in SUSPICIOUS_SENDER_PATTERNS:
            match = re.search(pattern, text)
            if match:
                score += 5.0
                indicators.append(f"suspicious_sender: {match.group()[:40]}")

        # URL analysis
        urls = re.findall(r"http\S+|www\.\S+", text)
        for url in urls:
            if re.search(r"\.(?:tk|ml|ga|cf|gq|xyz|top)\b", url):
                score += 5.0
                indicators.append(f"suspicious_url: {url[:50]}")
            if re.search(r"(?:bit\.ly|goo\.gl|tinyurl|t\.co)", url):
                score += 3.0
                indicators.append(f"shortened_url: {url[:50]}")

        # Personal data requests
        if re.search(r"(?i)(?:ssn|credit\s+card|bank\s+account|password|pin|cvv)", text):
            score += 8.0
            indicators.append("personal_data_request")

        normalized = min(score / 60.0 * 100, 100.0)
        return normalized, indicators

    def _train_default_model(self):
        """Train with comprehensive email fraud dataset."""
        training_data = [
            # Phishing emails
            ("Dear valued customer, your account has been suspended due to suspicious activity. Click here to verify your identity immediately.", 1),
            ("URGENT: Your PayPal account has been limited. Please verify your information within 24 hours or your account will be permanently closed.", 1),
            ("Security Alert: We detected unauthorized access to your account from an unknown device. Reset your password now to secure your account.", 1),
            ("Your Apple ID has been locked for security reasons. To unlock, please verify your identity at http://apple-verify.tk/login", 1),
            ("Dear Account Holder, we noticed unusual login activity. Confirm your identity by clicking the link below to avoid account suspension.", 1),
            ("Congratulations! You have been selected to receive a tax refund of $4,829.00. Submit your bank details to process the refund.", 1),
            ("IMPORTANT: Your email storage quota has been exceeded. Click here to increase your mailbox size or your emails will be deleted.", 1),
            ("Dear user, your Netflix subscription payment failed. Update your payment method immediately: http://netflix-billing.xyz", 1),
            ("Your package could not be delivered. Pay the $2.99 shipping fee to reschedule: http://delivery-update.tk", 1),
            ("I am Prince Abubakar from Nigeria. I need your help transferring $4.5 million USD. You will receive 30% as compensation.", 1),
            ("WINNER NOTIFICATION: Your email has won the Microsoft Lottery 2024. Contact claims@lottery-msft.com with your full details.", 1),
            ("HR Department: Your salary has been credited incorrectly. Verify your bank details to receive the corrected amount.", 1),
            ("IT Support: Your password expires today. Click this link to reset it now and avoid losing access to your workstation.", 1),
            ("Dear beneficiary, you have an unclaimed inheritance of $2.8 million from a deceased relative. Contact our legal team.", 1),
            ("Your Amazon Prime membership auto-renewal of $499.99 has been processed. If unauthorized, call 1-800-555-0199.", 1),
            ("FINAL NOTICE: Your domain name will expire in 24 hours. Renew immediately at http://domain-renewal.club to avoid losing it.", 1),
            ("We are pleased to inform you that your loan application of $50,000 has been pre-approved. Send processing fee of $200.", 1),
            ("Your Google Drive storage is 98% full. Upgrade now for free at http://gdrive-upgrade.ml/free-storage", 1),
            ("ALERT: Someone tried to access your bank account. Verify your identity: http://secure-banking.ga/verify", 1),
            ("Exclusive business proposal: Invest $1,000 and earn guaranteed returns of 500% within 30 days. Risk-free!", 1),

            # Legitimate emails
            ("Hi team, please find the Q3 report attached. Let me know if you have any questions about the projections.", 0),
            ("Your Amazon order #112-3456789 has shipped! Track your delivery at amazon.com/orders", 0),
            ("Meeting reminder: Product review tomorrow at 2 PM in Conference Room B. Please prepare your updates.", 0),
            ("Thanks for your purchase! Your receipt from Starbucks is attached. Have a great day!", 0),
            ("Hi Sarah, I've reviewed the contract changes. Everything looks good. Let's proceed with the signing.", 0),
            ("Your monthly bank statement for April 2024 is now available in your online banking portal.", 0),
            ("Welcome to our newsletter! Here are this week's top stories and industry insights.", 0),
            ("Reminder: Your dentist appointment is scheduled for May 15 at 10:00 AM with Dr. Smith.", 0),
            ("Hi, I wanted to follow up on our conversation from last week. Are you available for a call Thursday?", 0),
            ("Your flight itinerary for trip to New York on June 1st. Confirmation number: ABC123.", 0),
            ("Team lunch is on Friday at the Italian place. Please RSVP by Wednesday so I can make reservations.", 0),
            ("Here is the updated project timeline. We are on track for the June 30 deadline.", 0),
            ("Congratulations on completing the training course! Your certificate is attached.", 0),
            ("Please review the attached proposal before our client meeting on Monday.", 0),
            ("Your subscription renewal was successful. Next billing date: July 1, 2024.", 0),
            ("Hi everyone, here are the action items from today's standup meeting.", 0),
            ("Your return has been processed. Refund of $45.99 will appear in 3-5 business days.", 0),
            ("The office will be closed on Monday for the holiday. Enjoy the long weekend!", 0),
            ("Your Spotify Wrapped 2024 is here! Check out your top songs and artists.", 0),
            ("Job application received: Software Engineer position at TechCorp. We'll review and respond within 2 weeks.", 0),
        ]

        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]

        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words="english",
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )
        X_tfidf = self.vectorizer.fit_transform(
            [self._preprocess_email(t) for t in texts]
        )

        self.lr_model = LogisticRegression(
            C=1.0, max_iter=1000, class_weight="balanced", random_state=42
        )
        self.lr_model.fit(X_tfidf, labels)

        self.rf_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, class_weight="balanced", random_state=42
        )
        self.rf_model.fit(X_tfidf.toarray(), labels)

        self.is_trained = True
        logger.info("Email fraud detection models trained successfully")

    def predict(self, text: str) -> Dict[str, Any]:
        """Analyze email content for fraud indicators.

        Returns comprehensive fraud analysis including probability,
        risk category, explanation, and feature importance.
        """
        start = time.time()

        processed = self._preprocess_email(text)
        features = self._extract_features(text)
        rule_score, indicators = self._calculate_rule_score(text)

        # ML prediction
        ml_probability = 0.0
        if self.is_trained and self.vectorizer:
            X = self.vectorizer.transform([processed])
            lr_prob = self.lr_model.predict_proba(X)[0][1] * 100
            rf_prob = self.rf_model.predict_proba(X)[0][1] * 100
            ml_probability = (lr_prob * 0.4) + (rf_prob * 0.3) + (rule_score * 0.3)
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

        # Feature importance
        feature_importance = {
            "phishing_language": min(features["phishing_pattern_count"] * 12, 30),
            "urgency_tactics": min(features["urgency_phrase_count"] * 10, 25),
            "social_engineering": min(features["social_engineering_count"] * 15, 25),
            "suspicious_links": min(features["url_count"] * 8 + features["suspicious_tld_count"] * 12, 20),
            "personal_data_request": features["personal_data_request"] * 20,
            "money_references": min(features["money_reference_count"] * 8, 15),
        }

        total_imp = sum(feature_importance.values())
        if total_imp > 0:
            feature_importance = {
                k: round(v / total_imp * 100, 2) for k, v in feature_importance.items()
            }

        explanation = self._generate_explanation(
            fraud_probability, risk_category, features, indicators
        )

        processing_time = int((time.time() - start) * 1000)

        return {
            "is_fraud": is_fraud,
            "fraud_probability": fraud_probability,
            "risk_category": risk_category,
            "risk_score": fraud_probability,
            "explanation": explanation,
            "suspicious_keywords": [ind.split(": ")[-1][:50] for ind in indicators[:15]],
            "feature_importance": feature_importance,
            "model_used": "TF-IDF + LR + RF Ensemble (Email)",
            "processing_time_ms": processing_time,
        }

    def _generate_explanation(
        self, probability: float, risk_category: str,
        features: Dict, indicators: List[str]
    ) -> str:
        """Generate human-readable explanation for email fraud assessment."""
        parts = []

        if risk_category == "critical":
            parts.append(f"⚠️ CRITICAL: This email has a {probability:.1f}% probability of being a phishing/fraud attempt.")
        elif risk_category == "high":
            parts.append(f"🔴 HIGH RISK: This email shows strong phishing indicators ({probability:.1f}%).")
        elif risk_category == "medium":
            parts.append(f"🟡 MEDIUM RISK: This email contains some suspicious elements ({probability:.1f}%).")
        else:
            parts.append(f"🟢 LOW RISK: This email appears legitimate ({probability:.1f}% fraud probability).")

        if features["phishing_pattern_count"] > 0:
            parts.append(f"• Detected {features['phishing_pattern_count']} phishing language pattern(s).")

        if features["urgency_phrase_count"] > 0:
            parts.append(f"• Found {features['urgency_phrase_count']} urgency/pressure tactic(s).")

        if features["social_engineering_count"] > 0:
            parts.append(f"• Identified {features['social_engineering_count']} social engineering indicator(s).")

        if features["url_count"] > 0:
            parts.append(f"• Contains {features['url_count']} link(s) that may lead to phishing sites.")

        if features["suspicious_tld_count"] > 0:
            parts.append(f"• {features['suspicious_tld_count']} link(s) use suspicious top-level domains.")

        if features["personal_data_request"]:
            parts.append("• ⚠️ Requests personal/financial information (passwords, SSN, credit card, etc.).")

        if features["money_reference_count"] > 0:
            parts.append(f"• Contains {features['money_reference_count']} monetary reference(s).")

        if features["has_shortened_url"]:
            parts.append("• Contains shortened URL(s) which may hide malicious destinations.")

        return "\n".join(parts)

    def save_model(self, path: str):
        """Save trained models to disk."""
        model_data = {
            "vectorizer": self.vectorizer,
            "lr_model": self.lr_model,
            "rf_model": self.rf_model,
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(model_data, f)

    def _load_model(self, path: str):
        """Load pre-trained models from disk."""
        with open(path, "rb") as f:
            model_data = pickle.load(f)
        self.vectorizer = model_data["vectorizer"]
        self.lr_model = model_data["lr_model"]
        self.rf_model = model_data["rf_model"]
        self.is_trained = True
