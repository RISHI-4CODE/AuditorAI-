import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AuditorAgent Audit Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Routers
from audit_service.routers.audit import router as audit_router
from audit_service.routers.logs import router as logs_router
app.include_router(audit_router, prefix="")
app.include_router(logs_router, prefix="")

@app.get("/")
def root():
    return {"status": "ok", "service": "audit"}
