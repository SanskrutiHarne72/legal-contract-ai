from pathlib import Path
from PIL import Image
import streamlit as st


ROOT = Path(__file__).resolve().parent.parent

from pathlib import Path
import streamlit as st

def load_css():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"

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

    col1, col2 = st.columns([1,4])

    with col1:
        if logo:
            st.image(logo, width=120)

    with col2:
        st.markdown(f"""
        <h1 style="margin-bottom:0px;">{title}</h1>
        <p style="font-size:18px;color:gray;">
        {subtitle}
        </p>
        """, unsafe_allow_html=True)

def metric_card(title, value, icon):
    st.markdown(f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:25px;
        text-align:center;
        box-shadow:0 8px 20px rgba(0,0,0,.12);
        margin-bottom:15px;
    ">
        <h1>{icon}</h1>
        <h2>{value}</h2>
        <p>{title}</p>
    </div>
    """, unsafe_allow_html=True)

def feature_card(title, description, icon):
    st.markdown(f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:20px;
        box-shadow:0 8px 18px rgba(0,0,0,.12);
        margin-bottom:20px;
    ">
        <h2>{icon} {title}</h2>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def info_banner(text):
    st.markdown(f"""
    <div style="
        background:#1565C0;
        color:white;
        padding:18px;
        border-radius:15px;
        text-align:center;
        font-size:18px;
        margin-top:15px;
        margin-bottom:20px;
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)