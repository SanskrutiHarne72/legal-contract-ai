import streamlit as st
from services.database_service import get_total_contracts, get_recent_contracts, get_contract_type_data
from utils.ui import load_css, page_header


load_css()
page_header(
    "📊 Legal Workspace Dashboard",
    "Real-time analytics, repository status, and quick access to every legal tool."
)

total_contracts = get_total_contracts()


m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f'<div class="card"><h2 class="mono">{total_contracts}</h2><p>Contracts Saved</p></div>', unsafe_allow_html=True)

with m2:
    st.markdown('<div class="card"><h2 class="mono">12</h2><p>Reviews Completed</p></div>', unsafe_allow_html=True)

with m3:
    st.markdown('<div class="card"><h2 class="mono">4</h2><p>Open Risk Flags</p></div>', unsafe_allow_html=True)

with m4:
    st.markdown('<div class="card"><h2 class="mono">Connected</h2><p>Gemini AI Status</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Quick Navigation</h2></div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("Draft Contract →", use_container_width=True, key="dash_draft"):
        st.switch_page("pages/1_Draft_Contract.py")

with c2:
    if st.button("Review Contract →", use_container_width=True, key="dash_review"):
        st.switch_page("pages/3_Review_Contract.py")

with c3:
    if st.button("Explain Clause →", use_container_width=True, key="dash_explain"):
        st.switch_page("pages/4_Explain_Clause.py")

with c4:
    if st.button("Risk Analysis →", use_container_width=True, key="dash_risk"):
        st.switch_page("pages/5_Risk_Analysis.py")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Recent Repository Activity</h2></div>
""", unsafe_allow_html=True)

recent = get_recent_contracts()

if recent:
    for title, ctype, cdate in recent:
        st.markdown(f"""
        <div class="ledger-row">
            <h4>{title}</h4>
            <span class="tech-badge">{ctype}</span>
            <span class="meta">{cdate}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No recent contract activity.")