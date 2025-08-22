"""
Custom Portia tool that wraps our audit pipeline.
Runs PII, toxicity, bias, and hallucination checks and returns a unified risk score.
"""

from portia import tool
from app.auditor import run_audits
from app.models import AuditResult
from audit_service.adapters.gemini_adapter import GeminiAdapter

_gemini = GeminiAdapter()


@tool(name="custom_api_audit", description="Run audit checks on input/output text")
def audit_and_log(doc: str, mode: str = "output") -> dict:
    """
    Portia tool: runs audits and returns a structured result.
    If flags are raised, Gemini will sanitize the text.
    """
    # Run audits (ML + regex + wiki checks)
    result: AuditResult = run_audits(doc, mode)

    cleaned = result.original
    if any(v > 0 for v in result.flags.values()):
        cleaned = _gemini.sanitize(result.original, result.flags, result.findings)

    # Return structured dictionary for Portia orchestration
    return {
        "original": result.original,
        "cleaned": cleaned,
        "findings": result.findings,
        "reasons": result.reasons,
        "flags": result.flags,
        "outcome": result.outcome,   # e.g., PASS / FLAG / FAIL
        "risk_score": result.risk_score,
        "mode": mode,
    }
