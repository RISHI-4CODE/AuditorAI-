from typing import Dict, List

def aggregate(pii: Dict[str, list], toxicity: float, hallucination: float) -> tuple[int, list[str], str]:
    issues: List[str] = []
    weight = 0.0

    if pii:
        issues.append("pii_detected")
        weight += 0.5
        if any(k in pii for k in ["credit_card", "api_key_like", "aadhaar_like"]):
            weight += 0.2  # more severe PII

    if toxicity > 0.4:
        issues.append("toxicity_bias")
        weight += min(0.4, toxicity)

    if hallucination > 0.4:
        issues.append("hallucination")
        weight += min(0.4, hallucination)

    # normalize to 0..100
    risk_score = int(min(100, round(weight * 100)))
    tier = "low"
    if risk_score >= 90:
        tier = "high"
    elif risk_score >= 50:
        tier = "medium"

    return risk_score, issues, tier
