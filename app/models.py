# app/models.py
from typing import Dict, List, Optional
from pydantic import BaseModel

class AuditRequest(BaseModel):
    """Incoming audit request from pipeline."""
    response: str
    context: Optional[str] = None  # optional user question or conversation

class Findings(BaseModel):
    """Standard findings object returned by each audit check."""
    pii: Optional[Dict[str, List[str]]] = None
    security: Optional[List[str]] = None
    data_quality: Optional[List[str]] = None
    bias: Optional[Dict[str, List[str]]] = None

class AuditResult(BaseModel):
    """Final result after passing through all audit checks."""
    outcome: str  # PASS / FLAG / FAIL
    findings: Findings
    sanitized_summary: str  # safe string summary for logs
    original_response: str
    final_response: str
