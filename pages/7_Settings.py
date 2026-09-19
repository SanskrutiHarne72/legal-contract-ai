import streamlit as st
from utils.ui import load_css, page_header

st.set_page_config(
    page_title="Settings · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

page_header(
    "⚙️ Platform Configuration & Settings",
    "Manage AI model parameters, legal jurisdiction defaults (e.g. India, Maharashtra), and document language preferences."
)

# Initialize Session State Settings if not present
if "settings_country" not in st.session_state:
    st.session_state["settings_country"] = "India"

if "settings_state" not in st.session_state:
    st.session_state["settings_state"] = "Maharashtra"

if "settings_currency" not in st.session_state:
    st.session_state["settings_currency"] = "INR (₹)"

if "settings_language" not in st.session_state:
    st.session_state["settings_language"] = "Hindi"

if "settings_model" not in st.session_state:
    st.session_state["settings_model"] = "Local LegalML Engine (Trained Offline)"

if "settings_temp" not in st.session_state:
    st.session_state["settings_temp"] = 0.2

# ===========================
# Section 1: AI Model Configuration
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>AI Model & Engine Configuration</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        model_options = [
            "Local LegalML Engine (Trained Offline)",
            "Rule-Based Risk Engine Only"
        ]
        default_model_idx = model_options.index(st.session_state["settings_model"]) if st.session_state["settings_model"] in model_options else 0
        selected_model = st.selectbox("Active AI Reasoning Model", model_options, index=default_model_idx)
        
        selected_temp = st.slider(
            "Drafting Precision / Temperature",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state["settings_temp"]),
            step=0.05,
            help="Lower values (0.1 - 0.3) produce strict, highly conservative legal drafting."
        )

    with c2:
        st.markdown('<div class="status-pill" style="margin-top:28px;"><span class="dot"></span> Local ML Engine Active</div>', unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px; color:var(--text-muted); margin-top:10px;'>Loaded securely from local disk (No external API calls required).</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Section 2: Default Legal Jurisdiction & Language
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Default Legal Jurisdiction & Preferences</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        country_options = ["India", "United States", "United Kingdom", "Canada", "Australia", "Singapore", "European Union"]
        default_country_idx = country_options.index(st.session_state["settings_country"]) if st.session_state["settings_country"] in country_options else 0
        selected_country = st.selectbox("Primary Jurisdiction Country", country_options, index=default_country_idx)

        selected_state = st.text_input(
            "Default Governing State / Province",
            value=st.session_state["settings_state"],
            placeholder="e.g. Maharashtra, Delhi, California"
        )

    with col2:
        currency_options = ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"]
        default_curr_idx = currency_options.index(st.session_state["settings_currency"]) if st.session_state["settings_currency"] in currency_options else 0
        selected_currency = st.selectbox("Default Currency", currency_options, index=default_curr_idx)

        lang_options = ["Hindi", "English (India)", "English (US)", "English (UK)"]
        default_lang_idx = lang_options.index(st.session_state["settings_language"]) if st.session_state["settings_language"] in lang_options else 0
        selected_language = st.selectbox("Primary Document & Explanation Language", lang_options, index=default_lang_idx)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("💾 Save Workspace Settings", use_container_width=True):
    st.session_state["settings_country"] = selected_country
    st.session_state["settings_state"] = selected_state
    st.session_state["settings_currency"] = selected_currency
    st.session_state["settings_language"] = selected_language
    st.session_state["settings_model"] = selected_model
    st.session_state["settings_temp"] = selected_temp
    
    st.success(f"✅ Workspace Settings Saved Successfully!\n\n• Country: **{selected_country}**\n• State/Jurisdiction: **{selected_state}**\n• Currency: **{selected_currency}**\n• Primary Language: **{selected_language}**")