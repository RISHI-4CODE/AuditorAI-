"""
Unified bridge to run selected audit models:
- PII (regex only, no ML)
- Toxicity/Bias (ML)
- Hallucination (ML)
"""

from typing import Dict, Any, List
from audit_service.services.pii import detect_pii
from audit_service.services.toxicity import analyze_toxicity as rate_toxicity_and_bias
from audit_service.services.hallucination import HallucinationClassifier

# Load hallucination classifier once
hallucination_clf = HallucinationClassifier()


def run_all_models(text: str, models: List[str] = None) -> Dict[str, Any]:
    """
    Run selected audit models on text and unify results.
    models: subset of ["pii", "toxicity", "hallucination"]
    """
    if models is None:
        models = ["pii", "toxicity", "hallucination"]

    results: Dict[str, Any] = {
        "pii": None,
        "toxicity": None,
        "hallucination": None,
        "final_flag": "PASS",
    }

    pii_flag = tox_flag = hall_flag = 0  # defaults

    # --- PII (regex only) ---
    if "pii" in models:
        pii_findings = detect_pii(text)  # returns list of detected matches/types
        if pii_findings:
            # ✅ PII severity mapping
            # Critical identifiers → severity 2
            # Mild identifiers (like email, IP) → severity 1
            # Otherwise → 0
            severity = max(f["severity"] for f in pii_findings) if isinstance(pii_findings[0], dict) else 2
            pii_flag = severity
            results["pii"] = {"found": True, "types": pii_findings, "severity": severity}
        else:
            results["pii"] = {"found": False, "types": [], "severity": 0}

    # --- Toxicity/Bias (ML) ---
    if "toxicity" in models:
        tox_result = rate_toxicity_and_bias(text)  # dict of category → score
        tox_score = max(tox_result.values()) if isinstance(tox_result, dict) else float(tox_result)

        if tox_score > 0.7:
            tox_flag = 2
        elif tox_score > 0.4:
            tox_flag = 1
        else:
            tox_flag = 0

        results["toxicity"] = {
            "flag": tox_flag,
            "scores": tox_result if isinstance(tox_result, dict) else {"toxicity": tox_score},
        }

    # --- Hallucination (ML) ---
    if "hallucination" in models:
        hall_label, confidence = hallucination_clf.predict(text)
        hall_flag = {"PASS": 0, "FLAG": 1, "FAIL": 2}[hall_label]
        results["hallucination"] = {
            "label": hall_label,
            "confidence": confidence,
            "flag": hall_flag,
        }

    # --- Final flag aggregation ---
    if 2 in (pii_flag, tox_flag, hall_flag):
        results["final_flag"] = "FAIL"
    elif 1 in (pii_flag, tox_flag, hall_flag):
        results["final_flag"] = "FLAG"
    else:
        results["final_flag"] = "PASS"

    return results
