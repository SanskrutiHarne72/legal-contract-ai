import streamlit as st
from services.database_service import get_contracts, delete_contract
from services.pdf_generator import create_pdf

def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Contract Repository · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_css()

# ===========================
# Header Banner
# ===========================
st.markdown("""
<div class="subpage-hero">
    <h1>Legal Document Repository</h1>
    <p>Search, inspect, export, or manage all generated legal contracts stored securely in local SQLite database.</p>
</div>
""", unsafe_allow_html=True)

contracts = get_contracts()

if not contracts:
    st.info("📂 No contracts found in your local repository. Draft or generate an agreement to see it listed here.")
else:
    st.markdown("""
    <div class="section-head"><span class="tag">§ 01</span><h2>Repository Search & Management</h2></div>
    """, unsafe_allow_html=True)

    col_search, col_stats = st.columns([2.5, 1])

    with col_search:
        search_query = st.text_input("🔍 Search Contracts by Title or Type", placeholder="Type title, company, or agreement type...")

    with col_stats:
        st.markdown(f'<div class="card"><h2 class="mono">{len(contracts)}</h2><p>Stored Contracts</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    filtered_contracts = [
        c for c in contracts
        if not search_query or search_query.lower() in str(c[1]).lower() or search_query.lower() in str(c[2]).lower()
    ]

    if not filtered_contracts:
        st.warning(f"No contracts matching '{search_query}'.")
    else:
        for contract in filtered_contracts:
            contract_id, title, contract_type, created_date, contract_text = contract[0], contract[1], contract[2], contract[3], contract[4]

            with st.expander(f"📄 {title}  ·  [{contract_type}]  ·  {created_date}"):
                st.markdown(f"""
                <div class="ledger-row">
                    <div>
                        <h4>{title}</h4>
                        <span class="meta">Created: {created_date} | Storage ID: #{contract_id}</span>
                    </div>
                    <span class="tech-badge">{contract_type}</span>
                </div>
                """, unsafe_allow_html=True)

                st.text_area(
                    "Agreement Text",
                    value=contract_text,
                    height=350,
                    key=f"text_{contract_id}"
                )

                pdf_bytes = create_pdf(contract_text)

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.download_button(
                        label="⬇ Download Official PDF",
                        data=pdf_bytes,
                        file_name=f"{title.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_{contract_id}",
                        use_container_width=True
                    )
                with btn_col2:
                    if st.button("🗑 Delete Contract Record", key=f"del_{contract_id}", use_container_width=True):
                        delete_contract(contract_id)
                        st.success(f"Deleted '{title}'.")
                        st.rerun()

