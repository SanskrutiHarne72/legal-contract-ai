import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os
from pathlib import Path
from services.database_service import init_db

init_db()

from services.database_service import (
    get_total_contracts,
    get_recent_contracts,
    get_contract_type_data,
    get_contract_date_data,
    get_history_stats,
    get_recent_history,
)

# ---------- Theme colors ----------
INK = "#D4A853"
GOLD = "#D4A853"
GOLD_LIGHT = "#E5BE72"
MUTED = "#CBD5E1"
CREAM = "#172033"

# ---------- SVG Icons ----------
ICON_DRAFT = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><path d="M6 2h9l5 5v15H6z"/><path d="M15 2v6h6"/><path d="M9 13h6M9 17h6"/></svg>"""
ICON_REVIEW = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><circle cx="10" cy="10" r="6.2"/><path d="M20 20l-5.6-5.6"/></svg>"""
ICON_EXPLAIN = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><path d="M4 4h16v12H9l-4 4V4z"/><path d="M8 9h8M8 12.5h5"/></svg>"""
ICON_RISK = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><path d="M12 3l10 18H2z"/><path d="M12 9.5v5"/><circle cx="12" cy="17.3" r="0.6" fill="#B8935B" stroke="none"/></svg>"""


def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def icon_badge(svg): 
    return f'<div class="icon-badge">{svg}</div>'


