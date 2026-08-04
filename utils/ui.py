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
    logo = load_logo()
    col1, col2 = st.columns([1, 4])
    with col1:
        if logo:
            st.image(logo, use_container_width=True)
    with col2:
        st.markdown(f"""
        <h1 style="margin-bottom:0.25rem;">{title}</h1>
        <p style="font-size:1.05rem; color:#5D6B7A; margin-top:0;">
        {subtitle}
        </p>
        """, unsafe_allow_html=True)

def metric_card(title, value, icon):
    st.markdown(f"""
    <div style="
        background:white;
        border-radius:16px;
        padding:20px;
        text-align:center;
        box-shadow:0 4px 15px rgba(0,0,0,.08);
        border:1px solid rgba(184, 147, 91, 0.2);
        margin-bottom:15px;
    ">
        <h1 style="margin:0;">{icon}</h1>
        <h2 style="margin:0.25rem 0;">{value}</h2>
        <p style="margin:0; color:#5D6B7A;">{title}</p>
    </div>
    """, unsafe_allow_html=True)

def feature_card(title, description, icon):
    st.markdown(f"""
    <div style="
        background:white;
        border-radius:16px;
        padding:20px;
        box-shadow:0 4px 15px rgba(0,0,0,.08);
        border:1px solid rgba(184, 147, 91, 0.2);
        margin-bottom:20px;
    ">
        <h3 style="margin-top:0;">{icon} {title}</h3>
        <p style="color:#5D6B7A;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def info_banner(text):
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg, #0f1f3d 0%, #1B4368 100%);
        color:white;
        padding:18px;
        border-radius:15px;
        text-align:center;
        font-size:18px;
        margin-top:15px;
        margin-bottom:20px;
        border:1px solid rgba(184, 147, 91, 0.3);
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)