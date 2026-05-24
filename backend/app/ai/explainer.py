"""Explainable AI module for fraud detection explanations.

Provides human-readable explanations of why content was flagged,
highlights suspicious words, and shows feature importance breakdowns.
"""

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger("veridian.ai.explainer")


class FraudExplainer:
    """Generates detailed, human-readable explanations for fraud detection results."""

    # Risk factor categories with descriptions
    RISK_FACTOR_DESCRIPTIONS = {
        "spam_keywords": {
            "name": "Spam Keywords",
            "description": "Common words and phrases associated with spam messages",
            "icon": "🔤",
        },
        "scam_patterns": {
            "name": "Scam Patterns",
            "description": "Known patterns used in scam communications",
            "icon": "🎭",
        },
        "urgency_indicators": {
            "name": "Urgency Tactics",
            "description": "Language designed to create pressure and urgency",
            "icon": "⏰",
        },
        "financial_references": {
            "name": "Financial References",
            "description": "Mentions of money, accounts, or financial transactions",
            "icon": "💰",
        },
        "url_presence": {
            "name": "Suspicious Links",
            "description": "Presence of URLs that may lead to phishing sites",
            "icon": "🔗",
        },
        "uppercase_ratio": {
            "name": "Excessive Capitals",
            "description": "Heavy use of uppercase letters (shouting), common in spam",
            "icon": "🔠",
        },
        "text_entropy": {
            "name": "Text Randomness",
            "description": "Unusual text patterns suggesting automated or obfuscated content",
            "icon": "🎲",
        },
        "phishing_language": {
            "name": "Phishing Language",
            "description": "Words and phrases commonly used in phishing attempts",
            "icon": "🎣",
        },
        "urgency_tactics": {
            "name": "Urgency Tactics",
            "description": "Pressure tactics to force immediate action",
            "icon": "⚡",
        },
        "social_engineering": {
            "name": "Social Engineering",
            "description": "Psychological manipulation techniques",
            "icon": "🧠",
        },
        "suspicious_links": {
            "name": "Suspicious Links",
            "description": "Links that may lead to malicious websites",
            "icon": "🔗",
        },
        "personal_data_request": {
            "name": "Data Harvesting",
            "description": "Requests for personal or financial information",
            "icon": "📋",
        },
        "money_references": {
            "name": "Money References",
            "description": "References to monetary amounts or financial transactions",
            "icon": "💵",
        },
        "url_structure": {
            "name": "URL Structure",
            "description": "Suspicious URL length, characters, or formatting",
            "icon": "🏗️",
        },
        "domain_reputation": {
            "name": "Domain Reputation",
            "description": "Analysis of the domain's trustworthiness",
            "icon": "🌐",
        },
        "security_protocol": {
            "name": "Security Protocol",
            "description": "HTTPS usage and connection security",
            "icon": "🔒",
        },
        "phishing_indicators": {
            "name": "Phishing Indicators",
            "description": "Keywords and patterns common in phishing URLs",
            "icon": "🚩",
        },
        "obfuscation": {
            "name": "URL Obfuscation",
            "description": "Techniques used to hide the real destination",
            "icon": "🔍",
        },
    }

    # Safety recommendations by risk level
    RECOMMENDATIONS = {
        "critical": [
            "🚫 Do NOT click any links in this content.",
            "🚫 Do NOT share any personal information.",
            "🚫 Do NOT respond to this message.",
            "📱 Report this to the relevant platform immediately.",
            "🛡️ If you've already interacted, change your passwords and monitor your accounts.",
            "📞 Contact your bank if financial information was shared.",
        ],
        "high": [
            "⚠️ Exercise extreme caution with this content.",
            "🔍 Verify the sender through official channels.",
            "🚫 Do not click links — type official URLs manually.",
            "📱 Consider reporting this as suspicious.",
            "🛡️ Enable two-factor authentication on your accounts.",
        ],
        "medium": [
            "🔍 Verify the source before taking action.",
            "❓ Be cautious about sharing personal information.",
            "🌐 If visiting links, check the URL carefully first.",
            "📧 Contact the supposed sender through known channels.",
        ],
        "low": [
            "✅ This content appears to be safe.",
            "🔍 Always stay vigilant for unexpected requests.",
            "🛡️ Keep your security software up to date.",
        ],
    }

    def generate_full_explanation(
        self,
        scan_type: str,
        input_content: str,
        prediction_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a comprehensive explanation for a fraud detection result.

        Args:
            scan_type: Type of scan ('sms', 'email', 'url')
            input_content: The original content that was scanned
            prediction_result: The prediction output from the detector

        Returns:
            Dictionary containing detailed explanation components
        """
        risk_category = prediction_result.get("risk_category", "low")
        fraud_probability = prediction_result.get("fraud_probability", 0.0)
        feature_importance = prediction_result.get("feature_importance", {})
        suspicious_keywords = prediction_result.get("suspicious_keywords", [])

        # Build explanation components
        summary = self._generate_summary(scan_type, risk_category, fraud_probability)
        risk_factors = self._analyze_risk_factors(feature_importance)
        highlighted_content = self._highlight_suspicious_content(
            input_content, suspicious_keywords
        )
        recommendations = self.RECOMMENDATIONS.get(risk_category, self.RECOMMENDATIONS["low"])
        education = self._generate_educational_content(scan_type, risk_category)

        return {
            "summary": summary,
            "risk_category": risk_category,
            "fraud_probability": fraud_probability,
            "risk_factors": risk_factors,
            "highlighted_content": highlighted_content,
            "suspicious_keywords": suspicious_keywords,
            "recommendations": recommendations,
            "educational_tips": education,
            "scan_type": scan_type,
        }

    def _generate_summary(
        self, scan_type: str, risk_category: str, probability: float
    ) -> str:
        """Generate a concise summary of the analysis."""
        type_labels = {"sms": "SMS message", "email": "email", "url": "URL"}
        content_type = type_labels.get(scan_type, "content")

        if risk_category == "critical":
            return (
                f"This {content_type} has been identified as HIGHLY DANGEROUS with a "
                f"{probability:.1f}% fraud probability. Multiple critical fraud indicators "
                f"were detected. Do not interact with this content."
            )
        elif risk_category == "high":
            return (
                f"This {content_type} shows HIGH RISK characteristics with a "
                f"{probability:.1f}% fraud probability. Several fraud indicators were found. "
                f"Exercise extreme caution."
            )
        elif risk_category == "medium":
            return (
                f"This {content_type} has MODERATE RISK with a {probability:.1f}% fraud "
                f"probability. Some suspicious elements were detected. Verify the source "
                f"before taking action."
            )
        else:
            return (
                f"This {content_type} appears to be SAFE with only a {probability:.1f}% "
                f"fraud probability. No significant fraud indicators were found."
            )

    def _analyze_risk_factors(
        self, feature_importance: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Analyze and rank risk factors by importance."""
        factors = []
        for feature_name, importance in sorted(
            feature_importance.items(), key=lambda x: x[1], reverse=True
        ):
            factor_info = self.RISK_FACTOR_DESCRIPTIONS.get(feature_name, {
                "name": feature_name.replace("_", " ").title(),
                "description": f"Analysis of {feature_name.replace('_', ' ')}",
                "icon": "📊",
            })

            if importance > 0:
                if importance >= 30:
                    severity = "critical"
                elif importance >= 20:
                    severity = "high"
                elif importance >= 10:
                    severity = "medium"
                else:
                    severity = "low"

                factors.append({
                    "name": factor_info["name"],
                    "description": factor_info["description"],
                    "icon": factor_info["icon"],
                    "importance": importance,
                    "severity": severity,
                })

        return factors

    def _highlight_suspicious_content(
        self, content: str, suspicious_keywords: List[str]
    ) -> str:
        """Mark suspicious words in the content with highlighting markers."""
        highlighted = content
        for keyword in suspicious_keywords:
            # Clean keyword for regex
            clean_kw = re.escape(keyword.split(": ")[-1] if ": " in keyword else keyword)
            if clean_kw and len(clean_kw) > 1:
                try:
                    highlighted = re.sub(
                        rf"(?i)({clean_kw})",
                        r"⟦\1⟧",
                        highlighted,
                        count=3,  # Limit replacements
                    )
                except re.error:
                    pass
        return highlighted

    def _generate_educational_content(
        self, scan_type: str, risk_category: str
    ) -> List[str]:
        """Generate educational tips based on the scan type."""
        tips = {
            "sms": [
                "💡 Legitimate companies rarely ask for personal info via SMS.",
                "💡 Be wary of messages claiming you've won something you didn't enter.",
                "💡 Official banks will never ask for your PIN or OTP via text.",
                "💡 Don't click links in unexpected text messages — go to the official website directly.",
                "💡 Scammers create urgency to bypass your critical thinking.",
            ],
            "email": [
                "💡 Check the sender's actual email address, not just the display name.",
                "💡 Hover over links before clicking to see the real destination.",
                "💡 Legitimate organizations won't threaten immediate account closure.",
                "💡 Look for generic greetings like 'Dear Customer' instead of your actual name.",
                "💡 Check for spelling and grammar errors — they're common in phishing emails.",
                "💡 When in doubt, contact the organization directly through their official website.",
            ],
            "url": [
                "💡 Always check for HTTPS and a valid certificate before entering data.",
                "💡 Look carefully at the domain — 'paypa1.com' is not 'paypal.com'.",
                "💡 Be cautious with shortened URLs — they hide the true destination.",
                "💡 Legitimate sites rarely use IP addresses instead of domain names.",
                "💡 Check for excessive subdomains like 'login.paypal.com.malicious.tk'.",
                "💡 Type website URLs directly into your browser rather than clicking links.",
            ],
        }
        return tips.get(scan_type, tips["sms"])[:4]
