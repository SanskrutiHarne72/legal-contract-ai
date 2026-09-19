"""
train_risk_classifier.py
--------------------------
Trains a Random Forest risk-severity classifier (Module 4) on your
team's hand-labeled data/risk_labeling_batch.csv (produced by
prepare_risk_labeling.py, then filled in manually). Combines:
  - TF-IDF features from the clause text itself
  - the clause category (from the CUAD taxonomy)
  - the rule-based flags from risk_rules.py, as engineered features

This is why the rule-based layer (risk_rules.py) is worth keeping even
after this classifier exists: its flags double as both (a) a
zero-training-data fallback and (b) input features that make the
learned model more sample-efficient, since it doesn't have to
rediscover "sole discretion = risk marker" from scratch off ~200-300
rows.

Usage (only works once risk_label column is filled in):
    python scripts/train_risk_classifier.py
"""
import csv
from pathlib import Path

import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from risk_rules import check_clause_language, ONE_SIDEDNESS_RULES

BASE = Path(__file__).resolve().parent.parent
LABELED_PATH = BASE / "data" / "risk_labeling_batch.csv"
MODEL_PATH = BASE / "models" / "risk_classifier.joblib"
REPORT_PATH = BASE / "models" / "risk_report.txt"

FLAG_NAMES = [name for _, name, _, _ in ONE_SIDEDNESS_RULES]


def load_labeled_data():
    rows = []
    with open(LABELED_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["risk_label"].strip().lower() in ("low", "medium", "high"):
                rows.append(row)
    return rows


def rule_flag_features(text, category):
    """One binary feature per ONE_SIDEDNESS_RULES entry: did it fire?"""
    flags = {f["flag"] for f in check_clause_language(text, category)}
    return [1 if name in flags else 0 for name in FLAG_NAMES]


def main():
    rows = load_labeled_data()
    n_needed = 150
    if len(rows) < n_needed:
        print(f"Only {len(rows)} labeled rows found in {LABELED_PATH} "
              f"(risk_label filled in). Recommend at least {n_needed} before training "
              f"a Random Forest with reasonable per-class support -- have your team "
              f"continue labeling data/risk_labeling_batch.csv, then rerun this script.")
        if len(rows) < 30:
            print("Too few labeled rows to train meaningfully. Stopping.")
            return

    texts = [r["text"] for r in rows]
    categories = [r["category"] for r in rows]
    labels = [r["risk_label"].strip().lower() for r in rows]

    print(f"Training on {len(rows)} hand-labeled clauses")
    label_counts = {l: labels.count(l) for l in set(labels)}
    print(f"Label distribution: {label_counts}")

    # --- Feature 1: TF-IDF over clause text ---
    tfidf = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    X_text = tfidf.fit_transform(texts)

    # --- Feature 2: one-hot clause category ---
    cat_encoder = OneHotEncoder(handle_unknown="ignore")
    X_cat = cat_encoder.fit_transform(np.array(categories).reshape(-1, 1))

    # --- Feature 3: rule-based flag indicators ---
    X_flags = csr_matrix(np.array([rule_flag_features(t, c) for t, c in zip(texts, categories)]))

    X = hstack([X_text, X_cat, X_flags])

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    stratify = y if min(label_counts.values()) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    clf = RandomForestClassifier(n_estimators=300, max_depth=None, class_weight="balanced", random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred, target_names=label_encoder.classes_, zero_division=0
    )

    print(f"\nHeld-out accuracy: {acc:.4f}\n")
    print(report)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": clf,
        "tfidf": tfidf,
        "cat_encoder": cat_encoder,
        "label_encoder": label_encoder,
        "flag_names": FLAG_NAMES,
    }, MODEL_PATH)
    with open(REPORT_PATH, "w") as f:
        f.write(f"Held-out accuracy: {acc:.4f}\n\n{report}")

    print(f"Saved model bundle to {MODEL_PATH}")
    print(f"Saved report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
