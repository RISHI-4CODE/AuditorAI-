import re
from typing import Dict, List

_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone_10": r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10})\b",
    "api_key_like": r"\b(?:sk|AKIA|ghp|api_key|API_KEY)_[A-Za-z0-9\-]{10,}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "aadhaar_like": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
}

def detect_pii(text: str) -> Dict[str, List[str]]:
    findings = {}
    for name, pattern in _PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings[name] = list(set(matches))
    return findings

def sanitize_summary(findings: Dict[str, List[str]]) -> str:
    # Return a short, non-sensitive summary e.g. "email (1), phone (2)"
    if not findings:
        return ""
    parts = []
    for k, v in findings.items():
        parts.append(f"{k}({len(v)})")
    return ", ".join(parts)
