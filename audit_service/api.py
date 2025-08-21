# audit_service/api.py
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from audit_service.core import run_audit

app = FastAPI(title="Audit Service", version="1.0")

class AuditRequest(BaseModel):
    doc: str
    context: Optional[str] = None

class AuditResponse(BaseModel):
    outcome: str
    risk_score: int
    reasons: list[str]
    findings: Dict[str, Any]
    original: str
    cleaned: Optional[str] = None

@app.post("/audit", response_model=AuditResponse)
def audit(request: AuditRequest):
    result = run_audit(request.doc, request.context or "")
    return result

@app.get("/health")
def health():
    return {"status": "ok"}
