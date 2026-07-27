import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime

from services.database_service import (
    get_total_contracts,
    get_recent_contracts,
    get_contract_type_data,
    get_contract_date_data
)

# ---------- Theme colors used in matplotlib charts ----------
INK = "#1B4368"
GOLD = "#B8935B"
GOLD_LIGHT = "#D9BE8E"
MUTED = "#5D6B7A"

# ---------- Inline SVG marks / icons (on-brand, no emoji) ----------

SCALE_MARK_SM = """
<svg width="34" height="34" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <line x1="32" y1="6" x2="32" y2="50" stroke="#D9BE8E" stroke-width="1.6"/>
  <circle cx="32" cy="6" r="2.4" fill="#D9BE8E"/>
  <line x1="12" y1="16" x2="52" y2="16" stroke="#D9BE8E" stroke-width="1.6"/>
  <path d="M12 16 L6 30 Q12 36 18 30 Z" stroke="#D9BE8E" stroke-width="1.3" fill="none"/>
  <path d="M46 16 L40 30 Q46 36 52 30 Z" stroke="#D9BE8E" stroke-width="1.3" fill="none"/>
  <rect x="22" y="52" width="20" height="4" rx="1" fill="none" stroke="#D9BE8E" stroke-width="1.2"/>
  <line x1="32" y1="50" x2="32" y2="52" stroke="#D9BE8E" stroke-width="1.6"/>
</svg>
"""

SCALE_MARK_LG = SCALE_MARK_SM.replace('width="34" height="34"', 'width="88" height="88"')

ICON_DRAFT = """
<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 2h9l5 5v15H6z"/><path d="M15 2v6h6"/><path d="M9 13h6M9 17h6"/>
</svg>
"""

ICON_REVIEW = """
<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6" xmlns="http://www.w3.org/2000/svg">
  <circle cx="10" cy="10" r="6.2"/><path d="M20 20l-5.6-5.6"/>
</svg>
"""

ICON_EXPLAIN = """
<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 4h16v12H9l-4 4V4z"/><path d="M8 9h8M8 12.5h5"/>
</svg>
"""

ICON_RISK = """
<svg viewBox="0 0 24 24" fill="none" stroke="#B8935B" stroke-width="1.6" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3l10 18H2z"/><path d="M12 9.5v5"/><circle cx="12" cy="17.3" r="0.6" fill="#B8935B" stroke="none"/>
</svg>
"""


def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def icon_badge(svg):
    return f'<div class="icon-badge">{svg}</div>'


st.set_page_config(
    page_title="AI Legal Contract Assistant",
    page_icon="⚖️",
    layout="wide"
)

total_contracts = get_total_contracts()
recent_contracts = get_recent_contracts()
load_css()

# ==========================
# Sidebar
# ==========================

with st.sidebar:
    st.markdown(
        f'<div class="brand-block"><div class="brand-mark">{SCALE_MARK_SM}</div>'
        f'<h2>AI Legal</h2><div class="brand-tag">Contract Intelligence</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="text-align:center;">'
        '<div class="status-pill"><span class="dot"></span> Gemini Engine Connected</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-kicker">Workspace</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="version-tag" style="text-align:left;margin-left:4px;">{total_contracts} contracts on file</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="version-tag">VERSION 1.0 · BUILD 2026</div>', unsafe_allow_html=True)

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
# Hero Header
# ===========================

st.markdown(f"""
<div class="hero">
    <div class="hero-top">
        <div>
            <div class="eyebrow">{greeting} · Legal Automation Platform</div>
            <h1>AI Legal Contract Assistant</h1>
            <p class="lede">
                Draft, review, and analyze legal contracts with Gemini AI precision — 
                generate custom clauses, detect risk, and transform dense legalese into plain language.
            </p>
        </div>
        <div class="hero-mark-lg">{SCALE_MARK_LG}</div>
    </div>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="num">{total_contracts}</div>
            <div class="label">Contracts on file</div>
        </div>
        <div class="hero-stat">
            <div class="num">12</div>
            <div class="label">Reviews completed</div>
        </div>
        <div class="hero-stat">
            <div class="num">4</div>
            <div class="label">Open risk flags</div>
        </div>
        <div class="hero-stat">
            <div class="num">Active</div>
            <div class="label">AI status</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tech stack ribbon
st.markdown("""
<div class="tech-ribbon">
    <span class="label">Technology Stack</span>
    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">Google Gemini AI</span>
    <span class="tech-badge">PyMuPDF</span>
    <span class="tech-badge">ReportLab PDF</span>
    <span class="tech-badge">Pydantic</span>
    <span class="tech-badge">SQLite</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Quick Actions
# ===========================

st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Quick actions</h2></div>
<div class="section-sub">Select a tool to launch your legal workspace.</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_DRAFT)}
        <h3>Draft Contract</h3>
        <p>Generate a tailored legal contract from a plain-language brief.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Draft →", use_container_width=True, key="btn_draft"):
        st.switch_page("pages/1_Draft_Contract.py")

