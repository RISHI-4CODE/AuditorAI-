# audit_service/adapters/gemini_adapter.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from portia import tool

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

@tool(name="gemini.redo", description="Redo AI response with stricter safety prompt")
def redo_response(text: str, instructions: str, max_tokens: int = 512) -> str:
    """
    Portia tool: re-generate a safer response using Gemini.
    """
    try:
        prompt = f"{instructions}\n\nOriginal:\n{text}"
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)
        return resp.text.strip() if resp and resp.text else ""
    except Exception as e:
        print("[GeminiRedo] error:", e)
        return ""
