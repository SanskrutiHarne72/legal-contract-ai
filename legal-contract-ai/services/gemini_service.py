import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Try local .env first
api_key = os.getenv("GEMINI_API_KEY")

# If not found, try Streamlit Cloud secrets
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing.")

client = genai.Client(api_key=api_key)


def generate_contract(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"