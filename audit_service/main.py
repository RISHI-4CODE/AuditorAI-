# audit_service/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Routers
from audit_service.routers import audit, log, full

load_dotenv()

app = FastAPI(title="AI Auditor API")

# ✅ Enable CORS (so the dashboard frontend can call the API later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ in prod, restrict to your dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routers
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(log.router, prefix="/logs", tags=["logs"])
app.include_router(full.router, prefix="/full", tags=["full"])

# ✅ Simple health check
@app.get("/health")
def health():
    return {"status": "ok"}
