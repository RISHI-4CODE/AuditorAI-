# app/auditor_agent.py
from app.auditor import run_audits
from app.models import AuditResult
from app.notion_utils import log_audit_to_notion
from storage.db import SessionLocal, Base, engine
from storage.models import AuditLog


# Create tables if not exist
Base.metadata.create_all(bind=engine)


def audit_and_log(response_text: str, context: str = "") -> AuditResult:
    """
    Run audits on a response, then log the results to Notion.
    """
    # Run all audits
    result: AuditResult = run_audits(response_text, context)

    # Convert to dict for persistence
    result_dict = {
        "original": result.original,
        "findings": result.findings,
        "reasons": result.reasons,
        "outcome": result.outcome,
        "cleaned": result.cleaned,
    }

    # Log to Notion
    log_audit_to_notion(result_dict)

    # Log to DB
    db = SessionLocal()
    audit_entry = AuditLog(**result_dict)
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    db.close()

    return result
