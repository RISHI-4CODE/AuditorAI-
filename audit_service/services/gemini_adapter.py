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
    Thin wrapper around Google Gemini API to generate and sanitize responses.
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

    def sanitize(self, text: str, flags: dict, findings: dict, max_tokens: int = 512) -> str:
        """
        Use Gemini to clean the text based on audit flags.
        - pii: mask sensitive data
        - bias: rephrase/remove toxic terms
        - hallucination: correct or clearly mark unverifiable content
        """
        instructions = [
            "You are an auditing assistant.",
            "You MUST always return a corrected version of the text when flags are raised.",
            "Do not repeat the same text — actively edit it based on the issues.",
            "Be concise and keep the original meaning when possible.",
            "",
            "Rules:"
        ]

        if flags.get("pii", 0) > 0:
            instructions.append("-Replace emails with <EMAIL>, phone numbers with <PHONE_NUMBER>, etc.")
        if flags.get("bias", 0) > 0:
            instructions.append("- Remove or rephrase toxic/bias language into neutral tone.")
        if flags.get("hallucination", 0) > 0:
            instructions.append(
                "- If there are factual errors or unverifiable claims, correct them if you know the fact. "
                "Otherwise, explicitly mark them as 'uncertain' or 'unverified'."
            )

        prompt = "\n".join(instructions) + f"\n\nOriginal:\n{text}\n\nCleaned (corrected):"

        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip() if resp and resp.text else text
        except Exception as e:
            print("[GeminiAdapter.sanitize] error:", e)
            return text
