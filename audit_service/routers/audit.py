# audit_service/routers/audit.py
from fastapi import APIRouter, HTTPException
from audit_service.core import run_audit
from audit_service.models import AuditRequest, AuditResult  # ✅ now local


router = APIRouter()

@router.post("/audit/input", response_model=AuditResult)
def audit_input(payload: AuditRequest):
    """
    Audit user input before sending to the model.
    - ML models only (PII, bias, etc.)
    - Returns flags {0/1/2} but does NOT rewrite.
    - If flagged, system can warn/block user instead of rewriting.
    """
    text = payload.response.strip()
    if not text:
        raise HTTPException(400, "Empty user input")

    result = run_audit_input(text, context=payload.context or "")
    return AuditResult(**result)


@router.post("/audit/output", response_model=AuditResult)
def audit_output(payload: AuditRequest):
    """
    Audit AI output before returning to user.
    - Runs all ML checks (PII, bias, hallucination, etc.)
    - If flagged, calls Gemini rewrite automatically.
    """
    text = payload.response.strip()
    if not text:
        raise HTTPException(400, "Empty AI output")

    result = run_audit_output(text, context=payload.context or "")
    return AuditResult(**result)
