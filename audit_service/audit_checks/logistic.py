import os
import pickle
from typing import List
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH_DEFAULT = "models/logistic.pkl"

class HarmfulClassifier:
    def __init__(self, model_path: str = MODEL_PATH_DEFAULT):
        self.model_path = model_path
        self.pipe = None
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    self.pipe = pickle.load(f)
                    print("[HarmfulClassifier] Loaded model from", model_path)
            except Exception as e:
                print("[HarmfulClassifier] Failed loading model:", e)
                self.pipe = None
        else:
            self.pipe = None

    def predict_proba(self, text: str) -> float:
        if not self.pipe:
            # fallback heuristic: basic keywords that are likely harmful
            lowered = text.lower()
            keywords = ["ssn", "credit card", "password", "social security", "bomb", "kill", "hate speech"]
            if any(k in lowered for k in keywords):
                return 0.9
            return 0.01
        try:
            prob = self.pipe.predict_proba([text])[0][1]
            return float(prob)
        except Exception as e:
            print("[HarmfulClassifier] prediction error:", e)
            return 0.01

# Optional: helper to train locally (not used by API automatically)
def train_and_save(texts: List[str], labels: List[int], out_path=MODEL_PATH_DEFAULT):
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1,2))),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    pipe.fit(texts, labels)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        pickle.dump(pipe, f)
    print("Saved logistic model to", out_path)
