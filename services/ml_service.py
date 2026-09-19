"""
ml_service.py
--------------
Single entry point for every from-scratch NLP component built for this
project. Load this once at Streamlit app startup and call its
functions from your pages/*.py files.

    from services.ml_service import LegalMLService
    ml = LegalMLService()   # loads all models once

    ml.classify_clause(text)                        # Module 1 / 3 / 4
    ml.extract_entities(document_text)               # Module 2
    ml.render_india_clause("Governing Law", city=..., state=...)  # Module 1
    ml.score_risk(clauses)                            # Module 4
    ml.answer_question(question, document_clauses=..) # Module 5

No component in this file calls an external API or loads a pretrained
language model -- every model referenced here was trained from scratch
on CUAD (see scripts/train_classifier.py, train_crf.py) or is a
rule/template/retrieval system with no learned weights at all.
"""
import sys
from pathlib import Path
import joblib

SERVICES_DIR = Path(__file__).resolve().parent
if str(SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICES_DIR))

from risk_rules import score_document as _rule_based_risk_scan, summarize_flags
from extract_entities import extract_entities as _extract_entities
from legal_qa_retrieval import LegalFAQRetriever, answer_question as _answer_question
from india_clause_templates import (
    render_governing_law,
    render_arbitration,
    render_stamp_duty_note,
    render_confidentiality,
    render_termination,
    render_signatory_block,
    DISCLAIMER_TEXT,
)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

INDIA_RENDERERS = {
    "governing_law": render_governing_law,
    "arbitration": render_arbitration,
    "stamp_duty_note": render_stamp_duty_note,
    "confidentiality": render_confidentiality,
    "termination": render_termination,
    "signatory_block": render_signatory_block,
}


