# harmful-classifier/src/models/inference.py
import re
from pathlib import Path
import yaml

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]   # harmful-classifier/
CONFIG_PATH = BASE_DIR / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# ===============================
# Regex patterns for PII
# ===============================
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\b\+?[0-9][0-9\-\(\) ]{7,}[0-9]\b")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def predict_text(text: str):
    """
    Simple regex-based PII detector.
    Returns severity levels:
      0 = PASS (no PII)
      1 = FLAG (possible weak PII, e.g. phone)
      2 = FAIL (high-risk PII like credit cards/emails)
    """
    if CREDIT_CARD_REGEX.search(text):
        severity = 2
    elif EMAIL_REGEX.search(text):
        severity = 2
    elif PHONE_REGEX.search(text):
        severity = 1
    else:
        severity = 0

    return {
        "text": text,
        "severity": severity,
        "findings": {
            "email": bool(EMAIL_REGEX.search(text)),
            "phone": bool(PHONE_REGEX.search(text)),
            "credit_card": bool(CREDIT_CARD_REGEX.search(text)),
        },
    }


if __name__ == "__main__":
    # Demo predictions
    samples = [
        "You are a great friend!",
        "My phone number is 9876543210",
        "Credit card 4111-1111-1111-1111",
        "Email me at test@example.com",
    ]
    for s in samples:
        result = predict_text(s)
        print("\n---")
        print(f"Input: {s}")
        print(f"Severity: {result['severity']}")
        print(f"Findings: {result['findings']}")
