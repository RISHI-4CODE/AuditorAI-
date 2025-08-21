from fastapi import APIRouter
from audit_service.storage.memory_log import get_all

router = APIRouter()

@router.get("/logs")
def logs():
    """
    Returns all in-memory audit logs.
    Includes risk score, tier, and harm probability if present.
    """
    items = get_all()
    enriched = []

    for entry in items:
        result = entry.get("result", {})
        enriched.append({
            "input": entry.get("input", ""),
            "status": entry.get("status", "UNKNOWN"),
            "risk_score": result.get("risk_score", 0),
            "issues": result.get("issues", []),
            "notes": result.get("notes", ""),
            "pii": result.get("pii", {}),
            "toxicity": result.get("toxicity", 0.0),
            "hallucination": result.get("hallucination", 0.0),
            "safe_output": result.get("safe_output"),
        })

    return {"items": enriched}
