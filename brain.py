import os
import google.generativeai as genai
import streamlit as st

# --- Configuration ---
API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# --- System Prompt ---
SYSTEM_PROMPT = """You are PwnGPT, an ethical cybersecurity assistant specialized in solving CTF challenges.
Your goal is to analyze the challenge and suggest the best approach to find the flag.
Be concise and technical.
"""

# --- Simple Brain ---
class PwnGPTBrain:
    def __init__(self):
        pass

    def solve(self, challenge_name, description, hints=""):
        prompt = f"""
        {SYSTEM_PROMPT}

        Challenge Name: {challenge_name}
        Description: {description}
        Hints: {hints}

        What is the best approach to solve this challenge?
        """

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"