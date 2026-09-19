import streamlit as st
from services.pdf_reader import extract_text_from_pdf
from services.review_pipeline import run_review, format_report
from services.database_service import save_history_record
from utils.ui import load_css, page_header

st.set_page_config(
    page_title="Risk Analysis · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

page_header(
    "🛡️ Contract Risk Matrix & Audit",
    "Detect high-severity liabilities, missing protections, and potential contractual risks using trained ML models and Indian legal rules."
)

# ---------------------------------------------------------
# Risk overview cards
# ---------------------------------------------------------
r1, r2, r3 = st.columns(3)

with r1:
    st.markdown(
        '<div class="card"><span class="risk-badge risk-high">'
        'High Danger</span><h2 style="color:#F8FAFC; font-size:1.4rem; margin:0.4rem 0;">'
        'High-Risk Clauses</h2><p style="color:#CBD5E1; margin:0;">'
        'Liability, indemnity, and uncapped obligations</p></div>',
        unsafe_allow_html=True
    )

with r2:
    st.markdown(
        '<div class="card"><span class="risk-badge risk-medium">'
        'Moderate</span><h2 style="color:#F8FAFC; font-size:1.4rem; margin:0.4rem 0;">'
        'Medium-Risk Clauses</h2><p style="color:#CBD5E1; margin:0;">'
        'Ambiguous or negotiable provisions</p></div>',
        unsafe_allow_html=True
    )

with r3:
    st.markdown(
        '<div class="card"><span class="risk-badge risk-low">'
        'Protected</span><h2 style="color:#F8FAFC; font-size:1.4rem; margin:0.4rem 0;">'
        'Low-Risk / Standard</h2><p style="color:#CBD5E1; margin:0;">'
        'Standard contractual provisions</p></div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Contract input
# ---------------------------------------------------------
st.markdown("""
<div class="section-head">
<span class="tag">§ 01</span>
<h2>Provide Contract Content</h2>
</div>
""", unsafe_allow_html=True)

tab_upload, tab_paste = st.tabs(
    ["📄 Upload Contract PDF / DOCX", "📝 Paste Contract Text"]
)

contract_content = ""
uploaded_file = None
contract_name = "Contract"

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload a contract (PDF or DOCX)",
        type=["pdf", "docx"],
        key="risk_file"
    )

    if uploaded_file is not None:
        contract_content = extract_text_from_pdf(uploaded_file)
        contract_name = uploaded_file.name
        if contract_content and len(contract_content.strip()) >= 50:
            st.markdown(
                f'<div class="status-pill"><span class="dot"></span>'
                f' Ready: {uploaded_file.name} ({len(contract_content):,} chars)</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("Could not extract sufficient text from the uploaded file.")

with tab_paste:
    pasted_text = st.text_area(
        "Paste contract text",
        height=300,
        placeholder="Paste contract text here to evaluate risk..."
    )

    if pasted_text.strip():
        contract_content = pasted_text.strip()
        contract_name = "Pasted Contract"

# ---------------------------------------------------------
# Risk analysis execution
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button(
    "Run Risk Analysis",
    type="primary",
    use_container_width=True
):
    if not contract_content or len(contract_content.strip()) < 50:
        st.warning(
            "Please upload a valid document or paste contract text (at least 50 characters) before running risk analysis."
        )
    else:
        with st.spinner("⚖️ Running trained ML models and rule engine for risk analysis..."):
            result = run_review(contract_content)
            risk_report = format_report(result, contract_name=contract_name)

        high_count = sum(1 for c in result.clauses if any(f.get("severity") == "high" for f in c.rule_flags) or c.learned_severity == "high")
        med_count  = sum(1 for c in result.clauses if any(f.get("severity") == "medium" for f in c.rule_flags) or c.learned_severity == "medium")
        low_count  = sum(1 for c in result.clauses if any(f.get("severity") == "low" for f in c.rule_flags) or c.learned_severity == "low")
        miss_count = len(result.missing_categories)

        overall = "HIGH" if high_count > 0 or miss_count > 0 else ("MEDIUM" if med_count > 0 else "LOW")

        st.success("✅ Risk Analysis Completed Using Trained ML Models & Rule Engine")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-head">
        <span class="tag">§ 02</span>
        <h2>Risk Assessment Summary</h2>
        </div>
        """, unsafe_allow_html=True)

        if overall == "HIGH":
            st.error(f"🔴 OVERALL RISK ASSESSMENT: {overall}")
        elif overall == "MEDIUM":
            st.warning(f"🟠 OVERALL RISK ASSESSMENT: {overall}")
        else:
            st.success(f"🟢 OVERALL RISK ASSESSMENT: {overall}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("HIGH Risk Clauses", high_count)
        m2.metric("MEDIUM Risk Clauses", med_count)
        m3.metric("LOW Risk Clauses", low_count)
        m4.metric("Potentially Missing Provisions", miss_count)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-head">
        <span class="tag">§ 03</span>
        <h2>Full Risk Analysis Report</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(risk_report)
        st.markdown('</div>', unsafe_allow_html=True)

        save_history_record(
            contract_name=contract_name,
            contract_type=result.overview.contract_type_guess,
            activity_type="Risk Analyzed",
            description="Trained ML and rule-based contract risk analysis completed.",
            result_content=risk_report,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        from services.pdf_generator import create_pdf

        pdf_bytes = create_pdf(
            contract_text=risk_report,
            contract_title=f"Risk Analysis — {contract_name}",
            contract_type="Risk Analysis Report",
        )

        if not pdf_bytes.startswith(b"%PDF"):
            st.error("PDF generation failed: generated content is not a valid PDF.")
        else:
            safe_filename = contract_name.replace(" ", "_").replace("/", "_")
            if safe_filename.endswith(".pdf") or safe_filename.endswith(".docx"):
                safe_filename = safe_filename.rsplit(".", 1)[0]
            st.download_button(
                label="📄 Export Risk Analysis Report (PDF)",
                data=pdf_bytes,
                file_name=f"risk_analysis_report_{safe_filename}.pdf",
                mime="application/pdf",
                use_container_width=True
            )


