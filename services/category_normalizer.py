"""
category_normalizer.py
-----------------------
Reusable category normalization and multi-signal presence detection module.

Maps raw headings, CUAD categories, rule-detected categories, and alias strings
to a unified canonical taxonomy (e.g. "Termination", "Confidentiality",
"Governing Law", "Cap On Liability", "Indemnification", "Dispute Resolution",
"Compensation / Payment", "Non-Compete", "Non-Solicitation", "Force Majeure").

Used across section detection, classification, rule engine, and missing-clause analysis.
"""

import re
from typing import Set, List, Dict, Tuple, Optional

# Canonical categories
CANONICAL_CATEGORIES = {
    "Termination": [
        r"\btermination\b", r"\bterminate\b", r"\bnotice period\b", r"\bexpiry\b",
        r"\bexpiration\b", r"\bterm and termination\b"
    ],
    "Term / Duration": [
        r"\bterm & rental duration\b", r"\bterm and duration\b", r"\btenancy shall be for a fixed term\b",
        r"\btenancy term\b", r"\brental duration\b", r"\blease period\b", r"\bcommencing from\b"
    ],
    "Payment Terms / Rent": [
        r"\brent\b", r"\bmonthly rent\b", r"\brental charges\b", r"\bpayment terms\b",
        r"\bpayable in advance\b", r"\bpayment\b", r"\bcompensation\b", r"\bsalary\b",
        r"\bremuneration\b", r"\bfees\b", r"\bfee\b", r"\binvoice\b", r"\bconsideration\b"
    ],
    "Security Deposit": [
        r"\bsecurity deposit\b", r"\binterest-free security deposit\b", r"\bcaution deposit\b",
        r"\brefundable deposit\b", r"\bdeposit\b"
    ],
    "Utilities / Maintenance": [
        r"\bmaintenance and utilities\b", r"\belectricity and water\b", r"\butility charges\b",
        r"\bmaintenance charges\b", r"\btenantable condition\b"
    ],
    "Premises / Subletting": [
        r"\bpremises & residential use\b", r"\bpremises\b", r"\bresidential occupation\b",
        r"\bsublet\b", r"\bsubletting\b"
    ],
    "Confidentiality": [
        r"\bconfidential\b", r"\bconfidentiality\b", r"\bnon-disclosure\b", r"\bnda\b",
        r"\btrade secrets\b", r"\bsecret information\b", r"\bproprietary information\b"
    ],
    "Governing Law": [
        r"\bgoverning law\b", r"\bjurisdiction\b", r"\bchoice of law\b", r"\bapplicable law\b",
        r"\blaws of\b", r"\bcourts at\b", r"\bcourts of\b"
    ],
    "Cap On Liability": [
        r"\bcap on liability\b", r"\blimitation of liability\b", r"\bliability cap\b",
        r"\blimited liability\b", r"\bmaximum liability\b", r"\bextent of liability\b"
    ],
    "Indemnification": [
        r"\bindemnif\w*\b", r"\bindemnity\b", r"\bhold harmless\b"
    ],
    "Dispute Resolution": [
        r"\bdispute resolution\b", r"\barbitration\b", r"\bconciliation\b", r"\bmediation\b",
        r"\bdispute\b"
    ],
    "Non-Compete": [
        r"\bnon-compete\b", r"\bnon compete\b", r"\brestraint of trade\b", r"\bcovenant not to compete\b"
    ],
    "Non-Solicitation": [
        r"\bnon-solicitation\b", r"\bnon solicitation\b", r"\bno-solicit\b", r"\bsolicit\b"
    ],
    "Force Majeure": [
        r"\bforce majeure\b", r"\bact of god\b", r"\buncontrollable events\b", r"\bfrustration\b"
    ],
    "Intellectual Property": [
        r"\bintellectual property\b", r"\bip rights\b", r"\bcopyright\b", r"\bpatent\b",
        r"\btrademark\b", r"\bownership of ip\b", r"\bwork for hire\b"
    ],
    "Warranty": [
        r"\bwarranty\b", r"\bwarranties\b", r"\brepresentations\b", r"\breps and warranties\b"
    ],
}


