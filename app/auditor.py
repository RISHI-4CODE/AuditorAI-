# app/auditor.py
"""
Audit pipeline: runs checks for PII, bias/toxicity, and hallucinations.
Keeps it lean and consistent with Findings model.
"""

from typing import Dict, Any
from app.models import AuditResult
from audit_checks.pii import detect_pii
from audit_service.ml_models.bias_classifier import BiasToxicityClassifier
from audit_checks.hallucination import HallucinationClassifier
from audit_checks_prompt import L1_PROMPT, L2_PROMPT, L3_PROMPT

# Initialize ML classifiers (singleton style)
_hallu_clf = HallucinationClassifier()
_bias_clf = BiasToxicityClassifier()
# assume _pii_clf already exists elsewhere and injected here


def run_audits(response_text: str, context: str = "", user_prompt: str = "") -> AuditResult:
    """
    Run all audits on a given response text.
    Returns an AuditResult with outcome, reasons, findings, and flags.
    """
    findings: Dict[str, Any] = {}
    flags: Dict[str, int] = {}
    reasons: list[str] = []
    outcome = "PASS"

    # --- PII Audit ---
    pii_findings = detect_pii(response_text) or {}
    findings["pii"] = pii_findings

    if pii_findings:
        reasons.append("Contains potential PII (regex)")
        flags["pii"] = 2 if "api_key_like" in pii_findings or "credit_card" in pii_findings else 1
        if outcome == "PASS":
            outcome = "FLAG"
    else:
        # Run ML model for PII only if regex is clear
        ml_label, ml_conf = _pii_clf.predict(response_text)
        if ml_label != "PASS":
            findings["pii_ml"] = {"label": ml_label, "confidence": ml_conf}
            reasons.append(f"ML PII model flagged text ({ml_label}, conf={ml_conf:.2f})")
            flags["pii"] = 1 if ml_label == "FLAG" else 2
            if outcome == "PASS":
                outcome = ml_label
        else:
            flags["pii"] = 0

    # --- Bias / Toxicity Audit ---
    bias_label, bias_conf, bias_details = _bias_clf.predict(response_text)
    findings["bias"] = bias_details
    if bias_label in ("FLAG", "FAIL"):
        reasons.append("Bias/toxicity detected")
        flags["bias"] = 2 if bias_label == "FAIL" else 1
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
    severity_map = {0: 0.0, 1: 0.5, 2: 0.9}
    scores = [
        severity_map[flags["pii"]],
        severity_map[flags["bias"]],
        severity_map[flags["hallucination"]],
    ]
    risk_score = int(max(scores) * 100)

    # --- Choose Rewrite Prompt (L1/L2/L3) ---
    max_flag = max(flags.values())
    if max_flag == 0:
        cleaned = response_text
    elif max_flag == 1:
        cleaned = L1_PROMPT.format(user_prompt=user_prompt, previous_output=response_text)
    else:  # max_flag == 2
        cleaned = L2_PROMPT.format(user_prompt=user_prompt, previous_output=response_text)
        # If you want to escalate FAIL to ultra-strict:
        if outcome == "FAIL":
            cleaned = L3_PROMPT.format(user_prompt=user_prompt, previous_output=response_text)

    return AuditResult(
        outcome=outcome,
        reasons=reasons,
        findings=findings,
        flags=flags,
        original=response_text,
        cleaned=cleaned,
        risk_score=risk_score,
    )
