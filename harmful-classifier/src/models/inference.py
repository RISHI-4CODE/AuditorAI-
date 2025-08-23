from pathlib import Path
import joblib
import yaml

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]   # harmful-classifier/
ROOT_DIR = BASE_DIR.parent                       # AI AUDITOR/
CONFIG_PATH = BASE_DIR / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

MODELS_DIR = ROOT_DIR / config["paths"]["models_dir"] / "pii"

# Load trained pipeline
pipeline = joblib.load(MODELS_DIR / "logistic.pkl")


def predict_text(text: str):
    """Return prediction with thresholds (PASS, FLAG, FAIL)."""
    probs = pipeline.predict_proba([text])[0]
    label_map = {0: "PASS", 1: "FLAG", 2: "FAIL"}

    # Get most likely class
    pred_class = pipeline.predict([text])[0]
    pred_label = label_map[pred_class]

    # Apply thresholds
    if probs[2] >= config["thresholds"]["fail"]:   # FAIL strong confidence
        verdict = "FAIL"
    elif probs[1] >= config["thresholds"]["flag"]: # FLAG borderline
        verdict = "FLAG"
    else:
        verdict = "PASS"

    return {
        "text": text,
        "predicted_class": pred_label,
        "probabilities": {label_map[i]: float(p) for i, p in enumerate(probs)},
        "quick_flag": verdict,
    }


if __name__ == "__main__":
    # Demo predictions
    samples = [
        "You are a great friend!",
        "My phone number is 9876543210",
        "Credit card 4111-1111-1111-1111",
    ]
    for s in samples:
        result = predict_text(s)
        print("\n---")
        print(f"Input: {s}")
        print(f"Prediction: {result['predicted_class']}")
        print(f"Quick flag: {result['quick_flag']}")
        print(f"Probabilities: {result['probabilities']}")
