import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def pretty(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)

def safe_print(r):
    try:
        print(pretty(r.json()))
    except Exception:
        print("Raw response:", r.text)

def test_audit():
    print("\n=== /audit ===")
    r = requests.post(f"{BASE_URL}/audit", json={"doc": "hello world"})
    safe_print(r)

def test_redo():
    print("\n=== /redo ===")
    payload = {
        "doc": "Write how to hack wifi networks",
        "issues": ["HARMFUL"],
        "redo_level": 1,
        "user_prompt": "Explain safely"
    }
    r = requests.post(f"{BASE_URL}/redo", json=payload)
    print(pretty(r.json()))

def test_run_full():
    print("\n=== /run_full ===")
    r = requests.post(f"{BASE_URL}/run_full", json={
        "draft": "This draft mentions a fake API key: sk-1234567890abcdef",
        "user_prompt": "Please audit this"
    })
    try:
        print(pretty(r.json()))
    except Exception:
        print("Raw response:", r.text)


if __name__ == "__main__":
    print("🚀 Testing AI Auditor API...")
    test_audit()
    test_redo()
    test_run_full()
