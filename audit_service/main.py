import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from adapters.gemini_adapter import GeminiAdapter
from audit_checks.pii import detect_pii, sanitize_summary
from audit_checks.logistic import HarmfulClassifier
from audit_checks.prompts import L1_PROMPT, L2_PROMPT, L3_PROMPT
import time
from typing import List, Dict, Optional


load_dotenv()

app = FastAPI(title="AuditorAgent Audit Service")

# Initialize adapters / models
gemini = GeminiAdapter(api_key=os.getenv("GEMINI_API_KEY"))
classifier = HarmfulClassifier(model_path=os.getenv("LOGISTIC_MODEL_PATH", "models/logistic.pkl"))

MAX_REDO = int(os.getenv("MAX_REDO", "3"))

# Request/response models
class AuditRequest(BaseModel):
    text: str
    user_prompt: Optional[str] = None
    context: Optional[Dict[str,Any]] = None

class RedoRequest(BaseModel):
    user_prompt: str
    previous_output: str
    flags: List[str]
    redo_level: int
    context: Optional[Dict[str,Any]] = None

# Helper: aggregate quick checks
def run_quick_checks(text: str) -> Dict[str,Any]:
    # logistic classifier probability
    prob = classifier.predict_proba(text)
    pii_findings = detect_pii(text)
    # quick heuristic flags
    flags = []
    if prob >= 0.5:
        flags.append("ML_HARM_PROB")
    if pii_findings:
        flags.append("PII")
    # For simplicity: we treat ML prob >= 0.85 as CRITICAL
    return {
        "prob_harm": float(prob),
        "pii": pii_findings,
        "flags": flags
    }

# Aggregate -> risk score/bucket
def aggregate_quick(result: Dict[str,Any]) -> Dict[str,Any]:
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
    else:
        bucket = "LOW"
    return {"risk_score": score, "bucket": bucket, "flags": result["flags"], "pii_summary": sanitize_summary(result["pii"])}

@app.post("/audit")
def audit(payload: AuditRequest):
    text = payload.text or ""
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")
    quick = run_quick_checks(text)
    agg = aggregate_quick(quick)

    # For bias/toxicity/hallucination we can call Gemini lightweight classifiers if needed.
    # For speed we return current aggregation.
    resp = {
        "risk_score": agg["risk_score"],
        "bucket": agg["bucket"],
        "flags": agg["flags"],
        "pii_summary": agg["pii_summary"],
        "prob_harm": agg["prob_harm"]
    }
    return resp

@app.post("/redo")
def redo(payload: RedoRequest):
    # Constructs strict prompt based on retry level and flags and calls Gemini to rewrite
    level = int(payload.redo_level)
    if level <= 1:
        template = L1_PROMPT
    elif level == 2:
        template = L2_PROMPT
    else:
        template = L3_PROMPT

    prompt = template.format(user_prompt=payload.user_prompt, previous_output=payload.previous_output)
    # Use Gemini to rewrite safely
    redo_output = gemini.generate(prompt)
    return {"redo_output": redo_output}

# Convenience endpoint to run full generate->audit->redo loop locally (optional)
@app.post("/run_full")
def run_full(payload: AuditRequest):
    """
    This endpoint simulates: given a user prompt, call Gemini to generate,
    audit the output, auto-redo if needed (up to MAX_REDO) and return final output + audit trail.
    """
    user_prompt = payload.user_prompt or payload.text
    # 1) generate a draft
    draft = gemini.generate(user_prompt)
    trail = [{"stage": "initial", "text": draft}]
    audit_info = audit(AuditRequest(text=draft, user_prompt=user_prompt))
    retries = 0
    while audit_info["bucket"] != "LOW" and retries < MAX_REDO:
        retries += 1
        redo_resp = redo(RedoRequest(user_prompt=user_prompt, previous_output=draft, flags=audit_info["flags"], redo_level=retries))
        draft = redo_resp["redo_output"]
        trail.append({"stage": f"redo_{retries}", "text": draft})
        audit_info = audit(AuditRequest(text=draft, user_prompt=user_prompt))
        time.sleep(0.2)
    # If still not safe, return fallback
    if audit_info["bucket"] != "LOW":
        final = "⚠️ I’m unable to provide a safe response to that request."
        outcome = "FALLBACK"
    else:
        final = draft
        outcome = "PASS"

    # Build sanitized log (do NOT include raw flagged text if PII was present)
    log = {
        "user_prompt": user_prompt,
        "outcome": outcome,
        "attempts": retries,
        "risk": audit_info
    }
    return {"final": final, "audit_log": log, "trail": trail}
