import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAdapter:
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            resp = genai.GenerativeModel(self.model).generate_content(prompt)
            return resp.text.strip() if resp and resp.text else ""
        except Exception as e:
            print("[GeminiAdapter] generate error:", e)
            return ""
