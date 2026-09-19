"""
review_pipeline.py
-------------------
Full contract review pipeline that connects:
  1. PDF/DOCX/text extraction  (pdf_reader.py)
  2. Clause segmentation       (local, numbered-section aware)
  3. TF-IDF + SVM classifier   (clause_classifier.joblib)
  4. CRF entity tagger         (crf_tagger.joblib)
  5. Random Forest risk model  (risk_classifier.joblib)
  6. Rule-based risk scanner   (risk_rules.py)
  7. India-specific templates  (india_clause_templates.py)
  8. Structured report builder

CUAD category → display label mapping is applied so that end-users see
"Governing Law" / "Termination" etc. instead of internal CUAD labels.

The Random Forest is used only when the feature dimensions match the
saved model; otherwise we fall back gracefully to rule-based only and
surface a clear note to the user.

No external API is called. No output is invented.
"""

from __future__ import annotations

import re
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

import joblib
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
_SERVICES_DIR = Path(__file__).resolve().parent
_MODELS_DIR = _SERVICES_DIR.parent / "models"


# ─────────────────────────────────────────────────────────────────────────────
# CUAD category → human-readable display label
# The SVM was trained on CUAD taxonomy which uses non-intuitive names.
# ─────────────────────────────────────────────────────────────────────────────
CUAD_TO_DISPLAY: dict[str, str] = {
    "Governing Law": "Governing Law",
    "Termination For Convenience": "Termination",
    "Termination For Cause": "Termination (For Cause)",
    "Expiration Date": "Term / Expiry",
    "Effective Date": "Effective Date",
    "Renewal Term": "Renewal",
    "Auto-Renewal": "Auto-Renewal",
    "Notice Period To Terminate Renewal": "Notice to Terminate Renewal",
    "Confidentiality": "Confidentiality / NDA",
    "Non-Disparagement": "Non-Disparagement",
    "Non-Compete": "Non-Compete",
    "Non-Solicitation": "Non-Solicitation",
    "No-Solicit Of Customers": "Non-Solicitation (Customers)",
    "No-Solicit Of Employees": "Non-Solicitation (Employees)",
    "Indemnification": "Indemnification",
    "Insurance": "Insurance / Indemnification",
    "Cap On Liability": "Limitation of Liability",
    "Uncapped Liability": "Unlimited Liability",
    "Warranty Duration": "Warranty / Payment Term",
    "Audit Rights": "Audit Rights",
    "Change Of Control": "Change of Control",
    "Dispute Resolution": "Dispute Resolution",
    "Anti-Assignment": "Assignment Restrictions",
    "IP Ownership Assignment": "IP Ownership / Assignment",
    "License Grant": "License Grant",
    "Unlimited/All-You-Can-Eat License": "Unlimited License",
    "Irrevocable Or Perpetual License": "Perpetual License",
    "Revenue/Profit Sharing": "Revenue Sharing",
    "Price Restrictions": "Pricing Restrictions",
    "Minimum Commitment": "Minimum Commitment",
    "Volume Restriction": "Volume Restriction",
    "Most Favored Nation": "Most Favoured Nation",
    "Exclusivity": "Exclusivity",
    "Joint IP Ownership": "Joint IP Ownership",
    "Source Code Escrow": "Source Code Escrow",
    "Post-Termination Services": "Post-Termination Services",
    "Rofr/Rofo/Rofn": "Right of First Refusal / Offer",
    "Third Party Beneficiary": "Third Party Rights",
    "Liquidated Damages": "Liquidated Damages / Penalty",
    "Covenant Not To Sue": "Covenant Not to Sue",
    "Force Majeure": "Force Majeure",
    "Waiver Of Jury": "Waiver",
    "Affiliate License-Licensor": "Affiliate License",
    "Affiliate License-Licensee": "Affiliate License",
    "Payment Terms": "Payment",
    "Fees": "Fees / Payment",
}

# CUAD categories that carry inherent risk (flag for closer review)
INHERENTLY_RISKY_CUAD: set[str] = {
    "Uncapped Liability",
    "Irrevocable Or Perpetual License",
    "Unlimited/All-You-Can-Eat License",
    "Non-Compete",
    "Liquidated Damages",
    "Anti-Assignment",
    "Change Of Control",
    "Waiver Of Jury",
}

# Categories that, if ABSENT, may be worth flagging as potentially missing
EXPECTED_CLAUSE_CATEGORIES: list[str] = [
    "Governing Law",
    "Termination For Convenience",
    "Termination For Cause",
    "Confidentiality",
    "Cap On Liability",
    "Dispute Resolution",
    "Force Majeure",
]

