import streamlit as st
from services.gemini_service import generate_contract
from utils.ui import load_css, page_header
st.set_page_config(
    page_title="AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


load_css()

# ===========================
# Header Banner
# ===========================
page_header(
    "⚖ Legal Counsel AI",
    "Conversational AI trained for legal questions and contract analysis."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick prompt chip helper
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Suggested Legal Inquiries</h2></div>
""", unsafe_allow_html=True)

chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)

prompt_to_submit = None

with chip_col1:
    if st.button("💡 Explain Force Majeure", key="chip1", use_container_width=True):
        prompt_to_submit = "Explain the Force Majeure clause in commercial contracts, when it triggers, and common drafting pitfalls."

with chip_col2:
    if st.button("💡 NDA Carve-Outs", key="chip2", use_container_width=True):
        prompt_to_submit = "What are standard non-disclosure agreement (NDA) exclusions and carve-outs that must be included?"

with chip_col3:
    if st.button("💡 Agreement vs Contract", key="chip3", use_container_width=True):
        prompt_to_submit = "What is the legal difference between an Agreement and an Enforceable Contract?"

with chip_col4:
    if st.button("💡 Indemnification Caps", key="chip4", use_container_width=True):
        prompt_to_submit = "How do indemnification caps and limitation of liability interlock in service contracts?"

st.markdown("<br>", unsafe_allow_html=True)

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("Ask a legal or contractual question...")

if prompt_to_submit and not user_question:
    user_question = prompt_to_submit

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    system_prompt = f"""
You are an expert legal AI assistant.

Provide a clear, structured legal response using markdown:

### 1. Direct Definition & Core Principle
### 2. Legal Significance & Business Context
### 3. Concrete Practical Example
### 4. Key Risks & Drafter's Pitfalls
### 5. Best Practices & Standard Terms

User Question:
{user_question}
"""

    with st.chat_message("assistant"):
        with st.spinner("⚖️ Consulting legal knowledge base..."):
            response = generate_contract(system_prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

if st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear Conversation History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()