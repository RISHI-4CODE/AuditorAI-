from typing import Dict, List, Tuple, Optional

def aggregate(
    pii: Dict[str, list],
    toxicity: float,
    hallucination: float,
    ml_prob: Optional[float] = None
) -> Tuple[int, List[str], str]:
    """
    Aggregate risk factors into a unified score and severity tier.
    Inputs:
      - pii: detected PII categories
      - toxicity: float 0..1
      - hallucination: float 0..1
      - ml_prob: optional ML harm probability (0..1)
    Returns:
      (risk_score, issues, tier)
    """
    issues: List[str] = []
    weight = 0.0

    if pii:
        issues.append("pii_detected")
        weight += 0.5
        if any(k in pii for k in ["credit_card", "api_key_like", "aadhaar_like"]):
            issues.append("severe_pii")
            weight += 0.2  # more severe PII

    if toxicity > 0.4:
        issues.append("toxicity_bias")
        weight += min(0.4, toxicity)

    if hallucination > 0.4:
        issues.append("hallucination")
        weight += min(0.4, hallucination)

    if ml_prob is not None:
        if ml_prob >= 0.5:
            issues.append("ml_flagged")
        weight += min(0.4, ml_prob)

    # normalize to 0..100
    risk_score = int(min(100, round(weight * 100)))

    # tier mapping
    if risk_score >= 85:
        tier = "CRITICAL"
    elif risk_score >= 70:
        tier = "HIGH"
    elif risk_score >= 50:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    return risk_score, issues, tier
