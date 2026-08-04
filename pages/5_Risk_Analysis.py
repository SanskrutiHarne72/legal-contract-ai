import streamlit as st
from services.pdf_reader import extract_text_from_pdf
from services.gemini_service import generate_contract
from utils.ui import load_css, page_header

st.set_page_config(
    page_title="Risk Analysis · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()
page_header(
    "Page Title",
    "Page description"
)


# Risk gauge summary indicators
r1, r2, r3 = st.columns(3)
with r1:
    st.markdown('<div class="card"><span class="risk-badge risk-high">High Danger</span><h2>Unlimited Liability</h2><p>Indemnification carve-outs</p></div>', unsafe_allow_html=True)
with r2:
    st.markdown('<div class="card"><span class="risk-badge risk-medium">Moderate</span><h2>Unilateral Rights</h2><p>Termination & fee hikes</p></div>', unsafe_allow_html=True)
with r3:
    st.markdown('<div class="card"><span class="risk-badge risk-low">Protected</span><h2>Standard Covenants</h2><p>Governing law & notices</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Provide Contract Content</h2></div>
""", unsafe_allow_html=True)

tab_upload, tab_paste = st.tabs(["📄 Upload Contract PDF", "📝 Paste Contract Text"])

contract_content = ""

with tab_upload:
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF Agreement", type=["pdf"], key="risk_pdf")
    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            contract_content = extract_text_from_pdf(uploaded_file)
        st.markdown(f'<div class="status-pill"><span class="dot"></span> Ready: {uploaded_file.name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_paste:
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    pasted_text = st.text_area("Paste Agreement Text", height=200, placeholder="Paste contract text here to evaluate risk...")
    if pasted_text.strip():
        contract_content = pasted_text
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚨 Run Comprehensive Risk Audit", use_container_width=True):
    if not contract_content or len(contract_content.strip()) < 30:
        st.error("⚠️ Please upload a valid PDF or paste contract text before running risk analysis.")
    else:
        prompt = f"""
You are an enterprise legal risk officer auditing a commercial contract.

Analyze the contract text and produce a Risk Audit Matrix using these exact markdown headers:

# Executive Risk Assessment

### Overall Risk Rating
State clearly: HIGH RISK, MEDIUM RISK, or LOW RISK with a 100-point risk score.

## 🔴 High Severity Liabilities & Red Flags
List clauses containing unlimited liability, broad indemnification, onerous non-competes, or severe penalty terms.

## 🟠 Medium Severity Risks & Ambiguities
List vague SLA terms, automatic renewals without notice, or unclear payment triggers.

## 🟢 Low Risk Standard Provisions
List well-drafted boilerplate clauses that conform to industry standards.

## ⚠️ Omitted & Missing Protective Clauses
Detail standard legal protections that are conspicuously missing.

## 🛡️ Recommended Negotiation & Redline Strategy
Provide exact alternative phrasing to present to the counterparty.

Contract Content:
{contract_content[:12000]}
"""

        with st.spinner("⚖️ Gemini AI is scanning clauses for liabilities and risk factors..."):
            risk_report = generate_contract(prompt)

        st.success("✅ Risk Matrix Audit Generated!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-head"><span class="tag">§ 02</span><h2>Risk Audit Report</h2></div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(risk_report)
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            "📄 Export Risk Audit Report",
            data=risk_report,
            file_name="Contract_Risk_Report.txt",
            mime="text/plain",
            use_container_width=True
        )