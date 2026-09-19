"""
legal_qa_retrieval.py
-----------------------
Retrieval-based legal Q&A (Module 5). Replaces a conversational LLM
with two BM25 indexes -- no generation, no pretrained model.

Each FAQ entry uses a structured answer format:
  Definition / Legal Basis / Explanation / Example / Important Note

All legal citations have been verified against Indian statute text.
Content is general educational information -- NOT legal advice.
"""
import re
from rank_bm25 import BM25Okapi

TOKEN_RE = re.compile(r"\w+")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "me", "my", "we", "our", "you", "your", "it", "its",
    "and", "or", "but", "if", "in", "on", "at", "to", "for", "of",
    "by", "with", "about", "as", "into", "that", "this", "these", "those",
    "do", "does", "did", "have", "has", "had", "will", "would", "can",
    "could", "should", "may", "might", "shall", "what", "how", "when",
    "where", "who", "which", "why", "from", "not", "no",
}


def tokenize(text):
    """Tokenize text and remove stopwords for better BM25 discrimination."""
    if not text:
        return []
    tokens = TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


# ---------------------------------------------------------------------------
# FAQ Knowledge Base
# Each entry: question (for BM25 index), keywords (extra BM25 signal), answer
# Answers follow: Definition / Legal Basis / Explanation / Example / Important Note
# ---------------------------------------------------------------------------
FAQ_KB = [

    # =========================================================================
    # CONTRACT VALIDITY
    # =========================================================================
    {
        "question": "What makes a contract valid in India?",
        "keywords": "valid contract requirements offer acceptance consideration consent capacity lawful object Indian Contract Act 1872",
        "answer": """\
**Definition:**
A valid contract is a legally enforceable agreement between two or more parties.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 10, 11, 13, 23, and 25.

**Explanation:**
Section 10 of the Indian Contract Act, 1872 states that all agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object.

The essential elements are:
1. **Offer and Acceptance** (Sections 2(a) and 2(b)) — a clear proposal and its unconditional acceptance.
2. **Lawful Consideration** (Section 25) — something of value exchanged; a contract without consideration is generally void.
3. **Free Consent** (Section 14) — consent must not be obtained by coercion, undue influence, fraud, misrepresentation, or mistake.
4. **Competent Parties** (Section 11) — parties must be of the age of majority (18 years), of sound mind, and not disqualified by law.
5. **Lawful Object** (Section 23) — the purpose must not be forbidden by law, fraudulent, injurious to another, or against public policy.

**Example:**
A company signs a software services agreement with a vendor. Both parties are adults of sound mind, there is a service fee (consideration), both agreed without pressure, and the purpose is legal — this is a valid contract.

**Important Note:**
Meeting these elements creates a *presumptively* valid contract, but courts also consider whether the agreement is sufficiently certain in its terms (Section 29). The actual enforceability in a dispute depends on facts, evidence, and judicial interpretation. This is general information, not legal advice.""",
    },

    # =========================================================================
    # VOID vs VOIDABLE
    # =========================================================================
    {
        "question": "What is the difference between void and voidable contracts?",
        "keywords": "void voidable contract coercion undue influence fraud misrepresentation unlawful",
        "answer": """\
**Definition:**
A *void* contract has no legal effect from the outset. A *voidable* contract is valid but can be cancelled by one party under certain conditions.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 2(g), 2(i), 14, 15, 16, 17, 18, and 19.

**Explanation:**
- **Void contract (Section 2(g)):** An agreement that is not enforceable by law. It produces no legal rights or obligations. Examples: agreement with a minor (Section 11), agreement with an unlawful object (Section 23), agreement in restraint of trade (Section 27).
- **Voidable contract (Section 2(i)):** An agreement that is enforceable at the option of one of the parties. The affected party can either affirm or avoid the contract. A contract becomes voidable when consent is obtained by coercion (Section 15), undue influence (Section 16), fraud (Section 17), or misrepresentation (Section 18) — as provided in Section 19.

**Example:**
If a party signs a contract under threat (coercion), the contract is voidable at that party's option. If the party chooses to proceed, it remains valid; if they avoid it, the contract is rescinded.

**Important Note:**
The right to avoid a voidable contract may be lost if the aggrieved party affirms it, delays unreasonably, or if third-party rights have been created on the basis of the contract. Always consult a legal professional for the specific facts of your situation.""",
    },

    # =========================================================================
    # ORAL / VERBAL CONTRACT
    # =========================================================================
    {
        "question": "Is a verbal or oral agreement legally enforceable in India?",
        "keywords": "verbal oral agreement enforceable written proof evidence spoken",
        "answer": """\
**Definition:**
An oral (verbal) contract is an agreement made by spoken words, without a formal written document.

**Legal Basis:**
Indian Contract Act, 1872 — Section 10 (does not require writing as a general rule); Registration Act, 1908 — Section 17 (certain documents must be in writing and registered); Transfer of Property Act, 1882 (for immovable property transfers).

**Explanation:**
The Indian Contract Act, 1872 does not generally require a contract to be in writing. An oral agreement that satisfies all elements of Section 10 (offer, acceptance, consideration, free consent, competent parties, lawful object) is legally valid and enforceable.

However, certain types of agreements *must* be in writing and/or registered under specific laws:
- Sale of immovable property (Transfer of Property Act, 1882; Registration Act, 1908)
- Contracts of guarantee for some types (custom/commercial practice)
- Arbitration agreements (Arbitration and Conciliation Act, 1996 — Section 7)
- Insurance contracts, negotiable instruments, etc.

**Example:**
Two businesses orally agree on a 3-month consultancy arrangement with a defined fee. This oral contract is generally enforceable — but proving its terms in court without written evidence is very difficult.

**Important Note:**
Proving an oral contract in court depends entirely on oral testimony, witness evidence, or circumstantial evidence. Courts assess credibility and reliability. For any transaction of significance, a written, signed contract is strongly recommended. The enforceability of any specific oral agreement depends on facts and evidence.""",
    },

    # =========================================================================
    # MINOR IN CONTRACT
    # =========================================================================
    {
        "question": "Can a minor enter into a contract in India?",
        "keywords": "minor age majority 18 years capacity contract void child",
        "answer": """\
**Definition:**
A minor is a person who has not attained the age of majority — 18 years in most cases, or 21 years if a court of law has appointed a guardian for the person or property of the minor.

**Legal Basis:**
Indian Contract Act, 1872 — Section 11; Majority Act, 1875 — Section 3.

**Explanation:**
Section 11 of the Indian Contract Act, 1872 states that only persons who are of the age of majority are competent to contract. An agreement entered into with a minor is *void ab initio* (void from the beginning) — it has no legal effect and cannot be enforced against either party.

Importantly, in India (unlike English law), a minor's agreement cannot be ratified after the minor attains majority. The Supreme Court confirmed this in *Mohori Bibi v. Dharmodas Ghose* (1903), which held that a contract with a minor is void, not merely voidable.

**Example:**
A 16-year-old signs a loan agreement. The agreement is void from the start — the lender cannot enforce repayment under contract law. However, the minor may be required to restore any benefit received (under the law of restitution), depending on the facts.

**Important Note:**
While the contract itself is void, courts may still order restoration of benefits received by a minor under equitable principles. Also, a minor can be a beneficiary under a contract (e.g., receive a gift) but cannot be bound by obligations. Guardians can contract on behalf of minors in limited circumstances. The precise outcome depends on the specific facts and the court's findings.""",
    },

    # =========================================================================
    # CONSIDERATION
    # =========================================================================
    {
        "question": "What is consideration in a contract?",
        "keywords": "consideration price payment exchange promise value benefit",
        "answer": """\
**Definition:**
Consideration is something of value given by one party in exchange for the promise or act of the other party.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 2(d) and 25.

**Explanation:**
Section 2(d) defines consideration as: when at the desire of the promisor, the promisee or any other person has done or abstained from doing, or does or abstains from doing, or promises to do or abstain from doing something — that act or abstinence or promise is called consideration.

Key points:
- Consideration can be *past, present (executed), or future (executory)* — unlike English law which does not generally recognise past consideration.
- Consideration must move *at the desire of the promisor* (not a voluntary act of the promisee).
- Section 25 states that an agreement without consideration is generally *void*, with specific exceptions: natural love and affection between near relatives in a registered written agreement, compensation for a past voluntary act, a promise to pay a time-barred debt (in writing).

**Example:**
A purchases a laptop from B for Rs 50,000. A's promise to pay Rs 50,000 is the consideration for B's promise to deliver the laptop; B's delivery is consideration for A's payment.

**Important Note:**
Indian law does not require consideration to be adequate (courts will not question whether the exchange is fair in value), but it must be real and not illusory. Whether consideration is lawful depends on Section 23. Courts have occasionally distinguished token consideration from a complete absence of consideration, and results can depend on specific facts.""",
    },

    # =========================================================================
    # BREACH OF CONTRACT
    # =========================================================================
    {
        "question": "What is a breach of contract?",
        "keywords": "breach violation failure perform obligation remedy damages",
        "answer": """\
**Definition:**
A breach of contract occurs when a party fails or refuses to perform its obligations under a valid contract, without lawful excuse.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 37, 39, 73, 74, and 75; Specific Relief Act, 1963.

**Explanation:**
- **Section 37** requires parties to perform or offer to perform their respective promises unless performance is dispensed or excused.
- **Section 39** deals with *anticipatory breach* — where a party to a contract refuses to perform before the time for performance arrives.
- **Remedies:**
  - **Damages (Section 73):** Compensation for losses naturally arising from the breach. The injured party must mitigate its losses.
  - **Liquidated damages / penalty (Section 74):** Where a sum is agreed upon in advance, the court awards reasonable compensation not exceeding that sum, regardless of whether actual loss is proved.
  - **Specific Performance:** Under the Specific Relief Act, 1963, a court may direct the breaching party to actually perform the contract where monetary damages are inadequate.
  - **Injunction:** A court order restraining a party from doing something that would breach the contract.

**Example:**
A builder contracted to deliver a house by December 1. The builder fails to deliver by that date without any lawful excuse. The buyer can sue for damages under Section 73 — the costs reasonably incurred due to the delay.

**Important Note:**
Proving breach and quantifying damages requires evidence. The amount recoverable depends on the actual loss proved and the principle of mitigation. Consequential or remote losses may not be recoverable unless they were in the reasonable contemplation of both parties at the time of contracting (Section 73, proviso).""",
    },

    # =========================================================================
    # LIMITATION PERIOD
    # =========================================================================
    {
        "question": "What is the limitation period for filing a breach of contract claim in India?",
        "keywords": "limitation period 3 years breach contract suit file court",
        "answer": """\
**Definition:**
The limitation period is the maximum time within which a legal action must be filed after the cause of action arises.

**Legal Basis:**
Limitation Act, 1963 — Article 54 (for specific performance), Article 55 (for compensation for breach of contract), and the First Schedule generally.

**Explanation:**
Under the Limitation Act, 1963:
- A suit for *compensation for breach of contract* is generally governed by **Article 55** of the First Schedule — **3 years** from the date on which the contract is broken or (where the defendant repudiates the contract) from the date the plaintiff elects to treat it as broken.
- A suit for *specific performance* of a contract is governed by **Article 54** — **3 years** from the date fixed for performance, or if no date is fixed, when the plaintiff has notice that performance is refused.

The clock starts from the *date of accrual of the cause of action*, not the date the party discovers the breach.

**Example:**
If a supplier breaches a delivery contract on 1 January 2023, the buyer generally has until 31 December 2025 (3 years) to file a suit for damages.

**Important Note:**
This is a general rule. The precise article applicable, and the starting point of the limitation period, depends on the specific nature of the contract and the facts. Courts have held that acknowledgment of liability in writing or part payment by the defendant can extend the limitation period under Sections 18 and 19 of the Limitation Act, 1963. Always confirm with an advocate for your specific situation.""",
    },

    # =========================================================================
    # STAMP DUTY
    # =========================================================================
    {
        "question": "Does a contract need to be stamped to be valid in India?",
        "keywords": "stamp duty stamping Indian Stamp Act 1899 admissible evidence state",
        "answer": """\
**Definition:**
Stamp duty is a tax levied by the government on certain legal documents; a document is "stamped" when the prescribed duty is paid.

**Legal Basis:**
Indian Stamp Act, 1899 — Sections 17, 33, 35, and 38; state-level Stamp Acts (e.g., Maharashtra Stamp Act, 1958).

**Explanation:**
- Stamping does not determine the *validity* of a contract in most cases — an unstamped contract is not automatically void.
- However, under **Section 35 of the Indian Stamp Act, 1899**, an instrument chargeable to duty that is not duly stamped is *inadmissible in evidence* for any purpose. It cannot be acted upon, registered, or authenticated by a public officer until the deficient duty and the applicable penalty are paid.
- Stamp duty rates and the instruments that require stamping vary by state. Many states have adopted their own Stamp Acts or have amended the central Act.

**Example:**
A lease agreement for office premises is not adequately stamped. A party tries to produce it as evidence in court. The court can refuse to admit it as evidence until the deficiency plus penalty is paid (Section 35 procedure).

**Important Note:**
An inadequately stamped document *can* be admitted in evidence after payment of the deficient duty and penalty — it is not permanently excluded. The rates applicable depend on the type of instrument and the state. For any significant transaction, confirm the applicable stamp duty with a local advocate or the relevant Sub-Registrar before execution.""",
    },

    # =========================================================================
    # REGISTRATION
    # =========================================================================
    {
        "question": "When must a contract be registered in India?",
        "keywords": "registration compulsory immovable property Registration Act 1908 required",
        "answer": """\
**Definition:**
Registration is the process of recording a document with a government authority (the Sub-Registrar) to give it legal effect for certain transactions.

**Legal Basis:**
Registration Act, 1908 — Section 17 (compulsory registration), Section 49 (effect of non-registration); Transfer of Property Act, 1882.

**Explanation:**
**Section 17 of the Registration Act, 1908** lists instruments that must be compulsorily registered, including:
- Instruments of gift of immovable property.
- Non-testamentary instruments (e.g. sale deeds, mortgage deeds) creating, assigning, limiting, or extinguishing rights in immovable property of Rs 100 or more in value (the monetary threshold is nominal; the practical effect covers virtually all property transactions).
- Lease agreements for immovable property for a period exceeding one year (or for any term reserving a yearly rent).

**Section 49** provides that an unregistered document required to be registered cannot be admitted in evidence, and no court shall allow such a document to be used to affect immovable property unless it is registered.

Commercial contracts *not* involving immovable property (e.g. service agreements, vendor contracts, NDAs) are generally not required to be registered.

**Example:**
A sale deed for a flat must be registered before the Sub-Registrar. If it is not registered, neither party can produce it in court as proof of the sale.

**Important Note:**
The requirement and procedure for registration vary by state. Certain leases can be compulsorily or optionally registered depending on state rules. Registration does not by itself guarantee title or validity; it merely creates a record that is admissible in evidence.""",
    },

    # =========================================================================
    # GOVERNING LAW — SILENT
    # =========================================================================
    {
        "question": "What happens if a contract does not specify a governing law?",
        "keywords": "governing law silent conflict laws jurisdiction applicable",
        "answer": """\
**Definition:**
A governing law clause specifies which country's or state's law will be used to interpret and enforce the contract.

**Legal Basis:**
Private International Law principles as applied by Indian courts; the Indian Contract Act, 1872 (for domestic contracts).

**Explanation:**
If a contract is silent on governing law, Indian courts apply *conflict-of-laws* (private international law) principles to determine the applicable law. The generally accepted test is: **which law has the closest and most real connection to the transaction?** Factors considered include the place of contracting, place of performance, domicile of the parties, and the subject matter of the contract.

For purely domestic contracts (all parties and subject matter in India), Indian law applies as a matter of course.

**Example:**
An Indian company and a US company enter a services contract without a governing law clause. A dispute arises. An Indian court (if it has jurisdiction) will apply conflict-of-laws principles to determine whether Indian law or US law governs.

**Important Note:**
The absence of a governing law clause creates genuine uncertainty, particularly in cross-border transactions. Indian courts have applied different approaches in different fact patterns. In India, parties generally cannot choose a foreign law to govern a purely domestic contract. For cross-border contracts, a clearly drafted governing law and jurisdiction clause is strongly recommended. The outcome in any specific case depends on the facts and the court.""",
    },

    # =========================================================================
    # JURISDICTION CLAUSE
    # =========================================================================
    {
        "question": "What is a jurisdiction clause in a contract?",
        "keywords": "jurisdiction exclusive courts forum dispute resolution venue",
        "answer": """\
**Definition:**
A jurisdiction clause designates which court(s) have authority to hear and decide disputes arising from the contract.

**Legal Basis:**
Code of Civil Procedure, 1908 (CPC) — Section 20 (territorial jurisdiction); Indian Contract Act, 1872 — Section 28 (agreement in restraint of legal proceedings, with an exception).

**Explanation:**
An *exclusive jurisdiction clause* restricts the parties to litigating only in the specified court(s), ousting the jurisdiction of other courts that would otherwise have jurisdiction. Indian courts generally uphold such clauses between commercial parties as a matter of contract, so long as the chosen court *would otherwise have had jurisdiction* — the clause cannot confer jurisdiction on a court that has none under the CPC.

A *non-exclusive jurisdiction clause* submits the parties to the jurisdiction of named courts without preventing them from approaching other competent courts.

**Example:**
A contract between two Mumbai-based companies states: "Courts at Mumbai shall have exclusive jurisdiction." This clause is generally upheld, and a party who files suit in Delhi without a reason can be challenged on jurisdiction.

**Important Note:**
Section 28 of the Indian Contract Act, 1872 makes agreements that absolutely restrict a party from enforcing rights in courts void — but an exception in Section 28 allows parties to agree to limit proceedings to a particular court. The enforceability of jurisdiction clauses in specific cases depends on the facts, the nature of the agreement, and whether the chosen court had inherent jurisdiction. Always confirm with an advocate.""",
    },

    # =========================================================================
    # ARBITRATION
    # =========================================================================
    {
        "question": "How does arbitration work for Indian commercial contracts?",
        "keywords": "arbitration arbitrator Arbitration Conciliation Act 1996 award seat",
        "answer": """\
**Definition:**
Arbitration is a form of alternative dispute resolution where parties agree to have disputes decided by one or more neutral arbitrators instead of going to court.

**Legal Basis:**
Arbitration and Conciliation Act, 1996 (as amended in 2015 and 2019) — Sections 7 (arbitration agreement), 11 (appointment of arbitrator), 29A (time limit for award), 34 (setting aside award), and 36 (enforcement).

**Explanation:**
- An arbitration agreement must be in **writing** (Section 7).
- Parties may appoint arbitrators by agreement; if they cannot agree, the Supreme Court or High Court can appoint under Section 11.
- The **2015 amendment** introduced time limits: an arbitral award must be made within 12 months of the tribunal being constituted (extendable by 6 months with consent, and further by court order) — Section 29A.
- An arbitral award is **binding** on the parties and is enforced as if it were a decree of the court (Section 36), subject to the grounds for setting aside under Section 34 (e.g. incapacity, invalidity of agreement, public policy).
- The **seat of arbitration** determines the supervisory jurisdiction of Indian courts over the arbitration.

**Example:**
A construction contract contains: "All disputes shall be referred to a sole arbitrator appointed by mutual agreement, seated in Delhi, under the Arbitration and Conciliation Act, 1996." A dispute arises; the parties appoint an arbitrator; the arbitrator issues an award; the award is enforceable in court.

**Important Note:**
Arbitration does not eliminate court involvement — courts may intervene on appointment, interim relief (Section 9), and setting aside or enforcement of awards. The outcome of any arbitration depends on the specific arbitration agreement, the facts, and the arbitrator's findings.""",
    },

    # =========================================================================
    # MEDIATION vs ARBITRATION
    # =========================================================================
    {
        "question": "What is the difference between mediation and arbitration?",
        "keywords": "mediation arbitration ADR alternative dispute resolution settlement binding",
        "answer": """\
**Definition:**
Both are alternative dispute resolution (ADR) methods, but they differ fundamentally in process and outcome.

**Legal Basis:**
Arbitration and Conciliation Act, 1996 (arbitration); Mediation Act, 2023 (mediation); Code of Civil Procedure, 1908 — Section 89 (court referral to ADR).

**Explanation:**
| Feature | Mediation | Arbitration |
|---|---|---|
| Outcome | Non-binding (unless a settlement agreement is signed) | Binding award, enforceable as a court decree |
| Role of neutral | Facilitator; does not decide the dispute | Decides the dispute (like a judge) |
| Party control | Parties control the outcome | Arbitrator controls the decision |
| Governing law | Mediation Act, 2023 | Arbitration and Conciliation Act, 1996 |
| Confidentiality | Generally confidential | Generally confidential |

The **Mediation Act, 2023** provides a statutory framework for mediation in India, including pre-litigation mediation for commercial disputes, court-referred mediation, and online mediation. A mediated settlement agreement, once signed by the parties and the mediator, is enforceable as a court decree under Section 27 of the Mediation Act, 2023.

**Important Note:**
Mediation and arbitration clauses serve different purposes. Many contracts use a tiered clause: negotiation → mediation → arbitration. The enforceability of a mediated settlement, and the conduct of each process, depends on the specific agreement and applicable rules.""",
    },

    # =========================================================================
    # ELECTRONIC SIGNATURES
    # =========================================================================
    {
        "question": "Can an Indian company sign a contract electronically?",
        "keywords": "electronic digital signature IT Act 2000 valid e-sign online",
        "answer": """\
**Definition:**
An electronic signature is a digital means of signing a document without a handwritten signature.

**Legal Basis:**
Information Technology Act, 2000 — Sections 3 (digital signature), 3A (electronic signature), 5 (legal recognition), and the Second Schedule; Indian Contract Act, 1872 — Section 10 (does not require a particular form of signature).

**Explanation:**
- **Section 5 of the IT Act, 2000** provides that where a law requires information to be *authenticated* by a signature, it can be authenticated by an electronic signature.
- **Section 3** recognises digital signatures using asymmetric cryptosystem and hash function; **Section 3A** recognises other forms of electronic signatures prescribed by the central government.
- The **Second Schedule of the IT Act, 2000** lists documents that are *excluded* from the Act's applicability — these cannot be executed electronically and include: negotiable instruments (other than cheques), powers of attorney, trusts, wills, and contracts for sale or conveyance of immovable property.

**Example:**
A service agreement signed using a recognised e-signature platform (e.g. with an OTP or a digital signature certificate) is legally valid under the IT Act, 2000 for contracts that are not in the excluded list.

**Important Note:**
Not all e-signature methods have equal legal standing. A simple typed name in an email may not constitute a valid electronic signature under the IT Act in all contexts. The excluded categories (wills, property conveyances, powers of attorney) must still be executed in physical, handwritten form. Always verify with an advocate before relying on e-signatures for high-value or regulated transactions.""",
    },

    # =========================================================================
    # NDA — DEFINITION
    # =========================================================================
    {
        "question": "What is a Non-Disclosure Agreement NDA?",
        "keywords": "NDA non disclosure agreement confidential confidentiality secret proprietary information",
        "answer": """\
**Definition:**
A Non-Disclosure Agreement (NDA) — also called a Confidentiality Agreement — is a contract by which one or more parties agree to keep certain information confidential and not to disclose it to third parties without authorisation.

**Legal Basis:**
Indian Contract Act, 1872 — Section 10 (general contract validity); no specific statute governs NDAs in India; they are enforced as ordinary contracts. Specific remedies: Specific Relief Act, 1963; Code of Civil Procedure, 1908 (Order 39 — injunctions).

**Explanation:**
An NDA typically specifies:
- The *confidential information* covered (defined scope).
- The *disclosing party* and the *receiving party*.
- The *obligations* of the receiving party (not to disclose, use only for permitted purposes, protect with reasonable security).
- *Permitted disclosures* (e.g. to employees on a need-to-know basis, disclosure required by law).
- *Exclusions / carve-outs* (information already public, already known, independently developed).
- *Duration* of the obligation.
- *Remedies* for breach (damages; injunction is commonly sought since monetary damages may be difficult to quantify).

NDAs can be **unilateral** (one party discloses) or **mutual/bilateral** (both parties disclose).

**Example:**
Before sharing product designs with a potential manufacturer, a startup signs a mutual NDA. The manufacturer agrees not to copy or share the designs.

**Important Note:**
Indian courts have generally enforced NDAs as ordinary contracts. However, the enforceability of a specific NDA depends on its drafting, whether the definition of "confidential information" is sufficiently certain, and the facts of breach. Courts may limit remedies if the clause is overly broad.""",
    },

    # =========================================================================
    # NDA CARVE-OUTS
    # =========================================================================
    {
        "question": "What are the standard exclusions and carve-outs in an NDA?",
        "keywords": "NDA exclusions carve outs non disclosure exceptions public domain independently developed",
        "answer": """\
**Definition:**
NDA carve-outs (exclusions) are categories of information that are *not* treated as confidential under the agreement, even if they would otherwise fall within the definition of confidential information.

**Legal Basis:**
Indian Contract Act, 1872 — Section 23 (agreements against public policy are void); general principles of contract drafting. There is no specific Indian statute prescribing mandatory NDA exclusions — they are negotiated contractual provisions.

**Explanation:**
The following are widely recognised standard carve-outs in NDAs:

1. **Public domain:** Information that is or becomes publicly available through no breach by the receiving party.
2. **Prior knowledge:** Information the receiving party already knew before receiving it from the disclosing party, as evidenced by written records.
3. **Independent development:** Information the receiving party develops independently without reference to the confidential information.
4. **Third-party disclosure:** Information lawfully received from a third party who is not bound by any duty of confidence.
5. **Legal compulsion:** Information required to be disclosed by law, court order, regulatory authority, or stock exchange rules — typically with an obligation to give the disclosing party prior written notice where legally permissible.

**Example:**
A recipient company receives confidential data under an NDA. Later, the disclosing party publicly announces the same information in a press release. The carve-out for "public domain" information applies — the recipient is no longer bound to keep that specific information confidential.

**Important Note:**
The precise language of each carve-out matters greatly. Courts interpret exclusions based on their specific wording. A poorly drafted exclusion can be either too narrow (failing to protect the recipient) or too broad (gutting the NDA's protection). The burden of proving that an exclusion applies typically falls on the party claiming it.""",
    },

    # =========================================================================
    # NDA DURATION
    # =========================================================================
    {
        "question": "How long does an NDA last?",
        "keywords": "NDA duration term period confidentiality expires perpetual",
        "answer": """\
**Definition:**
The duration of an NDA is the period during which the confidentiality obligations remain in force.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 10 and 23 (general contract validity and public policy); no specific statutory limit on NDA duration in India.

**Explanation:**
NDA duration is determined by the parties and can take several forms:
- **Fixed term:** e.g. 2 years or 5 years from the date of the agreement or from the date of the last disclosure.
- **Relationship-linked:** the obligation lasts for the duration of the underlying business relationship plus a tail period (e.g. 2 years after termination).
- **Perpetual / indefinite:** for genuine trade secrets — courts in India have generally not struck down perpetual confidentiality obligations for true trade secrets, though excessively broad obligations might be scrutinised under public policy (Section 23).

**Example:**
A technology transfer agreement contains: "Confidentiality obligations shall survive termination of this Agreement for a period of 5 years." The recipient must keep the information confidential for 5 years after the agreement ends.

**Important Note:**
Indian courts have not definitively settled a fixed maximum permissible NDA duration. The reasonableness of duration may be assessed in light of the nature of the information and the parties' relationship. For particularly sensitive trade secrets, an indefinite period may be justified. For general business information, a shorter fixed term is more typical and more likely to be considered reasonable.""",
    },

    # =========================================================================
    # NON-COMPETE
    # =========================================================================
    {
        "question": "What is a non-compete clause and is it enforceable in India?",
        "keywords": "non compete restraint trade Section 27 void employment enforceable",
        "answer": """\
**Definition:**
A non-compete clause is a contractual provision that restricts a party — typically an employee or a business seller — from engaging in a competing business, profession, or trade for a specified period and/or within a specified geography.

**Legal Basis:**
Indian Contract Act, 1872 — Section 27.

**Explanation:**
**Section 27 of the Indian Contract Act, 1872** states: "Every agreement by which any one is restrained from exercising a lawful profession, trade, or business of any kind, is to that extent void."

This is a broad provision and Indian courts have consistently held that:
- **Post-employment non-compete clauses** (restrictions that apply *after* employment ends) are generally *void* under Section 27.
- **During-employment restrictions** (e.g. prohibition on simultaneously working for a competitor while employed) are generally enforceable, as the employee is bound by their duty of fidelity and the terms of service.
- **Sale of goodwill exception (Section 27, proviso):** A non-compete agreed upon in connection with the *sale of a business and its goodwill* is valid if it is reasonable in terms of geographical area and duration.

**Example:**
An IT employee's contract states they cannot join a competitor for 2 years after resignation. Under Section 27, this post-employment restriction is generally void in India, even if the employee signed it willingly.

**Important Note:**
This is a well-established position in Indian law, confirmed by multiple High Court decisions. However, the specific enforceability can depend on how the clause is drafted, the nature of the role, and the specific facts. Some courts have distinguished between preventing actual solicitation of clients or misuse of trade secrets (which may be separately enforceable) and a pure non-compete. This summary is general information — specific advice requires consultation with a legal professional.""",
    },

    # =========================================================================
    # INDEMNIFICATION
    # =========================================================================
    {
        "question": "What is an indemnification clause?",
        "keywords": "indemnification indemnity compensate losses damages liabilities third party claim",
        "answer": """\
**Definition:**
An indemnification clause is a contractual provision by which one party (the indemnitor) agrees to compensate the other party (the indemnitee) for specified losses, damages, claims, or liabilities.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 124 and 125 (contract of indemnity); Section 73 (general damages).

**Explanation:**
- **Section 124** defines a contract of indemnity as a contract by which one party promises to save the other from loss caused by the conduct of the promisor or by the conduct of any third person.
- **Section 125** provides the rights of the indemnity-holder when sued: the holder can recover all damages, costs, and sums paid in a suit covered by the indemnity, provided the holder acted as if the indemnifier were a party to the suit and had authorised the defence.

In commercial contracts, indemnification clauses often cover:
- Third-party claims (e.g. IP infringement claims against the indemnitee).
- Losses arising from the indemnitor's breach.
- Regulatory fines or penalties.

**Example:**
A software vendor's contract states: "Vendor shall indemnify Client against any third-party claim that the software infringes any intellectual property right." If a third party sues the Client, the Vendor must cover the resulting costs and damages.

**Important Note:**
Indian courts apply Sections 124–125, which are slightly narrower than the broad common-law formulations seen in international contracts. A one-sided indemnity (only one party indemnifying) is common but increases the indemnitor's risk. The enforceability and scope of any indemnity depends on its exact wording, the circumstances of the loss, and judicial interpretation.""",
    },

    # =========================================================================
    # INDEMNITY vs WARRANTY
    # =========================================================================
    {
        "question": "What is the difference between an indemnity and a warranty?",
        "keywords": "indemnity warranty difference damages breach representation factual assurance",
        "answer": """\
**Definition:**
A *warranty* is a contractual promise that certain facts are or will be true. An *indemnity* is a standalone promise to compensate for specified losses, regardless of whether there was a breach.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 12, 124 (indemnity); Sale of Goods Act, 1930 — Sections 12–14 (conditions and warranties in sale of goods).

**Explanation:**
| Feature | Warranty | Indemnity |
|---|---|---|
| Nature | Contractual promise about facts | Standalone compensation promise |
| Basis of claim | Breach of the warranty term | Loss covered by the indemnity clause |
| Proof required | Must prove breach; loss flows from breach | Must prove loss falls within the indemnity scope |
| Causation | Loss must flow from breach | Direct compensation; causation rules may differ |
| Defences | Mitigation, contributory acts | Depends on indemnity wording |

A warranty claim under general contract law requires proving a breach and that the loss flows from the breach (Section 73 principles). An indemnity is broader — it can cover losses that are not traceable to a specific breach, and can also cover third-party claims.

**Example:**
A seller warrants that goods are free of defects (warranty) and also indemnifies the buyer against third-party product liability claims (indemnity). If a defect causes a third party to sue the buyer, the indemnity directly covers the buyer's costs even if the warranty claim would have a causation issue.

**Important Note:**
The distinction has significant practical consequences in drafting and litigation. The precise effect of any warranty or indemnity clause depends on its specific wording, the governing law, and the facts of the claim.""",
    },

    # =========================================================================
    # LIABILITY CAP
    # =========================================================================
    {
        "question": "What is an indemnification cap or limitation of liability?",
        "keywords": "indemnification cap liability limit maximum ceiling amount damages capped",
        "answer": """\
**Definition:**
A liability cap is a contractual ceiling on the total amount of damages or indemnification that one party can claim from the other.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 73 and 74; general freedom of contract under Section 10.

**Explanation:**
Parties may agree to limit liability through a cap. Indian courts have generally upheld agreed caps between commercial parties under the principle of freedom of contract.

Common cap structures:
- Equal to the total fees paid under the contract in the preceding 12 months.
- A fixed specified sum.
- A multiple of the annual contract value.

Certain losses are commonly **carved out from the cap** (not subject to it):
- Fraud or wilful misconduct.
- Death or personal injury caused by negligence.
- IP indemnification obligations.
- Confidentiality breaches.
- Statutory liabilities that cannot be excluded by contract.

**Example:**
A technology services contract states: "Neither party's total liability shall exceed Rs 10 lakhs, except for claims arising from fraud or death/personal injury." If a party claims Rs 50 lakhs in damages from a service failure, it can only recover up to Rs 10 lakhs under the contract.

**Important Note:**
A liability cap cannot exclude liability for fraud or fraudulent misrepresentation. Under Section 23 of the Indian Contract Act, agreements that attempt to exclude liability for a party's own fraud may be void as against public policy. Consumer protection laws (Consumer Protection Act, 2019) may also override contractual liability limits in consumer contracts.""",
    },

    # =========================================================================
    # FORCE MAJEURE
    # =========================================================================
    {
        "question": "What is a force majeure clause?",
        "keywords": "force majeure extraordinary event natural disaster war government impossibility impracticable",
        "answer": """\
**Definition:**
A force majeure clause is a contractual provision that excuses one or both parties from performing their obligations when an extraordinary event beyond their control makes performance impossible or fundamentally impracticable.

**Legal Basis:**
Indian Contract Act, 1872 — Section 56 (doctrine of frustration); contractual force majeure clauses (separate from Section 56).

**Explanation:**
**Two distinct legal bases exist in India:**

1. **Contractual force majeure clause:** A negotiated provision that lists specific triggering events (e.g. natural disaster, war, epidemic, government order, strike) and prescribes the consequences (suspension, notice obligation, termination after a prolonged period). The scope is entirely determined by the clause's drafting.

2. **Section 56 — Doctrine of Frustration:** Even without a contractual clause, Section 56 provides that a contract becomes void if, after it is made, an act that is the basis of the contract becomes impossible or unlawful due to an event the promisor could not prevent. The standard under Section 56 is "impossibility," which courts have interpreted as including practical impossibility in some cases, but not mere commercial hardship.

The Supreme Court in *Energy Watchdog v. Central Electricity Regulatory Commission* (2017) distinguished between contractual force majeure clauses and the statutory doctrine of frustration under Section 56.

**Example:**
A government lockdown prevents a contractor from supplying goods. If the contract has a force majeure clause covering "government orders," the contractor may invoke it to suspend performance. Without such a clause, the contractor would need to rely on Section 56.

**Important Note:**
Whether a force majeure clause or Section 56 applies depends on the specific events listed, the notice requirements, and whether performance is truly impossible or merely more difficult (commercial hardship alone generally does not suffice). Courts assess force majeure claims on a case-by-case basis.""",
    },

    # =========================================================================
    # TERMINATION
    # =========================================================================
    {
        "question": "How can a contract be terminated in India?",
        "keywords": "terminate termination end contract notice mutual agreement breach frustration",
        "answer": """\
**Definition:**
Termination of a contract is the lawful ending of contractual obligations between the parties.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 37, 39, 56, 62, 63, 73; Specific Relief Act, 1963.

**Explanation:**
A contract may be terminated in the following ways:

1. **Performance (Section 37):** Both parties fully perform their obligations — the contract is discharged.
2. **Mutual agreement (Section 62):** Parties agree to rescind, alter, or substitute the contract — novation, rescission, or alteration.
3. **Acceptance of breach / repudiation (Section 39):** If one party repudiates the contract (refuses to perform), the other party can accept the repudiation and treat the contract as terminated, then claim damages.
4. **Frustration (Section 56):** An event beyond the parties' control makes performance impossible or unlawful — the contract becomes void.
5. **Express termination clause:** Most commercial contracts include a notice-based termination right (for cause and/or convenience). The party must follow the notice procedure specified in the contract.

**Example:**
A services agreement allows either party to terminate with 60 days' written notice. Party A sends written notice on 1 September. The contract terminates on 31 October. Fees for services rendered up to 31 October remain payable.

**Important Note:**
Terminating a contract in breach of its terms (e.g. without serving the required notice) can itself constitute a breach, entitling the other party to damages. Whether a termination is valid depends on whether the contractual procedure was followed, the facts, and any court findings.""",
    },

    # =========================================================================
    # TERMINATION FOR CONVENIENCE
    # =========================================================================
    {
        "question": "What is a termination for convenience clause?",
        "keywords": "termination convenience without cause notice period exit",
        "answer": """\
**Definition:**
A termination for convenience clause allows one or both parties to end the contract without needing to prove a breach or other legal ground, simply by giving advance notice.

**Legal Basis:**
Indian Contract Act, 1872 — Section 10 (freedom of contract); Sections 73–75 (consequences on termination).

**Explanation:**
This clause is a product of freedom of contract — the parties may agree to allow exit without cause. Key features:
- A specified notice period must be served (e.g. 30, 60, or 90 days).
- No reason for termination needs to be given.
- Upon termination, the terminating party typically pays for all work done and costs incurred up to the termination date.
- Some clauses include a "termination fee" payable if convenience termination is exercised.

This type of clause is particularly common in long-term service agreements, government contracts, and outsourcing arrangements.

**Example:**
A company hires a consultant under a 2-year agreement with a "termination for convenience" clause requiring 90 days' notice. After 6 months, the company exercises the clause. The consultant is entitled to fees for 6 months of work plus the 90-day notice period.

**Important Note:**
The presence of a termination for convenience clause does not eliminate liability for amounts accrued before termination. Indian courts have in some cases scrutinised whether such clauses were exercised in good faith, particularly in government contracts (where principles of legitimate expectation may apply). The specific consequences depend on the contract's wording.""",
    },

    # =========================================================================
    # IP OWNERSHIP
    # =========================================================================
    {
        "question": "Who owns IP created under a contract in India?",
        "keywords": "intellectual property IP ownership copyright work for hire assignment contractor employee",
        "answer": """\
**Definition:**
IP (intellectual property) ownership under a contract determines who holds the rights to creations (software, designs, inventions, etc.) produced during the contractual relationship.

**Legal Basis:**
Copyright Act, 1957 — Section 17 (first owner of copyright); Patents Act, 1970 — Section 6 (who may apply for patent); Indian Contract Act, 1872 — Section 10 (for IP assignment agreements).

**Explanation:**

**Copyright:**
- **Employee (Section 17, Copyright Act, 1957):** Where a work is created by an author in the course of their *employment under a contract of service*, in the absence of any agreement to the contrary, the *employer* is the first owner of the copyright.
- **Independent contractor:** Unlike employment, there is no automatic "work-for-hire" rule for independent contractors in India. Copyright vests in the *contractor* (the actual creator) unless there is an explicit written assignment to the client.

**Patents:**
- Under Section 6 of the Patents Act, 1970, a patent can be applied for by the *inventor* or their assignee. An employer does not automatically own an employee's invention unless there is a contractual assignment or the invention was made specifically as part of the employee's duties.

**Example:**
A freelance developer builds a mobile app for a startup under a service contract. Unless the contract contains an explicit IP assignment clause, the developer retains copyright in the code. The startup should include a clause: "All IP created under this agreement is assigned to [Client] upon payment."

**Important Note:**
For contractors and vendors, always include a clear, specific written IP assignment clause. Merely paying for the work does not transfer copyright in India. The assignment must cover all relevant IP rights and should be signed by the creator.""",
    },

    # =========================================================================
    # PENALTY / LIQUIDATED DAMAGES
    # =========================================================================
    {
        "question": "What is a penalty clause and are penalty clauses enforceable in India?",
        "keywords": "penalty clause liquidated damages pre-estimated loss breach Section 74",
        "answer": """\
**Definition:**
A penalty clause (or liquidated damages clause) is a contractual provision that specifies a sum payable by a party in the event of a breach.

**Legal Basis:**
Indian Contract Act, 1872 — Section 74.

**Explanation:**
**Section 74 of the Indian Contract Act, 1872** provides: "When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such breach... the party complaining of the breach is entitled, whether or not actual damage or loss is proved to have been caused thereby, to receive from the party who has broken the contract *reasonable compensation not exceeding the amount so named*."

This is significantly different from English law. In India:
- Courts do **not** apply a penalty/liquidated damages distinction that results in striking out the clause entirely.
- The clause is treated as an *upper ceiling* — the court will award what is *reasonable*, which may be less than the named sum, and cannot exceed it.
- The claimant need not prove actual loss (in contrast to general damages under Section 73), but the court still awards only reasonable compensation.

**Example:**
A contract states: "Supplier shall pay Rs 1 lakh per day of delay." The supplier delays by 5 days. Even if the buyer's actual loss was only Rs 2 lakhs, the buyer can claim up to Rs 5 lakhs (5 × Rs 1 lakh), but the court will award only *reasonable compensation* not exceeding that cap.

**Important Note:**
What constitutes "reasonable compensation" under Section 74 is determined by the court on the facts. Courts have held that a nominal or token liquidated damages clause does not prevent a party from proving actual loss (Section 73 may then apply). The outcome of any specific penalty clause dispute depends on the facts and the court's assessment.""",
    },

    # =========================================================================
    # OFFER AND ACCEPTANCE
    # =========================================================================
    {
        "question": "What constitutes a valid offer and acceptance in India?",
        "keywords": "offer acceptance proposal communication definite unconditional",
        "answer": """\
**Definition:**
An offer (proposal) is a communication of willingness to do or abstain from doing something, with the intention that the other party signify acceptance. Acceptance is the unconditional assent to the offer.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 2(a), 2(b), 4, 5, 6, 7, and 9.

**Explanation:**
- **Offer (Section 2(a)):** A proposal is made when one person signifies to another his willingness to do or abstain from doing anything, with a view to obtaining that other person's assent.
- **Communication of offer (Section 4):** The communication of an offer is complete when it comes to the knowledge of the person to whom it is made.
- **Acceptance (Section 7):** Acceptance must be *absolute and unqualified*. A conditional or qualified acceptance is a *counter-offer*, which terminates the original offer.
- **Communication of acceptance (Section 4):** As against the proposer, communication is complete when it is put in the course of transmission so as to be out of the power of the acceptor (e.g. when a letter is posted). As against the acceptor, when it comes to the proposer's knowledge.
- **Revocation (Sections 5–6):** An offer may be revoked before its acceptance is complete as against the proposer. Acceptance may be revoked before the communication of acceptance is complete as against the acceptor.

**Example:**
A sends B an email offering to sell goods for Rs 10,000. B replies "I accept, but at Rs 9,000." This is a counter-offer — A's original offer is terminated. If B then says "I accept at Rs 10,000," it is a new acceptance, not an acceptance of the original offer.

**Important Note:**
Silence does not constitute acceptance under Indian law. The precise moment of contract formation (especially in digital/email communications) can affect legal rights significantly.""",
    },

    # =========================================================================
    # TENDER
    # =========================================================================
    {
        "question": "What is a tender in Indian contract and procurement law?",
        "keywords": "tender bid procurement government public contract invitation ITT RFP RFQ quote offer",
        "answer": """\
**Definition:**
In Indian law, "tender" has two distinct meanings depending on context.

**Legal Basis:**
(1) Procurement: General Financial Rules (GFR), 2017; Central Vigilance Commission guidelines; applicable state procurement rules; Manual on Policies and Procedures for Purchase of Goods (Ministry of Finance).
(2) Contract law: Indian Contract Act, 1872 — Section 38.

**Explanation:**

**(1) Tender in Procurement / Government Contracts:**
A tender is a formal invitation by a purchaser (usually a government entity or a public sector undertaking) to potential suppliers to submit competitive bids for the supply of goods or services. Types under GFR 2017:
- **Open tender enquiry:** Advertised publicly; open to all eligible vendors.
- **Limited tender enquiry:** Issued to a selected list of registered vendors.
- **Single tender enquiry:** Issued to one specific vendor (used in exceptional circumstances).
A bid submitted in response to a tender is the vendor's *offer*; acceptance by the purchaser creates a contract.

**(2) Tender of Performance (Contract Law):**
Under **Section 38 of the Indian Contract Act, 1872**, a "tender of performance" means a promisor formally offering to perform their contractual obligation. If the promisee refuses to accept a valid tender, the promisor is discharged from liability for non-performance and does not lose their rights under the contract. A valid tender must be unconditional, made at the proper time and place, and cover the whole obligation.

**Example:**
(Procurement) A government ministry issues a tender for IT services. Five companies submit bids. The ministry accepts the lowest qualified bid — forming a contract.
(Contract law) A buyer tenders payment of the contract price to the seller, who refuses to deliver. The buyer is protected: the seller cannot later claim non-payment.

**Important Note:**
Government procurement tenders are subject to judicial review under Article 226 of the Constitution if they violate principles of fairness or public law. Courts have held that government entities must act fairly in the tender process (*Tata Cellular v. Union of India*, 1994).""",
    },

    # =========================================================================
    # TENDER OF PERFORMANCE
    # =========================================================================
    {
        "question": "What is tender of performance under the Indian Contract Act?",
        "keywords": "tender performance offer discharge obligation Section 38 refusal accept",
        "answer": """\
**Definition:**
Tender of performance is the act of a promisor formally offering to fulfil their contractual obligation in the manner and at the time specified in the contract.

**Legal Basis:**
Indian Contract Act, 1872 — Section 38.

**Explanation:**
**Section 38 of the Indian Contract Act, 1872** provides: "Where a promisor has made an offer of performance to the promisee, and the offer has not been accepted, the promisor is not responsible for non-performance, nor does he thereby lose his rights under the contract."

For a tender to be valid (Section 38, proviso):
1. It must be *unconditional*.
2. It must be made at a proper time and place.
3. It must be of the whole obligation.
4. The person tendering must have a reasonable opportunity to ensure that the person to whom tender is made is the promisee.

**Example:**
Under a sale contract, the seller is required to deliver goods on 1 October. The seller arrives at the buyer's warehouse on 1 October with the goods, but the buyer refuses to accept delivery. The seller has made a valid tender of performance — the seller's obligation is discharged, and the seller may claim breach of contract against the buyer.

**Important Note:**
A tender of money (e.g. payment) that is refused does not extinguish the debt itself under Indian law — the obligation to pay continues. However, the creditor who refuses a valid tender cannot claim interest for the period after the tender (Section 38, third proviso).""",
    },

    # =========================================================================
    # DEFENDANT
    # =========================================================================
    {
        "question": "Who is a defendant in a civil case?",
        "keywords": "defendant plaintiff civil suit party sued respondent CPC accused",
        "answer": """\
**Definition:**
In a civil lawsuit, the *defendant* is the party against whom the suit is filed and who is required to answer the plaintiff's claim.

**Legal Basis:**
Code of Civil Procedure, 1908 (CPC) — Order 1 (parties to suit), Order 8 (written statement and set-off), Order 7 (plaint); Constitution of India — Article 21 (right to fair procedure).

**Explanation:**
- **Plaintiff:** The party who initiates a civil suit by filing a *plaint* before a court of competent jurisdiction.
- **Defendant:** The party named in the plaint as having committed the alleged wrong or being liable for the relief sought. The defendant must file a *written statement* (reply) within 30 days of service of summons, extendable to a maximum of 90 days by the court (Order 8, Rule 1, CPC as amended by the Commercial Courts Act, 2015 for commercial disputes).
- In *appeals*, the terms shift: the party filing the appeal is the *appellant* and the other party is the *respondent*.
- In *arbitration*, parties are typically called *claimant* and *respondent*.
- In *criminal proceedings*, the accused is tried by the State; there is no "plaintiff" or "defendant" in the civil sense.

**Example:**
A company files a suit for recovery of money against a former partner. The company is the plaintiff; the former partner is the defendant. The defendant must file a written statement in response.

**Important Note:**
The defendant has constitutional protections under Article 21 (right to fair procedure) and statutory rights under the CPC. Being named as a defendant does not constitute a finding of liability — liability is determined only after a full hearing on evidence. The outcome of any civil case depends on the facts, evidence, and judicial findings.""",
    },

    # =========================================================================
    # DEFENDANT RIGHTS
    # =========================================================================
    {
        "question": "What rights does a defendant have in a civil contract dispute in India?",
        "keywords": "defendant rights written statement reply defence set off counterclaim CPC",
        "answer": """\
**Definition:**
The rights of a defendant in a civil suit are the procedural and substantive entitlements that allow the defendant to contest the plaintiff's claims.

**Legal Basis:**
Code of Civil Procedure, 1908 (CPC) — Order 8 (written statement, set-off, counter-claim), Order 11 (discovery), Order 18 (cross-examination), Order 41 (appeals); Constitution of India — Article 21.

**Explanation:**
Key rights of a defendant in an Indian civil suit:

1. **Right to be heard (Order 8):** File a written statement presenting defences, deny the plaintiff's claims, and raise preliminary objections (e.g. lack of jurisdiction, limitation, misjoinder of parties).
2. **Set-off (Order 8, Rule 6):** If the defendant has a money claim against the plaintiff arising from the same subject matter, the defendant can set it off against the plaintiff's claim in the same suit.
3. **Counterclaim (Order 8, Rule 6A):** The defendant can file a counterclaim for any cause of action (not limited to the subject matter of the suit) — essentially a cross-suit within the same proceedings.
4. **Discovery and inspection (Order 11):** Request production of documents from the plaintiff.
5. **Cross-examination (Order 18):** Cross-examine the plaintiff's witnesses.
6. **Right to appeal:** Challenge adverse orders or the final decree before the appellate court (Order 41).
7. **Stay / interim relief (Order 39):** Apply for stay or injunction if the plaintiff's conduct is causing harm.

**Important Note:**
These rights are subject to the court's discretion and procedural rules. Courts may impose costs or adverse inferences if procedural obligations are not met. The CPC applies to civil suits; separate procedural rules apply in arbitration and before consumer forums or tribunals.""",
    },

    # =========================================================================
    # AUTHORISED SIGNATORY
    # =========================================================================
    {
        "question": "Who can be an authorised signatory for a company in India?",
        "keywords": "authorised signatory company board resolution director power attorney Companies Act 2013",
        "answer": """\
**Definition:**
An authorised signatory is a person who has been legally empowered to sign contracts and other documents on behalf of a company.

**Legal Basis:**
Companies Act, 2013 — Sections 2(60) (officer who is in default), 179 (powers of board), 180; Indian Contract Act, 1872 — Section 10; Powers-of-Attorney Act, 1882.

**Explanation:**
A company is a separate legal person and acts through its agents — human beings authorised by the board of directors.

**Who may be authorised:**
- **Directors** — individually authorised by the board or by the company's Articles of Association (AoA).
- **Company Secretary** — authorised for specified filings and communications.
- **Any officer or employee** — granted authority by a *Board Resolution* specifying the scope of authority (e.g. "to sign contracts up to Rs 50 lakhs").
- **External agents** — via a registered *Power of Attorney* (PoA) granted by the board.

**What the signatory should establish:**
- Name and designation.
- The specific authority document (Board Resolution or PoA) under which they sign.
- The company's CIN (Corporate Identification Number) for formal documents.

**Example:**
The board passes a resolution: "Mr A, Director, is authorised to sign all vendor contracts on behalf of the company." Mr A signs a vendor agreement — it is binding on the company.

**Important Note:**
Signing a contract without proper authority (ultra vires the agent's authorisation) may render it unenforceable against the company, or may expose the signatory to personal liability. Always verify authority before relying on a counterparty's signatory. The doctrine of indoor management (*Royal British Bank v. Turquand*) generally protects third parties who rely on ostensible authority in good faith.""",
    },

    # =========================================================================
    # ASSIGNMENT
    # =========================================================================
    {
        "question": "Can contractual rights be assigned to a third party in India?",
        "keywords": "assignment assign novation third party rights transfer",
        "answer": """\
**Definition:**
Assignment is the transfer of contractual rights (or benefits) from one party (the assignor) to a third party (the assignee), without the need for a new contract.

**Legal Basis:**
Indian Contract Act, 1872 — Section 37 (performance by agent); Transfer of Property Act, 1882 — Section 130 (assignment of actionable claims); Indian Contract Act, 1872 — Sections 15–16 (no general section on assignment, but the courts apply common law principles).

**Explanation:**
The Indian Contract Act does not contain a general provision expressly dealing with assignment of contractual rights. However, the courts have recognised the following principles:

- **Rights (benefits)** can generally be assigned, unless the rights are personal in nature (i.e. dependent on the skill, judgment, or identity of the original party — e.g. a contract for personal services).
- **Obligations (burdens)** *cannot* be unilaterally assigned — assigning obligations requires *novation*, which is a tripartite agreement between the original parties and the new party (Section 62).
- Many commercial contracts include an **anti-assignment clause** requiring the other party's prior written consent.
- **Actionable claims** (e.g. a debt, a contractual right to money) can be assigned under Section 130 of the Transfer of Property Act, 1882 by a written instrument signed by the assignor.

**Example:**
A supplier is owed Rs 5 lakhs by a buyer under a supply contract. The supplier assigns this debt to a bank (as part of invoice discounting). The bank can now collect the Rs 5 lakhs directly from the buyer.

**Important Note:**
Whether a specific contractual right is assignable depends on the nature of the contract and its terms. Anti-assignment clauses are enforceable. Courts assess each case on its facts. If in doubt, obtain explicit consent from the counterparty in writing.""",
    },

    # =========================================================================
    # POWER OF ATTORNEY
    # =========================================================================
    {
        "question": "What is a Power of Attorney PoA in India?",
        "keywords": "power of attorney POA agent principal authority act behalf registered",
        "answer": """\
**Definition:**
A Power of Attorney (PoA) is a legal instrument by which one person (the *principal* or *donor*) grants authority to another person (the *attorney* or *agent*) to act on the principal's behalf in legal, financial, or business matters.

**Legal Basis:**
Powers-of-Attorney Act, 1882 — Sections 1A (definitions), 2 (acts under PoA); Registration Act, 1908 — Section 17 (compulsory registration for PoAs related to immovable property); Indian Stamp Act, 1899 (stamp duty on PoA).

**Explanation:**
Types:
- **General PoA:** Grants broad authority to act in various matters.
- **Special / Limited PoA:** Grants authority for a specific act or a defined set of acts only.
- **Durable PoA:** Remains valid even if the principal becomes incapacitated (not explicitly codified in India, but courts have recognised it in certain contexts).

**Registration:**
A PoA authorising the attorney to deal with *immovable property* must be executed before and authenticated by a Notary Public or certain other authorities, and should be registered with the Sub-Registrar for enforceability in property transactions.

**Example:**
An NRI (Non-Resident Indian) grants a Special PoA to a family member in India to sign the sale deed for their flat. The PoA must be notarised, apostilled (if executed abroad), and registered in India for the sale deed to be accepted by the Sub-Registrar.

**Important Note:**
A PoA cannot authorise the attorney to do acts that the principal themselves cannot legally do. A PoA is revocable by the principal (unless stated to be irrevocable and given for valuable consideration). A PoA becomes void on the death or insanity of the principal unless it is coupled with an interest.""",
    },

    # =========================================================================
    # EMPLOYMENT CONTRACT
    # =========================================================================
    {
        "question": "What clauses are typically found in an employment contract in India?",
        "keywords": "employment contract clauses probation notice salary confidentiality non compete IP",
        "answer": """\
**Definition:**
An employment contract is an agreement between an employer and an employee that governs the terms and conditions of employment.

**Legal Basis:**
Indian Contract Act, 1872 — Section 10 (general validity); applicable labour legislation: Industrial Employment (Standing Orders) Act, 1946; Shops and Establishments Act (state-specific); Industrial Disputes Act, 1947; Payment of Wages Act, 1936; Factories Act, 1948 (for factory workers).

**Explanation:**
A standard Indian employment contract for non-factory / professional employees typically includes:

1. **Designation and reporting structure.**
2. **Compensation and benefits:** Basic salary, HRA, allowances, bonuses, ESOPs.
3. **Probation period:** Usually 3–6 months; confirmation process.
4. **Working hours and leave policy:** As per applicable state Shops Act.
5. **Notice period for termination:** Usually 1–3 months; payment in lieu of notice.
6. **Confidentiality / NDA clause:** Obligation to protect employer's trade secrets.
7. **IP assignment clause:** Works created during employment belong to the employer (as per Section 17, Copyright Act, 1957).
8. **Non-solicitation clause:** Not to solicit the employer's clients or employees after departure.
9. **Non-compete clause:** Common in contracts but largely unenforceable post-employment under Section 27, Indian Contract Act, 1872.
10. **Governing law and dispute resolution.**

**Important Note:**
Labour law in India is both central and state-governed. Specific rights (e.g. gratuity, provident fund, ESIC) are governed by separate statutes regardless of what the employment contract says. Contractual terms cannot override statutory minimum entitlements. The Labour Codes (enacted in 2019–2020, pending full implementation) will consolidate many labour laws when notified.""",
    },

    # =========================================================================
    # NOTICE PERIOD
    # =========================================================================
    {
        "question": "What is a notice period in a contract?",
        "keywords": "notice period termination days written advance inform end contract",
        "answer": """\
**Definition:**
A notice period is the contractually prescribed time that one party must give the other before terminating the contract, allowing the other party to prepare for the change.

**Legal Basis:**
Indian Contract Act, 1872 — Section 10 (freedom of contract); Industrial Disputes Act, 1947 — Section 25-F (retrenchment notice for workmen); state Shops and Establishments Acts (for establishment employees).

**Explanation:**
Notice periods are purely contractual for commercial contracts — there is no general statutory minimum. For employment contracts:
- **Workmen (Industrial Disputes Act, 1947, Section 25-F):** One month's notice (or pay in lieu) is required before retrenching a workman employed for one year or more in a non-seasonal establishment with 50 or more employees.
- **Non-workmen / managerial employees:** Notice period is governed entirely by the employment contract; typical periods are 1–3 months.

Consequences of failing to serve notice:
- In commercial contracts: the terminating party may owe the other party *payment in lieu of the notice period* (or damages for breach of the notice clause).
- In employment: the employee may be required to pay the employer the equivalent notice period salary if they leave without notice (if the contract provides for this).

**Example:**
An employment contract requires 2 months' notice. An employee resigns with immediate effect. The employer may deduct 2 months' salary from the full and final settlement if the contract entitles the employer to do so, or may waive the notice.

**Important Note:**
The enforceability of notice pay recovery depends on the specific contractual clause and the facts. Courts and employment tribunals examine whether the recovery mechanism is a penalty or a genuine pre-estimate of loss (Section 74 principles). Garden leave arrangements (requiring the employee to stay away from work during the notice period) are practised but not specifically governed by statute.""",
    },

    # =========================================================================
    # SPECIFIC PERFORMANCE
    # =========================================================================
    {
        "question": "When can specific performance of a contract be ordered in India?",
        "keywords": "specific performance court order Specific Relief Act 1963 enforce contract",
        "answer": """\
**Definition:**
Specific performance is a court order directing a party to perform its contractual obligations as agreed, rather than paying monetary compensation.

**Legal Basis:**
Specific Relief Act, 1963 — Sections 10, 11, 14, 20, and 21 (as amended by the Specific Relief (Amendment) Act, 2018).

**Explanation:**
The **Specific Relief (Amendment) Act, 2018** significantly changed the law:

**Before 2018:** Specific performance was a discretionary remedy — courts could decline to order it even where the conditions were met.

**After 2018 (Section 10):** For contracts involving immovable property and certain other contracts, specific performance is now generally available *as a matter of right*, not merely at the court's discretion. The 2018 amendment was intended to promote infrastructure investment and reduce uncertainty.

**Contracts for which specific performance can be ordered (Section 10):**
- Where monetary compensation is not an adequate substitute.
- Where it is not possible to estimate actual compensation.
- Where the act to be performed is such that non-performance cannot be adequately compensated by money.

**Contracts that cannot be specifically enforced (Section 14):**
- Contracts that run continuously over a period (e.g. long-term service contracts requiring personal supervision).
- Contracts involving personal service (e.g. employment, where compelled performance would be unreasonable).
- Contracts that are determined to be inequitable.

**Example:**
A buyer enters a contract to purchase a unique piece of land. The seller refuses to complete. The buyer can sue for specific performance — a court order directing the seller to execute the sale deed.

**Important Note:**
Even after the 2018 amendment, courts retain discretion in defined circumstances. The availability of specific performance in any case depends on the nature of the contract, whether third-party rights have been created, and the specific facts.""",
    },

    # =========================================================================
    # CONSUMER PROTECTION
    # =========================================================================
    {
        "question": "What protection does the Consumer Protection Act give in a service contract?",
        "keywords": "consumer protection act 2019 deficiency service complaint forum redressal",
        "answer": """\
**Definition:**
The Consumer Protection Act, 2019 provides statutory remedies to consumers against deficiency in services and unfair trade practices.

**Legal Basis:**
Consumer Protection Act, 2019 — Sections 2(7) (consumer), 2(11) (deficiency), 2(47) (unfair trade practice), 34, 47, and 58 (jurisdiction); Consumer Protection (E-Commerce) Rules, 2020.

**Explanation:**
- **"Consumer" (Section 2(7)):** A person who buys goods or avails of services for *personal use* (not for commercial resale or manufacture). A person who avails of services for self-employment is also a consumer.
- **"Deficiency" (Section 2(11)):** Any fault, imperfection, shortcoming, or inadequacy in the quality, nature, or manner of performance of a service.
- **Jurisdiction (2019 Act):**
  - District Commission: Claims up to Rs 1 crore.
  - State Commission: Claims from Rs 1 crore to Rs 10 crore.
  - National Commission: Claims above Rs 10 crore.
- **Remedies:** Replacement, repair, refund, compensation for loss/injury, removal of deficiency, and punitive damages in appropriate cases.

**Example:**
A person pays Rs 5 lakhs for a home renovation service. The contractor fails to complete work as agreed, uses substandard materials, and abandons the project. The homeowner can file a complaint before the District Consumer Commission for compensation and refund.

**Important Note:**
The Consumer Protection Act, 2019 applies only to *consumers* — it does not apply to commercial disputes between businesses (B2B transactions) where the goods/services are for commercial purposes. The Act covers e-commerce transactions through the 2020 Rules. Specific time limits (2 years from the cause of action) apply for filing complaints.""",
    },

    # =========================================================================
    # GST
    # =========================================================================
    {
        "question": "How should GST be addressed in Indian commercial contracts?",
        "keywords": "GST tax goods services contract invoice GSTIN clause",
        "answer": """\
**Definition:**
GST (Goods and Services Tax) is an indirect tax levied on the supply of goods and services in India.

**Legal Basis:**
Central Goods and Services Tax Act, 2017 (CGST Act); Integrated Goods and Services Tax Act, 2017 (IGST Act); respective State GST Acts; GST Council notifications and circulars.

**Explanation:**
Commercial contracts should clearly address the following GST-related matters:

1. **GST exclusive or inclusive pricing:** State whether the quoted price includes GST or whether GST is payable in addition. Ambiguity leads to disputes.
2. **Who bears the GST:** Typically the recipient of the supply (the buyer/client) pays GST on top of the price, but this must be explicitly stated.
3. **GSTIN details:** Both parties' GST Identification Numbers should be included in the contract (required for input tax credit purposes).
4. **GST invoice obligation:** The supplier must issue a valid tax invoice within the time limits prescribed under CGST Rules, 2017 (Rule 47 — invoice within 30 days of supply for services).
5. **Change in GST rate:** A clause addressing what happens if the GST rate changes after contracting (who absorbs the additional tax).
6. **Reverse charge mechanism (RCM):** Certain supplies attract GST on the reverse charge basis — if applicable, this must be addressed.

**Example:**
A contract states: "The fee is Rs 10 lakhs plus GST at the applicable rate." If the applicable GST rate is 18%, the client pays Rs 11.8 lakhs. If the rate later increases to 20%, the contract clause determines who bears the additional Rs 20,000.

**Important Note:**
GST provisions and rates change frequently through GST Council notifications. Contract GST clauses should be reviewed periodically. Tax implications of a specific transaction should be confirmed with a qualified GST practitioner or chartered accountant, not derived solely from a contract clause.""",
    },

    # =========================================================================
    # CONFIDENTIALITY CLAUSE
    # =========================================================================
    {
        "question": "What is a confidentiality clause in a contract?",
        "keywords": "confidentiality clause secret information protect disclose third party",
        "answer": """\
**Definition:**
A confidentiality clause is a contractual provision that obligates one or both parties to keep specified information secret and to not disclose it to unauthorised third parties.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 10 and 73 (enforced as an ordinary contract); Specific Relief Act, 1963 (injunction for breach); no specific statutory framework for confidentiality clauses in Indian commercial law (unlike trade secrets laws in some jurisdictions).

**Explanation:**
A well-drafted confidentiality clause typically covers:
1. **Definition of confidential information:** What is protected (broad or specific scope).
2. **Obligations of the receiving party:** Not to disclose; use only for permitted purposes; protect with at least the same care as own confidential information.
3. **Permitted disclosures:** Disclosure to employees on a need-to-know basis (subject to equivalent obligations); disclosure required by law or court order.
4. **Exclusions / carve-outs:** Information already public, already known, independently developed, or received from a non-confidential third-party source.
5. **Duration:** How long the obligation lasts (fixed term or perpetual for trade secrets).
6. **Remedies:** Express right to seek injunctive relief (since monetary damages may be difficult to quantify and inadequate).

**Example:**
A technology company shares its source code with a development partner under a contract containing a confidentiality clause. The partner is not permitted to share the source code with any third party. If the partner does so, the company can seek an injunction and damages.

**Important Note:**
Indian courts have granted injunctions for breach of confidentiality clauses. However, courts assess whether the information was actually confidential, whether the clause is enforceable as drafted, and whether the balance of convenience favours an injunction. An overly broad definition of "confidential information" may be interpreted narrowly.""",
    },

    # =========================================================================
    # DISPUTE RESOLUTION
    # =========================================================================
    {
        "question": "What dispute resolution methods are used in Indian commercial contracts?",
        "keywords": "dispute resolution negotiation mediation arbitration litigation ADR",
        "answer": """\
**Definition:**
Dispute resolution refers to the processes by which parties to a contract resolve disagreements arising from the contract.

**Legal Basis:**
Code of Civil Procedure, 1908 — Section 89 (court referral to ADR); Arbitration and Conciliation Act, 1996; Mediation Act, 2023; Commercial Courts Act, 2015.

**Explanation:**
Indian commercial contracts typically use a **tiered dispute resolution mechanism**:

| Tier | Method | Nature | Governing law |
|---|---|---|---|
| 1 | Negotiation | Non-binding | Contractual |
| 2 | Mediation | Non-binding (unless settlement signed) | Mediation Act, 2023 |
| 3 | Arbitration | Binding | Arbitration and Conciliation Act, 1996 |
| 4 | Litigation | Binding | CPC, Commercial Courts Act, 2015 |

**Commercial Courts Act, 2015:** Established dedicated Commercial Courts in every district for commercial disputes above a specified value (currently Rs 3 lakhs), with mandatory pre-institution mediation under the Act before filing a commercial suit.

**Preferred method:** Arbitration is the most widely preferred method in commercial contracts due to speed (12-month statutory timeline under Section 29A), confidentiality, party autonomy in choosing arbitrators, and enforceability of awards internationally under the New York Convention.

**Important Note:**
A dispute resolution clause must be carefully drafted — a poorly drafted arbitration clause (e.g. naming a non-existent institution, vague scope) can lead to litigation over the clause itself before the dispute is even resolved. The effectiveness of any method depends on both parties' cooperation and the specific facts.""",
    },

    # =========================================================================
    # BOILERPLATE
    # =========================================================================
    {
        "question": "What are boilerplate clauses in a contract?",
        "keywords": "boilerplate standard entire agreement severability waiver amendment notice",
        "answer": """\
**Definition:**
Boilerplate clauses are standard "general" provisions typically found at the end of a commercial contract that govern the operation of the contract itself rather than the specific commercial terms.

**Legal Basis:**
Indian Contract Act, 1872 — various sections underpin the legal effect of these clauses; no single statute governs them.

**Explanation:**
Common boilerplate clauses and their legal significance:

1. **Entire Agreement / Merger clause:** The written contract is the complete and exclusive statement of the parties' agreement, superseding all prior negotiations, representations, and agreements. This limits reliance on pre-contractual representations.
2. **Severability clause:** If any provision is found void or unenforceable, the remaining provisions continue in full force. This reflects the principle in Section 57 of the Transfer of Property Act (for property) and general contract law.
3. **Waiver clause:** Failure or delay by a party to exercise any right under the contract is not a waiver of that right. This prevents an argument that non-enforcement constitutes consent to the breach.
4. **Amendment clause:** Any modification to the contract must be in writing and signed by both parties. Prevents informal oral variations.
5. **Notices clause:** Prescribes how formal communications must be sent (e.g. registered post, email with read receipt) and when they are deemed received.
6. **Counterparts clause:** The contract may be executed in separate copies, each of which is an original.
7. **No third-party rights:** Only the parties to the contract have rights under it (relevant in the context of the law on privity of contract).

**Important Note:**
Despite being "standard," boilerplate clauses have significant legal consequences and should not be accepted without review. For example, an entire agreement clause can bar a misrepresentation claim based on pre-contractual statements. Courts interpret these clauses strictly based on their specific wording.""",
    },

    # =========================================================================
    # GUARANTEE
    # =========================================================================
    {
        "question": "What is a contract of guarantee in India?",
        "keywords": "guarantee surety guarantor principal debtor creditor Section 126",
        "answer": """\
**Definition:**
A contract of guarantee is a contract by which one party (the *surety*) undertakes to perform the promise or discharge the liability of a third person (the *principal debtor*) if that person defaults.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 126 to 147.

**Explanation:**
- **Section 126** defines a contract of guarantee. The three parties are: the *principal debtor* (who owes the obligation), the *creditor* (to whom it is owed), and the *surety* (guarantor).
- **Consideration:** The consideration for the guarantee is the benefit flowing to the principal debtor (not necessarily directly to the surety) — Section 127.
- **Extent of liability:** A surety's liability is co-extensive with that of the principal debtor, unless the contract provides otherwise — Section 128.
- **Discharge of surety:** The surety is discharged if:
  - The creditor **varies the terms** of the principal contract without the surety's consent (Section 133).
  - The creditor **releases** the principal debtor (Section 134).
  - The creditor **parts with security** held at the time of the guarantee (Section 141).
  - The creditor gives the debtor **time to pay** without the surety's consent (Section 136).

**Example:**
A bank provides a loan to Company A. Company B (the surety) signs a corporate guarantee. If Company A defaults, the bank can directly proceed against Company B for the outstanding loan amount.

**Important Note:**
Indian courts have strictly applied the discharge provisions — particularly Section 133 (variation) and Section 141 (security). A creditor who fails to preserve security held at the time of the guarantee may lose the right to proceed against the surety. Guarantee documents require careful drafting and legal review.""",
    },

    # =========================================================================
    # PAYMENT TERMS
    # =========================================================================
    {
        "question": "What payment terms are standard in Indian commercial contracts?",
        "keywords": "payment terms invoice net days advance milestone currency interest",
        "answer": """\
**Definition:**
Payment terms are the contractual provisions that specify when, how, and in what currency a party must make payment.

**Legal Basis:**
Indian Contract Act, 1872 — Section 55 (time of performance); MSME Development Act, 2006 — Section 16 (interest on delayed payments to MSMEs); Foreign Exchange Management Act, 1999 (FEMA) — for cross-border payments.

**Explanation:**
Common payment structures in Indian commercial contracts:
1. **Net 30 / Net 60 / Net 90:** Full payment due within 30, 60, or 90 days of a valid invoice.
2. **Advance / milestone-based:** Percentage paid upfront (e.g. 30%), with the balance released on specific deliverables or milestones.
3. **Letter of Credit (LC):** Used in international trade for payment security.

**Late payment — MSME protection:**
If the buyer is a company or large enterprise and the supplier is a Micro, Small, or Medium Enterprise (MSME) registered under the MSMED Act, 2006:
- Payment must be made within **45 days** of acceptance of goods/services (or within the contractually agreed period, if that period does not exceed 45 days).
- If payment is delayed, **compound interest at three times the bank rate** as notified by RBI applies automatically under Section 16 of the MSME Development Act, 2006 — this cannot be contractually waived.

**Example:**
A startup (registered MSME) supplies software to a large company. The contract says "Net 60." Under the MSMED Act, the maximum permissible credit period is 45 days. The 60-day term may not override the 45-day statutory limit, and late payment interest accrues automatically.

**Important Note:**
The MSME late payment protection is a statutory right that cannot be excluded by contract. Cross-border payment terms are additionally governed by FEMA regulations and RBI guidelines, which must be consulted for international contracts.""",
    },

    # =========================================================================
    # LOCK-IN PERIOD
    # =========================================================================
    {
        "question": "What is a lock-in period in a contract?",
        "keywords": "lock in period minimum term early exit penalty lease rental",
        "answer": """\
**Definition:**
A lock-in period (also called a minimum term) is a contractually agreed period during which a party is not permitted to exit the contract, or can only do so by paying an early exit penalty.

**Legal Basis:**
Indian Contract Act, 1872 — Sections 10 (freedom of contract) and 74 (penalty / liquidated damages); Transfer of Property Act, 1882 (for lease lock-ins); Registration Act, 1908 (for leases exceeding 1 year).

**Explanation:**
Lock-in periods are used to provide stability to the party who has made upfront investments in anticipation of the contract duration. Common in:
- **Commercial lease agreements:** A tenant agrees not to vacate for, say, 3 years; breaking the lock-in results in forfeiture of security deposit or payment of remaining lock-in rent.
- **Long-term service or outsourcing contracts:** Client agrees to a minimum contract period.
- **Loan agreements:** Borrower agrees not to prepay for a specified period (often with a prepayment penalty).

**Exit during lock-in:**
The consequences depend on the contract. Typically: payment of the remaining rent/fees for the lock-in period, or a specified early-exit fee (treated as liquidated damages under Section 74 — courts award reasonable compensation up to the stated amount).

**Example:**
A company signs a 5-year office lease with a 3-year lock-in. If the company vacates after 18 months, it may owe 18 months' remaining lock-in rent as per the lease terms. The court, under Section 74, will award reasonable compensation not exceeding this amount.

**Important Note:**
The enforceability of a lock-in and the specific consequences of breach depend on the contract's precise terms and the facts. Courts will not automatically award the full lock-in rent if the landlord/service provider can mitigate loss by re-letting or finding a new client. Mitigation principles from Section 73 apply even in cases governed by Section 74.""",
    },

]  # END FAQ_KB


