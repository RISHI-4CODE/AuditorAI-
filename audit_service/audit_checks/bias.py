import re
from typing import Dict, List

# A small lexicon of biased/toxic words (can be expanded)
_TOXIC_TERMS = [
    "idiot", "stupid", "hate", "racist", "sexist", "dumb", "kill yourself",
    "loser", "ugly", "trash"
]

def detect_bias_toxicity(text: str) -> Dict[str, List[str]]:
    """
    Scan text for biased / toxic words or slurs.
    Returns dict { "toxic": [matches] } if found.
    """
    findings: Dict[str, List[str]] = {}
    matches: List[str] = []
    for term in _TOXIC_TERMS:
        hits = re.findall(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
        if hits:
            matches.extend(hits)
    if matches:
        findings["toxic"] = list(set(matches))
    return findings

def summarize_bias(findings: Dict[str, List[str]]) -> str:
    """
    Produce a safe summary (e.g. 'toxic(3)') for logs.
    """
    if not findings:
        return ""
    return ", ".join(f"{cat}({len(v)})" for cat, v in findings.items())
