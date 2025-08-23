import os
import joblib
import yaml
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

PROCESSED_DIR = config["paths"]["data_processed"]
MODELS_DIR = config["paths"]["models_dir"]
REPORTS_DIR = config["paths"]["reports_dir"]

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_data():
    # Personalized dataset
    dataset_path = os.path.join(PROCESSED_DIR, "personalized_dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"❌ Dataset not found at {dataset_path}. Run make_personalized_dataset.py first!"
        )

    # Read raw lines safely
    cleaned_rows = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue  # 🚫 skip broken rows with less than 2 params
            text = ",".join(parts[:-1]).strip()
            label = parts[-1].strip()
            if text and label:
                cleaned_rows.append([text, label])

    df = pd.DataFrame(cleaned_rows, columns=["text", "label"])

    # ✅ Keep only valid numeric labels (0,1,2)
    df = df[df["label"].isin(["0", "1", "2"])]

    # ✅ Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["text"], keep="first").reset_index(drop=True)
    after = len(df)
    print(f"🧹 Removed {before - after} duplicate rows → Final dataset size: {after}")

    # ✅ Show class distribution
    print("\n📊 Class distribution after cleaning:")
    print(df["label"].value_counts(normalize=True).round(3) * 100)

    # 🚨 Safety check for stratify
    counts = df["label"].value_counts()
    too_small = counts[counts < 2]
    if not too_small.empty:
        raise ValueError(
            f"❌ Some classes have fewer than 2 samples after cleaning: {too_small.to_dict()}. "
            f"Please regenerate or fix your dataset."
        )

    # Split into train/test
    train_df, test_df = train_test_split(
        df,
        test_size=config["training"]["test_size"],
        random_state=config["training"]["random_state"],
        stratify=df["label"]
    )
    return train_df, test_df



def compute_thresholds(y_true, y_probs, labels):
    """
    Compute thresholds for PASS/FLAG/FAIL using precision calibration.
    """
    thresholds = {}

    # Ensure labels are strings
    labels = [str(l) for l in labels]

    # For FAIL ("2") → pick threshold at 90% precision
    fail_index = labels.index("2")
    fail_probs = y_probs[:, fail_index]
    sorted_idx = np.argsort(fail_probs)[::-1]
    sorted_probs = fail_probs[sorted_idx]
    sorted_true = np.array(y_true)[sorted_idx].astype(str)

    tp, fp = 0, 0
    best_thr = 0.85  # fallback default
    for thr in sorted_probs:
        preds = (fail_probs >= thr).astype(int)
        tp = ((preds == 1) & (sorted_true == "2")).sum()
        fp = ((preds == 1) & (sorted_true != "2")).sum()
        if tp + fp > 0:
            precision = tp / (tp + fp)
            if precision >= 0.9:
                best_thr = float(thr)
                break

    thresholds["FAIL"] = best_thr
    thresholds["FLAG"] = float(best_thr * 0.6)  # midpoint zone
    thresholds["PASS"] = 0.0
    return thresholds



def train_logistic(train_df, test_df):
    # TF-IDF
    vectorizer = TfidfVectorizer(
        ngram_range=(config["training"]["tfidf_ngram_min"], config["training"]["tfidf_ngram_max"]),
        stop_words="english" if config["training"]["use_stop_words"] else None,
    )

    X_train = vectorizer.fit_transform(train_df["text"])
    y_train = train_df["label"]

    X_test = vectorizer.transform(test_df["text"])
    y_test = test_df["label"]

    # Logistic Regression
    clf = LogisticRegression(max_iter=1000, random_state=config["training"]["random_state"])
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    y_probs = clf.predict_proba(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    print("\n📊 Classification Report")
    print(classification_report(y_test, y_pred))

    # Save metrics JSON
    metrics_path = os.path.join(REPORTS_DIR, "metrics_baseline.json")
    with open(metrics_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Saved metrics → {metrics_path}")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots()
    ax.matshow(cm, cmap="Blues")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], va="center", ha="center")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix (Logistic)")
    cm_path = os.path.join(REPORTS_DIR, "confusion_matrix_logistic.png")
    plt.savefig(cm_path)
    print(f"✅ Saved confusion matrix → {cm_path}")

    # Compute thresholds
    thresholds = compute_thresholds(list(y_test), y_probs, clf.classes_.tolist())
    thr_path = os.path.join(REPORTS_DIR, "thresholds.json")
    with open(thr_path, "w") as f:
        json.dump(thresholds, f, indent=2)
    print(f"✅ Saved thresholds → {thr_path}")

    # Save model + vectorizer
    joblib.dump(clf, os.path.join(MODELS_DIR, "logistic.pkl"))
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"))
    print(f"✅ Saved model → {os.path.join(MODELS_DIR, 'logistic.pkl')}")
    print(f"✅ Saved vectorizer → {os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')}")


def main():
    train_df, test_df = load_data()
    train_logistic(train_df, test_df)


if __name__ == "__main__":
    main()
