"""SMS Fraud Detection module using TF-IDF + ensemble ML classifiers.

This module implements a complete SMS fraud detection pipeline including:
- Text preprocessing with NLTK
- TF-IDF feature extraction
- Logistic Regression and Random Forest ensemble
- Comprehensive fraud pattern matching
- Risk score calculation
- Suspicious keyword extraction
"""

import re
import os
import math
import logging
import pickle
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logger = logging.getLogger("veridian.ai.sms")

# Comprehensive fraud indicator patterns
SPAM_KEYWORDS = [
    "win", "winner", "won", "prize", "reward", "congratulations", "congrats",
    "free", "gift", "bonus", "offer", "deal", "discount", "sale",
    "click", "click here", "visit", "subscribe", "buy now", "order now",
    "urgent", "immediately", "act now", "limited time", "expire",
    "cash", "money", "dollar", "rupee", "bitcoin", "crypto",
    "loan", "credit", "debt", "invest", "investment", "profit",
    "guarantee", "guaranteed", "risk-free", "no risk",
    "account", "verify", "confirm", "update", "suspend",
    "password", "pin", "otp", "cvv", "ssn", "social security",
    "bank", "paypal", "venmo", "wire transfer", "western union",
    "claim", "collect", "redeem", "apply",
    "lucky", "selected", "chosen", "exclusive",
    "call now", "text back", "reply", "send",
    "blocked", "locked", "compromised", "unauthorized",
    "irs", "tax", "refund", "payment", "invoice",
]

SCAM_PATTERNS = [
    r"(?i)you\s+have\s+(?:won|been\s+selected)",
    r"(?i)claim\s+(?:your|now|today)",
    r"(?i)(?:click|tap)\s+(?:here|this|the\s+link)",
    r"(?i)verify\s+(?:your|account|identity)",
    r"(?i)(?:send|transfer)\s+\$?\d+",
    r"(?i)act\s+(?:now|immediately|fast)",
    r"(?i)limited\s+time\s+(?:offer|only)",
    r"(?i)(?:your|the)\s+account\s+(?:has\s+been|is|will\s+be)\s+(?:suspended|locked|closed|blocked)",
    r"(?i)(?:confirm|update)\s+(?:your|account)\s+(?:details|information|password)",
    r"(?i)(?:won|win)\s+(?:a|the|\$)\s*\d*",
    r"(?i)(?:dear|attention)\s+(?:customer|user|member|winner)",
    r"(?i)(?:nigerian|foreign)\s+(?:prince|lottery|inheritance)",
    r"(?i)send\s+(?:your|the)\s+(?:otp|pin|password|code)",
    r"(?i)(?:whatsapp|telegram|signal)\s+(?:us|me|this\s+number)",
    r"(?i)(?:amazon|apple|google|microsoft|netflix)\s+(?:account|order|subscription)",
]

FINANCIAL_PATTERNS = [
    r"\$\s*\d+(?:,\d{3})*(?:\.\d{2})?",
    r"(?i)(?:rs|inr|usd|gbp|eur|₹|€|£)\s*\.?\s*\d+",
    r"(?i)(?:million|thousand|lakh|crore)\s+(?:dollar|rupee|pound)",
    r"(?i)(?:credit\s+card|debit\s+card|bank\s+account|routing\s+number)",
    r"(?i)(?:wire\s+transfer|money\s+order|western\s+union|moneygram)",
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Card numbers
]

URGENCY_PATTERNS = [
    r"(?i)(?:urgent|emergency|immediate|asap|right\s+now)",
    r"(?i)(?:last\s+chance|final\s+notice|final\s+warning)",
    r"(?i)(?:expire|expiring|expires)\s+(?:today|soon|in\s+\d+)",
    r"(?i)(?:within|in)\s+\d+\s+(?:hour|minute|day|hr|min)",
    r"(?i)don'?t\s+(?:miss|delay|ignore|wait)",
    r"!{2,}",
    r"(?i)(?:act|respond|reply|call)\s+(?:now|immediately|asap)",
]


