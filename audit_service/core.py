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
    if not response_text.strip():
        return {
            "outcome": "FAIL",
            "flags": {"pii": 2, "toxicity": 2, "hallucination": 0},
            "original": response_text,
            "cleaned": None,
            "messages": ["❌ Empty input is not allowed."],
            "findings": []
        }

    results = run_all_models(response_text, models=["pii", "toxicity"])

    flags = {
        "pii": results["pii"].get("severity", 0),
        "toxicity": results["toxicity"]["flag"],
        "hallucination": 0  # not checked at input stage
    }

    outcome = _decide_outcome(flags)

    FLAG_MESSAGES = {
        "pii": "⚠️ Your message contains personally identifiable information (PII). Please remove or mask it.",
        "toxicity": "⚠️ Your message may contain toxic or offensive language. Please rephrase it."
    }

    messages = [FLAG_MESSAGES[f] for f, v in flags.items() if v > 0 and f in FLAG_MESSAGES]

    return {
        "outcome": outcome,
        "flags": flags,
        "original": response_text,
        "cleaned": None,
        "messages": messages,
        "findings": results  # keep full details
    }


def run_audit_output(response_text: str, context: str = "") -> Dict[str, Any]:
    if not response_text.strip():
        return {
            "outcome": "FAIL",
            "flags": {"pii": 2, "toxicity": 2, "hallucination": 2},
            "original": response_text,
            "cleaned": "⚠️ Empty response",
            "findings": []
        }

    results = run_all_models(response_text, models=["pii", "toxicity", "hallucination"])

    flags = {
        "pii": results["pii"].get("severity", 0),
        "toxicity": results["toxicity"]["flag"],
        "hallucination": results["hallucination"]["flag"],
    }

    outcome = _decide_outcome(flags)

    safe_output = None
    if outcome in ("FLAG", "FAIL"):
        try:
            safe_output = gemini.sanitize(response_text, flags, results)
        except Exception as e:
            print("[run_audit_output] Gemini sanitize failed:", e)
            safe_output = None

    return {
        "outcome": outcome,
        "flags": flags,
        "original": response_text,
        "cleaned": safe_output or response_text,
        "findings": results
    }




def _calculate_flags(response_text: str) -> Dict[str, int]:
    results = run_all_models(response_text, models=["pii", "toxicity", "hallucination"])
    return {
        "pii": results["pii"].get("severity", 0),
        "bias": results["toxicity"]["flag"],
        "hallucination": results["hallucination"]["flag"],
    }


