# audit_service/services/toxicity.py
"""
Toxicity detection service.
Wraps a real ML model (e.g. detoxify, Perspective API, or your trained model).
"""

from typing import Dict

# Example: using Detoxify (you must install detoxify: `pip install detoxify`)
from detoxify import Detoxify

# Load once at startup
_model = Detoxify("original")  # or "multilingual" depending on your needs

def analyze_toxicity(text: str) -> Dict[str, int]:
    """
    Run toxicity detection.
    Returns a dict with:
        - score: float (0–1)
        - flag: int (0=PASS, 1=FLAG, 2=FAIL)
    """
    if not text.strip():
        return {"score": 0.0, "flag": 0}

    # Run inference
    preds = _model.predict(text)

    # Aggregate toxicity score (detoxify has multiple categories: toxicity, insult, obscene, etc.)
    score = float(preds["toxicity"])

    # Decide thresholds
    if score > 0.8:
        flag = 2   # FAIL
    elif score > 0.5:
        flag = 1   # FLAG
    else:
        flag = 0   # PASS

    return {"score": score, "flag": flag}
