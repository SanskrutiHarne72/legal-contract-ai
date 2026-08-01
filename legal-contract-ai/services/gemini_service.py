import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_contract(prompt):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    return response.text