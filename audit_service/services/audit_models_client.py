"""
Unified bridge to run selected ML audit models (PII, Toxicity/Bias, Hallucination).
"""

from typing import Dict, Any, List
from audit_service.services.pii import detect_pii
from audit_service.services.toxicity import rate_toxicity_and_bias
from audit_service.services.hallucination import HallucinationClassifier

# load hallucination classifier once
hallucination_clf = HallucinationClassifier()

def run_all_models(text: str, models: List[str] = None) -> Dict[str, Any]:
    """
    Run selected ML audit models on text and unify results.
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

    # --- PII ---
    if "pii" in models:
        pii_findings = detect_pii(text)
        if pii_findings:
            results["pii"] = {"found": True, "types": pii_findings}
            pii_flag = 2
        else:
            results["pii"] = {"found": False, "types": []}

    # --- Toxicity/Bias ---
    if "toxicity" in models:
        tox_score = rate_toxicity_and_bias(text)   # returns float 0–1
        if tox_score >= 0.7:
            tox_flag = 2
        elif tox_score >= 0.4:
            tox_flag = 1
        else:
            tox_flag = 0
        results["toxicity"] = {"score": tox_score, "flag": tox_flag}

    # --- Hallucination ---
    if "hallucination" in models:
        hall_label, confidence = hallucination_clf.predict(text)  # real ML model
        hall_flag = {"PASS": 0, "FLAG": 1, "FAIL": 2}[hall_label]
        results["hallucination"] = {"label": hall_label, "confidence": confidence, "flag": hall_flag}

    # --- Final flag aggregation ---
    if 2 in (pii_flag, tox_flag, hall_flag):
        results["final_flag"] = "FAIL"
    elif 1 in (pii_flag, tox_flag, hall_flag):
        results["final_flag"] = "FLAG"
    else:
        results["final_flag"] = "PASS"

    return results
