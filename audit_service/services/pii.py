import os
import re
import joblib
from typing import Dict, List, Any

# Load ML model once (Portia Core mandatory)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

pii_model = joblib.load(os.path.join(MODEL_DIR, "pii", "logistic.pkl"))
# Regex fallback patterns
_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone": r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10})\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "api_key_like": r"\b(?:sk|AKIA|ghp)_[A-Za-z0-9]{20,}\b",
    "aadhaar_like": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
}

def detect_pii(text: str) -> Dict[str, Any]:
    """
    Detect PII using ML model (preferred) + regex fallback.
    Returns dict: {category: {"flag": 0|1|2, "matches": [...optional...]}}
    """
    findings: Dict[str, Any] = {}

    # --- ML DETECTION ---
    if _pii_model:
        try:
            probs = _pii_model.predict_proba([text])[0]  # per-category probs
            labels = _pii_model.classes_
            for label, prob in zip(labels, probs):
                if prob > 0.7:
                    findings[label] = {"flag": 2, "prob": float(prob)}
                elif prob > 0.4:
                    findings[label] = {"flag": 1, "prob": float(prob)}
                else:
                    findings[label] = {"flag": 0, "prob": float(prob)}
        except Exception:
            pass  # fallback to regex

    # --- REGEX FALLBACK ---
    if not findings:  # only if ML unavailable or silent
        for name, pattern in _PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[name] = {"flag": 2, "matches": list(set(matches))}

    return findings

def sanitize_summary(findings: Dict[str, Any]) -> Dict[str, int]:
    """
    Summarize PII findings without exposing raw values.
    Returns counts only, never actual sensitive data.
    """
    summary = {}
    for k, v in findings.items():
        if "matches" in v:
            summary[k] = len(v["matches"])
        else:
            summary[k] = v["flag"]  # ML case
    return summary
