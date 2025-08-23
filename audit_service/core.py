# audit_service/core.py
from typing import Dict, Any
from audit_service.services.audit_models_client import run_all_models
from audit_service.services.portia_client import rewrite_with_portia


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
    - Runs ONLY PII + Toxicity
    - Flags: 0=PASS, 1=FLAG, 2=FAIL
    - No rewrite
    """
    if not response_text.strip():
        return {
            "outcome": "FAIL",
            "flags": {"pii": 2, "bias": 2, "hallucination": 0},
            "original": response_text,
            "cleaned": None,
        }

    results = run_all_models(response_text, models=["pii", "toxicity"])

    flags = {
        "pii": 2 if results["pii"]["found"] else 0,
        "bias": results["toxicity"]["flag"],
        "hallucination": 0,  # not checked for user input
    }

    outcome = _decide_outcome(flags)

    return {
        "outcome": outcome,
        "flags": flags,
        "original": response_text,
        "cleaned": None,
    }


def _calculate_flags(response_text: str) -> Dict[str, int]:
    """
    Run all audits (PII, Toxicity, Hallucination) and return flags.
    Flags: 0=PASS, 1=FLAG, 2=FAIL
    """
    results = run_all_models(response_text, models=["pii", "toxicity", "hallucination"])

    return {
        "pii": 2 if results["pii"]["found"] else 0,
        "bias": results["toxicity"]["flag"],
        "hallucination": results["hallucination"]["flag"],
    }


def run_audit_output(response_text: str, context: str = "") -> Dict[str, Any]:
    """
    Audit AI output.
    - Runs all models (PII, Toxicity, Hallucination)
    - Flags remain per model
    - Rewrites with Portia if outcome = FLAG/FAIL
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
        # ✅ Pass full flags dict now
        safe_output = rewrite_with_portia(response_text, flags)

    return {
        "outcome": outcome,
        "flags": flags,               # <-- transparent per-model flags
        "original": response_text,
        "cleaned": safe_output or response_text,
    }