class LegalFAQRetriever:
    """BM25 retriever over the FAQ knowledge base.

    Indexes each entry on question tokens + keyword tokens so that
    short queries like "tender" or "defendant" match the right entry.
    """

    def __init__(self, faq_kb=None):
        self.faq_kb = faq_kb or FAQ_KB
        corpus = []
        for item in self.faq_kb:
            q_tokens = tokenize(item["question"])
            k_tokens = tokenize(item.get("keywords", ""))
            corpus.append(q_tokens + k_tokens)
        self.bm25 = BM25Okapi(corpus)

    def answer(self, user_question, top_k=1, score_threshold=0.5):
        """Retrieve the best matching FAQ answer."""
        if not user_question:
            return []
        query_tokens = tokenize(user_question)
        if not query_tokens:
            return []
        scores = self.bm25.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: -x[1])[:top_k]
        results = []
        for idx, score in ranked:
            if score < score_threshold:
                continue
            results.append({
                "matched_question": self.faq_kb[idx]["question"],
                "answer": self.faq_kb[idx]["answer"],
                "score": round(float(score), 3),
            })
        return results


class DocumentRetriever:
    """Per-document retrieval over extracted clauses, built per uploaded contract."""

    def __init__(self, clauses):
        self.clauses = clauses
        corpus = [tokenize(c["text"]) for c in clauses]
        self.bm25 = BM25Okapi(corpus) if corpus else None

    def query(self, user_question, top_k=3, score_threshold=0.0):
        if self.bm25 is None:
            return []
        query_tokens = tokenize(user_question)
        if not query_tokens:
            return []
        scores = self.bm25.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: -x[1])[:top_k]
        if not ranked:
            return []
        best_score = ranked[0][1]
        results = []
        for idx, score in ranked:
            if score < score_threshold and score < best_score:
                continue
            results.append({
                "clause_text": self.clauses[idx]["text"],
                "category": self.clauses[idx].get("category", "Unknown"),
                "score": round(float(score), 3),
            })
        return results


