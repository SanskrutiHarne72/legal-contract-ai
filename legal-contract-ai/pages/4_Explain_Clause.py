import streamlit as st
from services.gemini_service import generate_contract
from utils.ui import load_css, page_header
st.set_page_config(
    page_title="Explain Clause · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

load_css()

page_header(
    "📖 Clause Intelligence Lab",
    "Deconstruct legal jargon into simple explanations, risk analysis, and business insights."
)

# Preset clauses dictionary for quick testing
PRESETS = {
    "Select a preset sample clause...": "",
    "Broad Indemnification Clause": "Party A agrees to defend, indemnify, and hold harmless Party B, its officers, directors, employees, and agents from and against any and all claims, liabilities, losses, damages, costs, or expenses (including reasonable attorneys' fees) arising out of or related to any third-party claim connected to Party A's performance under this Agreement.",
    "Strict Non-Compete Provision": "During the term of employment and for a period of twenty-four (24) months thereafter, Employee shall not directly or indirectly engage in, perform services for, invest in, or establish any business entity that competes with the Company within North America.",
    "Unilateral Limitation of Liability": "In no event shall the Company be liable to Client for any indirect, incidental, consequential, special, or punitive damages. The Company's maximum aggregate liability shall not exceed $100.00 USD, regardless of the cause of action."
}

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("""
    <div class="section-head"><span class="tag">§ 01</span><h2>Clause Input</h2></div>
    """, unsafe_allow_html=True)

    selected_preset = st.selectbox("Sample Clause Presets", list(PRESETS.keys()))
    default_text = PRESETS[selected_preset] if selected_preset != "Select a preset sample clause..." else ""

    clause_input = st.text_area(
        "Paste Legal Clause Text",
        value=default_text,
        height=260,
        placeholder="Paste any contractual section or clause text here..."
    )

    explanation_level = st.selectbox(
        "Target Audience / Explanation Style",
        [
            "Very Simple (Plain English for Business Executives)",
            "Professional (Legal Operations & Management)",
            "Law Student (Detailed Legal Analysis & Precedents)"
        ]
    )

    explain_btn = st.button("✨ Deconstruct & Explain Clause", use_container_width=True)

with col_right:
    st.markdown("""
    <div class="section-head"><span class="tag">§ 02</span><h2>AI Breakdown</h2></div>
    """, unsafe_allow_html=True)

    if explain_btn:
        if not clause_input.strip():
            st.error("⚠️ Please paste a legal clause or select a sample preset first.")
        else:
            prompt = f"""
You are a senior legal strategist. Explain the following clause text clearly.

Explanation Style Target: {explanation_level}

Structure your analysis with these clear headers:

### 1. Plain English Meaning
Summarize what this clause actually means in simple terms.

### 2. Purpose & Drafter's Intent
Why do lawyers put this clause in a contract?

### 3. Key Risks & Red Flags
What potential dangers or hidden liabilities does this clause impose?

### 4. Strategic Advantages
Who does this clause favor and why?

### 5. Practical Scenario / Example
Give a short real-world business example of this clause in action.

Clause Text:
\"\"\"{clause_input}\"\"\"
"""
            with st.spinner("⚖️ Gemini AI is analyzing clause syntax and implications..."):
                explanation = generate_contract(prompt)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(explanation)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding: 48px 24px; color: var(--text-muted);">
            <div style="font-size:36px; margin-bottom:12px;">⚖️</div>
            <h3>Ready for Analysis</h3>
            <p>Paste a clause on the left or choose a preset to generate an instant plain-language breakdown.</p>
        </div>
        """, unsafe_allow_html=True)