import time
from fastapi import APIRouter
from audit_service.adapters.gemini_adapter import GeminiAdapter
from audit_service.audit_checks.prompts import L1_PROMPT, L2_PROMPT, L3_PROMPT
from audit_service.models.schemas import AuditRequest, RedoRequest
from audit_service.routers.audit import audit, redo
import os

router = APIRouter()

gemini = GeminiAdapter(api_key=os.getenv("GEMINI_API_KEY"))
MAX_REDO = int(os.getenv("MAX_REDO", "3"))


@router.post("/run_full")
def run_full(payload: AuditRequest):
    """
    Full audit workflow:
    1. Generate an initial draft.
    2. Run audit checks.
    3. If risk >= 50, auto-redo up to MAX_REDO times.
    4. Return final safe response + audit trail.
    """
    user_prompt = payload.user_prompt or payload.doc
    draft = gemini.generate(user_prompt)
    trail = [{"stage": "initial", "text": draft}]
    audit_info = audit(AuditRequest(doc=draft, user_prompt=user_prompt))
    retries = 0

    while audit_info.risk_score >= 50 and retries < MAX_REDO:
        retries += 1
        redo_resp = redo(
            RedoRequest(
                doc=draft,
                issues=audit_info.issues,
                redo_level=retries,
                user_prompt=user_prompt,
            )
        )
        draft = redo_resp["redo_output"]
        trail.append({"stage": f"redo_{retries}", "text": draft})
        audit_info = audit(AuditRequest(doc=draft, user_prompt=user_prompt))
        time.sleep(0.2)

    if audit_info.risk_score >= 50:
        final = "⚠️ I’m unable to provide a safe response to that request."
        outcome = "FALLBACK"
    else:
        final = draft
        outcome = "PASS"

    log = {
        "user_prompt": user_prompt,
        "outcome": outcome,
        "attempts": retries,
        "risk": audit_info.model_dump(),
    }
    return {"final": final, "audit_log": log, "trail": trail}
