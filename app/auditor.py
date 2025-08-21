# app/auditor.py
from typing import Dict, Any
from app.models import AuditResult
from audit_checks.pii import detect_pii, sanitize_summary
from audit_checks.security import detect_security, summarize_security
from audit_checks.data_quality import detect_data_quality, summarize_quality
from audit_checks.bias import detect_bias_toxicity, summarize_bias

def run_audits(response_text: str, context: str = "") -> AuditResult:
    """
    Run all audits on the given response text.
    Returns an AuditResult with outcome, reasons, findings, and risk score.
    """
    findings: Dict[str, Any] = {}
    reasons: list[str] = []
    outcome = "PASS"
    risk_score = 0  # Portia needs numeric score to drive YAML logic

    # --- Security Audit (hard FAIL) ---
    security_findings = detect_security(response_text)
    if security_findings:
        findings["security"] = security_findings
        reasons.append(summarize_security(security_findings))
        outcome = "FAIL"
        risk_score = max(risk_score, 95)  # security → critical

    # --- PII Audit (FLAG) ---
    pii_findings = detect_pii(response_text)
    if pii_findings:
        findings["pii"] = pii_findings
        reasons.append(sanitize_summary(pii_findings))
        if outcome == "PASS":
            outcome = "FLAG"
        risk_score = max(risk_score, 70)

    # --- Bias / Toxicity Audit (FLAG) ---
    bias_findings = detect_bias_toxicity(response_text)
    if bias_findings:
        findings["bias"] = bias_findings
        reasons.append(summarize_bias(bias_findings))
        if outcome == "PASS":
            outcome = "FLAG"
        risk_score = max(risk_score, 60)

    # --- Data Quality Audit (FLAG) ---
    dq_findings = detect_data_quality(response_text, context)
    if dq_findings:
        findings["data_quality"] = dq_findings
        reasons.append(summarize_quality(dq_findings))
        if outcome == "PASS":
            outcome = "FLAG"
        risk_score = max(risk_score, 55)

    return AuditResult(
        outcome=outcome,
        reasons=reasons,
        findings=findings,
        original=response_text,
        cleaned=response_text if outcome == "PASS" else None,
        risk_score=risk_score
    )
