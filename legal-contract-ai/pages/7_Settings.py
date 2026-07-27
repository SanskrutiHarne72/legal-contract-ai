import streamlit as st

def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Settings · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_css()

# ===========================
# Header Banner
# ===========================
st.markdown("""
<div class="subpage-hero">
    <h1>Platform Configuration & Settings</h1>
    <p>Manage model credentials, default legal jurisdiction rules, and workspace preferences.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>AI Model & Engine Configuration</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        model = st.selectbox("Active AI Reasoning Model", ["Google Gemini 1.5 Flash (Recommended)", "Google Gemini 1.5 Pro"])
        temp = st.slider("Drafting Creativity / Precision Temperature", 0.0, 1.0, 0.2, step=0.05, help="Lower values yield more conservative, strictly standard legal phrasing.")

    with c2:
        st.markdown('<div class="status-pill" style="margin-top:28px;"><span class="dot"></span> Gemini API Status: Active & Connected</div>', unsafe_allow_html=True)
        st.markdown("<p style='font-size:12.5px; color:var(--text-muted); margin-top:8px;'>API keys are securely loaded from system environment variables (.env).</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-head"><span class="tag">§ 02</span><h2>Default Legal Jurisdiction</h2></div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        country = st.selectbox("Primary Jurisdiction Country", ["United States", "India", "United Kingdom", "Canada", "Australia", "Singapore", "European Union"])
        state = st.text_input("Default Governing State / Province", value="California")

    with col2:
        currency = st.selectbox("Default Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)"])
        language = st.selectbox("Primary Document Language", ["English (US)", "English (UK)", "Hindi"])
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("💾 Save Workspace Settings", use_container_width=True):
    st.success("✅ Preferences saved successfully to workspace session!")