with c2:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_REVIEW)}
        <h3>Review Contract</h3>
        <p>Upload a contract PDF and get a complete structural analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Review →", use_container_width=True, key="btn_review"):
        st.switch_page("pages/3_Review_Contract.py")

with c3:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_EXPLAIN)}
        <h3>Explain Clause</h3>
        <p>Translate dense or ambiguous legal clauses into plain English.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Explain →", use_container_width=True, key="btn_explain"):
        st.switch_page("pages/4_Explain_Clause.py")

with c4:
    st.markdown(f"""
    <div class="action-card">
        {icon_badge(ICON_RISK)}
        <h3>Risk Analysis</h3>
        <p>Surface one-sided liabilities and high-risk terms instantly.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Risk →", use_container_width=True, key="btn_risk"):
        st.switch_page("pages/5_Risk_Analysis.py")

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Pipeline (How it works)
# ===========================

st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Workflow pipeline</h2></div>
<div class="section-sub">From contract ingestion to final decision in three seamless steps.</div>
""", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("""
    <div class="step-card">
        <div class="step-circle">01</div>
        <h3>Upload or Draft</h3>
        <p>Import PDF agreements extracted via PyMuPDF or assemble new contracts with AI assistance.</p>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown("""
    <div class="step-card">
        <div class="step-circle">02</div>
        <h3>Gemini Reasoning</h3>
        <p>Clauses are parsed, classified, cross-referenced for missing terms, and risk-rated.</p>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown("""
    <div class="step-card">
        <div class="step-circle">03</div>
        <h3>Export & Decide</h3>
        <p>Interrogate the assistant, resolve flagged issues, and produce publication-ready PDF documents.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Why AI Legal (Bento)
# ===========================

st.markdown("""
<div class="section-head"><span class="tag">§ 03</span><h2>Platform highlights</h2></div>
<div class="section-sub">Designed for law professionals, founders, and contract managers.</div>
""", unsafe_allow_html=True)

b1, b2, b3 = st.columns([1.3, 1, 1])

with b1:
    st.markdown("""
    <div class="bento-card dark">
        <div class="stat">10×</div>
        <h3>Accelerated Review</h3>
        <p>Surfaces liabilities, unfair indemnities, and missing standard clauses in seconds rather than hours.</p>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown("""
    <div class="bento-card">
        <h3>Plain-Language Summaries</h3>
        <p>Translates complex legal jargon into clear, actionable bullet points for non-legal stakeholders.</p>
    </div>
    """, unsafe_allow_html=True)

with b3:
    st.markdown("""
    <div class="bento-card">
        <h3>Private SQLite Storage</h3>
        <p>All generated agreements and review histories remain strictly stored in your local database environment.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Recent Activity
# ===========================

st.markdown("""
<div class="section-head"><span class="tag">§ 04</span><h2>Recent activity</h2></div>
""", unsafe_allow_html=True)

if recent_contracts:
    for title, contract_type, created_date in recent_contracts:
        st.markdown(f"""
        <div class="ledger-row">
            <h4>{title}</h4>
            <span class="tech-badge">{contract_type}</span>
            <span class="meta">{created_date}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No contracts created yet — draft or upload your first agreement above.")

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
<div class="section-head"><span class="tag">§ 05</span><h2>Analytics overview</h2></div>
""", unsafe_allow_html=True)

left_chart, right_chart = st.columns(2)

df = get_contract_type_data()

with left_chart:
    st.markdown('<div class="chart-card"><div class="chart-title">Contracts by Type</div>', unsafe_allow_html=True)

    if not df.empty:
        fig, ax = plt.subplots(figsize=(6, 3.8))
        ax.bar(df["contract_type"], df["total"], color=INK, width=0.55)
        ax.set_ylabel("Total", color=MUTED, fontsize=9)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(MUTED)
        fig.patch.set_alpha(0)
        plt.xticks(rotation=20, ha='right')
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
        ax.plot(
            counts["created_date"],
            counts["count"],
            marker="o",
            color=GOLD,
            linewidth=2.5
        )
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(MUTED)
        fig.patch.set_alpha(0)
        plt.xticks(rotation=25, ha='right')
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
        <div class="footer-col" style="max-width:300px;">
            <div class="brandline">AI Legal Contract Assistant</div>
            <p>An enterprise-grade workspace for drafting, reviewing, and analyzing
            legal contracts powered by Google Gemini AI.</p>
        </div>
        <div class="footer-col">
            <h5>Product Workspace</h5>
            <p>Draft Contract<br>Review Contract<br>Explain Clause<br>Risk Analysis</p>
        </div>
        <div class="footer-col">
            <h5>Management</h5>
            <p>Contract History<br>Analytics<br>Settings<br>Documentation</p>
        </div>
        <div class="footer-col">
            <h5>Technology</h5>
            <p>Streamlit · Google Gemini<br>PyMuPDF · ReportLab<br>Pydantic · SQLite</p>
        </div>
    </div>
    <div class="bottom-line">
        <span>© 2026 AI Legal Contract Assistant</span>
        <span>ENTERPRISE BUILD 2026 · v1.0</span>
    </div>
</div>
""", unsafe_allow_html=True)
