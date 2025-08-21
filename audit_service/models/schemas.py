from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class AuditRequest(BaseModel):
    doc: str = Field(..., description="AI-generated text to audit")
    user_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class RedoRequest(BaseModel):
    doc: str
    issues: List[str] = []
    redo_level: int = 1
    user_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ScoreDetail(BaseModel):
    score: float = Field(..., description="Normalized score in [0,1]")
    fallback: bool = Field(False, description="True if value came from fallback/default logic")


class AuditResult(BaseModel):
    risk_score: int
    issues: List[str] = []
    pii: Dict[str, list] = {}
    toxicity: ScoreDetail = Field(default_factory=lambda: ScoreDetail(score=0.0, fallback=True))
    hallucination: ScoreDetail = Field(default_factory=lambda: ScoreDetail(score=0.0, fallback=True))
    notes: Optional[str] = None
    safe_output: Optional[str] = None  # Optional safe rewrite
    raw: Dict[str, Any] = {}
