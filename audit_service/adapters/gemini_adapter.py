# audit_service/adapters/gemini_adapter.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY")
genai.configure(api_key=API_KEY)


class GeminiAdapter:
    """
    Thin wrapper around Google Gemini API to generate and redo responses.
    """

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip() if resp and resp.text else ""
        except Exception as e:
            print("[GeminiAdapter.generate] error:", e)
            return ""

    def redo(self, text: str, instructions: str, max_tokens: int = 512) -> str:
        try:
            prompt = f"{instructions}\n\nOriginal:\n{text}"
            resp = self.model.generate_content(prompt)
            return resp.text.strip() if resp and resp.text else ""
        except Exception as e:
            print("[GeminiAdapter.redo] error:", e)
            return ""
