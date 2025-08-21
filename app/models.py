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
    outcome: str                 # PASS / FLAG / FAIL
    reasons: List[str]           # human-readable explanations
    findings: Dict[str, any]     # merged findings from checks
    original: str                # raw response text
    cleaned: Optional[str]       # safe version if available
    risk_score: int              # numeric risk score for Portia policy
