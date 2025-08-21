import re
from typing import Dict, Any

def detect_low_quality(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Heuristic-based data quality audit.
    Returns a dict with issues found. Future extension: fact-checking against context.
    """
    findings = {}

    # Heuristic 1 – Overconfidence language
    overconfident_terms = ["always", "never", "guaranteed", "100%", "certainly"]
    over_hits = [w for w in overconfident_terms if re.search(rf"\b{w}\b", text, re.IGNORECASE)]
    if over_hits:
        findings["overconfidence"] = over_hits

    # Heuristic 2 – Placeholder / nonsense markers
    if re.search(r"(lorem ipsum|???|xxx|todo)", text, re.IGNORECASE):
        findings["placeholder"] = True

    # Heuristic 3 – Too short (maybe incomplete answer)
    if len(text.strip()) < 20:
        findings["too_short"] = True

    # Heuristic 4 – Repetition (same word repeated too much)
    words = text.lower().split()
    for w in set(words):
        if words.count(w) > len(words) * 0.2 and len(words) > 10:
            findings.setdefault("repetition", []).append(w)

    # Placeholder for context-based validation (future)
    if context:
        findings["context_check"] = "Not implemented yet"

    return findings

def quality_summary(findings: Dict[str, Any]) -> str:
    if not findings:
        return ""
    return ", ".join([f"{k}" for k in findings.keys()])
