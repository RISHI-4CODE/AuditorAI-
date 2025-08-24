# audit_service/services/hallucination.py

import re
import logging
from typing import Tuple
import wikipedia
import os
import google.generativeai as genai


class HallucinationClassifier:
    """
    Hybrid Hallucination Detector (Portia orchestration):
    1. Wikipedia entity cross-check (cheap, deterministic)
    2. Gemini fallback ONLY if uncertain (FLAG)
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
        """Capture capitalized entities (single + multi-word)."""
        return re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text)

    def _wiki_check(self, text: str) -> Tuple[str, int]:
        """
        Check claim against Wikipedia.
        Returns (label, severity) where severity = 0 (PASS), 1 (FLAG), 2 (FAIL).
        """
        entities = self._extract_entities(text)
        if not entities:
            return "FLAG", 1  # no entities → cannot fact-check

        try:
            for entity in entities:
                summary = wikipedia.summary(entity, sentences=2).lower()
                if entity.lower() not in summary:
                    return "FLAG", 1  # mismatch → uncertain

            return "PASS", 0
        except Exception as e:
            logging.warning(f"Wikipedia lookup failed: {e}")
            return "FLAG", 1

    def _gemini_fallback(self, text: str) -> Tuple[str, int]:
        """
        Use Gemini to classify hallucination if available.
        """
        if not self.use_llm_fallback:
            return "FLAG", 1

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
            raw = resp.text.strip().upper() if resp and resp.text else ""

            if raw == "FAIL":
                return "FAIL", 2
            elif raw == "PASS":
                return "PASS", 0
            else:
                return "FLAG", 1
        except Exception as e:
            logging.error(f"Gemini fallback failed: {e}")
            return "FLAG", 1

    def predict(self, text: str) -> Tuple[str, int]:
        """
        Main classification pipeline.
        Returns (label, severity).
        """
        label, severity = self._wiki_check(text)

        # Only escalate to Gemini if wiki was uncertain
        if label == "FLAG" and self.use_llm_fallback:
            return self._gemini_fallback(text)

        return label, severity
