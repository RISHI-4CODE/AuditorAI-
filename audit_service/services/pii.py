import re
from typing import List, Dict

# Regex-based PII patterns with severity
PII_PATTERNS = {
    # --- Contact Info ---
    "PHONE_NUMBER": (
        re.compile(r"\b(?:\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
        2,
    ),
    "EMAIL": (
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        1,
    ),
    "ADDRESS": (
        re.compile(r"\b\d{1,5}\s\w+(?:\s\w+){0,3}\s(?:Street|St|Avenue|Ave|Road|Rd|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b"),
        1,
    ),

    # --- Identity Numbers ---
    "SSN_US": (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), 2),
    "PASSPORT": (re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"), 2),  # Generic (USA, EU, etc.)

    # 🔧 PATCHED: driver license — require context words
    "DRIVER_LICENSE": (
        re.compile(r"\b(?:DL|Driver.?License|Lic|D[LR]N)[\s:]*[A-Z0-9]{5,15}\b", re.IGNORECASE),
        1,
    ),

    "AADHAAR_IN": (re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b"), 2),  # India Aadhaar
    "PAN_IN": (re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"), 2),  # India PAN

    # --- Finance ---
    "CREDIT_CARD": (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), 2),
    "IBAN": (re.compile(r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b"), 2),
    "BANK_ACCOUNT": (re.compile(r"\b\d{9,18}\b"), 2),

    # --- Digital Identifiers ---
    "IP_ADDRESS": (
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        1,
    ),
    "IPV6_ADDRESS": (
        re.compile(r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b"),
        1,
    ),
    "MAC_ADDRESS": (
        re.compile(r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b"),
        1,
    ),

    "API_KEY_PREFIXED": (
        re.compile(r"\b(?:sk|pk|api|key)[\-\_a-zA-Z0-9\$\#]{12,64}\b"),
        2,
    ),

    # 🔧 PATCHED: generic API keys — keep but downgrade severity
    "API_KEY_GENERIC": (
        re.compile(r"\b[a-zA-Z0-9\-\_\$\#]{20,64}\b"),
        1,  # was 2, now FLAG instead of FAIL
    ),

    "API_KEY_CONTEXTUAL": (
        re.compile(r"(?i)\bapi[\s\-_]?key\b[:=\s]*([A-Za-z0-9\-\_\$\#]{8,64})"),
        2,
    ),
    "JWT": (
        re.compile(r"eyJ[A-Za-z0-9_-]+?\.[A-Za-z0-9._-]+?\.[A-Za-z0-9._-]+"),
        2,
    ),

    "USERNAME": (
        re.compile(r"@[A-Za-z0-9_]{3,20}\b"),
        1,
    ),
}


def detect_pii(text: str) -> List[Dict]:
    """
    Detect PII using regex rules.
    Returns a list of dicts: {type, severity, match}
    """
    findings = []
    for pii_type, (pattern, severity) in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            for m in matches if isinstance(matches, list) else [matches]:
                findings.append(
                    {"type": pii_type, "severity": severity, "match": m}
                )
    return findings
