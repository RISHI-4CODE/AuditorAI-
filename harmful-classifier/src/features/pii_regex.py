import re

# Compile regexes once
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\\b\\+?[0-9][0-9\\-() ]{7,}[0-9]\\b")
SSN_REGEX = re.compile(r"\\b\\d{3}-\\d{2}-\\d{4}\\b")
CREDIT_CARD_REGEX = re.compile(r"\\b(?:\\d[ -]*?){13,16}\\b")

def pii_indicators(text: str) -> dict:
    """Return dictionary of PII matches."""
    return {
        "email": bool(EMAIL_REGEX.search(text)),
        "phone": bool(PHONE_REGEX.search(text)),
        "ssn": bool(SSN_REGEX.search(text)),
        "credit_card": bool(CREDIT_CARD_REGEX.search(text)),
    }

def contains_high_severity_pii(text: str) -> bool:
    """High severity PII (SSN, credit card)."""
    matches = pii_indicators(text)
    return matches["ssn"] or matches["credit_card"]
