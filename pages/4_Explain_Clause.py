import streamlit as st
from services.ml_service import LegalMLService
from services.pdf_reader import extract_text_from_pdf
from services.database_service import save_history_record
from services.risk_rules import check_clause_language
from utils.ui import load_css, page_header

st.set_page_config(
    page_title="Explain Clause · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

ml = LegalMLService()


def generate_local_explanation(clause_text: str) -> str:
    """
    Generate a plain-language explanation of a legal clause using local ML classification,
    entity extraction, and rule-based risk checks.
    """
    try:
        category = ml.classify_clause(clause_text)
    except Exception:
        category = "General Legal Clause"

    try:
        entities = ml.extract_entities(clause_text)
    except Exception:
        entities = []

    flags = check_clause_language(clause_text, category)

    meanings = {
        "Termination": "Specifies the terms, notice periods, and conditions under which the contract may be ended by either party.",
        "Governing Law": "Designates the applicable legal jurisdiction and governing laws (e.g. Indian law / local courts) that control disputes under the agreement.",
        "Indemnification": "Requires one party to compensate or defend the other for specific losses, damages, or third-party legal claims.",
        "Confidentiality": "Imposes strict obligations to protect proprietary, commercial, or private information from unauthorized disclosure.",
        "Cap On Liability": "Places a financial upper limit or restriction on total monetary damages recoverable under the contract.",
        "Limitation of Liability": "Restricts the types or amount of legal damages that can be claimed by either party.",
    }

    simple_lang = {
        "Termination": "Explains how, when, and with how much notice the parties can stop working together and cancel the agreement.",
        "Governing Law": "Sets which state or country's laws apply if there is a legal dispute, and which court will resolve it.",
        "Indemnification": "Protects one side by making the other side pay for certain damages, legal fees, or lawsuits.",
        "Confidentiality": "Requires keeping shared private or business information secret.",
        "Cap On Liability": "Limits the maximum money one party might have to pay if something goes wrong.",
    }

    legal_meaning_text = meanings.get(category, f"Sets out legal rights, obligations, and operational terms relating to '{category}'.")
    simple_lang_text = simple_lang.get(category, f"Explains the responsibilities and rules associated with '{category}' in straightforward terms.")

    entity_str = ", ".join([f"{e['text']} ({e['type']})" for e in entities]) if entities else "Parties and key terms as defined in the clause."
    terms_list = [f"- **{e['text']}**: Extracted entity ({e['type']})" for e in entities[:5]]
    important_terms_text = "\n".join(terms_list) if terms_list else "- **Notice / Terms**: Refer to the specific wording in the clause."

    if flags:
        concerns_lines = [f"- Potential concern: {f['explanation']}" for f in flags]
        concerns_text = "\n".join(concerns_lines)
    else:
        concerns_text = "No major one-sidedness or uncapped liability flags detected based on rule-based analysis."

    questions = {
        "Termination": "1. What is the required notice period?\n2. Is written notice required?\n3. Are there termination fees?",
        "Governing Law": "1. Which specific courts have jurisdiction?\n2. Does local law (e.g. Indian Contract Act) apply?",
        "Indemnification": "1. Is indemnification mutual?\n2. Are legal defense costs included?",
    }
    questions_text = questions.get(category, "1. What are the key timelines?\n2. Are the obligations mutual?\n3. Is liability capped?")

    examples = {
        "Termination": "Example: If Party A wishes to end the contract, they must provide 30 days written notice to Party B before termination takes effect.",
        "Governing Law": "Example: If a dispute arises, the lawsuit must be filed in the designated court jurisdiction (e.g. courts at Pune, under Indian laws).",
        "Indemnification": "Example: If a customer sues Party B due to Party A's negligence, Party A must pay Party B's legal fees and settlements.",
    }
    example_text = examples.get(category, f"Example: Under this {category} clause, both parties must adhere to the specified terms and conditions.")

    if any(f['severity'] == 'high' for f in flags):
        status_text = "⚠ Potential concern"
    elif any(f['severity'] == 'medium' for f in flags):
        status_text = "⚠ Needs clarification"
    else:
        status_text = "✓ Generally clear"

    response = f"""### LEGAL MEANING
{legal_meaning_text} (Classified as **{category}**)

### IN SIMPLE LANGUAGE
{simple_lang_text}

### WHO IS AFFECTED
{entity_str}

### RIGHTS & OBLIGATIONS
The clause sets out obligations governing **{category}**. Parties must comply with notice, location, or performance terms as stated.

### IMPORTANT TERMS
{important_terms_text}

### POTENTIAL CONCERNS
{concerns_text}

### QUESTIONS TO CONSIDER
{questions_text}

### HYPOTHETICAL EXAMPLE
{example_text}

### CLAUSE STATUS
{status_text}"""

    return response


page_header(
    "📖 Explain Clause",
    "Deconstruct legal jargon into simple explanations, understand rights and obligations, and identify potential concerns."
)

st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Clause Input</h2></div>
""", unsafe_allow_html=True)

input_method = st.radio("Choose Input Method", ["Paste Legal Clause Manually", "Upload Contract & Extract Text"])

clause_input = ""

if input_method == "Upload Contract & Extract Text":
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Contract (PDF or DOCX)", type=["pdf", "docx"])
    
    if uploaded_file:
        with st.spinner("Extracting text..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            if extracted_text:
                st.success("✓ File uploaded\n✓ Text extracted")
                clause_input = st.text_area("Select and Copy the exact clause from below, or trim the text:", value=extracted_text, height=300)
            else:
                st.error("Could not extract text. Please ensure it is not a scanned image.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    clause_input = st.text_area(
        "Paste Legal Clause Text",
        height=200,
        placeholder="Paste any contractual section or clause text here..."
    )

explain_btn = st.button("✨ Analyze Clause", use_container_width=True)

if explain_btn:
    if not clause_input.strip():
        st.error("⚠️ Please provide a clause to analyze.")
    else:
        st.markdown("---")
        st.markdown("### SELECTED CLAUSE")
        st.info(f"*{clause_input.strip()}*")
        st.markdown("---")

        with st.spinner("🔍 Analyzing clause using local ML pipeline..."):
            explanation = generate_local_explanation(clause_input.strip())

        # Save to contract history
        save_history_record(
            contract_name=f"Clause: {clause_input[:60].strip()}...",
            contract_type="Clause Explanation",
            activity_type="Clause Explained",
            description="Plain-language clause explanation generated locally.",
            result_content=explanation,
        )

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(explanation)
        st.markdown("---")
        st.markdown("### DISCLAIMER")
        st.markdown("*This is a local ML-assisted explanation. It does NOT constitute definitive legal advice. Please consult an appropriately qualified legal professional before making any decisions based on this information.*")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Download PDF ──────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        from services.pdf_generator import create_pdf
        
        clause_pdf_text = f"# CLAUSE EXPLANATION REPORT\n\n## SELECTED CLAUSE\n> {clause_input.strip()}\n\n{explanation}"
        pdf_bytes = create_pdf(
            contract_text=clause_pdf_text,
            contract_title="Clause Explanation Report",
            contract_type="Clause Explanation",
        )

        if not pdf_bytes.startswith(b"%PDF"):
            st.error("PDF generation failed: generated content is not a valid PDF.")
        else:
            st.download_button(
                label="📄 Download Clause Explanation PDF",
                data=pdf_bytes,
                file_name="clause_explanation_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )