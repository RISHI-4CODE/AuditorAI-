# audit_service/services/logistic_client.py
import os
from audit_service.audit_checks.logistic import HarmfulClassifier

_model_path = os.getenv("LOGISTIC_MODEL_PATH", "models/logistic.pkl")
_classifier = HarmfulClassifier(model_path=_model_path)

def score_harm_probability(text: str) -> float:
    """Return probability [0,1] that text is harmful."""
    return float(_classifier.predict_proba(text))
