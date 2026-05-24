"""Input validation utilities for sanitizing and validating user input."""

import re
from typing import Optional
from urllib.parse import urlparse


def sanitize_text(text: str) -> str:
    """Remove potentially dangerous characters while preserving meaningful content."""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def validate_url_format(url: str) -> bool:
    """Validate that a string is a properly formatted URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False


def validate_email_content(content: str) -> bool:
    """Validate email content is not empty and within reasonable bounds."""
    if not content or not content.strip():
        return False
    if len(content) > 50000:
        return False
    return True


def validate_sms_content(content: str) -> bool:
    """Validate SMS content is within expected bounds."""
    if not content or not content.strip():
        return False
    if len(content) > 1600:  # Standard SMS limit with concatenation
        return False
    return True


def extract_urls_from_text(text: str) -> list:
    """Extract all URLs from a text string."""
    url_pattern = re.compile(
        r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        r"(?:/[^\s]*)?"
    )
    return url_pattern.findall(text)


def mask_sensitive_data(text: str) -> str:
    """Mask potential sensitive data like credit card numbers and SSNs."""
    # Mask credit card numbers (basic pattern)
    text = re.sub(r"\b(\d{4})\s?(\d{4})\s?(\d{4})\s?(\d{4})\b", r"\1 **** **** \4", text)
    # Mask SSN patterns
    text = re.sub(r"\b(\d{3})-(\d{2})-(\d{4})\b", r"***-**-\3", text)
    # Mask phone numbers partially
    text = re.sub(r"\b(\d{3})[-.](\d{3})[-.](\d{4})\b", r"\1-***-\3", text)
    return text


def calculate_text_entropy(text: str) -> float:
    """Calculate Shannon entropy of text to detect randomized/obfuscated content."""
    if not text:
        return 0.0
    import math
    from collections import Counter

    freq = Counter(text)
    length = len(text)
    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
    )
    return round(entropy, 4)
