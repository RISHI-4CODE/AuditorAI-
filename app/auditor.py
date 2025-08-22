# app/auditor.py
"""
Audit pipeline: runs checks for PII, bias/toxicity, hallucinations, and harmfulness.
Keeps it lean and focused for hackathon demo.
"""

from typing import Dict, Any
from app.models import AuditResult
from audit_checks.pii import detect_pii
from audit_checks.bias import detect_bias_toxicity
from audit_checks.logistic import HarmfulClassifier
from audit_checks.hallucination import HallucinationClassifier

# Initialize ML classifiers (singleton style)
_harmful_clf = HarmfulClassifier()
_hallu_clf = HallucinationClassifier()

def run_audits(response_text: str, context: str = "") -> AuditResult:
    """
    Run all audits on a given response text.
    Returns an AuditResult with outcome, reasons, and findings.
    """
    findings: Dict[str, Any] = {}
    reasons: list[str] = []
    outcome = "PASS"

    # --- PII Audit ---
    pii_findings = detect_pii(response_text)
    if pii_findings:
        findings["pii"] = pii_findings
        reasons.append("Contains potential PII")
        if outcome == "PASS":
            outcome = "FLAG"

    # --- Bias / Toxicity Audit ---
    bias_findings = detect_bias_toxicity(response_text)
    if bias_findings:
        findings["bias"] = bias_findings
        reasons.append("Bias/toxicity detected")
        if outcome == "PASS":
            outcome = "FLAG"

    # --- Harmfulness Audit (ML classifier) ---
    harmful_prob = _harmful_clf.predict_proba(response_text)
    findings["harmful_ml"] = {"probability": harmful_prob}
    if harmful_prob >= 0.8:
        reasons.append(f"ML harmful classifier flagged (p={harmful_prob:.2f})")
        outcome = "FAIL"
    elif harmful_prob >= 0.5 and outcome == "PASS":
        reasons.append(f"ML harmful classifier suspicious (p={harmful_prob:.2f})")
        outcome = "FLAG"

    # --- Hallucination Audit ---
    hallu_label, hallu_conf = _hallu_clf.predict(response_text, context)
    findings["hallucination"] = {"label": hallu_label, "confidence": hallu_conf}
    if hallu_label == "FAIL":
        reasons.append(f"Hallucination check failed (conf={hallu_conf:.2f})")
        outcome = "FAIL"
    elif hallu_label == "FLAG" and outcome == "PASS":
        reasons.append(f"Possible hallucination (conf={hallu_conf:.2f})")
        outcome = "FLAG"

    # --- Risk Score ---
    # Simple heuristic: max of all contributing risks (scaled 0–100)
    scores = [harmful_prob, hallu_conf]
    if pii_findings: scores.append(0.7)
    if bias_findings: scores.append(0.6)
    risk_score = int(max(scores) * 100)

    return AuditResult(
        outcome=outcome,
        reasons=reasons,
        findings=findings,
        original=response_text,
        cleaned=response_text,  # cleaning/redo handled at orchestration level
        risk_score=risk_score
    )
