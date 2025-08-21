# storage/crud.py
from storage.db import SessionLocal
from storage.models import AuditLog
from app.models import AuditResult
import json

def save_audit_result(audit_result: AuditResult) -> AuditLog:
    session = SessionLocal()
    try:
        db_obj = AuditLog(
            outcome=audit_result.outcome,
            reasons=audit_result.findings.dict().get("reasons", []),
            findings=audit_result.findings.dict(),
            original=audit_result.original_response,
            cleaned=audit_result.final_response
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    finally:
        session.close()
