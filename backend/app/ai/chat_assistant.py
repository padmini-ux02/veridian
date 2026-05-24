"""AI Chat Assistant for fraud detection guidance.

Provides natural language responses to user questions about:
- Why specific content is flagged
- How to identify scam messages
- General fraud prevention advice
- Understanding risk scores and categories
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("veridian.ai.chat")


class ChatAssistant:
    """Rule-based AI chat assistant specialized in fraud detection guidance."""

    # Intent patterns and their corresponding response generators
    INTENT_PATTERNS = {
        "why_dangerous": [
            r"(?i)why\s+(?:is|was)\s+(?:this|it|the)\s+(?:message|sms|email|url|link|content)\s+(?:dangerous|risky|flagged|suspicious|fraud|harmful|unsafe|bad)",
            r"(?i)what\s+(?:makes?|made)\s+(?:this|it)\s+(?:dangerous|risky|suspicious|fraud|harmful|unsafe)",
            r"(?i)why\s+(?:did|does)\s+(?:it|this)\s+(?:get|got)\s+flagged",
            r"(?i)explain\s+(?:the\s+)?(?:risk|danger|threat|flags?)",
        ],
        "identify_scam": [
            r"(?i)how\s+(?:can|do|to)\s+(?:i|we|you)\s+(?:identify|detect|spot|recognize|tell|know)\s+(?:a\s+)?(?:scam|fraud|phishing|spam|fake)",
            r"(?i)(?:signs?|indicators?|red\s+flags?)\s+of\s+(?:a\s+)?(?:scam|fraud|phishing|spam|fake)",
            r"(?i)(?:what|how)\s+(?:to\s+)?(?:look|watch)\s+(?:for|out)\s+(?:in\s+)?(?:scam|fraud|phishing)",
            r"(?i)tips?\s+(?:for|to|on)\s+(?:identifying|detecting|spotting|avoiding)\s+(?:scam|fraud|phishing)",
        ],
        "what_to_do": [
            r"(?i)what\s+(?:should|can|do)\s+(?:i|we)\s+do\s+(?:if|when|about)",
            r"(?i)(?:steps?|actions?)\s+(?:to\s+)?take\s+(?:if|when|after)",
            r"(?i)(?:i|we)\s+(?:clicked|opened|responded|replied|gave|shared|sent)",
            r"(?i)(?:how\s+to\s+)?(?:report|block|protect|secure|recover)",
        ],
        "explain_score": [
            r"(?i)(?:what|how)\s+(?:does|is)\s+(?:the\s+)?(?:risk\s+)?score\s+(?:mean|work|calculated|determined)",
            r"(?i)(?:explain|understand)\s+(?:the\s+)?(?:risk|fraud|probability)\s+(?:score|rating|level|percentage)",
            r"(?i)(?:what|how)\s+(?:are|do)\s+(?:the\s+)?(?:categories|levels|ratings)\s+(?:mean|work|determined)",
        ],
        "sms_safety": [
            r"(?i)(?:is|are)\s+(?:this|these)\s+(?:sms|text|message)\s+(?:safe|legit|legitimate|real|genuine)",
            r"(?i)(?:sms|text\s+message)\s+(?:safety|security|protection|tips)",
            r"(?i)(?:how|tips?)\s+(?:to\s+)?(?:stay\s+)?safe\s+(?:from|with|against)\s+(?:sms|text)",
        ],
        "email_safety": [
            r"(?i)(?:email|mail)\s+(?:safety|security|protection|phishing)\s+(?:tips?|advice|guide)",
            r"(?i)(?:how\s+to\s+)?(?:protect|secure|safe)\s+(?:my|your|email|from\s+phishing)",
            r"(?i)(?:identify|detect|spot)\s+(?:phishing|fake|fraudulent)\s+(?:email|mail)",
        ],
        "url_safety": [
            r"(?i)(?:how\s+to\s+)?(?:check|verify|validate|test)\s+(?:if\s+)?(?:a\s+)?(?:url|link|website)\s+(?:is\s+)?(?:safe|legit|legitimate|secure)",
            r"(?i)(?:url|link|website)\s+(?:safety|security|verification|checker)",
            r"(?i)(?:is|check)\s+(?:this\s+)?(?:url|link|website|site)\s+(?:safe|secure|legit)",
        ],
        "general_help": [
            r"(?i)(?:help|assist|support|guide|info|information)",
            r"(?i)(?:what\s+can\s+you\s+do|how\s+does\s+this\s+work|capabilities|features)",
            r"(?i)(?:hello|hi|hey|greetings|good\s+(?:morning|afternoon|evening))",
        ],
    }

    def chat(
        self,
        message: str,
        scan_context: Optional[Dict] = None,
    ) -> Dict:
        """Process a user chat message and generate an appropriate response.

        Args:
            message: User's question or message
            scan_context: Optional context from a recent scan result

        Returns:
            Dictionary with response text and metadata
        """
        intent = self._detect_intent(message)

        if intent == "why_dangerous" and scan_context:
            response = self._explain_danger(scan_context)
        elif intent == "why_dangerous" and not scan_context:
            response = self._explain_danger_general()
        elif intent == "identify_scam":
            response = self._identify_scam_guide(message)
        elif intent == "what_to_do":
            response = self._what_to_do_guide(message, scan_context)
        elif intent == "explain_score":
            response = self._explain_scoring()
        elif intent == "sms_safety":
            response = self._sms_safety_guide()
        elif intent == "email_safety":
            response = self._email_safety_guide()
        elif intent == "url_safety":
            response = self._url_safety_guide()
        elif intent == "general_help":
            response = self._general_help()
        else:
            response = self._fallback_response(message)

        return {
            "response": response,
            "intent": intent,
            "has_context": scan_context is not None,
        }

    def _detect_intent(self, message: str) -> str:
        """Detect the user's intent from their message."""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return intent
        return "unknown"

    def _explain_danger(self, context: Dict) -> str:
        """Explain why specific scanned content was flagged."""
        risk_category = context.get("risk_category", "unknown")
        fraud_probability = context.get("fraud_probability", 0)
        scan_type = context.get("scan_type", "content")
        suspicious_keywords = context.get("suspicious_keywords", [])
        feature_importance = context.get("feature_importance", {})

        parts = [
            f"## Analysis of Your {scan_type.upper()} Scan\n",
            f"**Risk Level:** {risk_category.upper()} ({fraud_probability:.1f}% fraud probability)\n",
        ]

        parts.append("### Why This Was Flagged:\n")

        if feature_importance:
            sorted_features = sorted(
                feature_importance.items(), key=lambda x: x[1], reverse=True
            )
            for feature, importance in sorted_features[:5]:
                if importance > 5:
                    name = feature.replace("_", " ").title()
                    parts.append(f"- **{name}** (Impact: {importance:.1f}%)")

        if suspicious_keywords:
            parts.append(f"\n### Suspicious Elements Found:")
            for kw in suspicious_keywords[:8]:
                parts.append(f"- `{kw}`")

        parts.append(f"\n### What This Means:")
        if risk_category in ("critical", "high"):
            parts.append(
                "This content contains multiple strong fraud indicators. "
                "It's very likely a scam or phishing attempt designed to steal "
                "your personal information or money. **Do not interact with it.**"
            )
        elif risk_category == "medium":
            parts.append(
                "This content has some characteristics commonly found in fraudulent "
                "messages. While it may be legitimate, proceed with caution and "
                "verify the source through official channels."
            )
        else:
            parts.append(
                "This content shows minimal fraud indicators and appears to be "
                "safe. However, always remain vigilant about unexpected requests "
                "for personal information."
            )

        return "\n".join(parts)

    def _explain_danger_general(self) -> str:
        """General explanation when no scan context is available."""
        return """## Understanding Fraud Indicators

Messages, emails, and URLs are flagged based on multiple factors:

### Common Red Flags:
1. **Urgency & Pressure** — "Act now!", "Your account will be closed!", "Last chance!"
2. **Too Good to Be True** — Free prizes, lottery wins, unexpected inheritances
3. **Requests for Personal Data** — Asking for passwords, PINs, SSN, credit card numbers
4. **Suspicious Links** — Shortened URLs, misspelled domains, non-HTTPS links
5. **Impersonation** — Pretending to be banks, tech companies, or government agencies
6. **Poor Grammar/Spelling** — Professional organizations rarely send error-filled messages
7. **Generic Greetings** — "Dear Customer" instead of your actual name

### How Our System Works:
We use machine learning models trained on thousands of known fraud patterns combined with:
- **TF-IDF text analysis** — Identifies fraud-related language patterns
- **Pattern matching** — Detects known scam templates
- **URL analysis** — Examines link structure, domain reputation, and security
- **Behavioral analysis** — Identifies urgency tactics and manipulation

To get a specific analysis, try scanning a message, email, or URL using our detection tools!"""

    def _identify_scam_guide(self, message: str) -> str:
        """Guide on how to identify scam messages."""
        return """## How to Identify Scam Messages 🔍

### 📱 SMS/Text Scams:
- **Prize notifications** you never entered to win
- **Urgent account alerts** with links to "verify"
- **Unknown senders** claiming to be your bank
- **Requests for OTP/PIN** — your bank will NEVER ask for these via text
- **Shortened links** (bit.ly, tinyurl) from unknown sources

### 📧 Email Phishing:
- **Check the sender's email** — hover to see the actual address
- **Generic greetings** — "Dear Customer" instead of your name
- **Urgency language** — "Your account will be suspended in 24 hours"
- **Mismatched URLs** — the text says "paypal.com" but links to "paypa1.xyz"
- **Attachments from strangers** — never open unexpected files
- **Spelling/grammar errors** — legitimate companies proofread

### 🔗 Phishing URLs:
- **No HTTPS** — legitimate sites use encryption
- **IP addresses** instead of domain names (e.g., http://192.168.1.1)
- **Misspelled brands** — "amaz0n.com", "g00gle.com", "paypa1.com"
- **Suspicious TLDs** — .tk, .ml, .xyz, .club instead of .com, .org
- **Excessive subdomains** — "login.paypal.com.malicious.tk"

### 🛡️ Golden Rules:
1. **When in doubt, don't click** — go directly to the official website
2. **Verify independently** — call the company using their official number
3. **Never share OTP/PIN** — no legitimate service asks for these
4. **Trust your instincts** — if something feels wrong, it probably is
5. **Report suspicious content** — help protect others too"""

    def _what_to_do_guide(self, message: str, context: Optional[Dict]) -> str:
        """Guide on what to do when encountering or falling victim to fraud."""
        response = """## What To Do About Fraud 🛡️\n"""

        if context and context.get("risk_category") in ("critical", "high"):
            response += """### ⚠️ Immediate Actions (High Risk Detected):
1. **Do NOT click** any links in the content
2. **Do NOT reply** to the message or email
3. **Do NOT share** any personal information
4. **Block the sender** on your device
5. **Report it** using our reporting tool\n"""

        response += """
### If You've Already Interacted:

**If you clicked a link:**
- Close the page immediately
- Clear your browser cache and cookies
- Run a virus scan on your device
- Change passwords for any accounts you may have exposed

**If you shared personal information:**
- Change all related passwords immediately
- Enable two-factor authentication everywhere
- Contact your bank if financial info was shared
- Monitor your accounts for suspicious activity
- Consider placing a fraud alert with credit bureaus

**If you sent money:**
- Contact your bank/payment provider immediately
- File a fraud report
- Document everything (screenshots, messages, dates)
- Report to local law enforcement

### Reporting Channels:
- 📱 Forward suspicious SMS to 7726 (SPAM)
- 📧 Report phishing emails to reportphishing@apwg.org
- 🌐 Report phishing sites to Google Safe Browsing
- 🏛️ File a complaint at ic3.gov (FBI) or ftc.gov (FTC)
- 🔒 Use our built-in reporting tool to help protect others"""

        return response

    def _explain_scoring(self) -> str:
        """Explain how risk scores and categories work."""
        return """## Understanding Risk Scores 📊

### How We Calculate Risk:

Our fraud detection uses a **multi-layer approach**:

1. **ML Model Score (40%)** — Logistic Regression trained on fraud patterns
2. **Ensemble Score (30%)** — Random Forest for pattern diversity
3. **Rule-Based Score (30%)** — Expert-crafted pattern matching

### Risk Categories:

| Category | Score Range | Meaning |
|----------|-----------|---------|
| 🟢 **Low** | 0-34% | Content appears safe |
| 🟡 **Medium** | 35-59% | Some suspicious elements found |
| 🔴 **High** | 60-79% | Strong fraud indicators detected |
| ⚠️ **Critical** | 80-100% | Very likely fraudulent |

### Feature Importance:
Each scan analyzes multiple features and shows their contribution:
- **Spam Keywords** — Known fraud-related words
- **Scam Patterns** — Known scam message templates
- **Urgency Tactics** — Pressure language
- **Financial References** — Money/account mentions
- **Link Analysis** — URL safety assessment
- **Text Analysis** — Statistical text properties

### Important Notes:
- Scores are **probabilistic** — a low score doesn't guarantee safety
- **Context matters** — always use your own judgment alongside our analysis
- Models are **continuously improving** as we process more data
- **False positives** can occur — legitimate content may sometimes be flagged"""

    def _sms_safety_guide(self) -> str:
        """SMS-specific safety guidance."""
        return """## SMS Safety Guide 📱

### Protecting Yourself from SMS Fraud:

**1. Verify the Sender**
- Banks and companies have official short codes
- Be suspicious of messages from regular phone numbers claiming to be companies

**2. Never Share Sensitive Info via SMS**
- OTPs should only be entered on official apps/websites
- No legitimate service asks for your full PIN or password via text

**3. Handle Links Carefully**
- Don't click links from unknown numbers
- If a message claims to be from your bank, open the banking app directly instead

**4. Watch for These Red Flags:**
- "You've won!" when you didn't enter anything
- "Your account is blocked" with a link to "fix" it
- Requests to transfer money urgently
- Messages with strange formatting or many spelling errors

**5. Enable Safety Features:**
- Turn on SMS filtering on your phone
- Block and report spam numbers
- Use our Veridian scanner for suspicious messages

**6. If You Receive a Suspicious SMS:**
- Don't respond
- Don't click any links
- Block the number
- Report it (forward to 7726/SPAM)
- Scan it with Veridian for analysis"""

    def _email_safety_guide(self) -> str:
        """Email-specific safety guidance."""
        return """## Email Safety Guide 📧

### Protecting Against Email Phishing:

**1. Check the Sender Carefully**
- Hover over the sender name to see the actual email address
- `support@paypal.com` ≠ `support@paypa1-secure.tk`
- Be wary of slight misspellings in domain names

**2. Inspect Links Before Clicking**
- Hover over any link to preview the actual URL
- Look for HTTPS and correct domain spelling
- When in doubt, type the URL directly into your browser

**3. Red Flags in Emails:**
- Generic greetings ("Dear Customer", "Dear User")
- Threats of account suspension or legal action
- Requests to verify personal information
- Unexpected attachments (especially .exe, .zip, .js files)
- Poor grammar and spelling

**4. Email Security Best Practices:**
- Use strong, unique passwords for email accounts
- Enable two-factor authentication
- Don't open attachments from unknown senders
- Keep your email client and antivirus updated
- Use email filtering and spam protection

**5. Handling Suspicious Emails:**
- Don't click any links or download attachments
- Don't reply to the sender
- Report as phishing in your email client
- Forward to the organization being impersonated
- Scan the content with Veridian"""

    def _url_safety_guide(self) -> str:
        """URL-specific safety guidance."""
        return """## URL Safety Guide 🔗

### How to Verify URL Safety:

**1. Check the Protocol**
- ✅ `https://` — Encrypted connection (look for the padlock icon)
- ❌ `http://` — Unencrypted, avoid entering sensitive data

**2. Examine the Domain**
- Read the domain carefully: `paypal.com` vs `paypa1.com`
- The real domain is right before the TLD: `login.paypal.com` ✅ vs `paypal.login.malicious.com` ❌
- Be cautious of unusual TLDs: `.tk`, `.xyz`, `.club`

**3. Red Flags in URLs:**
- IP addresses instead of domain names
- Excessive subdomain depth
- URL shorteners from unknown sources
- Special characters like `@` in the URL
- Very long, complex URLs
- Misspelled brand names

**4. Tools for URL Verification:**
- Use Veridian URL scanner
- Check Google Safe Browsing status
- Look up domain age using WHOIS
- Verify SSL certificate details

**5. Safe Browsing Habits:**
- Type URLs directly rather than clicking links
- Use bookmarks for frequently visited sites
- Keep your browser and extensions updated
- Use a reputable antivirus with web protection
- Be extra cautious on mobile devices"""

    def _general_help(self) -> str:
        """General help and capabilities overview."""
        return """## Welcome to Veridian Assistant! 🛡️

I'm here to help you stay safe from fraud. Here's what I can do:

### 🔍 Ask Me About:
- **"Why is this message dangerous?"** — I'll explain the risk factors
- **"How can I identify scam messages?"** — I'll share detection tips
- **"What should I do if I clicked a phishing link?"** — I'll guide you through recovery steps
- **"How does the risk score work?"** — I'll explain our scoring system
- **"How to check if a URL is safe?"** — I'll provide URL safety tips

### 🛠️ Tools Available:
- **SMS Scanner** — Analyze text messages for spam/scam indicators
- **Email Scanner** — Check emails for phishing attempts
- **URL Scanner** — Verify if links are safe to visit
- **Report Tool** — Report suspicious content for review

### 💡 Quick Tips:
1. Never share passwords, PINs, or OTPs with anyone
2. Verify unexpected messages through official channels
3. Don't click links from unknown senders
4. If it sounds too good to be true, it probably is
5. Use our scanner before interacting with suspicious content

What would you like to know?"""

    def _fallback_response(self, message: str) -> str:
        """Response when intent is not clearly detected."""
        return f"""I'd be happy to help you with fraud detection and prevention! 

I'm not quite sure what you're asking about. Here are some things you can ask me:

- **"Why is this message dangerous?"** — Explain risk factors for a scanned message
- **"How to identify scam messages?"** — Tips for spotting fraud
- **"What should I do if I got scammed?"** — Recovery and reporting steps
- **"How does the risk score work?"** — Understanding our analysis
- **"Is this URL safe?"** — URL safety tips
- **"How to protect my email?"** — Email security best practices

You can also use our scanning tools to analyze specific SMS messages, emails, or URLs for fraud indicators.

What would you like to know more about?"""
