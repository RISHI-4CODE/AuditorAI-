import os
import time
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from typing import Dict, Any

from adapters.gemini_adapter import GeminiAdapter
from audit_checks.pii import detect_pii, sanitize_summary
from audit_checks.logistic import HarmfulClassifier
from audit_checks.prompts import L1_PROMPT, L2_PROMPT, L3_PROMPT
from models.schemas import AuditRequest, RedoRequest, AuditResult  # ✅ centralized schemas

load_dotenv()

app = FastAPI(title="AuditorAgent Audit Service")

# Initialize adapters / models
gemini = GeminiAdapter(api_key=os.getenv("GEMINI_API_KEY"))
classifier = HarmfulClassifier(model_path=os.getenv("LOGISTIC_MODEL_PATH", "models/logistic.pkl"))

MAX_REDO = int(os.getenv("MAX_REDO", "3"))


# Helper: aggregate quick checks
def run_quick_checks(text: str) -> Dict[str, Any]:
    prob = classifier.predict_proba(text)
    pii_findings = detect_pii(text)
    flags = []
    if prob >= 0.5:
        flags.append("ML_HARM_PROB")
    if pii_findings:
        flags.append("PII")
    return {
        "prob_harm": float(prob),
        "pii": pii_findings,
        "flags": flags,
    }


def aggregate_quick(result: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    if result["pii"]:
        score += 60
    score += int(result["prob_harm"] * 40)
    bucket = "LOW"
    if score >= 85:
        bucket = "CRITICAL"
    elif score >= 70:
        bucket = "HIGH"
    elif score >= 50:
        bucket = "MEDIUM"
    return {
        "risk_score": score,
        "bucket": bucket,
        "flags": result["flags"],
        "pii_summary": sanitize_summary(result["pii"]),
    }


@app.post("/audit", response_model=AuditResult)
def audit(payload: AuditRequest):
    text = payload.doc or ""
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    quick = run_quick_checks(text)
    agg = aggregate_quick(quick)

    return AuditResult(
        risk_score=agg["risk_score"],
        issues=agg["flags"],
        pii=quick["pii"],
        toxicity=quick["prob_harm"],
        hallucination=0.0,  # placeholder until Portia Core hallucination checks
        notes=None,
        raw=agg,
    )


@app.post("/redo")
def redo(payload: RedoRequest):
    level = int(payload.redo_level)
    if level <= 1:
        template = L1_PROMPT
    elif level == 2:
        template = L2_PROMPT
    else:
        template = L3_PROMPT

    prompt = template.format(
        user_prompt=payload.user_prompt or "",
        previous_output=payload.doc,
    )
    redo_output = gemini.generate(prompt)
    return {"redo_output": redo_output}


@app.post("/run_full")
def run_full(payload: AuditRequest):
    user_prompt = payload.user_prompt or payload.doc
    draft = gemini.generate(user_prompt)
    trail = [{"stage": "initial", "text": draft}]
    audit_info = audit(AuditRequest(doc=draft, user_prompt=user_prompt))
    retries = 0

    while audit_info.risk_score >= 50 and retries < MAX_REDO:  # MEDIUM or higher risk
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
        "risk": audit_info.dict(),
    }
    return {"final": final, "audit_log": log, "trail": trail}
