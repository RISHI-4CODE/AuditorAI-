import re
from typing import Dict, List

# Patterns that indicate unsafe or malicious instructions
_PATTERNS = {
    "malware": r"\b(malware|virus|trojan|worm|ransomware)\b",
    "hacking": r"\b(hack|exploit|backdoor|keylogger|rootkit|ddos|sql injection)\b",
    "weapons": r"\b(bomb|explosive|weapon|poison|grenade|firearm)\b",
    "violence": r"\b(kill|murder|terrorist|attack|shoot)\b",
    "fraud": r"\b(credit card skimmer|phishing|forgery|identity theft)\b",
}

def detect_security_issues(text: str) -> Dict[str, List[str]]:
    """
    Scan text for unsafe / malicious instructions.
    Returns dict {category: [matches]} if found.
    """
    findings = {}
    for category, pattern in _PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            findings[category] = list(set(matches))
    return findings

def summarize_security(findings: Dict[str, List[str]]) -> str:
    """
    Produce a safe summary for logging (e.g. 'hacking(2), weapons(1)').
    """
    if not findings:
        return ""
    return ", ".join(f"{cat}({len(v)})" for cat, v in findings.items())
