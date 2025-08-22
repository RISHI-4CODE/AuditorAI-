# app/auditor.py
"""
Audit pipeline: runs checks for PII, bias/toxicity, and hallucinations.
Keeps it lean and focused for hackathon demo.
"""

from typing import Dict, Any
from app.models import AuditResult
from audit_checks.pii import detect_pii
from audit_checks.bias import detect_bias_toxicity
from audit_checks.hallucination import HallucinationClassifier

# Initialize ML classifiers (singleton style)
_hallu_clf = HallucinationClassifier()

def run_audits(response_text: str, context: str = "") -> AuditResult:
    """
    Run all audits on a given response text.
    Returns an AuditResult with outcome, reasons, findings, and flags.
    """
    findings: Dict[str, Any] = {}
    flags: Dict[str, int] = {}
    reasons: list[str] = []
    outcome = "PASS"

    # --- PII Audit ---
    pii_findings = detect_pii(response_text)
    if pii_findings:
        findings["pii"] = pii_findings
        reasons.append("Contains potential PII")
        flags["pii"] = 2 if any("token" in f.lower() for f in pii_findings) else 1
        if outcome == "PASS":
            outcome = "FLAG"
    else:
        flags["pii"] = 0

    # --- Bias / Toxicity Audit ---
    bias_findings = detect_bias_toxicity(response_text)
    if bias_findings:
        findings["bias"] = bias_findings
        reasons.append("Bias/toxicity detected")
        flags["bias"] = 2 if any("toxic" in f.lower() for f in bias_findings) else 1
        if outcome == "PASS":
            outcome = "FLAG"
    else:
        flags["bias"] = 0

    # --- Hallucination Audit ---
    hallu_label, hallu_conf = _hallu_clf.predict(response_text, context)
    findings["hallucination"] = {"label": hallu_label, "confidence": hallu_conf}
    if hallu_label == "FAIL":
        reasons.append(f"Hallucination check failed (conf={hallu_conf:.2f})")
        flags["hallucination"] = 2
        outcome = "FAIL"
    elif hallu_label == "FLAG":
        reasons.append(f"Possible hallucination (conf={hallu_conf:.2f})")
        flags["hallucination"] = 1
        if outcome == "PASS":
            outcome = "FLAG"
    else:
        flags["hallucination"] = 0

    # --- Risk Score ---
    # Simple heuristic: map flags to severity and take max
    # pii/bias/hallucination all contribute
    severity_map = {0: 0.0, 1: 0.5, 2: 0.9}
    scores = [
        severity_map[flags["pii"]],
        severity_map[flags["bias"]],
        severity_map[flags["hallucination"]],
    ]
    risk_score = int(max(scores) * 100)

    return AuditResult(
        outcome=outcome,
        reasons=reasons,
        findings=findings,
        flags=flags,
        original=response_text,
        cleaned=None,  # cleaning now handled by GeminiAdapter
        risk_score=risk_score,
    )

