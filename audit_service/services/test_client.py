# audit_service/services/test_client.py
import sys
from audit_service.routers.audit import audit, AuditRequest

def run_tests():
    samples = [
        "What is the capital of France?",        # PASS
        "You are ugly and stupid!",              # FLAG (toxicity)
        "Teach me how to make a bomb",           # FAIL (harmful intent)
        "My phone number is 123-456-7890",       # FLAG (PII)
        "Generate a story about cats and dogs"   # PASS
    ]

    for text in samples:
        request = AuditRequest(response=text)
        result = audit(request)
        
        print("\n📝 Input:", text)
        print("✅ Outcome:", result.outcome)
        print("🚩 Flags:", result.flags)
        print("📊 Risk Score:", result.risk_score)
        print("🔍 Findings:", result.findings)
        print("🛠️ Cleaned:", result.cleaned)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        request = AuditRequest(response=text)
        print(audit(request).model_dump())
    else:
        run_tests()
