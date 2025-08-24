# audit_service/models.py
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict


class AuditRequest(BaseModel):
    """Incoming audit request from pipeline."""
    response: str
    context: Optional[str] = None  # for hallucination checks if needed


class AuditResult(BaseModel):
    """Final result after passing through all audit checks."""
    outcome: str                  # PASS / FLAG / FAIL
    flags: Dict[str, int]         # {pii: 0/1/2, bias: 0/1/2, hallucination: 0/1/2}
    original: str                 # raw response text
    cleaned: Optional[str] = None # Gemini-cleaned text if needed


    model_config = ConfigDict(extra="allow")