# CUAD Category to Canonical Mapping
CUAD_TO_CANONICAL: Dict[str, str] = {
    "Governing Law": "Governing Law",
    "Termination For Convenience": "Termination",
    "Termination For Cause": "Termination",
    "Expiration Date": "Termination",
    "Effective Date": "Effective Date",
    "Renewal Term": "Termination",
    "Auto-Renewal": "Termination",
    "Notice Period To Terminate Renewal": "Termination",
    "Confidentiality": "Confidentiality",
    "Non-Disparagement": "Confidentiality",
    "Non-Compete": "Non-Compete",
    "Non-Solicitation": "Non-Solicitation",
    "No-Solicit Of Customers": "Non-Solicitation",
    "No-Solicit Of Employees": "Non-Solicitation",
    "Indemnification": "Indemnification",
    "Insurance": "Indemnification",
    "Cap On Liability": "Cap On Liability",
    "Uncapped Liability": "Cap On Liability",
    "Warranty Duration": "Warranty",
    "Audit Rights": "Audit Rights",
    "Change Of Control": "Change of Control",
    "Dispute Resolution": "Dispute Resolution",
    "Anti-Assignment": "Assignment",
    "IP Ownership Assignment": "Intellectual Property",
    "License Grant": "Intellectual Property",
    "Unlimited/All-You-Can-Eat License": "Intellectual Property",
    "Irrevocable Or Perpetual License": "Intellectual Property",
    "Revenue/Profit Sharing": "Compensation / Payment",
    "Price Restrictions": "Compensation / Payment",
    "Minimum Commitment": "Compensation / Payment",
    "Volume Restriction": "Compensation / Payment",
    "Most Favored Nation": "Commercial Terms",
    "Exclusivity": "Exclusivity",
    "Joint IP Ownership": "Intellectual Property",
    "Source Code Escrow": "Intellectual Property",
    "Post-Termination Services": "Termination",
    "Rofr/Rofo/Rofn": "Commercial Terms",
    "Third Party Beneficiary": "General Terms",
    "Liquidated Damages": "Compensation / Payment",
    "Covenant Not To Sue": "General Terms",
    "Force Majeure": "Force Majeure",
    "Waiver Of Jury": "General Terms",
    "Affiliate License-Licensor": "Intellectual Property",
    "Affiliate License-Licensee": "Intellectual Property",
    "Payment Terms": "Compensation / Payment",
    "Fees": "Compensation / Payment",
}


def normalize_category(category_name: str) -> str:
    """Returns canonical category string for any heading, CUAD label, or category alias."""
    if not category_name:
        return "General"
    
    clean = category_name.strip()
    
    # Direct match in CUAD map
    if clean in CUAD_TO_CANONICAL:
        return CUAD_TO_CANONICAL[clean]
    
    # Direct match in canonical keys
    for canonical in CANONICAL_CATEGORIES:
        if clean.lower() == canonical.lower():
            return canonical

    # Regex pattern search over raw string
    for canonical, patterns in CANONICAL_CATEGORIES.items():
        for pat in patterns:
            if re.search(pat, clean, re.IGNORECASE):
                return canonical
                
    return clean


def detect_heading_category(heading_text: str) -> Optional[str]:
    """Detects canonical clause category strictly from a section heading line."""
    if not heading_text or not heading_text.strip():
        return None
        
    heading_clean = heading_text.strip()
    
    # Match patterns against section heading
    for canonical, patterns in CANONICAL_CATEGORIES.items():
        for pat in patterns:
            if re.search(pat, heading_clean, re.IGNORECASE):
                return canonical
                
    return None


def extract_present_categories(
    classified_clauses: List[dict],
    required_categories: List[str]
) -> Tuple[Set[str], Set[str]]:
    """
    Combines multiple signals (Section Headings + ML Classifier Predictions + Rule Detections)
    to determine the normalized set of present categories in a contract.
    
    Returns (present_canonical_categories, missing_required_categories)
    """
    present_canonical: Set[str] = set()

    for clause in classified_clauses:
        heading = clause.get("heading", "")
        cuad_cat = clause.get("cuad_category", "")
        display_cat = clause.get("display_category", "")
        text = clause.get("text", "")

        # Signal 1: Heading Category
        heading_cat = detect_heading_category(heading)
        if heading_cat:
            present_canonical.add(heading_cat)

        # Signal 2: Classifier Category (Mapped to Canonical)
        if cuad_cat and cuad_cat != "Unknown":
            present_canonical.add(normalize_category(cuad_cat))
        if display_cat and display_cat != "Unknown":
            present_canonical.add(normalize_category(display_cat))

        # Signal 3: Text Heading-like Prefix Signal (e.g. first line of clause text)
        first_line = text.split("\n")[0] if text else ""
        if len(first_line) < 100:
            prefix_cat = detect_heading_category(first_line)
            if prefix_cat:
                present_canonical.add(prefix_cat)

    # Missing Categories calculation
    missing_required: Set[str] = set()
    for req in required_categories:
        norm_req = normalize_category(req)
        if norm_req not in present_canonical:
            missing_required.add(req)

    return present_canonical, missing_required
