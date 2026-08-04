import streamlit as st

from utils.ui import load_css, page_header

st.set_page_config(
    page_title="About · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_css()

# ===========================
page_header(
    "ℹ️ About AI Legal Contract Assistant",
    "An AI-powered platform for drafting, reviewing, analyzing, and managing legal contracts."
)
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>System Architecture & Overview</h2></div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="glass-card">
        <h3>🎯 Project Mission</h3>
        <p>The AI Legal Contract Assistant bridges the gap between complex legal drafting and modern software automation. Powered by Google Gemini AI, it helps founders, legal operations teams, and individuals draft tailored contracts, analyze liabilities, and understand dense legal provisions in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <h3>⚡ Core Capabilities</h3>
        <p>• <strong>AI Contract Drafting:</strong> Guided multi-clause agreement builder<br>
        • <strong>PDF Ingestion & Review:</strong> PyMuPDF document parsing & structural analysis<br>
        • <strong>Risk Audit Matrix:</strong> Automated liability and missing clause detector<br>
        • <strong>Clause Simplifier:</strong> Plain-language legal translation<br>
        • <strong>PDF Export:</strong> ReportLab publication-ready document generation</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Technology Stack</h2></div>
""", unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6 = st.columns(6)

with t1:
    st.markdown('<div class="card"><h2>Streamlit</h2><p>Frontend Framework</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="card"><h2>Gemini AI</h2><p>Reasoning Engine</p></div>', unsafe_allow_html=True)
with t3:
    st.markdown('<div class="card"><h2>PyMuPDF</h2><p>PDF Text Parser</p></div>', unsafe_allow_html=True)
with t4:
    st.markdown('<div class="card"><h2>ReportLab</h2><p>PDF Generator</p></div>', unsafe_allow_html=True)
with t5:
    st.markdown('<div class="card"><h2>SQLite</h2><p>Local Database</p></div>', unsafe_allow_html=True)
with t6:
    st.markdown('<div class="card"><h2>Pydantic</h2><p>Data Validation</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="footer-dark">
    <div class="footer-grid">
        <div class="footer-col" style="max-width:320px;">
            <div class="brandline">AI Legal Contract Assistant</div>
            <p>Developed as an advanced engineering capstone project establishing a modern standard for AI-assisted legal technology.</p>
        </div>
        <div class="footer-col">
            <h5>Version Info</h5>
            <p>Version 1.0.0<br>Build 2026.07<br>Release Channel: Stable</p>
        </div>
        <div class="footer-col">
            <h5>Security & Privacy</h5>
            <p>Local SQLite Storage<br>No Third-party Data Vaults<br>Environment Secured API Keys</p>
        </div>
    </div>
    <div class="bottom-line">
        <span>© 2026 AI Legal Contract Assistant</span>
        <span>FINAL YEAR ENGINEERING CAPSTONE</span>
    </div>
</div>
""", unsafe_allow_html=True)