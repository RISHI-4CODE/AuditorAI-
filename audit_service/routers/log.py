from fastapi import APIRouter
from audit_service.storage.memory_log import get_all

router = APIRouter()

@router.get("/logs")
def logs():
    return {"items": get_all()}