class LegalMLService:
    """Loads every trained model once and exposes one clean method per
    module. Instantiate a single instance at app startup (e.g. via
    st.cache_resource in Streamlit) rather than per-request."""

    def __init__(self, models_dir=MODELS_DIR):
        models_dir = Path(models_dir)

        # Module 1 / 3 / 4 backbone
        clf_path = models_dir / "clause_classifier.joblib"
        self.clause_classifier = joblib.load(clf_path) if clf_path.exists() else None

        # Module 2 backbone
        crf_path = models_dir / "crf_tagger.joblib"
        self.crf_tagger = joblib.load(crf_path) if crf_path.exists() else None

        # Module 4 learned layer (optional -- only exists once your team
        # has hand-labeled data/risk_labeling_batch.csv and run
        # train_risk_classifier.py)
        risk_path = models_dir / "risk_classifier.joblib"
        self.risk_bundle = joblib.load(risk_path) if risk_path.exists() else None

        # Module 5
        self.faq_retriever = LegalFAQRetriever()

        self._warn_missing()

    def _warn_missing(self):
        if self.clause_classifier is None:
            print("[ml_service] WARNING: clause_classifier.joblib not found -- "
                  "run scripts/train_classifier.py")
        if self.crf_tagger is None:
            print("[ml_service] WARNING: crf_tagger.joblib not found -- "
                  "run scripts/train_crf.py")
        if self.risk_bundle is None:
            print("[ml_service] INFO: risk_classifier.joblib not found -- "
                  "risk scoring will use rule-based flags only until your "
                  "team labels data/risk_labeling_batch.csv and runs "
                  "train_risk_classifier.py")

    # ------------------------------------------------------------------
    # Module 1 & 3: clause classification (also feeds Module 4)
    # ------------------------------------------------------------------
    def classify_clause(self, clause_text):
        if self.clause_classifier is None:
            raise RuntimeError("clause_classifier not loaded -- run scripts/train_classifier.py")
        return self.clause_classifier.predict([clause_text])[0]

    # ------------------------------------------------------------------
    # Module 1: India-specific template rendering
    # ------------------------------------------------------------------
    def render_india_clause(self, clause_type, **kwargs):
        """clause_type: one of INDIA_RENDERERS keys, e.g. 'governing_law'."""
        renderer = INDIA_RENDERERS.get(clause_type)
        if renderer is None:
            raise ValueError(f"No India template for '{clause_type}'. "
                              f"Available: {list(INDIA_RENDERERS)}")
        return renderer(**kwargs)

    def drafting_disclaimer(self):
        return DISCLAIMER_TEXT

    # ------------------------------------------------------------------
    # Module 2: entity extraction from uploaded PDF text
    # ------------------------------------------------------------------
    def extract_entities(self, document_text):
        if self.crf_tagger is None:
            raise RuntimeError("crf_tagger not loaded -- run scripts/train_crf.py")
        return _extract_entities(document_text, self.crf_tagger)

    # ------------------------------------------------------------------
    # Module 4: risk scoring (rules always; learned classifier if available)
    # ------------------------------------------------------------------
    def score_risk(self, clauses):
        """clauses: list of {"text": str, "category": str}.
        Always returns rule-based flags. Adds a learned severity
        prediction per clause too, once risk_classifier.joblib exists."""
        rule_flags = _rule_based_risk_scan(clauses)
        result = {
            "rule_flags": rule_flags,
            "summary": summarize_flags(rule_flags),
        }
        if self.risk_bundle is not None:
            result["learned_predictions"] = self._predict_risk_learned(clauses)
        return result

    def _predict_risk_learned(self, clauses):
        from scipy.sparse import hstack
        import numpy as np
        from train_risk_classifier import rule_flag_features

        bundle = self.risk_bundle
        texts = [c["text"] for c in clauses]
        categories = [c.get("category", "Unknown") for c in clauses]

        X_text = bundle["tfidf"].transform(texts)
        X_cat = bundle["cat_encoder"].transform(np.array(categories).reshape(-1, 1))
        X_flags = np.array([rule_flag_features(t, c) for t, c in zip(texts, categories)])
        X = hstack([X_text, X_cat, X_flags])

        preds = bundle["model"].predict(X)
        labels = bundle["label_encoder"].inverse_transform(preds)
        return [
            {"text": t, "predicted_severity": l}
            for t, l in zip(texts, labels)
        ]

    # ------------------------------------------------------------------
    # Module 5: retrieval-based Q&A
    # ------------------------------------------------------------------
    def answer_question(self, question, document_clauses=None):
        return _answer_question(question, document_clauses=document_clauses, faq_retriever=self.faq_retriever)


if __name__ == "__main__":
    # Smoke test -- exercises every module through the single service class
    ml = LegalMLService()

    sample_text = (
        "Either party may terminate this Agreement without notice for any reason. "
        "The Vendor shall indemnify the Client against all claims arising from "
        "this Agreement. This Agreement shall be governed by the laws of Maharashtra."
    )

    print("\n--- classify_clause ---")
    print(ml.classify_clause("This Agreement shall be governed by the laws of Maharashtra."))

    print("\n--- render_india_clause (governing_law) ---")
    print(ml.render_india_clause("governing_law", city="Pune", state="Maharashtra"))

    print("\n--- extract_entities ---")
    for span in ml.extract_entities(sample_text):
        print(f"  [{span['type']}] {span['text']}")

    print("\n--- score_risk ---")
    clauses = [
        {"text": "Either party may terminate this Agreement without notice for any reason.", "category": "Termination"},
        {"text": "The Vendor shall indemnify the Client against all claims arising from this Agreement.", "category": "Indemnification"},
    ]
    risk = ml.score_risk(clauses)
    print(f"  Overall: {risk['summary']['overall']}, {len(risk['rule_flags'])} flags")

    print("\n--- answer_question ---")
    result = ml.answer_question("Is a non-compete enforceable in India?")
    if result["results"]:
        print(f"  [{result['source']}] {result['results'][0]['answer'][:120]}...")
