"""
contract_reviewer.py
---------------------
Local, rule-based contract review engine aligned with the STRICT ACCURACY
system prompt provided by the user.

Principles enforced:
  - Only flags clauses actually found in the contract text.
  - Never invents section numbers or case law.
  - Uses careful language ("may", "appears to", "could result in").
  - Links every risk to an actual clause or missing provision.
  - No overall numeric risk score unless requested.
  - Identifies missing clauses as "Potentially missing provision".
  - Checks Indian law relevance for each flag.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ClauseReview:
    title: str
    what_it_says: str
    potential_concern: str
    why_it_matters: str
    legal_basis: str
    severity: str          # HIGH / MEDIUM / LOW / INFO
    recommended_action: str
    matched_text: str = ""


@dataclass
class MissingClause:
    title: str
    why_relevant: str
    severity: str          # HIGH / MEDIUM / LOW


@dataclass
class ReviewResult:
    clause_reviews: List[ClauseReview] = field(default_factory=list)
    missing_clauses: List[MissingClause] = field(default_factory=list)
    info_items: List[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Clause detection helpers
# ─────────────────────────────────────────────────────────────────────────────

def _find(patterns: list[str], text: str) -> Optional[re.Match]:
    """Return first match from a list of regex patterns, or None."""
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m
    return None


def _extract_context(text: str, match: re.Match, chars: int = 300) -> str:
    """Return surrounding context around a regex match."""
    start = max(0, match.start() - 50)
    end = min(len(text), match.end() + chars)
    snippet = text[start:end].strip()
    # Collapse whitespace / newlines for readability
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet[:350]


# ─────────────────────────────────────────────────────────────────────────────
# Clause presence checks
# ─────────────────────────────────────────────────────────────────────────────

CLAUSE_PRESENCE_PATTERNS: dict[str, list[str]] = {
    "Governing Law": [
        r"\bgoverning law\b",
        r"\bgovern(?:ed|s) by the laws? of\b",
        r"\bapplicable law\b",
    ],
    "Jurisdiction": [
        r"\bjurisdiction\b",
        r"\bcourts? of\b",
        r"\bexclusive jurisdiction\b",
    ],
    "Termination": [
        r"\btermination\b",
        r"\bterminate\b",
        r"\bterminated\b",
    ],
    "Confidentiality": [
        r"\bconfidentiality\b",
        r"\bconfidential information\b",
        r"\bnon-disclosure\b",
        r"\bNDA\b",
    ],
    "Indemnification": [
        r"\bindemnif(?:y|ied|ication)\b",
        r"\bharmless\b",
        r"\bindemnity\b",
    ],
    "Limitation of Liability": [
        r"\blimitation of liability\b",
        r"\bliability.{0,30}shall not exceed\b",
        r"\bliability.{0,30}limited to\b",
        r"\bcap on liability\b",
    ],
    "Force Majeure": [
        r"\bforce majeure\b",
        r"\bact of god\b",
        r"\bcircumstances beyond.{0,20}control\b",
    ],
    "Dispute Resolution": [
        r"\bdispute resolution\b",
        r"\bdispute.{0,30}arbitration\b",
        r"\bresolv(?:e|ing).{0,30}dispute\b",
    ],
    "Arbitration": [
        r"\barbitration\b",
        r"\barbitrat(?:e|or)\b",
    ],
    "Intellectual Property": [
        r"\bintellectual property\b",
        r"\bIP rights?\b",
        r"\bcopyright\b",
        r"\bpatent\b",
        r"\btrademark\b",
    ],
    "Non-Compete / Non-Solicitation": [
        r"\bnon.compete\b",
        r"\bnon.solicit\b",
        r"\brestrictive covenant\b",
        r"\bcompetition.{0,20}restrict\b",
    ],
    "Data Protection / Privacy": [
        r"\bdata protection\b",
        r"\bpersonal data\b",
        r"\bprivacy\b",
        r"\bGDPR\b",
        r"\bPDPB\b",
        r"\bIT Act\b",
    ],
    "Assignment": [
        r"\bassignment\b",
        r"\bassign.{0,30}rights?\b",
        r"\btransfer.{0,30}rights?\b",
    ],
    "Notice Provisions": [
        r"\bnotice\b",
        r"\bwritten notice\b",
        r"\bnotification\b",
    ],
    "Payment": [
        r"\bpayment\b",
        r"\bfee\b",
        r"\bcompensation\b",
        r"\binvoice\b",
    ],
    "Representations and Warranties": [
        r"\brepresentations?\b",
        r"\bwarranties\b",
        r"\bwarranty\b",
        r"\bwarrants? that\b",
    ],
}

IMPORTANT_MISSING_CLAUSES = {
    "Limitation of Liability": MissingClause(
        title="Limitation of Liability",
        why_relevant=(
            "Without a liability cap, a party could be exposed to unlimited financial claims. "
            "Commercial contracts typically include a cap (often linked to fees paid) under "
            "Section 73 of the Indian Contract Act, 1872, which limits recoverable damages "
            "to those that arise naturally or were in contemplation of parties at the time "
            "of contracting."
        ),
        severity="HIGH",
    ),
    "Governing Law": MissingClause(
        title="Governing Law",
        why_relevant=(
            "Without a governing law clause, parties may dispute which jurisdiction's law applies "
            "in the event of a disagreement. This is particularly relevant for cross-border contracts."
        ),
        severity="HIGH",
    ),
    "Dispute Resolution": MissingClause(
        title="Dispute Resolution / Arbitration",
        why_relevant=(
            "Absence of a dispute resolution clause means parties would default to court litigation. "
            "Under the Arbitration and Conciliation Act, 1996 (India), parties may choose arbitration "
            "as a faster and private alternative — but only if agreed in writing."
        ),
        severity="MEDIUM",
    ),
    "Force Majeure": MissingClause(
        title="Force Majeure",
        why_relevant=(
            "Without a force majeure clause, non-performance due to extraordinary events "
            "(pandemics, natural disasters, war) may need to rely on Section 56 of the Indian "
            "Contract Act, 1872 (frustration of contract), which has a higher threshold and "
            "limited remedies."
        ),
        severity="MEDIUM",
    ),
    "Confidentiality": MissingClause(
        title="Confidentiality / Non-Disclosure",
        why_relevant=(
            "If the parties exchange sensitive commercial or technical information, a confidentiality "
            "clause should be present to prevent unauthorized disclosure. Without it, remedies rely "
            "on general equity principles, which are harder to enforce."
        ),
        severity="MEDIUM",
    ),
    "Termination": MissingClause(
        title="Termination",
        why_relevant=(
            "Without a termination clause, parties must rely on common law rights to rescind under "
            "Section 39 (anticipatory breach) or Section 62 (novation/rescission) of the Indian "
            "Contract Act, 1872. The absence of clear termination provisions can create uncertainty."
        ),
        severity="MEDIUM",
    ),
    "Notice Provisions": MissingClause(
        title="Notice Provisions",
        why_relevant=(
            "Without a notice clause, disputes may arise about whether and when notices (including "
            "termination notices) were validly served. This is especially important for triggering "
            "contractual rights."
        ),
        severity="LOW",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Risk analysis rules — each checks for risky language within found clauses
# ─────────────────────────────────────────────────────────────────────────────

def _check_unlimited_liability(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bunlimited liability\b",
        r"\bno limit(?:ation)? (?:on|of) liability\b",
        r"\bfull(?:y)? liable\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Unlimited Liability",
        what_it_says="The contract appears to impose liability without any financial cap.",
        potential_concern=(
            "One or both parties may be exposed to claims of any amount, potentially "
            "exceeding the value of the contract."
        ),
        why_it_matters=(
            "Without a limitation of liability clause, courts will award actual damages "
            "as proved. Under Section 73 of the Indian Contract Act, 1872, recoverable "
            "damages are those that arise naturally or were in reasonable contemplation — "
            "but there is no automatic cap."
        ),
        legal_basis="Indian Contract Act, 1872 — Section 73 (compensation for loss or damage caused by breach)",
        severity="HIGH",
        recommended_action=(
            "Negotiate a liability cap, typically set at the fees paid under the contract "
            "in the preceding 12 months. Obtain legal review to confirm appropriate cap level."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_unilateral_termination(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"terminat.{0,60}without (?:any |prior )?notice",
        r"terminat.{0,60}at (?:its |their |our )?(?:sole )?(?:and absolute )?discretion",
        r"terminat.{0,60}at will\b",
        r"immediately terminat",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Unilateral or Immediate Termination",
        what_it_says=(
            "A clause appears to allow one party to terminate the contract without notice or "
            "at their sole discretion."
        ),
        potential_concern=(
            "The other party may have no opportunity to remedy a default or prepare for termination, "
            "which could cause significant disruption."
        ),
        why_it_matters=(
            "While parties may contractually agree to termination without notice, abrupt termination "
            "may still give rise to claims under Section 73 (damages for breach) or Section 39 "
            "(anticipatory breach) of the Indian Contract Act, 1872, depending on circumstances."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — Sections 37 (obligation to perform), 39 (anticipatory breach), "
            "73 (compensation for breach)"
        ),
        severity="HIGH",
        recommended_action=(
            "Negotiate a cure period (typically 15–30 days for a material breach) before termination "
            "takes effect. Ensure termination rights are mutual or clearly justified."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_unilateral_discretion(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bsole (?:and absolute )?discretion\b",
        r"\bfull discretion\b",
        r"\babsolute discretion\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Sole / Absolute Discretion",
        what_it_says=(
            "One party appears to have the right to act in its 'sole' or 'absolute' discretion "
            "without requiring the other party's consent or meeting a stated standard."
        ),
        potential_concern=(
            "Unilateral discretion clauses may be exercised in a way that is unfavorable to the "
            "other party, with limited recourse."
        ),
        why_it_matters=(
            "Indian courts may imply an obligation of reasonableness or good faith in exercising "
            "contractual discretion in some contexts, though Indian law does not have a general "
            "implied duty of good faith as broadly as some common law jurisdictions."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — general principles; judicial interpretation in specific contexts "
            "(requires verification for the specific clause)"
        ),
        severity="MEDIUM",
        recommended_action=(
            "Negotiate an objective standard for exercising discretion (e.g., 'acting reasonably') "
            "or require the other party's prior written consent."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_broad_indemnity(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bindemnif.{0,100}(?:all|any|every).{0,30}(?:loss|claim|damage|cost|expense)",
        r"\bindemnif.{0,100}(?:whatsoever|howsoever|without limitation)",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Broad Indemnification",
        what_it_says=(
            "The indemnification clause appears to cover 'all' or unlimited losses, claims, "
            "damages, or costs."
        ),
        potential_concern=(
            "An overly broad indemnity may require one party to cover costs beyond what is "
            "reasonable or proportionate, including losses not directly caused by the indemnifying party."
        ),
        why_it_matters=(
            "Section 124 of the Indian Contract Act, 1872 defines a contract of indemnity as one "
            "where one party promises to save the other from loss caused by the promisor's own conduct "
            "or by the conduct of a third party. Courts may limit the scope of indemnities that appear "
            "disproportionate or that cover consequential losses beyond reasonable contemplation."
        ),
        legal_basis="Indian Contract Act, 1872 — Sections 124–125 (contract of indemnity)",
        severity="HIGH",
        recommended_action=(
            "Narrow the indemnity to losses arising directly from the indemnifying party's breach, "
            "negligence, or willful misconduct. Consider carving out consequential and indirect losses. "
            "Ensure the indemnity is mutual where appropriate."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_non_compete(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bnon.compet(?:e|ition)\b",
        r"\bnot.{0,20}compet(?:e|ing)\b",
        r"\brestrictive covenant\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Non-Compete / Restrictive Covenant",
        what_it_says=(
            "The contract contains a clause that appears to restrict one or both parties from "
            "competing or engaging in similar business activities."
        ),
        potential_concern=(
            "Post-term non-compete clauses restricting trade or employment are generally not "
            "enforceable in India when the restriction applies after the contract ends."
        ),
        why_it_matters=(
            "Section 27 of the Indian Contract Act, 1872 provides that every agreement in restraint "
            "of trade is void, with limited exceptions (such as sale of goodwill). The Supreme Court "
            "of India has interpreted this strictly. Post-employment non-competes are generally "
            "treated as void. However, restrictions during the contract term are generally valid."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — Section 27 (agreement in restraint of trade, void); "
            "subject to judicial interpretation in specific factual circumstances"
        ),
        severity="MEDIUM",
        recommended_action=(
            "Verify whether the non-compete restriction applies during or after the contract term. "
            "Post-term restrictions are likely unenforceable under Section 27. Seek legal review "
            "before relying on this clause."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_perpetual_obligation(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bperpetual\b",
        r"\bin perpetuity\b",
        r"\bforever\b",
        r"\bwithout (?:any )?time limit\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Perpetual Obligation",
        what_it_says=(
            "A clause imposes an obligation (such as confidentiality, license, or restriction) "
            "with no stated time limit — described as perpetual or in perpetuity."
        ),
        potential_concern=(
            "A perpetual obligation may be difficult to comply with indefinitely and may "
            "create unexpected long-term liabilities."
        ),
        why_it_matters=(
            "Courts may decline to enforce a perpetual obligation if it amounts to a "
            "restraint of trade (Section 27, Indian Contract Act, 1872) or if it is found "
            "to be unconscionable. However, perpetual confidentiality obligations for genuinely "
            "sensitive information are sometimes upheld."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — Section 27 (where applicable); general principles "
            "of contract enforceability"
        ),
        severity="MEDIUM",
        recommended_action=(
            "Negotiate a defined time period for the obligation (e.g., 3–5 years post-termination "
            "for confidentiality). Confirm whether a perpetual obligation is genuinely necessary "
            "for this clause."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_broad_waiver(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bwaives?\s+(?:any and )?all\s+(?:rights|claims|remedies)\b",
        r"\birrevocably waives?\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Broad Waiver of Rights",
        what_it_says=(
            "A clause contains a broad waiver of rights, claims, or remedies — potentially "
            "without defining the scope of what is being waived."
        ),
        potential_concern=(
            "A broad or irrevocable waiver may prevent a party from pursuing legitimate claims "
            "or remedies in the future, even where the waiving party was not aware of the full "
            "implications at the time of signing."
        ),
        why_it_matters=(
            "Under Section 62–63 of the Indian Contract Act, 1872, parties may agree to waive "
            "rights by novation, rescission, or alteration. However, courts may scrutinize "
            "waivers that appear to be obtained under unequal bargaining positions."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — Sections 62–63; general principles of waiver under "
            "Indian contract and equity law"
        ),
        severity="HIGH",
        recommended_action=(
            "Narrow the scope of the waiver to specifically identified rights or claims. "
            "Avoid blanket waivers. Seek legal review before agreeing to irrevocable waivers."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_automatic_renewal(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bauto(?:matically)?[\s-]renew\b",
        r"\brenew(?:al|ed|s)\b.{0,80}\bauto(?:matically)?\b",
        r"\bdeemed (?:to be )?renewed\b",
        r"\broll(?:s|ed)? over\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Automatic Renewal",
        what_it_says=(
            "The contract appears to renew automatically at the end of its term unless one "
            "party provides timely notice of non-renewal."
        ),
        potential_concern=(
            "Automatic renewal clauses may bind a party for an additional term if they fail "
            "to provide notice within the required window (which may be 30–90 days before expiry)."
        ),
        why_it_matters=(
            "While automatic renewal clauses are generally enforceable in India, failure to "
            "diarize renewal notice deadlines can result in unintended contractual commitments "
            "and potential liability for early termination fees."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — general principles of contract formation and consent; "
            "enforceability depends on specific clause language"
        ),
        severity="LOW",
        recommended_action=(
            "Note the notice-of-non-renewal deadline. Set a reminder well in advance. "
            "Negotiate a shorter notice period or manual renewal if automatic renewal is "
            "not operationally suitable."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_liquidated_damages(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bliquidated damages?\b",
        r"\bpenalty\b",
        r"\bpenalties\b",
        r"\bpre.determined (?:damages?|amount)\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Liquidated Damages / Penalties",
        what_it_says=(
            "The contract contains a clause for liquidated damages or penalties in the event "
            "of a specified breach or default."
        ),
        potential_concern=(
            "If the liquidated damages amount is disproportionate to the actual anticipated loss, "
            "it may be treated as a penalty clause and may not be enforceable in full."
        ),
        why_it_matters=(
            "Section 74 of the Indian Contract Act, 1872 provides that a party is entitled to "
            "receive a reasonable compensation — not exceeding the stipulated amount — regardless "
            "of whether actual loss is proved. The Supreme Court of India has clarified that "
            "Section 74 applies to both penalty and liquidated damages clauses, and courts will "
            "award only reasonable compensation."
        ),
        legal_basis=(
            "Indian Contract Act, 1872 — Section 74 (compensation for breach where penalty stipulated); "
            "Fateh Chand v. Balkishan Das, AIR 1963 SC 1405 (landmark SC interpretation)"
        ),
        severity="MEDIUM",
        recommended_action=(
            "Verify that the liquidated damages amount is a genuine pre-estimate of loss, "
            "not a punitive figure. Note that Indian courts may reduce the awarded amount "
            "under Section 74 if the sum is disproportionate."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_ip_assignment(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bIP.{0,20}(?:assign(?:ed|ment)|transfer(?:red)?|vest(?:s|ed)?)\b",
        r"\b(?:assign(?:ed|ment)|transfer(?:red)?|vest(?:s|ed)?).{0,20}IP\b",
        r"\bintellectual property.{0,50}(?:assign|transfer|vest|own)\b",
        r"\bwork(?:s)? (?:for hire|made for hire)\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Intellectual Property Assignment",
        what_it_says=(
            "The contract contains a clause relating to the assignment or transfer of "
            "intellectual property rights."
        ),
        potential_concern=(
            "IP assignment clauses may transfer ownership of valuable creations (software, "
            "designs, written works) from the creator to the commissioning party. The scope "
            "and future use rights should be clearly defined."
        ),
        why_it_matters=(
            "Under the Copyright Act, 1957 (India), an assignment of copyright must be in "
            "writing and signed by the assignor. The scope, purpose, territory, and duration "
            "of the assignment should be specified (Section 19). For patents, the Patents Act, "
            "1970 governs assignment."
        ),
        legal_basis=(
            "Copyright Act, 1957 — Section 19 (assignment of copyright must be in writing); "
            "Patents Act, 1970 — Section 68 (assignment of patents)"
        ),
        severity="MEDIUM",
        recommended_action=(
            "Confirm the scope of the IP assignment — whether it covers all IP or only "
            "project-specific work product. Negotiate a license-back if the creator needs "
            "to retain any usage rights. Ensure the assignment is in writing and properly "
            "executed as required by law."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_arbitration(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\barbitration\b",
        r"\barbitrat(?:e|or|ing)\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Arbitration Clause",
        what_it_says=(
            "The contract contains an arbitration clause, which appears to require disputes "
            "to be resolved through arbitration rather than court litigation."
        ),
        potential_concern=(
            "Arbitration clauses are generally enforceable in India under the Arbitration and "
            "Conciliation Act, 1996. However, specific details — such as the seat of arbitration, "
            "number of arbitrators, and institutional rules — are important."
        ),
        why_it_matters=(
            "If the seat of arbitration is outside India, different procedural rules and enforcement "
            "mechanisms apply. The seat determines the curial law. For domestic arbitrations, "
            "Indian courts have supervisory jurisdiction."
        ),
        legal_basis=(
            "Arbitration and Conciliation Act, 1996 (India) — particularly Sections 7 (arbitration "
            "agreement), 11 (appointment of arbitrators), and 34 (grounds to set aside award)"
        ),
        severity="LOW",
        recommended_action=(
            "Verify the seat of arbitration, governing rules (institutional vs. ad hoc), "
            "number of arbitrators, and language. Confirm that arbitration is suitable given "
            "the value and nature of potential disputes."
        ),
        matched_text=_extract_context(text, m),
    )


def _check_data_protection(text: str) -> Optional[ClauseReview]:
    m = _find([
        r"\bpersonal data\b",
        r"\bdata protection\b",
        r"\bprivacy\b",
        r"\bpersonal information\b",
        r"\bdata subject\b",
    ], text)
    if not m:
        return None
    return ClauseReview(
        title="Data Protection / Privacy",
        what_it_says=(
            "The contract references personal data, data protection, or privacy obligations."
        ),
        potential_concern=(
            "The Digital Personal Data Protection Act, 2023 (DPDPA) imposes obligations on "
            "entities that process personal data of Indian residents. The compliance requirements "
            "should be reflected in the contract."
        ),
        why_it_matters=(
            "If one party processes personal data on behalf of the other, the contract should "
            "clearly define data processing obligations, security measures, breach notification "
            "requirements, and data retention policies in line with the DPDPA, 2023. "
            "The Information Technology Act, 2000 and IT (Amendment) Act, 2008 may also apply "
            "to sensitive personal data."
        ),
        legal_basis=(
            "Digital Personal Data Protection Act, 2023 (India); "
            "Information Technology Act, 2000 — Section 43A (sensitive personal data)"
        ),
        severity="MEDIUM",
        recommended_action=(
            "Confirm whether the contract adequately addresses data processing obligations "
            "under the DPDPA, 2023. Consider adding specific data processing terms covering "
            "security, breach notification, sub-processor restrictions, and deletion obligations."
        ),
        matched_text=_extract_context(text, m),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Master analysis function
# ─────────────────────────────────────────────────────────────────────────────

_RISK_CHECKERS = [
    _check_unlimited_liability,
    _check_unilateral_termination,
    _check_unilateral_discretion,
    _check_broad_indemnity,
    _check_non_compete,
    _check_perpetual_obligation,
    _check_broad_waiver,
    _check_automatic_renewal,
    _check_liquidated_damages,
    _check_ip_assignment,
    _check_arbitration,
    _check_data_protection,
]


def review_contract(contract_text: str) -> ReviewResult:
    """
    Main entry point. Analyses the contract text and returns a ReviewResult
    containing:
      - clause_reviews: list of clauses identified with concerns
      - missing_clauses: list of important provisions not found
      - info_items: neutral informational notes
    """
    result = ReviewResult()

    # ── Step 1: Detect which standard clauses are present ───────────────────
    present_clause_types: set[str] = set()
    for clause_type, patterns in CLAUSE_PRESENCE_PATTERNS.items():
        m = _find(patterns, contract_text)
        if m:
            present_clause_types.add(clause_type)

    # ── Step 2: Identify missing important provisions ────────────────────────
    for clause_type, missing in IMPORTANT_MISSING_CLAUSES.items():
        if clause_type not in present_clause_types:
            result.missing_clauses.append(missing)

    # ── Step 3: Run language-based risk checkers ─────────────────────────────
    seen_titles: set[str] = set()
    for checker in _RISK_CHECKERS:
        review = checker(contract_text)
        if review and review.title not in seen_titles:
            seen_titles.add(review.title)
            result.clause_reviews.append(review)

    # ── Step 4: Info items — neutral observations ────────────────────────────
    if "Arbitration" in present_clause_types and "Jurisdiction" in present_clause_types:
        result.info_items.append(
            "Both an arbitration clause and a jurisdiction clause appear to be present. "
            "Verify whether they are consistent — arbitration clauses typically oust "
            "court jurisdiction for substantive disputes, while courts may retain supervisory "
            "jurisdiction over the arbitration."
        )
    if "Indemnification" in present_clause_types and "Limitation of Liability" in present_clause_types:
        result.info_items.append(
            "Both an indemnification clause and a limitation of liability clause are present. "
            "Confirm whether the liability cap applies to indemnification obligations — "
            "contracts sometimes exclude indemnities from the cap, which can significantly "
            "increase actual exposure."
        )
    if "Non-Compete / Non-Solicitation" in present_clause_types:
        result.info_items.append(
            "A non-compete or non-solicitation clause has been detected. Under Section 27 of "
            "the Indian Contract Act, 1872, post-term non-compete restrictions are generally "
            "void as restraint of trade. Restrictions during the contract term are typically valid."
        )

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Report formatter
# ─────────────────────────────────────────────────────────────────────────────

_SEVERITY_PRIORITY = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}


def format_review_report(
    result: ReviewResult,
    contract_name: str = "Contract",
) -> str:
    """
    Formats the ReviewResult into a Markdown string following the strict
    accuracy system prompt structure.
    """
    lines: list[str] = []

    high = [c for c in result.clause_reviews if c.severity == "HIGH"]
    medium = [c for c in result.clause_reviews if c.severity == "MEDIUM"]
    low = [c for c in result.clause_reviews if c.severity == "LOW"]

    high_missing = [m for m in result.missing_clauses if m.severity == "HIGH"]
    med_missing = [m for m in result.missing_clauses if m.severity == "MEDIUM"]
    low_missing = [m for m in result.missing_clauses if m.severity == "LOW"]

    # ── Executive Summary ────────────────────────────────────────────────────
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"**Document reviewed:** {contract_name}")
    lines.append(
        f"**Potentially important clauses identified:** "
        f"{len(result.clause_reviews)} issue(s) detected"
    )
    lines.append(
        f"**Missing provisions:** "
        f"{len(result.missing_clauses)} potentially missing clause(s)"
    )
    lines.append("")

    if high or high_missing:
        lines.append("**Key issues requiring attention (HIGH PRIORITY):**")
        for c in high:
            lines.append(f"- {c.title}")
        for m in high_missing:
            lines.append(f"- Potentially missing: {m.title}")
        lines.append("")

    if medium or med_missing:
        lines.append("**Medium priority issues:**")
        for c in medium:
            lines.append(f"- {c.title}")
        for m in med_missing:
            lines.append(f"- Potentially missing: {m.title}")
        lines.append("")

    if low or low_missing:
        lines.append("**Lower priority / informational:**")
        for c in low:
            lines.append(f"- {c.title}")
        for m in low_missing:
            lines.append(f"- Potentially missing: {m.title}")
        lines.append("")

    lines.append(
        "> **Disclaimer:** This review is generated by a local rule-based analysis system. "
        "It does not constitute legal advice. The analysis is based on pattern matching "
        "and predefined rules — it may miss clauses, misidentify risks, or be unable to "
        "interpret context. Always consult a qualified legal professional before acting "
        "on this review."
    )
    lines.append("")
    lines.append("---")

    # ── Clause-by-Clause Review ──────────────────────────────────────────────
    if result.clause_reviews:
        lines.append("")
        lines.append("## Clause-by-Clause Review")
        lines.append("")

        # Sort: HIGH → MEDIUM → LOW
        sorted_reviews = sorted(
            result.clause_reviews,
            key=lambda c: _SEVERITY_PRIORITY.get(c.severity, 9)
        )

        for i, cr in enumerate(sorted_reviews, start=1):
            sev_icon = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}.get(cr.severity, "⚪")
            lines.append(f"### {i}. {sev_icon} {cr.title} — **{cr.severity} PRIORITY**")
            lines.append("")
            lines.append(f"**What it says:**  \n{cr.what_it_says}")
            lines.append("")
            lines.append(f"**Potential concern:**  \n{cr.potential_concern}")
            lines.append("")
            lines.append(f"**Why it may matter:**  \n{cr.why_it_matters}")
            lines.append("")
            lines.append(f"**Legal basis:**  \n{cr.legal_basis}")
            lines.append("")
            lines.append(f"**Severity:** {cr.severity}")
            lines.append("")
            lines.append(f"**Recommended action:**  \n{cr.recommended_action}")
            if cr.matched_text:
                lines.append("")
                lines.append(
                    f"<details><summary>Matched contract text (excerpt)</summary>\n\n"
                    f"> {cr.matched_text}\n\n</details>"
                )
            lines.append("")
            lines.append("---")

    # ── Missing Clauses ──────────────────────────────────────────────────────
    if result.missing_clauses:
        lines.append("")
        lines.append("## Potentially Missing Provisions")
        lines.append("")
        lines.append(
            "> The following provisions were **not clearly detected** in the contract text. "
            "Their absence does not automatically make the contract defective, but they may "
            "be relevant depending on the nature of the agreement."
        )
        lines.append("")

        sorted_missing = sorted(
            result.missing_clauses,
            key=lambda m: _SEVERITY_PRIORITY.get(m.severity, 9)
        )
        for m in sorted_missing:
            sev_icon = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}.get(m.severity, "⚪")
            lines.append(f"- {sev_icon} **{m.title}** ({m.severity} PRIORITY)  ")
            lines.append(f"  {m.why_relevant}")
            lines.append("")

    # ── Informational Notes ──────────────────────────────────────────────────
    if result.info_items:
        lines.append("")
        lines.append("## Informational Notes")
        lines.append("")
        for note in result.info_items:
            lines.append(f"- {note}")
            lines.append("")

    # ── Risk Summary ─────────────────────────────────────────────────────────
    lines.append("")
    lines.append("## Risk Summary")
    lines.append("")
    lines.append("| Priority | Issues Found |")
    lines.append("|---|---|")
    lines.append(f"| HIGH | {len(high)} clause issue(s), {len(high_missing)} missing provision(s) |")
    lines.append(f"| MEDIUM | {len(medium)} clause issue(s), {len(med_missing)} missing provision(s) |")
    lines.append(f"| LOW | {len(low)} clause issue(s), {len(low_missing)} missing provision(s) |")
    lines.append("")
    lines.append(
        "> **Important:** This analysis does not assign an overall numeric risk score. "
        "Risk depends on the specific facts, the parties' bargaining positions, and the "
        "applicable legal context, which cannot be fully assessed by an automated tool."
    )

    return "\n".join(lines)
