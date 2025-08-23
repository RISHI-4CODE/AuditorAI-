import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
DATA_PATH = BASE_DIR / "data" / "processed" / "harmful_responses.csv"

# Ensure reports dir exists
REPORTS_DIR.mkdir(exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)
X = df["text"]
y = df["label"]

# Load model + vectorizer
vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
model = joblib.load(MODEL_DIR / "logistic.pkl")

# Transform text
X_vec = vectorizer.transform(X)

# Predictions
y_pred = model.predict(X_vec)

# Metrics
report = classification_report(y, y_pred, target_names=["SAFE", "HARMFUL"], output_dict=True)
cm = confusion_matrix(y, y_pred).tolist()

# Save metrics
metrics_path = REPORTS_DIR / "metrics_baseline.json"
with open(metrics_path, "w") as f:
    json.dump({"classification_report": report, "confusion_matrix": cm}, f, indent=2)

print(f"✅ Saved evaluation metrics to {metrics_path}")

# Save confusion matrix as image
plt.figure(figsize=(5, 4))
plt.imshow(cm, cmap="Blues")
plt.title("Confusion Matrix")
plt.colorbar()
plt.xticks([0, 1], ["SAFE", "HARMFUL"])
plt.yticks([0, 1], ["SAFE", "HARMFUL"])
plt.xlabel("Predicted")
plt.ylabel("True")

for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i][j], ha="center", va="center", color="red")

cm_path = REPORTS_DIR / "confusion_matrix_baseline.png"
plt.savefig(cm_path)
print(f"✅ Saved confusion matrix to {cm_path}")