# India-specific legal notes keyed by display label
INDIA_LEGAL_NOTES: dict[str, str] = {
    "Termination": (
        "Under the Indian Contract Act, 1872 (Sections 37, 39, 73), parties must perform "
        "their contractual obligations. Abrupt termination without cure opportunity may give "
        "rise to a damages claim. Courts will award actual loss proved, not a notional figure."
    ),
    "Termination (For Cause)": (
        "Material breach clauses are generally enforceable under ICA 1872 Section 39 "
        "(anticipatory breach). Ensure 'material breach' is clearly defined to avoid disputes."
    ),
    "Governing Law": (
        "If the governing law is Indian law, the Indian Contract Act, 1872 governs formation, "
        "performance, and breach. Cross-border contracts should confirm which courts have "
        "territorial jurisdiction and whether arbitration overrides court jurisdiction."
    ),
    "Confidentiality / NDA": (
        "Confidentiality obligations are enforceable under general Indian contract law. "
        "Where electronic data is involved, the Information Technology Act, 2000 (Section 43A) "
        "and the Digital Personal Data Protection Act, 2023 may impose additional obligations."
    ),
    "Non-Compete": (
        "Post-termination non-compete clauses are generally void under Section 27 of the "
        "Indian Contract Act, 1872 as agreements in restraint of trade. Restrictions limited "
        "to the duration of the agreement are typically enforceable."
    ),
    "Non-Solicitation (Employees)": (
        "Non-solicitation of employees post-termination may also be challenged under Section 27 "
        "ICA 1872 if drafted too broadly. Courts will assess reasonableness."
    ),
    "Indemnification": (
        "Sections 124-125 of the Indian Contract Act, 1872 govern indemnity contracts. "
        "Overly broad indemnities covering 'all losses whatsoever' may be limited by courts "
        "under general contract principles of reasonable contemplation."
    ),
    "Insurance / Indemnification": (
        "Sections 124-125 of the Indian Contract Act, 1872 govern indemnity. "
        "Ensure the clause specifies whether indemnity is mutual and whether a cap applies."
    ),
    "Limitation of Liability": (
        "Section 73 of the Indian Contract Act, 1872 limits recoverable damages to those "
        "arising naturally or in reasonable contemplation. A contractual liability cap provides "
        "additional certainty and is generally enforceable in India."
    ),
    "Unlimited Liability": (
        "Without a liability cap, a party may be exposed to claims limited only by Section 73 "
        "ICA 1872 (natural/foreseeable loss). Courts will not automatically cap liability. "
        "Negotiating a cap (e.g., 12 months of fees) is strongly advisable."
    ),
    "Dispute Resolution": (
        "The Arbitration and Conciliation Act, 1996 (as amended) is the primary statute "
        "governing arbitration in India. Ensure the clause specifies seat, language, and number "
        "of arbitrators. Domestic arbitration awards are enforceable as court decrees."
    ),
    "Liquidated Damages / Penalty": (
        "Section 74 of the Indian Contract Act, 1872 provides that a party is entitled to "
        "reasonable compensation not exceeding the stipulated amount, regardless of whether "
        "actual loss is proved. Courts may reduce disproportionate liquidated damages amounts."
    ),
    "Force Majeure": (
        "Without a force majeure clause, parties must rely on Section 56 ICA 1872 (frustration "
        "of contract), which has a high threshold — complete impossibility of performance is "
        "required, not mere difficulty. A well-drafted force majeure clause provides "
        "greater flexibility and clarity."
    ),
    "IP Ownership / Assignment": (
        "Under the Copyright Act, 1957 (Section 19), assignment of copyright must be in "
        "writing and signed by the assignor. The scope, territory, and duration must be "
        "specified. For patents, Patents Act, 1970 (Section 68) governs assignment."
    ),
    "Auto-Renewal": (
        "Automatic renewal clauses are enforceable in India. Parties should note renewal "
        "notice deadlines carefully — missing them may result in unintended contract extension."
    ),
    "Term / Expiry": (
        "The contract term and expiry should be clearly defined. If no term is specified, "
        "the contract may be treated as ongoing until terminated by either party."
    ),
    "Term / Duration": (
        "Under Section 106 & 107 of the Transfer of Property Act, 1882, leases of immovable property "
        "exceeding 11 months require compulsory registration under Section 17 of the Registration Act, 1908. "
        "Standard 11-month residential agreements are widely executed to optimize stamp duty and registration requirements."
    ),
    "Payment Terms / Rent": (
        "Under Section 105 of the Transfer of Property Act, 1882, rent is the price payable in exchange for "
        "the right to enjoy property. Rent amounts, due dates, grace periods, and mode of payment are enforceable "
        "as agreed between landlord and tenant subject to state Rent Control laws."
    ),
    "Security Deposit": (
        "Under general principles of contract and Section 74 of the Indian Contract Act, 1872, an interest-free "
        "security deposit must be refunded upon peaceful vacation and delivery of possession, minus valid deductions "
        "for unpaid bills or actual property damage beyond normal wear and tear."
    ),
    "Utilities / Maintenance": (
        "Under Section 108(m) of the Transfer of Property Act, 1882, the tenant is bound to keep the property in good "
        "condition, subject to reasonable wear and tear. Utility payments (electricity, water) must be settled as agreed."
    ),
    "Premises / Subletting": (
        "Under Section 108(j) of the Transfer of Property Act, 1882, the lessee may transfer or sublet their interest "
        "unless explicitly restricted by the lease deed. Express non-subletting clauses effectively prohibit unapproved third-party occupation."
    ),
    "Assignment Restrictions": (
        "Restrictions on assignment are generally enforceable in India. Verify whether "
        "assignment is permitted upon a change of control, merger, or group restructuring."
    ),
}



# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SegmentedClause:
    index: int
    heading: str          # detected heading / number, or ""
    text: str             # full text of this segment
    cuad_category: str    # raw CUAD prediction
    display_category: str # mapped human label
    confidence: Optional[float] = None
    rule_flags: List[dict] = field(default_factory=list)
    learned_severity: Optional[str] = None   # "high"/"medium"/"low" from RF
    india_note: str = ""
    classifier_error: str = ""


@dataclass
class ContractOverview:
    parties: List[str] = field(default_factory=list)
    effective_date: Optional[str] = None
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    duration: Optional[str] = None
    contract_type_guess: str = "Commercial Agreement"
    entities_raw: List[dict] = field(default_factory=list)
    crf_error: str = ""


@dataclass
class ReviewOutput:
    overview: ContractOverview
    clauses: List[SegmentedClause]
    missing_categories: List[dict]        # [{category, severity, explanation}]
    text_length: int
    text_sample: str                      # first 400 chars for debugging
    n_segments: int
    classifier_available: bool
    crf_available: bool
    rf_available: bool
    rf_error: str = ""
    extraction_error: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Clause segmenter
# ─────────────────────────────────────────────────────────────────────────────

# Numbered section patterns: "1.", "1.1", "ARTICLE 1", "Section 2", "(a)"
_NUMBERED = re.compile(
    r"^(?:"
    r"\d+(?:\.\d+)*\.?\s+"          # 1.  /  1.2.3.
    r"|[A-Z]{2,}\s+\d+\s*[:\.\-]?"  # ARTICLE 1 / SECTION 2
    r"|(?:Article|Section|Clause|Schedule|Annexure|Exhibit|Appendix)\s+\d+"
    r"|\([a-z]{1,3}\)\s+"            # (a) (ii)
    r"|\([ivxlc]+\)\s+"              # roman
    r")",
    re.IGNORECASE,
)

_HEADING_LINE = re.compile(
    r"^(?:\d+(?:\.\d+)*\.?\s+)?[A-Z][A-Z\s,\-&/']{4,60}$"
)


