# audit_service/core.py
from typing import Dict, Any
from audit_service.audit_checks.pii import detect_pii, sanitize_summary
from audit_service.audit_checks.bias import detect_bias_toxicity, summarize_bias
from audit_service.audit_checks.data_quality import detect_low_quality, quality_summary
from audit_service.audit_checks.security import detect_security, summarize_security
from audit_service.audit_checks.logistic import HarmfulClassifier

# Initialize ML model once
_classifier = HarmfulClassifier()

def run_audit(response_text: str, context: str = "") -> Dict[str, Any]:
    """
    Run all audits + ML classifier and return a unified result.
    """
    findings: Dict[str, Any] = {}
    reasons: list[str] = []
    outcome = "PASS"
    risk_score = 0

    # --- Security Audit ---
    sec_findings = detect_security(response_text)
    if sec_findings:
        findings["security"] = sec_findings
        reasons.append(summarize_security(sec_findings))
        outcome = "FAIL"
        risk_score += 50  # hard fail weights

    # --- PII Audit ---
    pii_findings = detect_pii(response_text)
    if pii_findings:
        findings["pii"] = pii_findings
        reasons.append(sanitize_summary(pii_findings))
        if outcome == "PASS":
            outcome = "FLAG"
        risk_score += 20

    # --- Bias / Toxicity Audit ---
    bias_findings = detect_bias_toxicity(response_text)
    if bias_findings:
        findings["bias"] = bias_findings
        reasons.append(summarize_bias(bias_findings))
        if outcome == "PASS":
            outcome = "FLAG"
        risk_score += 20

    # --- Data Quality Audit ---
    dq_findings = detect_low_quality(response_text, context)
    if dq_findings:
        findings["data_quality"] = dq_findings
        reasons.append(quality_summary(dq_findings))
        if outcome == "PASS":
            outcome = "FLAG"
        risk_score += 10

    # --- ML Harmful Classifier ---
    ml_score = _classifier.predict_proba(response_text)
    risk_score = min(100, risk_score + int(ml_score * 100))
    if ml_score > 0.7:
        outcome = "FAIL"

    # --- Final result ---
    return {
        "outcome": outcome,  # PASS / FLAG / FAIL
        "risk_score": risk_score,
        "reasons": reasons,
        "findings": findings,
        "original": response_text,
        "cleaned": response_text if outcome == "PASS" else None,
    }