def answer_question(user_question, document_clauses=None, faq_retriever=None):
    """Top-level entry point: tries document index first, then FAQ KB."""
    if not user_question:
        return {"source": "none", "results": [], "message": "No question provided."}

    faq_retriever = faq_retriever or LegalFAQRetriever()

    if document_clauses:
        doc_retriever = DocumentRetriever(document_clauses)
        doc_hits = doc_retriever.query(user_question)
        if doc_hits:
            return {"source": "document", "results": doc_hits}

    faq_hits = faq_retriever.answer(user_question)
    if faq_hits:
        return {"source": "faq", "results": faq_hits}

    return {
        "source": "none",
        "results": [],
        "message": (
            "No relevant answer was found in the local legal knowledge base. "
            "Try rephrasing your question, or consult a qualified legal "
            "professional for advice specific to your situation."
        ),
    }


if __name__ == "__main__":
    retriever = LegalFAQRetriever()
    tests = [
        "What are standard NDA exclusions and carve-outs?",
        "tender",
        "defendant rights in civil case",
        "Is a non-compete clause enforceable in India?",
        "Do I need to stamp my contract?",
        "force majeure",
        "Can I terminate a contract without notice?",
        "Can a minor enter a contract?",
        "weather tomorrow",
        "best pizza recipe",
    ]
    for q in tests:
        result = answer_question(q, faq_retriever=retriever)
        if result["results"]:
            top = result["results"][0]
            print(f"\nQ: {q}\n[{result['source']}, score={top['score']}]\n{top['answer'][:200]}...\n")
        else:
            print(f"\nQ: {q}\n-> {result['message']}\n")
