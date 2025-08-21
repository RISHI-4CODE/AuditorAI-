import os
import google.generativeai as genai
from audit_service.audit_checks.pii import detect_pii
from audit_service.audit_checks.prompts import L1_PROMPT
from audit_service.audit_checks.logistic import HarmfulClassifier

_MODEL = "gemini-1.5-flash"
_classifier = HarmfulClassifier(model_path=os.getenv("LOGISTIC_MODEL_PATH", "models/logistic.pkl"))

def _client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    return genai

def _safe_number(val: str, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(val.strip())))
    except Exception:
        return default

def rate_toxicity_and_bias(text: str) -> float:
    """
    Returns float [0,1]: toxicity/bias likelihood.
    Checks logistic model first (Portia Core mandatory).
    """
    # Logistic baseline
    prob = _classifier.predict_proba(text)
    if prob >= 0.85:  # hard Portia cutoff
        return 1.0

    genai = _client()
    prompt = f"""Rate this text for toxicity/bias on a 0..1 scale.
Return ONLY a number.
Text:
{text}"""
    try:
        resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
        return _safe_number(resp.text, default=prob)
    except Exception:
        return prob

def rate_hallucination(text: str) -> float:
    """
    Estimate hallucination risk [0,1].
    """
    genai = _client()
    prompt = f"""Estimate hallucination risk of the following text on a 0..1 scale.
Return ONLY a number.
Text:
{text}"""
    try:
        resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
        return _safe_number(resp.text, default=0.5)
    except Exception:
        return 0.5

def rewrite_safe(text: str, issues: list[str]) -> str:
    """
    Rewrite the text safely, respecting Portia Core:
    - Remove PII
    - Reduce toxicity/bias
    - Avoid unverifiable claims
    - Apply strict fallback if violations remain
    """
    # Portia mandatory check
    if detect_pii(text):
        return "⚠️ Redacted due to sensitive information."

    genai = _client()
    prompt = L1_PROMPT.format(user_prompt="Audit Rewrite", previous_output=text)
    try:
        resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
        return resp.text.strip() if resp and resp.text else text
    except Exception:
        return "⚠️ Unable to safely rewrite."
