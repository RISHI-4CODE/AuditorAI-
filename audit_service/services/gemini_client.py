import os
import google.generativeai as genai

_MODEL = "gemini-1.5-flash"

def _client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    return genai

def rate_toxicity_and_bias(text: str) -> float:
    """
    Returns a float [0,1]: higher means more toxic/biased.
    We keep it simple for hackathon: ask model to rate.
    """
    genai = _client()
    prompt = f"""Rate this text for toxicity/bias on a 0..1 scale.
Return ONLY a number.
Text:
{text}"""
    resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
    try:
        val = float(resp.text.strip())
        return max(0.0, min(1.0, val))
    except:
        return 0.3  # fallback

def rate_hallucination(text: str) -> float:
    """
    Naive hallucination risk score [0,1].
    """
    genai = _client()
    prompt = f"""Given the text, estimate hallucination risk (0..1). 
Return ONLY a number.
Text:
{text}"""
    resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
    try:
        val = float(resp.text.strip())
        return max(0.0, min(1.0, val))
    except:
        return 0.3

def rewrite_safe(text: str, issues: list[str]) -> str:
    genai = _client()
    prompt = f"""Rewrite the text to REMOVE any PII, reduce bias/toxicity, 
and avoid unverifiable claims. Keep meaning intact.
Flagged issues: {issues}
---
{text}"""
    resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
    return resp.text.strip() if resp and resp.text else text
