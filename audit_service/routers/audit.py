from fastapi import APIRouter, HTTPException
from audit_service.models.schemas import AuditRequest, RedoRequest, AuditResult
from audit_service.services.pii import detect_pii
from audit_service.services.gemini_client import rate_toxicity_and_bias, rate_hallucination, rewrite_safe
from audit_service.services.scoring import aggregate
from audit_service.services.logistic_client import score_harm_probability
from audit_service.storage.memory_log import add as log_add
from integrations.slack_notify import post_high_risk
from integrations.notion_logger import log_to_notion

router = APIRouter()

@router.post("/audit", response_model=AuditResult)
def audit(payload: AuditRequest):
    text = payload.doc.strip()
    if not text:
        raise HTTPException(400, "Empty doc")

    pii = detect_pii(text)
    tox = rate_toxicity_and_bias(text)
    hall = rate_hallucination(text)
    harm_prob = score_harm_probability(text)   # NEW logistic model check

    # aggregate now includes harm probability
    score, issues, tier = aggregate(pii, tox, hall, harm_prob=harm_prob)

    safe_output = None
    if score >= 50:  # auto-redo path
        safe_output = rewrite_safe(text, issues)

    result = AuditResult(
        risk_score=score,
        issues=issues,
        pii=pii,
        toxicity=tox,
        hallucination=hall,
        notes=f"tier={tier}, harm_prob={harm_prob:.2f}",
        safe_output=safe_output,
        raw={}
    )

    # side-effects: log + Slack + Notion
    status = "Escalated" if score >= 90 else ("Auto-redone" if score >= 50 else "Passed")
    log_add({"input": text, "result": result.model_dump(), "status": status})

    # ✅ Only log to Notion for high-risk audits
    if score >= 90:
        log_to_notion(text, score, status, safe_output or "")
        post_high_risk(text, score, safe_output or "")

    return result

@router.post("/redo")
def redo(payload: RedoRequest):
    return {"safe_output": rewrite_safe(payload.doc, payload.issues)}
