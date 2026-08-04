import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os
from services.database_service import init_db
from pathlib import Path
init_db()

from services.database_service import (
    get_total_contracts,
    get_recent_contracts,
    get_contract_type_data,
    get_contract_date_data
)

# ---------- Theme colors ----------
INK = "#1B4368"
GOLD = "#B8935B"
GOLD_LIGHT = "#D9BE8E"
MUTED = "#5D6B7A"
CREAM = "#FAF8F5"

# ---------- SVG Icons ----------
SCALE_MARK_SM = """<svg width="34" height="34" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><line x1="32" y1="6" x2="32" y2="50" stroke="#D9BE8E" stroke-width="1.6"/><circle cx="32" cy="6" r="2.4" fill="#D9BE8E"/><line x1="12" y1="16" x2="52" y2="16" stroke="#D9BE8E" stroke-width="1.6"/><path d="M12 16 L6 30 Q12 36 18 30 Z" stroke="#D9BE8E" stroke-width="1.3" fill="none"/><path d="M46 16 L40 30 Q46 36 52 30 Z" stroke="#D9BE8E" stroke-width="1.3" fill="none"/><rect x="22" y="52" width="20" height="4" rx="1" fill="none" stroke="#D9BE8E" stroke-width="1.2"/><line x1="32" y1="50" x2="32" y2="52" stroke="#D9BE8E" stroke-width="1.6"/></svg>"""

SCALE_MARK_LG = SCALE_MARK_SM.replace('width="34" height="34"', 'width="96" height="96"')

ICON_DRAFT = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><path d="M6 2h9l5 5v15H6z"/><path d="M15 2v6h6"/><path d="M9 13h6M9 17h6"/></svg>"""
ICON_REVIEW = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><circle cx="10" cy="10" r="6.2"/><path d="M20 20l-5.6-5.6"/></svg>"""
ICON_EXPLAIN = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><path d="M4 4h16v12H9l-4 4V4z"/><path d="M8 9h8M8 12.5h5"/></svg>"""
ICON_RISK = """<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6"><path d="M12 3l10 18H2z"/><path d="M12 9.5v5"/><circle cx="12" cy="17.3" r="0.6" fill="#B8935B" stroke="none"/></svg>"""


def load_css():
    from pathlib import Path

def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"

    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    else:
        st.error(f"CSS file not found: {css_path}")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Custom CSS not found. Please ensure `assets/style.css` exists for the best visual experience.")


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

