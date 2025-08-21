# storage/models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from storage.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    outcome = Column(String, index=True)
    reasons = Column(JSON)
    findings = Column(JSON)
    original = Column(String)
    cleaned = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
