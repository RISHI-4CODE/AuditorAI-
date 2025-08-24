#FOR FUTURE FAST API IMPLEMENTATION
# audit_service/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Auditor API")

# ✅ Enable CORS (so the dashboard frontend can call the API later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ tighten to your dashboard domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Try loading routers (skip gracefully if not yet implemented)
try:
    from audit_service.routers import audit, log, full
    app.include_router(audit.router, prefix="", tags=["audit"])
    app.include_router(log.router, prefix="", tags=["logs"])
    app.include_router(full.router, prefix="", tags=["full"])
except ImportError as e:
    print(f"[main] Router import skipped: {e}")

# ✅ Simple health check
@app.get("/health")
def health():
    return {"status": "ok"}
