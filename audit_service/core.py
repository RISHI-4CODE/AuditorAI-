# audit_service/core.py
from typing import Dict, Any
from audit_service.services.audit_models_client import run_all_models
from audit_service.services.gemini_adapter import GeminiAdapter   # ✅ use Gemini instead of Portia

# single Gemini instance for reuse
gemini = GeminiAdapter()


def _decide_outcome(flags: Dict[str, int]) -> str:
    """Derive overall outcome from per-model flags."""
    if 2 in flags.values():
        return "FAIL"
    elif 1 in flags.values():
        return "FLAG"
    return "PASS"


def run_audit_input(response_text: str, context: str = "") -> Dict[str, Any]:
    """
    Audit user input.
    - Runs PII (regex), Toxicity (ML)
    - Flags: 0=PASS, 1=FLAG, 2=FAIL
    - Does not rewrite (don’t change user input)
    - Adds user-facing messages when blocked
    """
    if not response_text.strip():
        return {
            "outcome": "FAIL",
            "flags": {"pii": 2, "bias": 2},
            "original": response_text,
            "cleaned": None,
            "messages": ["❌ Empty input is not allowed."],
        }

    results = run_all_models(response_text, models=["pii", "toxicity"])

    flags = {
        "pii": results["pii"].get("severity", 0),
        "bias": results["toxicity"]["flag"],
    }

    outcome = _decide_outcome(flags)

    # User-facing feedback messages
    FLAG_MESSAGES = {
        "pii": "⚠️ Your message contains personally identifiable information (PII) such as emails, phone numbers, or addresses. Please remove or mask this before resubmitting.",
        "bias": "⚠️ Your message may contain biased, toxic, or offensive language. Please rephrase it in a respectful tone.",
    }

    messages = []
    for flag, value in flags.items():
        if value > 0 and flag in FLAG_MESSAGES:
            messages.append(FLAG_MESSAGES[flag])

    return {
        "outcome": outcome,
        "flags": flags,
        "original": response_text,
        "cleaned": None,   # never rewrite input
        "messages": messages,
    }



def _calculate_flags(response_text: str) -> Dict[str, int]:
    results = run_all_models(response_text, models=["pii", "toxicity", "hallucination"])
    return {
        "pii": results["pii"].get("severity", 0),
        "bias": results["toxicity"]["flag"],
        "hallucination": results["hallucination"]["flag"],
    }


def run_audit_output(response_text: str, context: str = "") -> Dict[str, Any]:
    """
    Audit AI output.
    - Runs all models (PII regex, Toxicity ML, Hallucination)
    - If FLAG/FAIL, sanitize using GeminiAdapter
    """
    if not response_text.strip():
        return {
            "outcome": "FAIL",
            "flags": {"pii": 2, "bias": 2, "hallucination": 2},
            "original": response_text,
            "cleaned": "⚠️ Empty response",
        }

    flags = _calculate_flags(response_text)
    outcome = _decide_outcome(flags)

    safe_output = None
    if outcome in ("FLAG", "FAIL"):
        try:
            safe_output = gemini.sanitize(response_text, flags, findings={})
        except Exception as e:
            print("[run_audit_output] Gemini sanitize failed:", e)
            safe_output = None

    return {
        "outcome": outcome,
        "flags": flags,
        "original": response_text,
        "cleaned": safe_output or response_text,
    }
