import os
import requests
from dotenv import load_dotenv

# Load from .env
load_dotenv()

PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")
PORTIA_REWRITE_URL = os.getenv("PORTIA_REWRITE_URL", "https://api.portia.ai/v1/rewrite")

# audit_service/services/portia_client.py

import os
import requests
from dotenv import load_dotenv

# Load env vars from .env if not already loaded
load_dotenv()

PORTIA_API_KEY = os.getenv("PORTIA_API_KEY")
PORTIA_REWRITE_URL = os.getenv("PORTIA_REWRITE_URL", "https://api.portia.ai/v1/rewrite")


def rewrite_with_portia(text: str, issues: list[str]) -> str:
    """
    Call Portia API to rewrite unsafe or flagged text.
    Smarter: adapts rewrite instructions based on triggered issues.
    """
    if not PORTIA_API_KEY:
        raise RuntimeError("❌ PORTIA_API_KEY is missing. Set it in .env")

    # Build targeted instructions for Portia
    instructions = []
    if "pii" in issues:
        instructions.append("Remove or mask personal data (emails, phone numbers, IDs).")
    if "bias" in issues:
        instructions.append("Rephrase text to be respectful, neutral, and non-toxic.")
    if "hallucination" in issues:
        instructions.append("Rewrite to remove unverified or false claims. Stick to facts.")

    # Fallback instruction
    if not instructions:
        instructions = ["Ensure the text is safe and compliant."]

    payload = {
        "text": text,
        "issues": issues,
        "instructions": " ".join(instructions),
    }

    headers = {
        "Authorization": f"Bearer {PORTIA_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(PORTIA_REWRITE_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("rewritten_text", text)  # fallback if Portia gives nothing
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Portia rewrite failed: {e}")
        return text