import streamlit as st
from services.database_service import init_db, get_history_stats, get_recent_history, get_total_contracts
from utils.ui import load_css, page_header

init_db()
load_css()

page_header(
    "\U0001f3e0 Dashboard",
    "AI-assisted contract drafting, review, explanation and risk screening."
)

# Welcome / disclaimer
st.markdown("""
<div class="glass-card" style="margin-bottom:1.5rem;">
    <p style="margin:0; color:#CBD5E1;">
        <strong style="color:#D4A853;">Welcome to your AI-powered contract assistant.</strong><br>
        Draft contracts, review existing agreements, understand difficult clauses, identify potential risks,
        and manage your previous analyses from one place.<br><br>
        <em style="font-size:0.85rem; color:#94a3b8;">
        Disclaimer: This application provides AI-assisted contract analysis for informational purposes.
        It does not constitute legal advice. Important legal decisions should be verified with a qualified legal professional.
        </em>
    </p>
</div>
""", unsafe_allow_html=True)

# Stats
try:
    stats = get_history_stats()
    total_drafted = get_total_contracts()
except Exception:
    stats = {"Total": 0, "Drafted": 0, "Reviewed": 0, "Clause Explained": 0, "Risk Analyzed": 0}
    total_drafted = 0

m0, m1, m2, m3, m4 = st.columns(5)
with m0:
    st.metric("Total Activities", stats["Total"])
with m1:
    st.metric("Drafted", stats["Drafted"])
with m2:
    st.metric("Reviewed", stats["Reviewed"])
with m3:
    st.metric("Explained", stats["Clause Explained"])
with m4:
    st.metric("Risk Analyzed", stats["Risk Analyzed"])

st.markdown("<br>", unsafe_allow_html=True)

# Quick Action Cards
st.markdown('<div class="section-head"><span class="tag">\u00a7 01</span><h2>Quick Actions</h2></div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown('<div class="action-card"><h3>\U0001f4dd Draft a Contract</h3><p>Create a structured contract from your requirements.</p></div>', unsafe_allow_html=True)
    if st.button("Start Drafting \u2192", use_container_width=True, key="dash_draft"):
        st.switch_page("pages/1_Draft_Contract.py")

with c2:
    st.markdown('<div class="action-card"><h3>\U0001f50d Review a Contract</h3><p>Analyze an existing contract for potential issues.</p></div>', unsafe_allow_html=True)
    if st.button("Start Review \u2192", use_container_width=True, key="dash_review"):
        st.switch_page("pages/3_Review_Contract.py")

with c3:
    st.markdown('<div class="action-card"><h3>\U0001f4a1 Explain a Clause</h3><p>Understand complicated legal language in simple terms.</p></div>', unsafe_allow_html=True)
    if st.button("Explain Clause \u2192", use_container_width=True, key="dash_explain"):
        st.switch_page("pages/4_Explain_Clause.py")

with c4:
    st.markdown('<div class="action-card"><h3>\u26a0\ufe0f Risk Analysis</h3><p>Identify potential contractual risks requiring review.</p></div>', unsafe_allow_html=True)
    if st.button("Analyze Risk \u2192", use_container_width=True, key="dash_risk"):
        st.switch_page("pages/5_Risk_Analysis.py")

with c5:
    st.markdown('<div class="action-card"><h3>\U0001f4da Contract History</h3><p>View and manage all previous contract activities.</p></div>', unsafe_allow_html=True)
    if st.button("View History \u2192", use_container_width=True, key="dash_history"):
        st.switch_page("pages/6_Contract_History.py")

st.markdown("<br>", unsafe_allow_html=True)

# Recent Activity
st.markdown('<div class="section-head"><span class="tag">\u00a7 02</span><h2>Recent Activity</h2></div>', unsafe_allow_html=True)

try:
    recent = get_recent_history(limit=5)
except Exception:
    recent = []

ACTIVITY_ICONS = {
    "Drafted": "\U0001f4dd",
    "Reviewed": "\U0001f50d",
    "Clause Explained": "\U0001f4a1",
    "Risk Analyzed": "\u26a0\ufe0f",
}

if recent:
    for name, ctype, activity, created_at, status in recent:
        icon = ACTIVITY_ICONS.get(activity, "\U0001f4c4")
        status_color = "#22c55e" if status == "Completed" else "#ef4444"
        st.markdown(f"""
        <div class="ledger-row">
            <div>
                <h4 style="margin:0;">{icon} {name}</h4>
                <span style="font-size:0.8rem;color:#94a3b8;">{ctype} &nbsp;|&nbsp; {activity} &nbsp;|&nbsp; {created_at}</span>
            </div>
            <span class="tech-badge" style="color:{status_color};">{status}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("\U0001f4da View All History", use_container_width=False):
        st.switch_page("pages/6_Contract_History.py")
else:
    st.info("\U0001f4c2 No contract activity yet. Start by drafting or uploading a contract.")
    if st.button("\U0001f4dd Start Drafting"):
        st.switch_page("pages/1_Draft_Contract.py")
