from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AuditRequest(BaseModel):
    doc: str = Field(..., description="AI-generated text to audit")

class RedoRequest(BaseModel):
    doc: str
    issues: List[str] = []

class AuditResult(BaseModel):
    risk_score: int
    issues: List[str]
    pii: Dict[str, list]
    toxicity: float
    hallucination: float
    notes: Optional[str] = None
    safe_output: Optional[str] = None  # optional immediate rewrite
    raw: Dict[str, Any] = {}
