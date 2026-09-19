"""
risk_rules.py
--------------
Rule-based risk flagging for Module 4. This is the part of risk
analysis that works *today*, with zero labeled training data --
transparent if/else rules over clause text and category, not a
learned model. It can run standalone, or be combined later with the
Random Forest classifier (train_risk_classifier.py) once your team has
hand-labeled enough clauses.

Two kinds of checks:
  1. Missing-protection checks: does the contract have a clause in
     categories that responsible drafting normally covers at all?
  2. One-sidedness checks: within a clause that IS present, does its
     language show markers of being skewed toward one party (e.g.
     unilateral "sole discretion" language, uncapped liability,
     one-directional indemnification)?

Every flag below is traceable to the specific rule that fired --
that's the whole point of choosing rules over an opaque model here.
"""
import re

# Categories a "reasonably protective" commercial contract is expected
# to address. If the classifier + CRF pipeline finds no clause in one
# of these categories anywhere in the document, that's flagged as a
# missing-protection risk regardless of clause content.
EXPECTED_CATEGORIES = [
    "Governing Law",
    "Termination",
    "Cap On Liability",
    "Confidentiality",
    "Indemnification",
]

# (regex pattern, flag_name, severity, explanation) -- one-sidedness
# markers within clause text. Case-insensitive.
ONE_SIDEDNESS_RULES = [
    (
        r"\bsole (?:and absolute )?discretion\b",
        "unilateral_discretion",
        "medium",
        "Clause grants one party unilateral 'sole discretion' with no "
        "stated standard or the other party's consent required.",
    ),
    (
        r"\bunlimited liability\b|\bno limit(?:ation)? (?:on|of) liability\b",
        "uncapped_liability",
        "high",
        "Clause does not cap liability, exposing a party to potentially "
        "unlimited financial risk.",
    ),
    (
        r"\bwithout (?:any )?notice\b",
        "no_notice_termination",
        "medium",
        "Clause allows an action (e.g. termination) without prior notice "
        "to the other party.",
    ),
    (
        r"\bshall indemnify\b(?!.*\bmutually\b)(?!.*\beach party\b)",
        "one_directional_indemnity",
        "medium",
        "Indemnification appears to run in one direction only; check "
        "whether the other party has reciprocal protection elsewhere.",
    ),
    (
        r"\bperpetual\b|\bin perpetuity\b",
        "perpetual_obligation",
        "medium",
        "Clause imposes an obligation (e.g. confidentiality, license) "
        "with no time limit.",
    ),
    (
        r"\bwaives?\s+(?:any and )?all\s+(?:rights|claims)\b",
        "broad_waiver",
        "high",
        "Clause contains a broad waiver of rights or claims -- confirm "
        "scope and whether it is mutual.",
    ),
    (
        r"\bat will\b",
        "at_will_termination",
        "low",
        "Agreement or a specific obligation can be ended 'at will', "
        "which reduces predictability for the other party.",
    ),
]


from category_normalizer import normalize_category, CANONICAL_CATEGORIES


def check_missing_categories(present_categories):
    """present_categories: iterable of clause categories found anywhere in
    the document (from headings, classifier predictions, or rules)."""
    normalized_present = {normalize_category(c) for c in present_categories if c}
    flags = []
    for category in EXPECTED_CATEGORIES:
        norm_expected = normalize_category(category)
        if norm_expected not in normalized_present:
            flags.append({
                "flag": "missing_category",
                "category": category,
                "severity": "high" if category in ("Cap On Liability", "Governing Law") else "medium",
                "explanation": f"No clause found addressing '{category}'. Contracts of this "
                                f"type typically include one; its absence should be confirmed "
                                f"with the drafting party, not assumed to be intentional.",
            })
    return flags



def check_clause_language(clause_text, category=None):
    """Run one-sidedness regex rules over a single clause's text."""
    flags = []
    for pattern, flag_name, severity, explanation in ONE_SIDEDNESS_RULES:
        if re.search(pattern, clause_text, flags=re.IGNORECASE):
            flags.append({
                "flag": flag_name,
                "category": category,
                "severity": severity,
                "explanation": explanation,
                "matched_text": clause_text[:200],
            })
    return flags


def score_document(clauses):
    """clauses: list of {"text": str, "category": str} for every clause
    extracted from a document. Returns all rule-based flags found,
    combining missing-category checks and per-clause language checks."""
    present_categories = {c.get("category") for c in clauses if c.get("category")}
    all_flags = check_missing_categories(present_categories)
    for clause in clauses:
        all_flags.extend(check_clause_language(clause["text"], clause.get("category")))
    return all_flags


SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1}


def summarize_flags(flags):
    """Roll up flags into a simple document-level severity summary."""
    if not flags:
        return {"overall": "low", "counts": {"high": 0, "medium": 0, "low": 0}}
    counts = {"high": 0, "medium": 0, "low": 0}
    for f in flags:
        counts[f["severity"]] += 1
    overall = "high" if counts["high"] else ("medium" if counts["medium"] else "low")
    return {"overall": overall, "counts": counts}


if __name__ == "__main__":
    sample_clauses = [
        {"text": "Either party may terminate this Agreement without notice for any reason.", "category": "Termination"},
        {"text": "The Vendor shall indemnify the Client against all claims arising from this Agreement.", "category": "Indemnification"},
        {"text": "The Client may, in its sole discretion, withhold payment pending review.", "category": "Payment"},
        {"text": "This Agreement shall be governed by the laws of Maharashtra.", "category": "Governing Law"},
    ]
    flags = score_document(sample_clauses)
    for f in flags:
        print(f"[{f['severity'].upper()}] ({f['flag']}) {f['explanation']}")
    print("\nSummary:", summarize_flags(flags))
