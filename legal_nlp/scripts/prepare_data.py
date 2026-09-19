"""
prepare_data.py
----------------
Extracts (clause_text, category_label) pairs from the raw CUAD_v1.json
(SQuAD-style QA format) into a flat CSV usable for training a classical
TF-IDF + SVM clause-type classifier.

CUAD encodes each of the 41 clause categories as a separate "question"
per contract, with the answer(s) being the text span(s) belonging to
that category. This script:
  1. Parses every contract's paragraph/qas structure.
  2. Extracts the category name from the question id
     (format: "<contract_title>__<Category Name>").
  3. Extracts every non-impossible answer span as one training example.
  4. Writes data/clauses_labeled.csv with columns: text, label, source_contract

Usage:
    python scripts/prepare_data.py
"""
import json
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW_PATH = BASE / "data" / "cuad_raw" / "CUADv1.json"
OUT_PATH = BASE / "data" / "clauses_labeled.csv"

MIN_CHARS = 20   # skip tiny/noisy spans
MAX_CHARS = 2000 # skip pathologically long spans (rare parsing artifacts)


def extract_category(qa_id: str) -> str:
    """qa_id looks like '<contract_title>__<Category Name>'."""
    if "__" in qa_id:
        return qa_id.rsplit("__", 1)[1].strip()
    return "Unknown"


def clean_text(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    with open(RAW_PATH, encoding="utf-8") as f:
        cuad = json.load(f)

    rows = []
    skipped_empty, skipped_len = 0, 0

    for contract in cuad["data"]:
        title = contract["title"]
        for para in contract["paragraphs"]:
            for qa in para["qas"]:
                if qa.get("is_impossible", False):
                    continue
                label = extract_category(qa["id"])
                for ans in qa.get("answers", []):
                    text = clean_text(ans.get("text", ""))
                    if not text:
                        skipped_empty += 1
                        continue
                    if len(text) < MIN_CHARS or len(text) > MAX_CHARS:
                        skipped_len += 1
                        continue
                    rows.append({"text": text, "label": label, "source_contract": title})

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "source_contract"])
        writer.writeheader()
        writer.writerows(rows)

    labels = {}
    for r in rows:
        labels[r["label"]] = labels.get(r["label"], 0) + 1

    print(f"Wrote {len(rows)} labeled clause examples to {OUT_PATH}")
    print(f"Skipped: {skipped_empty} empty, {skipped_len} out-of-length-range")
    print(f"Distinct categories: {len(labels)}")
    print("\nTop 10 categories by example count:")
    for label, count in sorted(labels.items(), key=lambda x: -x[1])[:10]:
        print(f"  {label:45s} {count}")


if __name__ == "__main__":
    main()
