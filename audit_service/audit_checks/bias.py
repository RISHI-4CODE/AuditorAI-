# audit_service/audit_checks/bias.py
import re
from typing import Dict, List

# Minimal lexicon of biased/toxic terms (expandable for demo)
_TOXIC_TERMS = [
    "idiot", "stupid", "hate", "racist", "sexist", "dumb", "kill yourself",
    "loser", "ugly", "trash"
]

def detect_bias_toxicity(text: str) -> Dict[str, List[str]]:
    """
    Detect biased / toxic words in text.
    Returns dict { "toxic": [matches] } if found.
    """
    matches: List[str] = []
    for term in _TOXIC_TERMS:
        hits = re.findall(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
        if hits:
            matches.extend(hits)
    return {"toxic": list(set(matches))} if matches else {}

def summarize_bias(findings: Dict[str, List[str]]) -> str:
    """Summarize bias findings for logs (e.g. 'toxic(3)')."""
    if not findings:
        return ""
    return ", ".join(f"{cat}({len(v)})" for cat, v in findings.items())
