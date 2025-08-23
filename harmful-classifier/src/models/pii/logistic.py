# src/models/pii/train_logistic.py
import os
import json
import joblib
import yaml
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline

# ---------- Load config ----------
BASE_DIR = Path(__file__).resolve().parents[2]   # harmful-classifier/
ROOT_DIR = BASE_DIR.parent                       # AI AUDITOR/
CONFIG_PATH = BASE_DIR / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Paths from config.yaml
DATA_DIR = ROOT_DIR / config["paths"]["data_processed"] / "pii-masking-300k" / "data"
MODELS_DIR = ROOT_DIR / config["paths"]["models_dir"] / "pii"
REPORTS_DIR = ROOT_DIR / config["paths"]["reports_dir"]


os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ---------- Label mapping ----------
FLAG_ENTITIES = {"B-EMAIL", "B-PHONE", "B-USER"}
FAIL_ENTITIES = {"B-CREDITCARD", "B-SSN", "B-ADDRESS", "B-PASSPORT", "B-BANK"}

def map_labels(bio_labels):
    """Convert token BIO labels → class 0=PASS, 1=FLAG, 2=FAIL"""
    entities = set(bio_labels)
    if entities == {"O"}:
        return 0
    if any(ent in FAIL_ENTITIES for ent in entities):
        return 2
    if any(ent in FLAG_ENTITIES for ent in entities):
        return 1
    return 1  # default FLAG

# ---------- Dataset loading ----------
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def load_datasets():
    train = load_jsonl(DATA_DIR / "train.jsonl")
    test = load_jsonl(DATA_DIR / "test.jsonl")

    def convert(samples):
        texts, labels = [], []
        for s in samples:
            texts.append(" ".join(s["mbert_text_tokens"]))
            labels.append(map_labels(s["mbert_bio_labels"]))
        return texts, labels

    X_train, y_train = convert(train)
    X_test, y_test = convert(test)
    return X_train, y_train, X_test, y_test

# ---------- Train + Save ----------
def main():
    print("📂 Loading dataset...")
    X_train, y_train, X_test, y_test = load_datasets()

    print("⚡ Training Logistic Regression (PII PASS/FLAG/FAIL)...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=50000)),
        ("clf", LogisticRegression(max_iter=200, class_weight="balanced")),
    ])
    pipeline.fit(X_train, y_train)

    print("🔍 Evaluating...")
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["PASS", "FLAG", "FAIL"], output_dict=True)

    metrics = {"accuracy": acc, "report": report}
    with open(REPORTS_DIR / "metrics_baseline.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"📑 Metrics saved → {REPORTS_DIR / 'metrics_baseline.json'}")

    # Save model + vectorizer
    joblib.dump(pipeline, MODELS_DIR / "logistic.pkl")
    print(f"💾 Model saved → {MODELS_DIR / 'logistic.pkl'}")

if __name__ == "__main__":
    main()
