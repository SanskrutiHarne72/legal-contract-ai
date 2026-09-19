import streamlit as st
from services.ml_service import LegalMLService
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
    "AI-powered legal information based on Indian law — structured, cited, and clearly explained."
)

# ===========================
# Disclaimer banner
# ===========================
st.info(
    "**⚠ Important Disclaimer:** This assistant provides general legal information under Indian law "
    "for educational purposes only. It does **not** constitute legal advice, and the information "
    "presented may not reflect the latest legislative changes. Results can depend on specific facts, "
    "evidence, and judicial interpretation. **Always consult a qualified legal professional "
    "for advice on your specific situation.**",
    icon="⚖️",
)

# ===========================
# Initialize chat history
# ===========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===========================
# Suggested prompt chips
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Suggested Legal Inquiries</h2></div>
""", unsafe_allow_html=True)

chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
prompt_to_submit = None

with chip_col1:
    if st.button("💡 Force Majeure Clause", key="chip1", use_container_width=True):
        prompt_to_submit = "What is a force majeure clause and when does it apply in Indian contracts?"

with chip_col2:
    if st.button("💡 NDA Carve-Outs", key="chip2", use_container_width=True):
        prompt_to_submit = "What are the standard exclusions and carve-outs in an NDA?"

with chip_col3:
    if st.button("💡 Non-Compete India", key="chip3", use_container_width=True):
        prompt_to_submit = "Is a non-compete clause enforceable in India?"

with chip_col4:
    if st.button("💡 Tender in Law", key="chip4", use_container_width=True):
        prompt_to_submit = "What is a tender in Indian contract and procurement law?"

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# Load ML Service
# ===========================
@st.cache_resource
def get_ml_service():
    return LegalMLService()

ml_service = get_ml_service()

# ===========================
# Render previous chat history
# ===========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===========================
# Accept input
# ===========================
user_question = st.chat_input("Ask a legal or contractual question under Indian law...")

if prompt_to_submit and not user_question:
    user_question = prompt_to_submit

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("⚖️ Consulting local legal knowledge base..."):
            result = ml_service.answer_question(user_question)

            if result.get("results"):
                top = result["results"][0]
                source = result.get("source", "faq")

                # Format the structured response
                response = top["answer"]

                # Append source note
                if source == "document":
                    response += (
                        "\n\n---\n*Source: Extracted from the uploaded contract document.*"
                    )
                else:
                    response += (
                        "\n\n---\n*Source: Local legal knowledge base (India-scoped general information). "
                        "Not legal advice. Consult a qualified legal professional for your specific situation.*"
                    )
            else:
                response = (
                    "**No relevant answer was found in the local legal knowledge base.**\n\n"
                    "This question may be outside the scope of the current knowledge base, or your query "
                    "may need to be rephrased using legal terminology. Please try:\n"
                    "- Using specific legal terms (e.g. *force majeure*, *indemnity*, *arbitration*, *tender*)\n"
                    "- Asking about a specific clause type or legal concept\n"
                    "- Consulting a qualified legal professional for detailed advice"
                )

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ===========================
# Clear history button
# ===========================
if st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear Conversation History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
