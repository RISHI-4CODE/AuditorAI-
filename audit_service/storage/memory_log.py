from typing import List, Dict, Any
from datetime import datetime

_LOG: List[Dict[str, Any]] = []

def add(entry: Dict[str, Any]):
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    _LOG.append(entry)

def get_all() -> List[Dict[str, Any]]:
    return list(reversed(_LOG))[:200]  # latest 200