st.set_page_config(
    page_title="AI Legal Contract Assistant · Final Year Capstone",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe database loading
try:
    total_contracts = get_total_contracts()
    recent_contracts = get_recent_contracts()
except Exception as e:
    st.error(f"Database connection error: {e}")
    total_contracts = 0
    recent_contracts = []

load_css()

logo_path = Path(__file__).parent / "assets" / "logo.png"

# ==========================
# Sidebar
# ==========================
with st.sidebar:
    # Brand Logo Image
    if logo_path.exists():
        st.markdown('<div style="text-align: center; padding: 0.5rem 0 1rem 0;">', unsafe_allow_html=True)
        st.image(str(logo_path), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="brand-block">'
            f'<h2>AI Legal</h2>'
            f'<div class="brand-tag">Contract Intelligence</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Badge
    st.markdown(
        '<div style="text-align:center; margin-bottom:0.75rem;">'
        '<span class="capstone-badge">🎓 Final Year Capstone</span>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Status
    st.markdown(
        '<div style="text-align:center; margin-bottom:1.25rem;">'
        '<span class="status-pill"><span class="dot"></span> Local ML Online</span>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Stats Header
    st.markdown(
        '<div class="sidebar-kicker">Workspace Stats</div>',
        unsafe_allow_html=True
    )
    
    # Stat Card 1
    st.markdown(
        f'<div class="sidebar-card">'
        f'<div class="stat-value">{total_contracts}</div>'
        f'<div class="stat-label">Contracts Saved</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Stat Card 2
    st.markdown(
        '<div class="sidebar-card">'
        '<div class="stat-value">v2.5</div>'
        '<div class="stat-label">Platform Version</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Quick Access Links
    st.markdown(
        '<div class="sidebar-kicker">Quick Navigation</div>',
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<div class="sidebar-links">'
        '<div><span>📝</span> 1. Draft Contract</div>'
        '<div><span>📄</span> 2. Review Contract</div>'
        '<div><span>💡</span> 3. Explain Clause</div>'
        '<div><span>🚨</span> 4. Risk Analysis</div>'
        '<div><span>📁</span> 5. Contract Vault</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Version Tag
    st.markdown(
        '<div class="version-tag">ENTERPRISE EDITION v2.5 · 2026</div>',
        unsafe_allow_html=True
    )

# ===========================
# Greeting
# ===========================
hour = datetime.now().hour
if hour < 12:
    greeting = "Good Morning"
elif hour < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

# ===========================
# Hero Banner
# ===========================
hero_col1, hero_col2 = st.columns([3, 1])

with hero_col1:
    st.markdown(f"""
    <div class="hero">
        <div class="eyebrow">🎓 Final Year Capstone Project · {greeting}</div>
        <h1>AI Legal Contract Assistant</h1>
        <p class="lede">
            An enterprise-grade legal technology platform powered by trained local ML models. 
            Draft legal agreements, perform automated risk audits, detect missing protective clauses, 
            and transform complex legalese into plain language.
        </p>
        <div class="hero-stats">
            <div class="hero-stat">
                <div class="num">{total_contracts}</div>
                <div class="label">Contracts Saved</div>
            </div>
            <div class="hero-stat">
                <div class="num">100%</div>
                <div class="label">Local Privacy</div>
            </div>
            <div class="hero-stat">
                <div class="num">Local ML</div>
                <div class="label">Reasoning Engine</div>
            </div>
            <div class="hero-stat">
                <div class="num">Active</div>
                <div class="label">System Health</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_col2:
    if logo_path.exists():
        st.markdown('<div class="glass-card" style="text-align:center; padding:1.5rem;">', unsafe_allow_html=True)
        st.image(str(logo_path), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Tech Stack Ribbon
st.markdown("""
<div class="tech-ribbon">
    <span class="label">Technology Stack</span>
    <span class="tech-badge">Python 3.14</span>
    <span class="tech-badge">Streamlit UI</span>
    <span class="tech-badge">Local ML Pipeline</span>
    <span class="tech-badge">PyMuPDF</span>
    <span class="tech-badge">ReportLab PDF</span>
    <span class="tech-badge">SQLite Database</span>
</div>
""", unsafe_allow_html=True)

# ===========================
# Quick Action Cards
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Core Application Modules</h2></div>
<div class="section-sub">Select an automated tool to launch your workspace.</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_DRAFT)}
        <h3>Draft Contract</h3>
        <p>Assemble custom agreements with guided clause selection and local template engine generation.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Drafting →", use_container_width=True, key="btn_draft"):
        st.switch_page("pages/1_Draft_Contract.py")

with c2:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_REVIEW)}
        <h3>Review Contract</h3>
        <p>Upload a contract PDF and receive a full structural risk report and summary.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Review →", use_container_width=True, key="btn_review"):
        st.switch_page("pages/3_Review_Contract.py")

with c3:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_EXPLAIN)}
        <h3>Explain Clause</h3>
        <p>Translate complex or ambiguous legal provisions into clear business terms.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Explainer →", use_container_width=True, key="btn_explain"):
        st.switch_page("pages/4_Explain_Clause.py")

with c4:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_RISK)}
        <h3>Risk Analysis</h3>
        <p>Identify one-sided indemnities, liabilities, and omitted protective clauses.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Risk Matrix →", use_container_width=True, key="btn_risk"):
        st.switch_page("pages/5_Risk_Analysis.py")

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Workflow Pipeline
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>System Architecture & Workflow</h2></div>
<div class="section-sub">From document ingestion to AI analysis and publication-ready PDF output.</div>
""", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("""
    <div class="step-card">
        <div class="step-circle">01</div>
        <h3>Ingest or Formulate</h3>
        <p>Import PDF agreements parsed via PyMuPDF or specify agreement parameters through structured wizard forms.</p>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown("""
    <div class="step-card">
        <div class="step-circle">02</div>
        <h3>Local Cognitive Audit</h3>
        <p>Clauses are cross-referenced against legal standards, risk scored, and classified for unfair liabilities.</p>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown("""
    <div class="step-card">
        <div class="step-circle">03</div>
        <h3>Decide & Export PDF</h3>
        <p>Review interactive AI reports, refine terms, and generate official formatted PDF documents via ReportLab.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Platform Bento Highlights
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 03</span><h2>Key Differentiators</h2></div>
<div class="section-sub">Why this AI legal platform stands out for real-world legal operations.</div>
""", unsafe_allow_html=True)

b1, b2, b3 = st.columns([1.3, 1, 1])

with b1:
    st.markdown("""
    <div class="bento-card dark">
        <div class="stat">10×</div>
        <h3>Accelerated Legal Audit</h3>
        <p>Surfaces indemnities, unlimited liabilities, and missing standard provisions in seconds instead of hours.</p>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown("""
    <div class="bento-card">
        <h3>Plain-Language Translations</h3>
        <p>Converts impenetrable legalese into clear business summaries for non-lawyer decision makers.</p>
    </div>
    """, unsafe_allow_html=True)

with b3:
    st.markdown("""
    <div class="bento-card">
        <h3>Private SQLite Repository</h3>
        <p>All contract data and history are stored locally in an embedded SQLite database environment.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Recent Activity
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 04</span><h2>Recent Activity</h2></div>
""", unsafe_allow_html=True)

_AICONS = {"Drafted": "📝", "Reviewed": "🔍", "Clause Explained": "💡", "Risk Analyzed": "⚠️"}

try:
    _recent_history = get_recent_history(5)
except Exception:
    _recent_history = []

if _recent_history:
    for _name, _ctype, _activity, _created_at, _status in _recent_history:
        _icon = _AICONS.get(_activity, "📄")
        st.markdown(f"""
        <div class="ledger-row">
            <div>
                <h4 style="margin:0;">{_icon} {_name}</h4>
                <span style="font-size:0.8rem; color:#5D6B7A;">{_activity} · {_ctype} · {_created_at}</span>
            </div>
            <span class="tech-badge">{_status}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No contract activity yet — draft or review your first agreement above.")

st.markdown("<br>", unsafe_allow_html=True)

# ===============================
# Legal Tip of the Day
# ===============================
tips = [
    "Always specify governing law, jurisdiction, and venue in cross-border agreements.",
    "Ensure indemnification caps match overall agreement liability boundaries.",
    "Explicitly define IP ownership for all work product produced during the engagement.",
    "Include clear termination rights for breach alongside curing periods.",
    "In corporate NDAs, verify carve-outs for information required by law to be disclosed."
]

st.markdown(f"""
<div class="tip">
    <h3>Legal Tip of the Day</h3>
    <p>"{random.choice(tips)}"</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Analytics Dashboard
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 05</span><h2>Analytics Overview</h2></div>
""", unsafe_allow_html=True)

left_chart, right_chart = st.columns(2)

df = get_contract_type_data()

with left_chart:
    st.markdown('<div class="chart-card"><div class="chart-title">Contracts by Type</div>', unsafe_allow_html=True)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(6, 3.8))
        fig.patch.set_facecolor('#172033')
        ax.set_facecolor('#172033')
        ax.bar(df["contract_type"], df["total"], color='#D4A853', width=0.55)
        ax.set_ylabel("Total", color='#CBD5E1', fontsize=9)
        ax.tick_params(colors='#CBD5E1', labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color('#334155')
        plt.xticks(rotation=20, ha='right', color='#CBD5E1')
        st.pyplot(fig)
    else:
        st.info("No contract classification data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with right_chart:
    st.markdown('<div class="chart-card"><div class="chart-title">Contract Growth Trend</div>', unsafe_allow_html=True)
    df_dates = get_contract_date_data()
    if not df_dates.empty:
        df_dates["created_date"] = pd.to_datetime(
            df_dates["created_date"],
            errors="coerce"
        )
        df_dates = df_dates.dropna()

        counts = (
            df_dates.groupby(df_dates["created_date"].dt.date)
            .size()
            .reset_index(name="count")
        )

        fig, ax = plt.subplots(figsize=(6, 3.8))
        fig.patch.set_facecolor('#172033')
        ax.set_facecolor('#172033')
        ax.plot(
            counts["created_date"],
            counts["count"],
            marker="o",
            color='#D4A853',
            linewidth=2.5
        )
        ax.tick_params(colors='#CBD5E1', labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color('#334155')
        plt.xticks(rotation=25, ha='right', color='#CBD5E1')
        st.pyplot(fig)
    else:
        st.info("No timeline data available.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Footer
# ===========================
st.markdown("""
<div class="footer-dark">
    <div class="footer-grid">
        <div class="footer-col" style="max-width:320px;">
            <div class="brandline">AI Legal Contract Assistant</div>
            <p>An enterprise-grade, AI-assisted platform for drafting, reviewing, and analyzing
            legal contracts — developed as a Final Year Engineering Capstone Project.</p>
        </div>
        <div class="footer-col">
            <h5>Core Modules</h5>
            <p>Draft Contract<br>Review Contract<br>Explain Clause<br>Risk Analysis</p>
        </div>
        <div class="footer-col">
            <h5>Management</h5>
            <p>Contract History<br>Analytics<br>Settings<br>Documentation</p>
        </div>
        <div class="footer-col">
            <h5>Technologies</h5>
            <p>Streamlit · Local ML Engine<br>PyMuPDF · ReportLab<br>Pydantic · SQLite</p>
        </div>
    </div>
    <div class="bottom-line">
        <span>© 2026 AI Legal Contract Assistant</span>
        <span>FINAL YEAR CAPSTONE PROJECT · v2.5</span>
    </div>
</div>
""", unsafe_allow_html=True)