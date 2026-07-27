import streamlit as st
from services.pdf_reader import extract_text_from_pdf
from services.gemini_service import generate_contract

def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Review Contract · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_css()

# ===========================
# Header Banner
# ===========================
st.markdown("""
<div class="subpage-hero">
    <h1>Contract Review & Ingestion Workspace</h1>
    <p>Upload existing legal agreements to analyze risk factors, detect missing protections, and receive plain-language summaries.</p>
</div>
""", unsafe_allow_html=True)

# ===========================
# Ingestion Card
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Document Upload</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Agreement PDF or Document",
        type=["pdf", "docx"],
        help="Select a legal contract file (PDF recommended) for instant AI review."
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Review Criteria & Options
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Analysis Criteria</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        explain = st.checkbox("Plain-Language Clause Explanation", value=True)
        risk = st.checkbox("Liability & Risk Detection", value=True)
        missing = st.checkbox("Omitted Standard Clauses Check", value=True)
    with c2:
        summary = st.checkbox("Executive Summary Generation", value=True)
        suggestions = st.checkbox("Strategic Counter-proposal Suggestions", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="status-pill"><span class="dot"></span> Ingested: <strong>{uploaded_file.name}</strong></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Execute Contract Review", use_container_width=True):
        with st.spinner("📖 Extracting text from document..."):
            contract_text = extract_text_from_pdf(uploaded_file)

        if not contract_text or len(contract_text.strip()) < 50:
            st.error("⚠️ Could not extract sufficient text from the document. Please ensure the PDF is not scanned as pure images.")
        else:
            prompt = f"""
You are an enterprise legal counsel performing a comprehensive contract audit.

Audit the following legal contract text.

Return your analysis structured with these exact H2 headers:

## 1. Executive Summary
Provide a concise overview of the purpose, scope, and key parties.

## 2. Risk Score & Overall Rating
Assign a numeric Risk Score from 0 to 100 (where 100 is maximum danger).
Classify as: LOW RISK, MEDIUM RISK, or HIGH RISK. Provide a 2-sentence rationale.

## 3. High Risk Liabilities & Unfair Terms
Detail all high-risk indemnities, unlimited liabilities, unfair termination rights, or broad non-competes.

## 4. Medium Risk & Ambiguous Clauses
Identify vague wording, missing deadlines, or unclear payment mechanics.

## 5. Missing Standard Protections
List standard protective clauses (e.g. Limitation of Liability, Force Majeure, IP Assignment) that are missing.

## 6. Recommended Revisions & Counter-proposals
Provide concrete line-item amendments to protect the user's interests.

## 7. Plain-English Breakdown
Explain the contract terms in plain, conversational language for non-lawyers.

Contract Text:
{contract_text[:12000]}
"""

            with st.spinner("⚖️ Gemini AI is evaluating contract clauses..."):
                review_report = generate_contract(prompt)

            st.success("✅ Comprehensive Review Completed!")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="section-head"><span class="tag">§ 03</span><h2>Audit Report</h2></div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(review_report)
            st.markdown('</div>', unsafe_allow_html=True)

            st.download_button(
                label="📄 Download Review Report",
                data=review_report,
                file_name=f"Audit_Report_{uploaded_file.name}.txt",
                mime="text/plain",
                use_container_width=True
            )