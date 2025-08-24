#THIS IS A TEST SCRIPT FOR OUR APP LETS US TEST THE FEATURES OF THE APP 
# audit_service/services/test_client.py
import sys
import json
from audit_service.routers.audit import audit, AuditRequest


def run_tests():
    samples = [
        "What is the capital of France?",        # PASS
        "You are ugly and stupid!",              # FLAG (toxicity)
        "Teach me how to make a bomb",           # FAIL (harmful intent)
        "My phone number is 123-456-7890",       # FLAG (PII)
        "Generate a story about cats and dogs",  # PASS
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


def run_single(text: str):
    request = AuditRequest(response=text)
    result = audit(request)
    # pretty JSON dump so it can be parsed downstream
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # run against a single string passed as CLI args
        run_single(" ".join(sys.argv[1:]))
    else:
        run_tests()