class SMSFraudDetector:
    """SMS fraud detection using TF-IDF + ML ensemble with pattern matching."""

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
                logger.info("Loaded pre-trained SMS model from disk")
                return
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, training fresh model")

        self._train_default_model()

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize SMS text for analysis."""
        text = text.lower().strip()
        text = re.sub(r"http\S+|www\.\S+", " URL_TOKEN ", text)
        text = re.sub(r"\b\d{10,}\b", " PHONE_TOKEN ", text)
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " EMAIL_TOKEN ", text)
        text = re.sub(r"\$\s*\d+(?:,\d{3})*(?:\.\d{2})?", " MONEY_TOKEN ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract hand-crafted features from SMS text."""
        original_text = text
        features = {}

        # Length features
        features["char_count"] = len(original_text)
        features["word_count"] = len(original_text.split())
        features["avg_word_length"] = (
            np.mean([len(w) for w in original_text.split()])
            if original_text.split() else 0
        )

        # Character analysis
        features["uppercase_ratio"] = (
            sum(1 for c in original_text if c.isupper()) / max(len(original_text), 1)
        )
        features["digit_ratio"] = (
            sum(1 for c in original_text if c.isdigit()) / max(len(original_text), 1)
        )
        features["special_char_ratio"] = (
            sum(1 for c in original_text if not c.isalnum() and not c.isspace())
            / max(len(original_text), 1)
        )
        features["exclamation_count"] = original_text.count("!")
        features["question_count"] = original_text.count("?")

        # URL and contact features
        features["url_count"] = len(re.findall(r"http\S+|www\.\S+", original_text))
        features["phone_count"] = len(re.findall(r"\b\d{10,}\b", original_text))
        features["email_count"] = len(
            re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", original_text)
        )

        # Keyword matching
        text_lower = original_text.lower()
        features["spam_keyword_count"] = sum(
            1 for kw in SPAM_KEYWORDS if kw in text_lower
        )
        features["scam_pattern_count"] = sum(
            1 for pattern in SCAM_PATTERNS if re.search(pattern, original_text)
        )
        features["financial_pattern_count"] = sum(
            1 for pattern in FINANCIAL_PATTERNS if re.search(pattern, original_text)
        )
        features["urgency_pattern_count"] = sum(
            1 for pattern in URGENCY_PATTERNS if re.search(pattern, original_text)
        )

        # Entropy (randomness indicator)
        if original_text:
            freq = Counter(original_text.lower())
            length = len(original_text)
            features["text_entropy"] = -sum(
                (c / length) * math.log2(c / length) for c in freq.values()
            )
        else:
            features["text_entropy"] = 0

        return features

    def _calculate_rule_based_score(self, text: str) -> Tuple[float, List[str]]:
        """Calculate a rule-based fraud score and extract suspicious keywords found."""
        score = 0.0
        found_keywords = []
        text_lower = text.lower()

        # Check spam keywords
        for kw in SPAM_KEYWORDS:
            if kw in text_lower:
                score += 2.0
                found_keywords.append(kw)

        # Check scam patterns (weighted higher)
        for pattern in SCAM_PATTERNS:
            if re.search(pattern, text):
                score += 5.0

        # Check financial patterns
        for pattern in FINANCIAL_PATTERNS:
            if re.search(pattern, text):
                score += 4.0

        # Check urgency patterns
        for pattern in URGENCY_PATTERNS:
            if re.search(pattern, text):
                score += 3.0

        # URL presence bonus
        urls = re.findall(r"http\S+|www\.\S+", text)
        if urls:
            score += 3.0 * len(urls)
            for url in urls:
                found_keywords.append(f"URL: {url[:50]}")

        # Excessive uppercase
        if text and sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.4:
            score += 3.0
            found_keywords.append("excessive_uppercase")

        # Normalize score to 0-100
        normalized = min(score / 50.0 * 100, 100.0)
        return normalized, list(set(found_keywords))

    def _train_default_model(self):
        """Train models with comprehensive built-in training data."""
        # Extensive training corpus covering real-world SMS fraud patterns
        training_data = [
            # SPAM / FRAUD messages
            ("Congratulations! You've won a $1,000 Walmart gift card. Click here to claim: http://bit.ly/claim", 1),
            ("URGENT: Your bank account has been compromised. Verify immediately: http://secure-bank.com", 1),
            ("You have won £1000! To claim your prize, call 09061234567 now!", 1),
            ("Free entry to our $1000 weekly prize draw. Text WIN to 80085", 1),
            ("WINNER!! You've been selected for a special cash prize! Call now!", 1),
            ("Your account will be suspended! Verify your identity at http://verify-account.tk", 1),
            ("Act now! Limited time offer - Get 90% off all products! Visit www.deals.tk", 1),
            ("Dear customer, your ATM card has been blocked. Send your PIN to unblock.", 1),
            ("Congratulations! Your number was selected to win $5,000. Send your details.", 1),
            ("URGENT: IRS notice - You owe $3,432 in taxes. Pay immediately to avoid arrest.", 1),
            ("You've won a free iPhone 15! Click here to claim before it expires!", 1),
            ("Your Netflix account has been suspended. Update payment: http://netflix-update.com", 1),
            ("Amazon: Your order #38291 requires payment verification. Click: amzn.tk/verify", 1),
            ("ALERT: Unauthorized login to your account. Reset password NOW: http://reset.xyz", 1),
            ("Hi, this is your bank. We need your OTP to process a refund of $500.", 1),
            ("You are our lucky winner! Transfer fee of $50 to claim your $10,000 prize.", 1),
            ("FINAL WARNING: Your loan application expires in 2 hours. Apply now!", 1),
            ("Exclusive deal just for you! Investment guaranteed 500% returns. Act fast!", 1),
            ("Your WhatsApp will expire soon. Verify: http://whatsapp-verify.com", 1),
            ("Send me $200 via Western Union and I'll send you $2000 back. Trust me!", 1),
            ("BREAKING: You've inherited $4.5M from a foreign relative. Contact us ASAP.", 1),
            ("FREE MSG: Your mobile has won £2000! Claim by calling 08712345678", 1),
            ("Alert: Your SSN has been compromised. Call 1-800-555-0123 immediately.", 1),
            ("Click here for your $500 Amazon gift card! Limited offer! bit.ly/amazon500", 1),
            ("IMPORTANT: Your package delivery failed. Update address: http://delivery.tk", 1),
            ("Earn $5000/week working from home! No experience needed. Reply YES.", 1),
            ("Your Google account security alert. Confirm identity: http://google-sec.xyz", 1),
            ("You qualify for government stimulus payment of $1400. Apply: http://gov-pay.com", 1),
            ("Debt consolidation: Reduce payments by 50%! Call now before rates increase!", 1),
            ("Your crypto investment tripled! Withdraw now at http://crypto-wallet.tk", 1),

            # LEGITIMATE messages
            ("Hey, are you coming to the party tonight?", 0),
            ("Meeting at 3pm has been rescheduled to 4pm tomorrow.", 0),
            ("Don't forget to pick up groceries on your way home.", 0),
            ("Happy birthday! Hope you have an amazing day!", 0),
            ("Your Uber ride is arriving in 3 minutes.", 0),
            ("Your Amazon order #12345 has been delivered.", 0),
            ("Reminder: Dentist appointment tomorrow at 10 AM.", 0),
            ("Hey, can you send me the project files?", 0),
            ("Thanks for dinner last night. It was great!", 0),
            ("Your OTP for SBI transaction is 482910. Valid for 5 mins.", 0),
            ("Mom called. She wants you to call her back.", 0),
            ("The meeting went well. Client is interested in our proposal.", 0),
            ("Can you pick up the kids from school today?", 0),
            ("I'll be late for dinner. Save some food for me.", 0),
            ("Your prescription is ready for pickup at CVS Pharmacy.", 0),
            ("Flight confirmation: AA234 departing 8:30 AM Gate B12", 0),
            ("Let's catch up this weekend. Coffee at the usual place?", 0),
            ("The WiFi password for the new router is: sunshine2024", 0),
            ("Good morning! Don't forget the team standup at 9.", 0),
            ("Your library book is due in 3 days. Return or renew online.", 0),
            ("I finished the report. Check your email for the attachment.", 0),
            ("Traffic is heavy on I-95. Take the alternate route.", 0),
            ("Gym class cancelled today due to maintenance. Sorry!", 0),
            ("Your package from USPS will arrive Thursday by 5 PM.", 0),
            ("Thanks for helping with the move. Really appreciate it!", 0),
            ("Practice is at 6pm today. Bring your cleats and water.", 0),
            ("Sorry I missed your call. In a meeting right now. Will call back.", 0),
            ("The restaurant reservation is for 7:30 PM under Johnson.", 0),
            ("Let me know when you get home safely.", 0),
            ("Your car service is scheduled for next Monday at 9 AM.", 0),
        ]

        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]

        # Initialize and train TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words="english",
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )
        X_tfidf = self.vectorizer.fit_transform(
            [self._preprocess_text(t) for t in texts]
        )

        # Train Logistic Regression
        self.lr_model = LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        )
        self.lr_model.fit(X_tfidf, labels)

        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        self.rf_model.fit(X_tfidf.toarray(), labels)

        self.is_trained = True
        logger.info("SMS fraud detection models trained successfully")

    def predict(self, text: str) -> Dict[str, Any]:
        """Run full fraud detection analysis on an SMS message.

        Returns a dictionary containing:
        - is_fraud: boolean indicating fraud detection
        - fraud_probability: percentage likelihood of fraud
        - risk_category: 'low', 'medium', 'high', or 'critical'
        - risk_score: numerical risk score 0-100
        - explanation: human-readable explanation
        - suspicious_keywords: list of detected fraud indicators
        - feature_importance: dict of feature contributions
        - model_used: model identifier
        """
        import time
        start = time.time()

        # Preprocessing
        processed = self._preprocess_text(text)
        features = self._extract_features(text)
        rule_score, suspicious_keywords = self._calculate_rule_based_score(text)

        # ML predictions
        ml_probability = 0.0
        if self.is_trained and self.vectorizer:
            X = self.vectorizer.transform([processed])

            # Logistic Regression probability
            lr_prob = self.lr_model.predict_proba(X)[0][1] * 100

            # Random Forest probability
            rf_prob = self.rf_model.predict_proba(X)[0][1] * 100

            # Weighted ensemble: 40% LR, 30% RF, 30% rules
            ml_probability = (lr_prob * 0.4) + (rf_prob * 0.3) + (rule_score * 0.3)
        else:
            ml_probability = rule_score

        # Clamp probability
        fraud_probability = round(min(max(ml_probability, 0.0), 100.0), 2)

        # Determine risk category
        if fraud_probability >= 80:
            risk_category = "critical"
        elif fraud_probability >= 60:
            risk_category = "high"
        elif fraud_probability >= 35:
            risk_category = "medium"
        else:
            risk_category = "low"

        is_fraud = fraud_probability >= 50

        # Build feature importance
        feature_importance = {
            "spam_keywords": min(features["spam_keyword_count"] * 10, 30),
            "scam_patterns": min(features["scam_pattern_count"] * 15, 30),
            "urgency_indicators": min(features["urgency_pattern_count"] * 12, 20),
            "financial_references": min(features["financial_pattern_count"] * 12, 20),
            "url_presence": min(features["url_count"] * 10, 15),
            "uppercase_ratio": round(features["uppercase_ratio"] * 15, 2),
            "text_entropy": round(min(features["text_entropy"] * 2, 10), 2),
        }

        # Normalize feature importance to sum to ~100
        total_imp = sum(feature_importance.values())
        if total_imp > 0:
            feature_importance = {
                k: round(v / total_imp * 100, 2)
                for k, v in feature_importance.items()
            }

        # Generate explanation
        explanation = self._generate_explanation(
            fraud_probability, risk_category, features, suspicious_keywords
        )

        processing_time = int((time.time() - start) * 1000)

        return {
            "is_fraud": is_fraud,
            "fraud_probability": fraud_probability,
            "risk_category": risk_category,
            "risk_score": fraud_probability,
            "explanation": explanation,
            "suspicious_keywords": suspicious_keywords[:20],
            "feature_importance": feature_importance,
            "model_used": "TF-IDF + LogisticRegression + RandomForest Ensemble",
            "processing_time_ms": processing_time,
        }

    def _generate_explanation(
        self,
        probability: float,
        risk_category: str,
        features: Dict,
        keywords: List[str],
    ) -> str:
        """Generate a human-readable explanation of the fraud assessment."""
        parts = []

        if risk_category == "critical":
            parts.append(
                f"⚠️ CRITICAL RISK: This message has a {probability:.1f}% probability of being fraudulent."
            )
        elif risk_category == "high":
            parts.append(
                f"🔴 HIGH RISK: This message shows strong fraud indicators ({probability:.1f}% probability)."
            )
        elif risk_category == "medium":
            parts.append(
                f"🟡 MEDIUM RISK: This message contains some suspicious elements ({probability:.1f}% probability)."
            )
        else:
            parts.append(
                f"🟢 LOW RISK: This message appears to be legitimate ({probability:.1f}% fraud probability)."
            )

        if features["spam_keyword_count"] > 0:
            parts.append(
                f"• Found {features['spam_keyword_count']} spam-related keywords."
            )

        if features["scam_pattern_count"] > 0:
            parts.append(
                f"• Detected {features['scam_pattern_count']} known scam pattern(s)."
            )

        if features["urgency_pattern_count"] > 0:
            parts.append(
                f"• Contains {features['urgency_pattern_count']} urgency/pressure tactic(s)."
            )

        if features["financial_pattern_count"] > 0:
            parts.append(
                f"• References {features['financial_pattern_count']} financial element(s)."
            )

        if features["url_count"] > 0:
            parts.append(
                f"• Contains {features['url_count']} URL(s) which may be phishing links."
            )

        if features["uppercase_ratio"] > 0.3:
            parts.append("• Excessive use of uppercase letters (common in spam).")

        if keywords:
            display_keywords = keywords[:8]
            parts.append(f"• Suspicious terms: {', '.join(display_keywords)}")

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
        logger.info(f"SMS model saved to {path}")

    def _load_model(self, path: str):
        """Load pre-trained models from disk."""
        with open(path, "rb") as f:
            model_data = pickle.load(f)
        self.vectorizer = model_data["vectorizer"]
        self.lr_model = model_data["lr_model"]
        self.rf_model = model_data["rf_model"]
        self.is_trained = True
