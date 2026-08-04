import streamlit as st
from datetime import datetime, date

from services.gemini_service import generate_contract
from services.pdf_generator import create_pdf
from services.database_service import init_db, save_contract
from utils.ui import load_css, page_header

init_db()

st.set_page_config(
    page_title="Draft Contract · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

page_header(
    "📝 Contract Drafting Workspace",
    "Build legally rigorous, customized agreements in minutes with guided clause selection and Gemini AI."
)

# Load Default Settings from Session State
default_country = st.session_state.get("settings_country", "India")
default_state = st.session_state.get("settings_state", "Maharashtra")
default_curr = st.session_state.get("settings_currency", "INR (₹)")
default_lang = st.session_state.get("settings_language", "Hindi")

# ===========================
# Step 1: Basic Information
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Basic Information</h2></div>
<div class="section-sub">Define agreement type, title, jurisdiction, and validity period.</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        contract_type = st.selectbox(
            "Contract Type",
            [
                "Employment Agreement",
                "Rental Agreement",
                "Non Disclosure Agreement (NDA)",
                "Freelance Agreement",
                "Service Agreement",
                "Partnership Agreement",
                "Sales Agreement",
                "Consultancy Agreement",
                "Vendor Agreement",
                "Custom Contract"
            ]
        )

        contract_title = st.text_input(
            "Contract Title",
            placeholder="e.g. Master Services Agreement 2026"
        )

        effective_date = st.date_input(
            "Effective Date",
            value=date.today()
        )

    with col2:
        expiry_date = st.date_input(
            "Expiry Date",
            value=date.today()
        )

        country = st.text_input(
            "Country",
            value=default_country,
            placeholder="e.g. India or United States"
        )

        state = st.text_input(
            "State / Jurisdiction",
            value=default_state,
            placeholder="e.g. Maharashtra or Delhi"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 2: Party A Details
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Party A (First Party)</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        party_a_name = st.text_input("Full Name", key="party_a_name", placeholder="e.g. Rahul Sharma")
        party_a_company = st.text_input("Company Name", key="party_a_company", placeholder="e.g. Apex Tech Pvt Ltd")
        party_a_email = st.text_input("Email Address", key="party_a_email", placeholder="rahul@apextech.in")

    with col2:
        party_a_phone = st.text_input("Phone Number", key="party_a_phone", placeholder="+91 98200 12345")
        party_a_address = st.text_area("Official Address", key="party_a_address", height=100, placeholder="Plot 45, BKC, Mumbai, Maharashtra 400051...")
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 3: Party B Details
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 03</span><h2>Party B (Second Party)</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        party_b_name = st.text_input("Full Name", key="party_b_name", placeholder="e.g. Priya Patel")
        party_b_company = st.text_input("Company Name", key="party_b_company", placeholder="e.g. Patel Digital Solutions")
        party_b_email = st.text_input("Email Address", key="party_b_email", placeholder="priya@pateldigital.com")

    with col2:
        party_b_phone = st.text_input("Phone Number", key="party_b_phone", placeholder="+91 98111 67890")
        party_b_address = st.text_area("Official Address", key="party_b_address", height=100, placeholder="102 MG Road, Pune, Maharashtra 411001...")
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 4: Contract Details & Scope
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 04</span><h2>Scope & Deliverables</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    purpose = st.text_area("Purpose of Contract", height=90, placeholder="Define the primary objective and business goal...")
    scope = st.text_area("Scope of Work", height=120, placeholder="Detail specific tasks, responsibilities, and project boundaries...")
    deliverables = st.text_area("Key Deliverables", height=100, placeholder="List clear tangible deliverables and milestones...")

    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("Project Start Date", value=date.today())
    with c2:
        end_date = st.date_input("Project End Date", value=date.today())
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 5: Commercial Terms
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 05</span><h2>Commercial & Payment Terms</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        payment_amount = st.number_input("Payment Amount", min_value=0.0, step=500.0, value=50000.0)
        curr_options = ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"]
        default_curr_idx = curr_options.index(default_curr) if default_curr in curr_options else 0
        currency = st.selectbox("Currency", curr_options, index=default_curr_idx)

    with col2:
        payment_method = st.selectbox("Payment Method", ["Bank Transfer (NEFT/RTGS)", "UPI", "Cheque", "Online Payment", "Cash"])
        payment_schedule = st.selectbox("Payment Schedule", ["Milestone-based", "Monthly", "One Time", "Weekly", "Quarterly"])
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 6: Responsibilities
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 06</span><h2>Party Obligations</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    party_a_responsibility = st.text_area("Responsibilities of Party A", height=110, placeholder="List duties expected from Party A...")
    party_b_responsibility = st.text_area("Responsibilities of Party B", height=110, placeholder="List duties expected from Party B...")
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 7: Legal Clauses Selection
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 07</span><h2>Standard Legal Protective Clauses</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        confidentiality = st.checkbox("Confidentiality & Non-Disclosure", value=True)
        intellectual_property = st.checkbox("Intellectual Property Ownership", value=True)
        non_compete = st.checkbox("Non-Compete Provision")
        non_solicitation = st.checkbox("Non-Solicitation")
        termination = st.checkbox("Termination Rights & Notice", value=True)
        arbitration = st.checkbox("Binding Arbitration")

    with c2:
        force_majeure = st.checkbox("Force Majeure Clause", value=True)
        indemnification = st.checkbox("Indemnification", value=True)
        limitation_liability = st.checkbox("Limitation of Liability", value=True)
        governing_law = st.checkbox("Governing Law & Jurisdiction", value=True)
        dispute_resolution = st.checkbox("Dispute Resolution Mechanism")
        notice_clause = st.checkbox("Formal Notice Provision")
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Step 8: Additional Custom Terms
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 08</span><h2>Custom Provisions & Special Conditions</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    additional_terms = st.text_area("Special Terms / Custom Covenants", height=120, placeholder="Specify any additional non-standard agreements...")
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Actions & Contract Generation
# ===========================
st.markdown("<br>", unsafe_allow_html=True)

act_col1, act_col2 = st.columns(2)

with act_col1:
    if st.button("📋 Review Brief Summary", use_container_width=True):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Contract Brief Overview")
        st.markdown(f"**Title:** {contract_title or 'Untitled Agreement'}")
        st.markdown(f"**Type:** {contract_type}")
        st.markdown(f"**Parties:** {party_a_name or 'Party A'} & {party_b_name or 'Party B'}")
        st.markdown(f"**Commercials:** {payment_amount} {currency} ({payment_schedule})")
        st.markdown(f"**Jurisdiction:** {state}, {country}")
        st.markdown(f"**Language:** {default_lang}")
        st.markdown('</div>', unsafe_allow_html=True)

with act_col2:
    generate_btn = st.button("🚀 Draft Contract with Gemini AI", use_container_width=True)

if generate_btn:
    if not contract_title or not party_a_name or not party_b_name:
        st.error("⚠️ Please fill in at least the Contract Title, Party A Name, and Party B Name before drafting.")
    else:
        clauses = []
        if confidentiality: clauses.append("Confidentiality")
        if intellectual_property: clauses.append("Intellectual Property")
        if non_compete: clauses.append("Non-Compete")
        if non_solicitation: clauses.append("Non-Solicitation")
        if termination: clauses.append("Termination")
        if arbitration: clauses.append("Arbitration")
        if force_majeure: clauses.append("Force Majeure")
        if indemnification: clauses.append("Indemnification")
        if limitation_liability: clauses.append("Limitation of Liability")
        if governing_law: clauses.append("Governing Law")
        if dispute_resolution: clauses.append("Dispute Resolution")
        if notice_clause: clauses.append("Notice Clause")

        hindi_instruction = "If the requested document language is Hindi, include a clear Hindi Summary (हिंदी संक्षेप) section at the end of the contract." if default_lang == "Hindi" else ""

        prompt = f"""
You are an expert legal counsel specialized in drafting enterprise agreements under the laws of {state}, {country}.

Generate a comprehensive, formal legal agreement: {contract_type}.

Structuring guidelines:
1. Title and Preamble
2. Recitals
3. Definitions
4. Scope of Work and Deliverables
5. Obligations of Party A and Party B
6. Payment Terms and Consideration ({currency})
7. Protective Legal Clauses: {", ".join(clauses)}
8. Term and Termination
9. Governing Law ({state}, {country})
10. Signatures and Execution Blocks

Contract Information:
- Title: {contract_title}
- Jurisdiction: {state}, {country}
- Party A: {party_a_name} ({party_a_company}), {party_a_address}
- Party B: {party_b_name} ({party_b_company}), {party_b_address}
- Purpose: {purpose}
- Scope: {scope}
- Deliverables: {deliverables}
- Consideration: {payment_amount} {currency} via {payment_method} ({payment_schedule})
- Obligations Party A: {party_a_responsibility}
- Obligations Party B: {party_b_responsibility}
- Additional Terms: {additional_terms}

{hindi_instruction}

Format the agreement with clear numbered section headers.
"""

        with st.spinner("⚖️ Gemini AI is drafting your formal legal contract..."):
            contract = generate_contract(prompt)

        st.session_state["generated_contract"] = contract
        save_contract(
            title=contract_title,
            contract_type=contract_type,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            contract=contract
        )

        st.success("✅ Contract drafted and saved to repository!")

if "generated_contract" in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-head"><span class="tag">§ 09</span><h2>Generated Agreement</h2></div>', unsafe_allow_html=True)
    
    st.text_area(
        "Agreement Document",
        value=st.session_state["generated_contract"],
        height=650
    )

    pdf_file = create_pdf(st.session_state["generated_contract"])

    st.download_button(
        label="📄 Download Official PDF Document",
        data=pdf_file,
        file_name=f"{contract_title.replace(' ', '_') if contract_title else 'Legal_Contract'}.pdf",
        mime="application/pdf",
        use_container_width=True
    )