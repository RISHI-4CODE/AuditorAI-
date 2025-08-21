# app/auditor_agent.py
from portia import tool
from app.auditor import run_audits
from app.models import AuditResult
from app.notion_utils import log_audit_to_notion
from storage.db import SessionLocal, Base, engine
from storage.models import AuditLog

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

@tool(name="custom_api_audit", description="Run audit checks on AI output and log results")
def audit_and_log(doc: str, context: str = "") -> dict:
    """
    Portia tool: runs audits, logs results (DB + Notion), returns risk score + cleaned text.
    """
    # Run audits
    result: AuditResult = run_audits(doc, context)

    # Dict format for persistence + Portia
    result_dict = {
        "original": result.original,
        "findings": result.findings,
        "reasons": result.reasons,
        "outcome": result.outcome,
        "cleaned": result.cleaned,
        "risk_score": result.risk_score if hasattr(result, "risk_score") else 0
    }

    # Log to Notion
    log_audit_to_notion(result_dict)

    # Persist in DB
    db = SessionLocal()
    audit_entry = AuditLog(**result_dict)
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    db.close()

    return result_dict
