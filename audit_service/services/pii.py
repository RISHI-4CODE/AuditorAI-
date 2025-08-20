import re
from typing import Dict, List

_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone": r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10})\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "api_key_like": r"\b(?:sk|AKIA|ghp)_[A-Za-z0-9]{20,}\b",
    "aadhaar_like": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
}

def detect_pii(text: str) -> Dict[str, List[str]]:
    findings = {}
    for name, pattern in _PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings[name] = list(set(matches))
    return findings
