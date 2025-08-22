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

    def _extract_text(self, resp) -> str:
        """Normalize Gemini response -> plain string."""
        if not resp:
            return ""
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()
        if hasattr(resp, "candidates") and resp.candidates:
            parts = resp.candidates[0].content.parts
            return "".join(p.text for p in parts if hasattr(p, "text")).strip()
        return ""

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            resp = self.model.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_tokens},
            )
            return self._extract_text(resp)
        except Exception as e:
            print("[GeminiAdapter.generate] error:", e)
            return ""

    def redo(self, text: str, flags: dict, max_tokens: int = 512) -> str:
        """
        Redo response stricter based on audit flags.
        - flags: {"pii": 0/1/2, "bias": 0/1/2, "hallucination": 0/1/2}
        """
        try:
            instructions = []
            if flags.get("pii", 0) > 0:
                instructions.append("Remove all personal data, emails, tokens, or sensitive identifiers.")
            if flags.get("bias", 0) > 0:
                instructions.append("Ensure response is neutral, non-toxic, and unbiased.")
            if flags.get("hallucination", 0) > 0:
                instructions.append("Verify correctness and only include facts that can be validated.")

            # If no issues, fallback to softer improvement
            if not instructions:
                instructions.append("Improve clarity and correctness without altering meaning.")

            prompt = f"{' '.join(instructions)}\n\nOriginal:\n{text}"
            resp = self.model.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_tokens},
            )
            return self._extract_text(resp)
        except Exception as e:
            print("[GeminiAdapter.redo] error:", e)
            return ""
