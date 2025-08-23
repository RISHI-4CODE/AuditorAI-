import wikipedia
from typing import Tuple

class HallucinationClassifier:
    def __init__(self):
        # You can adjust language if needed
        wikipedia.set_lang("en")

    def predict(self, response_text: str, context: str = "") -> Tuple[str, float]:
        """
        Check if response_text is supported by Wikipedia.
        Returns (label, confidence) where label ∈ {PASS, FLAG, FAIL}.
        """

        if not response_text.strip():
            return "PASS", 0.0  # nothing to check

        sentences = [s.strip() for s in response_text.split(".") if s.strip()]
        supported, unsupported = 0, 0

        for sent in sentences:
            try:
                # Search Wikipedia for each sentence
                results = wikipedia.search(sent, results=2)
                if not results:
                    unsupported += 1
                else:
                    supported += 1
            except Exception:
                unsupported += 1  # if API fails, count as unsupported

        total = supported + unsupported
        if total == 0:
            return "PASS", 0.0

        support_ratio = supported / total

        # Label decision
        if support_ratio > 0.7:
            return "PASS", support_ratio
        elif support_ratio > 0.4:
            return "FLAG", support_ratio
        else:
            return "FAIL", support_ratio
