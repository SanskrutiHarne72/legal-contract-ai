import streamlit as st
from agents.drafting_agent import generate_contract
from services.file_service import save_contract

def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Quick Generator · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_css()

st.markdown("""
<div class="subpage-hero">
    <h1>Quick Contract Generator</h1>
    <p>Rapidly draft a contract using a streamlined single-prompt agent workflow.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="wizard-card">', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    contract_type = st.selectbox(
        "Contract Type",
        ["Employment", "Rental", "NDA", "Service", "Partnership", "Sales", "Consultancy"]
    )
    party_a = st.text_input("Party A (First Party)", placeholder="e.g. Corp A")
    party_b = st.text_input("Party B (Second Party)", placeholder="e.g. Corp B")

with c2:
    effective_date = st.date_input("Effective Date")
    payment = st.text_input("Payment Terms", placeholder="e.g. $10,000 net 30")
    jurisdiction = st.text_input("Jurisdiction", placeholder="e.g. New York, USA")

terms = st.text_area("Additional Provisions & Notes", height=120, placeholder="Paste custom clauses or instructions...")

st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚀 Fast Generate Contract", use_container_width=True):
    if not party_a or not party_b:
        st.error("⚠️ Please specify both Party A and Party B before generating.")
    else:
        data = {
            "contract_type": contract_type,
            "party_a": party_a,
            "party_b": party_b,
            "effective_date": str(effective_date),
            "payment": payment,
            "jurisdiction": jurisdiction,
            "terms": terms,
        }

        with st.spinner("Drafting agreement..."):
            contract = generate_contract(data)

        st.success("✅ Contract generated successfully!")

        st.text_area("Generated Agreement Text", contract, height=500)

        filename = f"{contract_type}_contract.txt"
        path = save_contract(filename, contract)

        st.download_button(
            "📄 Download Text Document",
            contract,
            file_name=filename,
            use_container_width=True
        )