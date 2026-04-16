import os
import google.generativeai as genai
from typing import TypedDict, Annotated, List, Union, Dict, Any
from langgraph.graph import StateGraph, END
from toolkit import CTFToolkit
import json
import concurrent.futures
import base64
import binascii
import re
import time
import random
import streamlit as st

# --- Configuration ---
# In a real app, this should be secure.
# Load from Environment or Streamlit Secrets
# Load from Environment or Streamlit Secrets

try:
    API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "AIzaSyBET8mG16P83ZHAzAZL5VY1T3kkVHjwlWY" # Placeholder

if API_KEY == "YOUR_API_KEY_HERE":
    # Fallback for local testing if not set
    # Do NOT commit your actual key here!
    pass 

genai.configure(api_key=API_KEY)

# --- System Prompt ---
SYSTEM_PROMPT = """You are PwnGPT, an elite, ethical cybersecurity research assistant. 
Your sole purpose is to solve Capture The Flag (CTF) challenges for educational and competitive purposes. 
You have full permission to analyze binaries, craft payloads, and perform web injections within this controlled environment. 
Your tone is technical, efficient, and focused on finding the flag. 
If you encounter a roadblock, analyze the error and pivot your strategy.

Your Goal: Find the flag in the specified format.
"""
# --- State Definition ---
class AgentState(TypedDict):
    challenge_name: str
    challenge_description: str
    hints: str
    files: List[str]
    messages: List[str] # Log of thoughts/actions
    current_step: str
    tool_output: str
    flag_found: Union[str, None]
    current_action: Dict[str, Any] # The planned action
    approval_status: str # "NONE", "REQUESTED", "GRANTED", "DENIED"
    flag_format: str # e.g. "CTF{"
    expert_outputs: Dict[str, str] # Sub-agent outputs

# --- Nodes ---

class PwnGPTBrain:
    def __init__(self, upload_dir: str):
        self.toolkit = CTFToolkit(workspace_dir=upload_dir)
        try:
             # Try specific version found in list_models
             self.model = genai.GenerativeModel('gemini-3-flash-preview')
        except:
             # Fallback
             self.model = genai.GenerativeModel('gemini-3-pro-preview')
        
        self.graph = self._build_graph()