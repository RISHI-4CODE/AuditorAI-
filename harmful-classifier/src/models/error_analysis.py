import os
import json
import yaml
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import sys

# --- Setup paths ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

DATA_PATH = os.path.join(BASE_DIR, config["paths"]["data_processed"], "personalized_dataset.csv")

# ✅ FIXED: Always point to real models folder
MODELS_DIR = r"C:\Users\admin\Desktop\AI AUDITOR\models"
REPORTS_DIR = os.path.join(BASE_DIR, config["paths"]["reports_dir"])
os.makedirs(REPORTS_DIR, exist_ok=True)

# --- Load model + vectorizer ---
clf = joblib.load(os.path.join(MODELS_DIR, "logistic.pkl"))
vectorizer = joblib.load(os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"))

# --- Load dataset ---
df = pd.read_csv(DATA_PATH)

# Ensure labels are integers
y = df["label"].astype(int).tolist()
X = df["text"].astype(str).tolist()

# --- Split same way as training ---
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=config["training"]["test_size"],
    random_state=config["training"]["random_state"]
)

# --- Vectorize ---
X_test_vec = vectorizer.transform(X_test)

# --- Predictions ---
y_pred = clf.predict(X_test_vec)

# Force predictions to integers too
y_pred = [int(p) for p in y_pred]
y_probs = clf.predict_proba(X_test_vec)


# --- Save misclassified samples ---
misclassified = []
for text, true, pred, probs in zip(X_test, y_test, y_pred, y_probs):
    if true != pred:
        misclassified.append({
            "text": text,
            "true_label": int(true),
            "predicted_label": int(pred),
            "probs": probs.tolist()
        })

mis_path = os.path.join(REPORTS_DIR, "misclassified_samples.csv")
pd.DataFrame(misclassified).to_csv(mis_path, index=False)

# --- Classification report ---
report = classification_report(y_test, y_pred, target_names=["PASS", "FLAG", "FAIL"], digits=3)
with open(os.path.join(REPORTS_DIR, "error_report.txt"), "w") as f:
    f.write(report)

print("=== Classification Report ===")
print(report)
print(f"\n❌ Misclassified samples saved to {mis_path}")

# --- Confusion Matrix ---
cm = confusion_matrix(y_test, y_pred, labels=[0,1,2])
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["PASS","FLAG","FAIL"], yticklabels=["PASS","FLAG","FAIL"])
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix - Logistic Baseline")
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "confusion_matrix_error_analysis.png"))
print(f"📊 Confusion matrix saved to {REPORTS_DIR}/confusion_matrix_error_analysis.png")
