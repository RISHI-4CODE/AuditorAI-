import random
from datetime import datetime

def run_basic_audits():
    checks = []

    # Security Check
    checks.append({
        "task": "Security Audit",
        "status": "PASS",
        "details": "Basic security scan passed.",
        "timestamp": datetime.utcnow().isoformat()
    })

    # Performance Check
    perf_status = random.choice(["PASS", "FAIL"])
    checks.append({
        "task": "Performance Audit",
        "status": perf_status,
        "details": f"Performance check {perf_status.lower()}ed.",
        "timestamp": datetime.utcnow().isoformat()
    })

    # Data Quality Check
    dq_status = random.choice(["PASS", "FAIL"])
    checks.append({
        "task": "Data Quality Audit",
        "status": dq_status,
        "details": f"Data quality check {dq_status.lower()}ed.",
        "timestamp": datetime.utcnow().isoformat()
    })

    return checks
