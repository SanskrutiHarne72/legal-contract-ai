from pathlib import Path
from PIL import Image
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

def load_css():
    css_path = ROOT / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )

def load_logo():
    logo = ROOT / "assets" / "logo.png"
    if logo.exists():
        return Image.open(logo)
    return None

def page_header(title, subtitle):
    st.markdown(f"""
    <div class="page-header-card">
        <div>
            <div class="page-header-badge">
                <span class="dot"></span> Enterprise AI Active · Local ML Engine
            </div>
            <h1 class="page-header-title">{title}</h1>
            <p class="page-header-sub">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def stepper_progress(active_step=1):
    """
    Renders an enterprise step-by-step drafting workflow progress bar.
    """
    s1_class = "active" if active_step >= 1 else ""
    s2_class = "active" if active_step >= 2 else ""
    s3_class = "active" if active_step >= 3 else ""

    st.markdown(f"""
    <div class="stepper-bar">
        <div class="stepper-step {s1_class}">
            <div class="stepper-num">1</div>
            <div>Select Contract Type</div>
        </div>
        <div class="stepper-divider"></div>
        <div class="stepper-step {s2_class}">
            <div class="stepper-num">2</div>
            <div>Fill Dynamic Covenants</div>
        </div>
        <div class="stepper-divider"></div>
        <div class="stepper-step {s3_class}">
            <div class="stepper-num">3</div>
            <div>AI Draft & Export</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(title, value, icon):
    st.markdown(f"""
    <div style="
        background:#172033;
        border-radius:16px;
        padding:22px;
        text-align:center;
        box-shadow:0 8px 25px rgba(0, 0, 0, 0.4);
        border:1px solid #334155;
        margin-bottom:15px;
    ">
        <h1 style="margin:0; font-size:2.2rem;">{icon}</h1>
        <h2 style="margin:0.4rem 0 0.2rem; font-family:'Playfair Display', serif; color:#D4A853; font-weight:700;">{value}</h2>
        <p style="margin:0; color:#CBD5E1; font-weight:600; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.08em;">{title}</p>
    </div>
    """, unsafe_allow_html=True)

def feature_card(title, description, icon):
    st.markdown(f"""
    <div style="
        background:#172033;
        border-radius:16px;
        padding:24px;
        box-shadow:0 8px 25px rgba(0, 0, 0, 0.4);
        border:1px solid #334155;
        margin-bottom:20px;
    ">
        <h3 style="margin-top:0; font-family:'Playfair Display', serif; color:#F8FAFC; font-size:1.25rem;">{icon} {title}</h3>
        <p style="color:#CBD5E1; font-size:0.92rem; line-height:1.6; margin-bottom:0;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def info_banner(text):
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg, #111827 0%, #172033 100%);
        color:#F8FAFC;
        padding:20px 24px;
        border-radius:16px;
        text-align:center;
        font-size:1rem;
        font-weight:600;
        margin-top:15px;
        margin-bottom:20px;
        border:1px solid #334155;
        box-shadow:0 8px 25px rgba(0, 0, 0, 0.4);
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)