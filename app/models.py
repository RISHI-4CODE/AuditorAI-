from typing import Dict, List, Optional, Union
from pydantic import BaseModel

class AuditRequest(BaseModel):
    """Incoming audit request from pipeline."""
    response: str
    context: Optional[str] = None  # optional user question or conversation

class Findings(BaseModel):
    """Findings from different checks (all simplified to lists of strings)."""
    pii: Optional[List[str]] = None
    bias: Optional[List[str]] = None
    hallucination: Optional[Dict[str, Union[str, float]]] = None  # {"label": ..., "confidence": ...}

class AuditResult(BaseModel):
    """Final result after passing through all audit checks."""
    outcome: str                 # PASS / FLAG / FAIL
    reasons: List[str]           # human-readable explanations
    findings: Dict[str, any]     # merged findings from checks
    flags: Dict[str, int]        # {pii: 0/1/2, bias: 0/1/2, hallucination: 0/1/2}
    original: str                # raw response text
    cleaned: Optional[str]       # Gemini-cleaned text if needed
    risk_score: int              # numeric risk score for Portia policy
