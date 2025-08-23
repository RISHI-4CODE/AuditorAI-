import os
import json
import joblib
import yaml
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

# ---------- Dataset loading ----------
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def load_datasets():
    train = load_jsonl(DATA_DIR / "train_preprocessed.jsonl")
    test = load_jsonl(DATA_DIR / "test_preprocessed.jsonl")

    def convert(samples):
        texts, labels = [], []
        for s in samples:
            texts.append(" ".join(s["mbert_text_tokens"]))
            # severity will already be in the privacy_mask field
            severities = [m.get("severity", 0) for m in s.get("privacy_mask", [])]
            label = max(severities) if severities else 0  # pick max severity
            labels.append(label)
        return texts, labels

    X_train, y_train = convert(train)
    X_test, y_test = convert(test)
    return X_train, y_train, X_test, y_test

# ---------- Train + Save ----------
def main():
    print("📂 Loading dataset...")
    X_train, y_train, X_test, y_test = load_datasets()

    print("⚡ Training Logistic Regression (PII severity: 0=mild, 1=sensitive, 2=critical)...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=50000)),
        ("clf", LogisticRegression(max_iter=300, class_weight="balanced", multi_class="auto")),
    ])
    pipeline.fit(X_train, y_train)

    print("🔍 Evaluating...")
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    report = classification_report(
        y_test,
        y_pred,
        labels=[0, 1, 2],
        target_names=["MILD", "SENSITIVE", "CRITICAL"],
        output_dict=True,
        zero_division=0
    )

    metrics = {"accuracy": acc, "report": report}
    with open(REPORTS_DIR / "pii_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"📑 Metrics saved → {REPORTS_DIR / 'pii_metrics.json'}")

    # Save model
    joblib.dump(pipeline, MODELS_DIR / "pii_severity.pkl")
    print(f"💾 Model saved → {MODELS_DIR / 'pii_severity.pkl'}")

if __name__ == "__main__":
    main()