# src/models/train_logistic.py

import joblib
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

from src.data_prep import load_toxigen_data

DATA_PATH = "data/processed/toxigen-data/toxigen.csv"
MODEL_PATH = "models/logistic.pkl"
VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"
REPORT_PATH = "reports/metrics_baseline.json"
CM_PATH = "reports/confusion_matrix_baseline.png"

def main():
    X_train, X_test, y_train, y_test = load_toxigen_data(DATA_PATH)

    # TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Logistic Regression
    clf = LogisticRegression(max_iter=200)
    clf.fit(X_train_tfidf, y_train)

    # Save artifacts
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    # Evaluation
    y_pred = clf.predict(X_test_tfidf)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["PASS","FLAG","FAIL"], yticklabels=["PASS","FLAG","FAIL"])
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.savefig(CM_PATH)
    plt.close()

    print("✅ Training complete. Artifacts saved.")

if __name__ == "__main__":
    main()
