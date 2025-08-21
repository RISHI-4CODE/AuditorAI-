# audit_service/audit_checks/data_quality.py
import re
from typing import Dict, Any

def detect_data_quality(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Heuristic-based data quality audit.
    Flags overconfidence, placeholders, repetition, and incomplete answers.
    """
    findings: Dict[str, Any] = {}

    # Heuristic 1 – Overconfidence language
    overconfident_terms = ["always", "never", "guaranteed", "100%", "certainly"]
    hits = [w for w in overconfident_terms if re.search(rf"\b{w}\b", text, re.IGNORECASE)]
    if hits:
        findings["overconfidence"] = hits

    # Heuristic 2 – Placeholder / nonsense markers
    if re.search(r"(lorem ipsum|???|xxx|todo)", text, re.IGNORECASE):
        findings["placeholder"] = True

    # Heuristic 3 – Too short (maybe incomplete answer)
    if len(text.strip()) < 20:
        findings["too_short"] = True

    # Heuristic 4 – Repetition
    words = text.lower().split()
    for w in set(words):
        if words.count(w) > len(words) * 0.2 and len(words) > 10:
            findings.setdefault("repetition", []).append(w)

    return findings

def summarize_quality(findings: Dict[str, Any]) -> str:
    """Summarize quality findings (e.g. 'overconfidence, too_short')."""
    return ", ".join(findings.keys()) if findings else ""