# ==========================
# Sidebar
# ==========================
with st.sidebar:
    
    
    # Brand
    st.markdown(
        f'<div class="brand-block">'
        f'<div class="brand-mark">{SCALE_MARK_SM}</div>'
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
        '<span class="status-pill"><span class="dot"></span> Gemini Online</span>'
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
    
    # Quick Access
    st.markdown(
        '<div class="sidebar-kicker">Quick Access</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sidebar-links">'
        '<span>›</span> Draft Contract<br>'
        '<span>›</span> Review & Audit<br>'
        '<span>›</span> Risk Analysis<br>'
        '<span>›</span> Clause Explainer'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown(
        '<div class="version-tag">ENTERPRISE EDITION · 2026</div>',
        unsafe_allow_html=True
    )
    # Badge + Status
    st.markdown(
        '<div style="text-align:center; margin-bottom:1rem;">'
        '<div class="capstone-badge">🎓 Final Year Capstone</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<div style="text-align:center; margin-bottom:1.5rem;">'
        '<div class="status-pill"><span class="dot"></span> Gemini Online</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Stats
    st.markdown('<div class="sidebar-kicker">Workspace Stats</div>', unsafe_allow_html=True)
    
    st.markdown(
        f'<div class="sidebar-card">'
        f'<div class="stat-value">{total_contracts}</div>'
        f'<div class="stat-label">Contracts Saved</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<div class="sidebar-card">'
        '<div class="stat-value">v2.5</div>'
        '<div class="stat-label">Platform Version</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Quick Access
    st.markdown('<div class="sidebar-kicker">Quick Access</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-links">'
        '<span>›</span> Draft Contract<br>'
        '<span>›</span> Review & Audit<br>'
        '<span>›</span> Risk Analysis<br>'
        '<span>›</span> Clause Explainer'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown('<div class="version-tag">ENTERPRISE EDITION · 2026</div>', unsafe_allow_html=True)
    # Workspace Stats Section
    st.markdown('<div class="sidebar-kicker">Workspace Stats</div>', unsafe_allow_html=True)

    # Contract Count Card
    st.markdown(
        f'<div class="sidebar-card">'
        f'<div class="stat-value">{total_contracts}</div>'
        f'<div class="stat-label">Contracts Saved</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Secondary stat (you can change this number or make it dynamic later)
    st.markdown(
        '<div class="sidebar-card">'
        '<div class="stat-value">v2.5</div>'
        '<div class="stat-label">Platform Version</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Quick Links Section (Optional - makes sidebar feel like a dashboard)
    st.markdown('<div class="sidebar-kicker">Quick Access</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:rgba(255,255,255,0.6); font-size:0.82rem; padding:0 0.5rem;">'
        '• Draft Contract<br>• Review & Audit<br>• Risk Analysis<br>• Clause Explainer'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown('<div class="version-tag">ENTERPRISE EDITION · 2026</div>', unsafe_allow_html=True)
# ===========================
# Greeting
# ===========================
hour = datetime.now().hour
greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"

# ===========================
# Hero Banner
# ===========================
st.markdown(f"""
<div class="hero">
    <div class="hero-top">
        <div>
            <div class="eyebrow"><span>🎓 Final Year Project</span> · <span>{greeting}</span> · Legal Automation Platform</div>
            <h1>AI Legal Contract Assistant</h1>
            <p class="lede">
                An intelligent legal tech engine powered by Google Gemini AI — 
                draft custom contracts, perform automated risk audits, detect missing liabilities, and transform dense legalese into plain language.
            </p>
        </div>
        <div class="hero-mark-lg">{SCALE_MARK_LG}</div>
    </div>
    <div class="hero-stats">
        <div class="hero-stat"><div class="num">{total_contracts}</div><div class="label">Contracts Saved</div></div>
        <div class="hero-stat"><div class="num">100%</div><div class="label">Local Privacy</div></div>
        <div class="hero-stat"><div class="num">Gemini 1.5</div><div class="label">Reasoning Model</div></div>
        <div class="hero-stat"><div class="num">Active</div><div class="label">System Health</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tech Stack Ribbon
st.markdown("""
<div class="tech-ribbon">
    <span class="label">Technology Stack</span>
    <span class="tech-badge">Python 3.12</span>
    <span class="tech-badge">Streamlit UI</span>
    <span class="tech-badge">Google Gemini AI</span>
    <span class="tech-badge">PyMuPDF</span>
    <span class="tech-badge">ReportLab PDF Engine</span>
    <span class="tech-badge">SQLite Database</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Quick Action Cards
# ===========================
st.markdown("""<div class="section-head"><span class="tag">§ 01</span><h2>Core Application Modules</h2></div><div class="section-sub">Launch your desired AI legal tool below.</div>""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="action-card">{icon_badge(ICON_DRAFT)}<h3>Draft Contract</h3><p>Assemble custom agreements with guided clause selection and Gemini AI generation.</p></div>', unsafe_allow_html=True)
    if st.button("Launch Drafting →", use_container_width=True, key="btn_draft"):
        st.switch_page("pages/1_Draft_Contract.py")

with c2:
    st.markdown(f'<div class="action-card">{icon_badge(ICON_REVIEW)}<h3>Review Contract</h3><p>Upload a contract PDF and receive a full structural risk report and summary.</p></div>', unsafe_allow_html=True)
    if st.button("Launch Review →", use_container_width=True, key="btn_review"):
        st.switch_page("pages/3_Review_Contract.py")

with c3:
    st.markdown(f'<div class="action-card">{icon_badge(ICON_EXPLAIN)}<h3>Explain Clause</h3><p>Translate complex or ambiguous legal provisions into clear business terms.</p></div>', unsafe_allow_html=True)
    if st.button("Launch Explainer →", use_container_width=True, key="btn_explain"):
        st.switch_page("pages/4_Explain_Clause.py")

with c4:
    st.markdown(f'<div class="action-card">{icon_badge(ICON_RISK)}<h3>Risk Analysis</h3><p>Identify one-sided indemnities, liabilities, and omitted protective clauses.</p></div>', unsafe_allow_html=True)
    if st.button("Launch Risk Matrix →", use_container_width=True, key="btn_risk"):
        st.switch_page("pages/5_Risk_Analysis.py")

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Workflow Pipeline
# ===========================
st.markdown("""<div class="section-head"><span class="tag">§ 02</span><h2>System Architecture & Workflow</h2></div><div class="section-sub">From document ingestion to AI analysis and publication-ready PDF output.</div>""", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("""<div class="step-card"><div class="step-circle">01</div><h3>Ingest or Formulate</h3><p>Import PDF agreements parsed via PyMuPDF or specify agreement parameters through structured wizard forms.</p></div>""", unsafe_allow_html=True)
with s2:
    st.markdown("""<div class="step-card"><div class="step-circle">02</div><h3>Gemini Cognitive Audit</h3><p>Clauses are cross-referenced against legal standards, risk scored, and classified for unfair liabilities.</p></div>""", unsafe_allow_html=True)
with s3:
    st.markdown("""<div class="step-card"><div class="step-circle">03</div><h3>Decide & Export PDF</h3><p>Review interactive AI reports, refine terms, and generate official formatted PDF documents via ReportLab.</p></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Bento Highlights
# ===========================
st.markdown("""<div class="section-head"><span class="tag">§ 03</span><h2>Key Differentiators</h2></div><div class="section-sub">Why this AI legal platform stands out for real-world legal operations.</div>""", unsafe_allow_html=True)

b1, b2, b3 = st.columns([1.3, 1, 1])
with b1:
    st.markdown("""<div class="bento-card dark"><div class="stat">10×</div><h3>Accelerated Legal Audit</h3><p>Surfaces indemnities, unlimited liabilities, and missing standard provisions in seconds instead of hours.</p></div>""", unsafe_allow_html=True)
with b2:
    st.markdown("""<div class="bento-card"><h3>Plain-Language Translations</h3><p>Converts impenetrable legalese into clear business summaries for non-lawyer decision makers.</p></div>""", unsafe_allow_html=True)
with b3:
    st.markdown("""<div class="bento-card"><h3>Private SQLite Repository</h3><p>All contract data and history are stored locally in an embedded SQLite database environment.</p></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Recent Activity
# ===========================
st.markdown("""<div class="section-head"><span class="tag">§ 04</span><h2>Recent Repository Activity</h2></div>""", unsafe_allow_html=True)

if recent_contracts:
    for title, contract_type, created_date in recent_contracts:
        st.markdown(f"""<div class="ledger-row"><h4>{title}</h4><span class="tech-badge">{contract_type}</span><span class="meta">{created_date}</span></div>""", unsafe_allow_html=True)
else:
    st.info("📂 No contracts saved in database yet — draft or upload your first agreement above.")

st.markdown("<br>", unsafe_allow_html=True)

# ===============================
# Legal Tip
# ===============================
tips = [
    "Always specify governing law, jurisdiction, and venue in cross-border agreements.",
    "Ensure indemnification caps match overall agreement liability boundaries.",
    "Explicitly define IP ownership for all work product produced during the engagement.",
    "Include clear termination rights for breach alongside curing periods.",
    "In corporate NDAs, verify carve-outs for information required by law to be disclosed.",
    "Never accept unlimited liability clauses without carve-outs for consequential damages.",
    "Always require written notice for termination to avoid oral cancellation disputes.",
    "Define 'Confidential Information' precisely to avoid overbroad obligations."
]

st.markdown(f"""<div class="tip"><h3>Legal Tip of the Day</h3><p>"{random.choice(tips)}"</p></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Analytics
# ===========================
st.markdown("""<div class="section-head"><span class="tag">§ 05</span><h2>Analytics Overview</h2></div>""", unsafe_allow_html=True)

left_chart, right_chart = st.columns(2)
df = get_contract_type_data()

with left_chart:
    st.markdown('<div class="chart-card"><div class="chart-title">Contracts by Type</div>', unsafe_allow_html=True)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(6, 3.8))
        bars = ax.bar(df["contract_type"], df["total"], color=INK, width=0.55, edgecolor=GOLD, linewidth=0.5)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontsize=9, color=MUTED)
        ax.set_ylabel("Total", color=MUTED, fontsize=9)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(MUTED)
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
        plt.xticks(rotation=20, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No contract classification data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with right_chart:
    st.markdown('<div class="chart-card"><div class="chart-title">Contract Growth Trend</div>', unsafe_allow_html=True)
    df_dates = get_contract_date_data()
    if not df_dates.empty:
        df_dates["created_date"] = pd.to_datetime(df_dates["created_date"], errors="coerce")
        df_dates = df_dates.dropna()
        counts = df_dates.groupby(df_dates["created_date"].dt.date).size().reset_index(name="count")
        fig, ax = plt.subplots(figsize=(6, 3.8))
        ax.fill_between(counts["created_date"], counts["count"], alpha=0.3, color=GOLD)
        ax.plot(counts["created_date"], counts["count"], marker="o", color=GOLD, linewidth=2.5, markersize=6, markerfacecolor=CREAM, markeredgecolor=GOLD, markeredgewidth=2)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(MUTED)
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
        plt.xticks(rotation=25, ha='right')
        plt.tight_layout()
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
            <p>An enterprise-grade, AI-assisted platform for drafting, reviewing, and analyzing legal contracts.</p>
        </div>
        <div class="footer-col"><h5>Core Modules</h5><p>Draft Contract<br>Review Contract<br>Explain Clause<br>Risk Analysis</p></div>
        <div class="footer-col"><h5>Management</h5><p>Contract History<br>Analytics<br>Settings<br>Documentation</p></div>
        <div class="footer-col"><h5>Technologies</h5><p>Streamlit · Google Gemini AI<br>PyMuPDF · ReportLab<br>Pydantic · SQLite</p></div>
    </div>
    <div class="bottom-line">
        <span>© 2026 AI Legal Contract Assistant</span>
        <span>FINAL YEAR CAPSTONE PROJECT · v2.5</span>
    </div>
</div>
""", unsafe_allow_html=True)