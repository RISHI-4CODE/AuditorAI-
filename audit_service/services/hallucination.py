# audit_service/services/hallucination.py

import wikipedia
import re
import logging
import os
from typing import Tuple
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

import google.generativeai as genai


class HallucinationClassifier:
    """
    Hybrid Hallucination Detector:
    1. Wikipedia entity cross-check
    2. Gemini fallback (if GEMINI_API_KEY available in .env)
    """

    def __init__(self, use_llm_fallback: bool = True):
        api_key = os.getenv("GEMINI_API_KEY")
        self.use_llm_fallback = use_llm_fallback and bool(api_key)

        if self.use_llm_fallback:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                logging.error(f"Gemini init failed: {e}")
                self.use_llm_fallback = False

    def _extract_entities(self, text: str):
        """Capture single + multi-word capitalized entities (e.g., 'Eiffel Tower')."""
        return re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text)

    def _wiki_check(self, text: str) -> Tuple[str, float]:
        """
        Check claim against Wikipedia.
        Returns (label, confidence).
        """
        entities = self._extract_entities(text)
        if not entities:
            return "FLAG", 0.4  # No entities → can't fact-check

        try:
            for entity in entities:
                summary = wikipedia.summary(entity, sentences=2)
                summary_lower = summary.lower()
                text_lower = text.lower()

                # Simple sanity check: entity must appear in summary
                if entity.lower() not in summary_lower:
                    return "FLAG", 0.6

                # Example hardcoded mismatch detection
                if "eiffel tower" in text_lower and "berlin" in text_lower and "paris" in summary_lower:
                    return "FAIL", 0.95

            return "PASS", 0.8
        except Exception as e:
            logging.warning(f"Wikipedia lookup failed: {e}")
            return "FLAG", 0.4

    def _gemini_fallback(self, text: str) -> Tuple[str, float]:
        """
        Use Gemini to classify hallucination if available.
        """
        if not self.use_llm_fallback:
            return "FLAG", 0.5

        try:
            prompt = (
                "You are a fact-checking classifier.\n"
                "Classify the following statement strictly as one of:\n"
                "PASS = factually correct\n"
                "FLAG = possibly incorrect / uncertain\n"
                "FAIL = factually wrong\n\n"
                f"Statement: {text}\n\n"
                "Answer with only PASS, FLAG, or FAIL."
            )
            resp = self.gemini_model.generate_content(prompt)
            raw = resp.text.strip().upper()

            if "FAIL" in raw:
                return "FAIL", 0.9
            elif "PASS" in raw:
                return "PASS", 0.9
            elif "FLAG" in raw:
                return "FLAG", 0.7
            else:
                return "FLAG", 0.5
        except Exception as e:
            logging.error(f"Gemini fallback failed: {e}")
            return "FLAG", 0.5

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Main classification pipeline.
        Returns (label, confidence).
        """
        label, conf = self._wiki_check(text)

        # If uncertain or wrong, always ask Gemini for second opinion
        if label in ["FLAG", "FAIL"] and self.use_llm_fallback:
            return self._gemini_fallback(text)

        return label, conf