def _is_section_boundary(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _NUMBERED.match(stripped):
        return True
    if _HEADING_LINE.match(stripped) and len(stripped) < 80:
        return True
    return False


def segment_contract(text: str, min_chars: int = 60, max_clauses: int = 120) -> list[dict]:
    """
    Split contract text into clause segments.
    Returns list of {"heading": str, "text": str}.
    """
    lines = text.splitlines()
    segments: list[dict] = []
    current_heading = ""
    current_lines: list[str] = []

    def flush():
        body = " ".join(l.strip() for l in current_lines if l.strip())
        body = re.sub(r"\s{2,}", " ", body).strip()
        # If body is short or empty, combine heading with body
        full_clause_text = (current_heading + " " + body).strip() if current_heading else body
        if len(full_clause_text) >= min_chars or (current_heading and len(full_clause_text) >= 20):
            segments.append({"heading": current_heading, "text": full_clause_text})

    for line in lines:
        if _is_section_boundary(line):
            flush()
            current_heading = line.strip()
            current_lines = [line.strip()]
        else:
            current_lines.append(line)

    flush()  # last segment

    # If segmentation produced nothing meaningful, fall back to paragraph split
    if not segments:
        paras = re.split(r"\n{2,}", text)
        segments = [
            {"heading": "", "text": re.sub(r"\s+", " ", p).strip()}
            for p in paras if len(p.strip()) >= 20
        ]

    return segments[:max_clauses]



# ─────────────────────────────────────────────────────────────────────────────
# Feature builder for Random Forest (must match train_risk_classifier.py exactly)
# ─────────────────────────────────────────────────────────────────────────────

def _build_rf_features(texts, categories, bundle):
    """Build feature matrix identical to training time."""
    from scipy.sparse import hstack, csr_matrix
    from risk_rules import check_clause_language, ONE_SIDEDNESS_RULES

    flag_names_trained = bundle.get("flag_names", [
        r["flag"] for r in [
            {"flag": "unilateral_discretion"},
            {"flag": "uncapped_liability"},
            {"flag": "no_notice_termination"},
            {"flag": "one_directional_indemnity"},
            {"flag": "perpetual_obligation"},
            {"flag": "broad_waiver"},
            {"flag": "at_will_termination"},
        ]
    ])

    X_text = bundle["tfidf"].transform(texts)
    X_cat = bundle["cat_encoder"].transform(np.array(categories).reshape(-1, 1))

    flag_rows = []
    for text, cat in zip(texts, categories):
        flags_fired = {f["flag"] for f in check_clause_language(text, cat)}
        flag_rows.append([1 if fn in flags_fired else 0 for fn in flag_names_trained])
    X_flags = csr_matrix(np.array(flag_rows))

    return hstack([X_text, X_cat, X_flags])


# ─────────────────────────────────────────────────────────────────────────────
# Model loader (singleton cache)
# ─────────────────────────────────────────────────────────────────────────────

_MODEL_CACHE: dict = {}


def _load_models() -> dict:
    global _MODEL_CACHE
    if _MODEL_CACHE:
        return _MODEL_CACHE

    result: dict = {
        "classifier": None,
        "crf": None,
        "risk_bundle": None,
    }

    clf_path = _MODELS_DIR / "clause_classifier.joblib"
    if clf_path.exists():
        try:
            result["classifier"] = joblib.load(clf_path)
        except Exception as e:
            result["classifier_error"] = str(e)

    crf_path = _MODELS_DIR / "crf_tagger.joblib"
    if crf_path.exists():
        try:
            result["crf"] = joblib.load(crf_path)
        except Exception as e:
            result["crf_error"] = str(e)

    risk_path = _MODELS_DIR / "risk_classifier.joblib"
    if risk_path.exists():
        try:
            result["risk_bundle"] = joblib.load(risk_path)
        except Exception as e:
            result["risk_bundle_error"] = str(e)

    _MODEL_CACHE = result
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline function
# ─────────────────────────────────────────────────────────────────────────────

def run_review(contract_text: str) -> ReviewOutput:
    """
    Full pipeline:
      text → segments → classify → entity extraction → risk rules → RF risk → report
    """
    import sys
    _svc = str(_SERVICES_DIR)
    if _svc not in sys.path:
        sys.path.insert(0, _svc)

    from risk_rules import score_document, summarize_flags, check_clause_language
    from extract_entities import extract_entities

    models = _load_models()
    clf = models.get("classifier")
    crf = models.get("crf")
    risk_bundle = models.get("risk_bundle")

    # ── 1. Segment ──────────────────────────────────────────────────────────
    raw_segments = segment_contract(contract_text)
    n_segments = len(raw_segments)

    from category_normalizer import detect_heading_category, normalize_category

    # ── 2. Classify each segment ─────────────────────────────────────────────
    classified: list[SegmentedClause] = []
    for idx, seg in enumerate(raw_segments):
        text = seg["text"]
        heading = seg["heading"]
        cuad_cat = "Unknown"
        display_cat = "Unknown"
        clf_err = ""

        # Heading-based category detection takes structural priority if present
        heading_cat = detect_heading_category(heading) or detect_heading_category(text.split("\n")[0])

        if clf is not None:
            try:
                cuad_cat = clf.predict([text])[0]
                display_cat = heading_cat if heading_cat else CUAD_TO_DISPLAY.get(cuad_cat, normalize_category(cuad_cat))
            except Exception as e:
                clf_err = f"Classifier error: {e}"
                display_cat = heading_cat if heading_cat else "Unclassified"
        else:
            clf_err = "Clause classifier not loaded (clause_classifier.joblib missing)."
            display_cat = heading_cat if heading_cat else "Unclassified"

        classified.append(SegmentedClause(
            index=idx + 1,
            heading=heading,
            text=text,
            cuad_category=cuad_cat,
            display_category=display_cat,
            classifier_error=clf_err,
        ))


    # ── 3. Multi-signal Category Detection & Missing Category Check ─────────
    from category_normalizer import extract_present_categories, normalize_category

    classified_clause_dicts = [
        {
            "heading": c.heading,
            "cuad_category": c.cuad_category,
            "display_category": c.display_category,
            "text": c.text,
        }
        for c in classified
    ]

    present_canonical, _ = extract_present_categories(
        classified_clause_dicts, EXPECTED_CLAUSE_CATEGORIES
    )

    all_rule_flags = score_document(
        [{"text": c.text, "category": c.cuad_category} for c in classified]
    )

    # Filter missing category flags using normalized multi-signal present set
    missing_cat_flags = []
    for category in EXPECTED_CLAUSE_CATEGORIES:
        norm_expected = normalize_category(category)
        if norm_expected not in present_canonical:
            missing_cat_flags.append({
                "flag": "missing_category",
                "category": category,
                "severity": "high" if category in ("Cap On Liability", "Governing Law") else "medium",
                "explanation": f"No clause found addressing '{category}'. Contracts of this "
                                f"type typically include one; its absence should be confirmed "
                                f"with the drafting party, not assumed to be intentional.",
            })

    # Attach per-clause rule flags
    per_clause_flags: dict[int, list] = {}
    for flag in all_rule_flags:
        if flag.get("flag") == "missing_category":
            continue
        matched_text = flag.get("matched_text", "")
        for i, c in enumerate(classified):
            if matched_text and matched_text[:80] in c.text:
                per_clause_flags.setdefault(i, []).append(flag)
                break

    # Second pass: per-clause language rules
    for i, c in enumerate(classified):
        flags = check_clause_language(c.text, c.cuad_category)
        if flags:
            existing = per_clause_flags.get(i, [])
            seen_flag_names = {f["flag"] for f in existing}
            for f in flags:
                if f["flag"] not in seen_flag_names:
                    existing.append(f)
            per_clause_flags[i] = existing

    for i, c in enumerate(classified):
        c.rule_flags = per_clause_flags.get(i, [])


    # ── 5. Random Forest risk predictions ────────────────────────────────────
    rf_error = ""
    if risk_bundle is not None and classified:
        try:
            texts_for_rf = [c.text for c in classified]
            cats_for_rf = [c.cuad_category for c in classified]
            X = _build_rf_features(texts_for_rf, cats_for_rf, risk_bundle)

            expected_n = risk_bundle["model"].n_features_in_
            actual_n = X.shape[1]
            if expected_n != actual_n:
                rf_error = (
                    f"Random Forest feature mismatch: model expects {expected_n} features, "
                    f"got {actual_n}. Risk predictions will use rule-based flags only. "
                    f"Re-train the model if this persists."
                )
            else:
                preds = risk_bundle["model"].predict(X)
                labels = risk_bundle["label_encoder"].inverse_transform(preds)
                for c, label in zip(classified, labels):
                    c.learned_severity = str(label)
        except Exception as e:
            rf_error = f"Random Forest prediction failed: {e}"

    # ── 6. India-specific notes ───────────────────────────────────────────────
    for c in classified:
        note = INDIA_LEGAL_NOTES.get(c.display_category, "")
        c.india_note = note

    # ── 7. Entity extraction (CRF) ───────────────────────────────────────────
    overview = ContractOverview()
    if crf is not None:
        try:
            entities = extract_entities(contract_text, crf)
            overview.entities_raw = entities
            for ent in entities:
                etype = ent.get("type", "")
                etext = ent.get("text", "").strip()
                if not etext:
                    continue
                if etype == "Parties":
                    overview.parties.append(etext)
                elif etype == "Effective Date" and not overview.effective_date:
                    overview.effective_date = etext
                elif etype == "Governing Law" and not overview.governing_law:
                    overview.governing_law = etext
                elif etype == "Jurisdiction" and not overview.jurisdiction:
                    overview.jurisdiction = etext
                elif etype in ("Term", "Duration") and not overview.duration:
                    overview.duration = etext
        except Exception as e:
            overview.crf_error = f"Entity extraction error: {e}"
    else:
        overview.crf_error = "CRF tagger not loaded (crf_tagger.joblib missing). Entity extraction skipped."

    # Also extract governing law / jurisdiction from regex if CRF missed it
    if not overview.governing_law:
        m = re.search(r"governed by.{0,40}laws? of ([A-Za-z\s,]+?)[\.\,\;]", contract_text, re.IGNORECASE)
        if m:
            overview.governing_law = m.group(1).strip()
    if not overview.jurisdiction:
        m = re.search(r"(?:courts?|jurisdiction).{0,30}(?:at|of|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", contract_text)
        if m:
            overview.jurisdiction = m.group(1).strip()

    # ── Multi-signal Contract Type Detection ──────────────────────────────
    text_lower = contract_text.lower()

    # Keyword scoring dictionary
    rental_keywords = [
        "landlord", "tenant", "lessor", "lessee", "premises", "rent", "security deposit",
        "lease", "rental", "sublet", "subletting", "possession", "maintenance and utilities",
        "house rent agreement", "residential agreement", "tenancy"
    ]
    employment_keywords = [
        "employer", "employee", "salary", "designation", "employment", "probation",
        "remuneration", "duties and responsibilities", "job description"
    ]
    nda_keywords = [
        "non-disclosure", "disclosing party", "receiving party", "confidential information",
        "trade secrets", "proprietary information", "nda agreement"
    ]
    software_keywords = [
        "license grant", "licensor", "licensee", "software license", "end user license",
        "source code", "intellectual property license"
    ]

    rental_score = sum(1 for kw in rental_keywords if kw in text_lower)
    employment_score = sum(1 for kw in employment_keywords if kw in text_lower)
    nda_score = sum(1 for kw in nda_keywords if kw in text_lower)
    software_score = sum(1 for kw in software_keywords if kw in text_lower)

    if rental_score >= 2 or "rent agreement" in text_lower or "lease agreement" in text_lower:
        overview.contract_type_guess = "Residential Rental / Lease Agreement"
    elif employment_score >= 2 or "employment agreement" in text_lower:
        overview.contract_type_guess = "Employment Agreement"
    elif nda_score >= 2 or "non-disclosure agreement" in text_lower:
        overview.contract_type_guess = "Non-Disclosure Agreement (NDA)"
    elif software_score >= 2 or "software license" in text_lower:
        overview.contract_type_guess = "Software / Intellectual Property License"
    else:
        type_hints = {c.cuad_category for c in classified}
        if "Non-Compete" in type_hints or "Non-Solicitation" in type_hints:
            overview.contract_type_guess = "Employment / Service Agreement (with restrictions)"
        elif "License Grant" in type_hints:
            overview.contract_type_guess = "Software / Intellectual Property License"
        elif "Confidentiality" in type_hints and len(classified) < 15:
            overview.contract_type_guess = "Non-Disclosure Agreement (NDA)"
        elif "Indemnification" in type_hints or "Insurance" in type_hints:
            overview.contract_type_guess = "Commercial Services Agreement"
        else:
            overview.contract_type_guess = "Commercial Agreement"


    return ReviewOutput(
        overview=overview,
        clauses=classified,
        missing_categories=missing_cat_flags,
        text_length=len(contract_text),
        text_sample=contract_text[:400],
        n_segments=n_segments,
        classifier_available=(clf is not None),
        crf_available=(crf is not None),
        rf_available=(risk_bundle is not None),
        rf_error=rf_error,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Report formatter
# ─────────────────────────────────────────────────────────────────────────────

_RISK_ORDER = {"high": 0, "medium": 1, "low": 2, None: 3}
_SEV_ICON = {"high": "🔴", "medium": "🟠", "low": "🟢", "HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}


def _effective_severity(clause: SegmentedClause) -> str:
    """Return the highest severity for a clause."""
    rule_sevs = [f.get("severity", "low") for f in clause.rule_flags]
    rf_sev = clause.learned_severity
    cuad_risk = "high" if clause.cuad_category in INHERENTLY_RISKY_CUAD else None
    candidates = [s for s in [rf_sev, cuad_risk] + rule_sevs if s]
    order = {"high": 0, "medium": 1, "low": 2}
    candidates_sorted = sorted(candidates, key=lambda s: order.get(str(s).lower(), 9))
    return candidates_sorted[0] if candidates_sorted else "low"


def format_report(output: ReviewOutput, contract_name: str = "Contract") -> str:
    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("# Contract Review Report")
    lines.append(f"**Document:** {contract_name}")
    lines.append("")
    lines.append(
        "> **Disclaimer:** This review is produced by a local ML pipeline (TF-IDF/SVM clause "
        "classifier trained on CUAD, CRF entity tagger, Random Forest risk model, and "
        "handwritten risk rules). It does not constitute legal advice. "
        "**Every finding below is linked to actual contract text.** "
        "Always consult a qualified legal professional before acting on this review."
    )
    lines.append("")

    # ── Pipeline status ───────────────────────────────────────────────────────
    lines.append("## Pipeline Status")
    lines.append("")
    lines.append(f"| Component | Status |")
    lines.append(f"|---|---|")
    lines.append(f"| Text extraction | {'OK — ' + str(output.text_length) + ' characters' if output.text_length > 0 else 'FAILED'} |")
    lines.append(f"| Clause segmentation | {output.n_segments} segments detected |")
    lines.append(f"| TF-IDF + SVM classifier | {'Loaded and active' if output.classifier_available else 'NOT LOADED'} |")
    lines.append(f"| CRF entity tagger | {'Loaded and active' if output.crf_available else 'NOT LOADED'} |")
    lines.append(f"| Random Forest risk model | {'Loaded' + (' — active' if not output.rf_error else ' — ' + output.rf_error[:80]) if output.rf_available else 'NOT LOADED'} |")
    lines.append(f"| Rule-based risk scanner | Always active |")
    lines.append(f"| India-specific rules | Always active |")
    lines.append("")

    if not output.classifier_available:
        lines.append("> **WARNING:** Clause classifier not available. Clause categories cannot be predicted.")
        lines.append("")
    if output.rf_error:
        lines.append(f"> **NOTE (Random Forest):** {output.rf_error}")
        lines.append("")

    lines.append("---")

    # ── 1. Contract Overview ──────────────────────────────────────────────────
    ov = output.overview
    lines.append("")
    lines.append("## 1. Contract Overview")
    lines.append("")
    lines.append(f"| Field | Detected Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Likely contract type | {ov.contract_type_guess} |")
    lines.append(f"| Parties | {', '.join(ov.parties) if ov.parties else '_Not clearly detected by CRF_'} |")
    lines.append(f"| Effective date | {ov.effective_date or '_Not detected_'} |")
    lines.append(f"| Governing law | {ov.governing_law or '_Not detected_'} |")
    lines.append(f"| Jurisdiction | {ov.jurisdiction or '_Not detected_'} |")
    lines.append(f"| Contract duration | {ov.duration or '_Not detected_'} |")
    lines.append("")

    if ov.crf_error:
        lines.append(f"> **Entity extraction note:** {ov.crf_error}")
        lines.append("")

    lines.append(
        "> *Entity detection uses the trained CRF model. Values marked 'Not detected' mean the "
        "model did not find a confident match — they may still exist in the contract.*"
    )
    lines.append("")
    lines.append("---")

    # ── Categorise clauses by effective severity ──────────────────────────────
    flagged_clauses = [c for c in output.clauses if c.rule_flags or c.cuad_category in INHERENTLY_RISKY_CUAD or c.learned_severity in ("high", "medium")]
    clean_clauses = [c for c in output.clauses if c not in flagged_clauses]

    high_clauses = [c for c in flagged_clauses if _effective_severity(c) == "high"]
    medium_clauses = [c for c in flagged_clauses if _effective_severity(c) == "medium"]
    low_clauses = [c for c in flagged_clauses if _effective_severity(c) == "low"]

    # ── 2. Clause Analysis ────────────────────────────────────────────────────
    lines.append("")
    lines.append("## 2. Full Clause Analysis")
    lines.append("")
    lines.append(
        f"**{output.n_segments}** segments were extracted from the contract. "
        f"**{len(flagged_clauses)}** raised at least one risk flag. "
        f"**{len(clean_clauses)}** had no detected flags."
    )
    lines.append("")

    def _render_clause(c: SegmentedClause, number: int):
        sev = _effective_severity(c)
        icon = _SEV_ICON.get(sev, "⚪")
        heading_display = f" — *{c.heading}*" if c.heading else ""
        rf_label = ""
        if c.learned_severity:
            rf_label = f" | RF Model: **{c.learned_severity.upper()}**"

        lines.append(f"### Clause {number}{heading_display}")
        lines.append("")
        lines.append(f"**Category (SVM classifier):** {c.display_category}  ")
        lines.append(f"**Effective Risk Level:** {icon} **{sev.upper()}**{rf_label}  ")

        if c.classifier_error:
            lines.append(f"**Classifier note:** {c.classifier_error}  ")

        lines.append("")
        lines.append("**Evidence — actual clause text:**")
        lines.append(f"> {c.text[:500]}{'...' if len(c.text) > 500 else ''}")
        lines.append("")

        if c.rule_flags:
            lines.append("**Detected issues (rule-based scanner):**")
            lines.append("")
            for flag in c.rule_flags:
                fsev = flag.get("severity", "low").upper()
                ficon = _SEV_ICON.get(fsev, "⚪")
                fname = flag.get("flag", "")
                fexpl = flag.get("explanation", "")
                lines.append(f"- {ficon} **{fname}** ({fsev}): {fexpl}")
            lines.append("")

        if c.cuad_category in INHERENTLY_RISKY_CUAD:
            lines.append(
                f"**Note (classifier):** This clause was classified as "
                f"**'{c.display_category}'** — a category that typically warrants careful review."
            )
            lines.append("")

        if c.india_note:
            lines.append("**India-specific legal consideration:**")
            lines.append(f"> {c.india_note}")
            lines.append("")

        if not c.rule_flags and c.cuad_category not in INHERENTLY_RISKY_CUAD and not c.learned_severity in ("high", "medium"):
            lines.append(
                "_No significant risk was detected by the configured rules/models for this clause._"
            )
            lines.append("")

        lines.append("---")

    # ── 3. High-Risk Findings ─────────────────────────────────────────────────
    lines.append("")
    lines.append(f"## 3. High-Priority Findings ({len(high_clauses)} clause(s))")
    lines.append("")
    if high_clauses:
        for i, c in enumerate(high_clauses, 1):
            _render_clause(c, i)
    else:
        lines.append("_No high-priority findings detected._")
        lines.append("")

    # ── 4. Medium-Risk Findings ───────────────────────────────────────────────
    lines.append("")
    lines.append(f"## 4. Medium-Priority Findings ({len(medium_clauses)} clause(s))")
    lines.append("")
    if medium_clauses:
        for i, c in enumerate(medium_clauses, 1):
            _render_clause(c, i)
    else:
        lines.append("_No medium-priority findings detected._")
        lines.append("")

    # ── 5. Low / Informational ────────────────────────────────────────────────
    lines.append("")
    lines.append(f"## 5. Low-Priority / Informational ({len(low_clauses)} clause(s))")
    lines.append("")
    if low_clauses:
        for i, c in enumerate(low_clauses, 1):
            _render_clause(c, i)
    else:
        lines.append("_No low-priority findings detected._")
        lines.append("")

    # ── 6. Missing Clauses ────────────────────────────────────────────────────
    lines.append("")
    lines.append(f"## 6. Potentially Missing Provisions ({len(output.missing_categories)} detected)")
    lines.append("")
    if output.missing_categories:
        lines.append(
            "> The classifier did not find a clause for the following expected categories. "
            "This may mean the clause is absent, or that it exists but was classified under a "
            "different label. Verify manually before concluding a clause is missing."
        )
        lines.append("")
        for mc in output.missing_categories:
            msev = mc.get("severity", "medium")
            micon = _SEV_ICON.get(msev, "⚪")
            mcat = mc.get("category", "")
            mexpl = mc.get("explanation", "")
            india = INDIA_LEGAL_NOTES.get(mcat, "")
            lines.append(f"### {micon} Potentially missing: {mcat} ({msev.upper()})")
            lines.append("")
            lines.append(mexpl)
            if india:
                lines.append("")
                lines.append(f"**India-specific note:** {india}")
            lines.append("")
            lines.append("---")
    else:
        lines.append("_No missing provisions detected based on configured rules._")
        lines.append("")

    # ── 7. India-Specific Summary ─────────────────────────────────────────────
    lines.append("")
    lines.append("## 7. India-Specific Considerations")
    lines.append("")
    lines.append(
        "> The clause classifier was trained on the CUAD dataset (general English-language "
        "contracts, primarily US-originated). **It was not trained on Indian law.** "
        "India-specific legal applicability is handled separately through handwritten rules "
        "and templates grounded in Indian statutes."
    )
    lines.append("")

    india_noted = [(c.display_category, c.india_note) for c in output.clauses if c.india_note]
    seen_notes: set = set()
    for cat, note in india_noted:
        if cat not in seen_notes:
            seen_notes.add(cat)
            lines.append(f"**{cat}:**  ")
            lines.append(note)
            lines.append("")

    if not seen_notes:
        lines.append("_No India-specific notes apply to the detected clause categories._")
        lines.append("")

    # ── 8. Overall Summary ────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## 8. Review Summary")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|---|---|")
    lines.append(f"| Total segments analysed | {output.n_segments} |")
    lines.append(f"| Clauses with HIGH risk flags | {len(high_clauses)} |")
    lines.append(f"| Clauses with MEDIUM risk flags | {len(medium_clauses)} |")
    lines.append(f"| Clauses with LOW risk flags | {len(low_clauses)} |")
    lines.append(f"| Clauses with no flags | {len(clean_clauses)} |")
    lines.append(f"| Potentially missing provisions | {len(output.missing_categories)} |")
    lines.append("")
    lines.append(
        "> **No overall numeric risk score is assigned.** Risk depends on context, "
        "parties' bargaining positions, and applicable law — factors an automated tool "
        "cannot fully assess. This report should be reviewed by a qualified legal professional."
    )

    return "\n".join(lines)
