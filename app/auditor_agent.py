# app/auditor_agent.py
"""
Custom Portia tool that wraps our audit pipeline.
Runs PII, toxicity, bias, and hallucination checks and returns a unified risk score.
"""

from portia import tool
from app.auditor import run_audits
from app.models import AuditResult

@tool(name="custom_api_audit", description="Run audit checks on input/output text")
def audit_and_log(doc: str, mode: str = "output") -> dict:
    """
    Portia tool: runs audits and returns a structured result.
    This version is simplified for hackathon demo (no DB/Notion logging).
    """
    # Run audits (ML + regex + wiki checks)
    result: AuditResult = run_audits(doc, mode)

    # Return structured dictionary for Portia orchestration
    return {
        "original": result.original,
        "findings": result.findings,
        "reasons": result.reasons,
        "outcome": result.outcome,   # e.g., PASS / FLAG / FAIL
        "cleaned": result.cleaned,
        "risk_score": result.risk_score,
        "mode": mode,
    }
