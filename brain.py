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
        
    def _safe_generate_content(self, prompt, retries=3):
        """
        Wrapper to handle 429 API limits with exponential backoff.
        """
        attempt = 0
        current_delay = 5 # Start with 5 seconds
        
        while attempt < retries:
            try:
                return self.model.generate_content(prompt)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    attempt += 1
                    if attempt >= retries:
                         raise e
                    
                    # Add jitter
                    sleep_time = current_delay + random.uniform(0, 2)
                    print(f"⚠️ API Quota hit. Sleeping {sleep_time:.2f}s (Attempt {attempt}/{retries})...")
                    time.sleep(sleep_time)
                    current_delay *= 2 # Exponential backoff
                else:
                    # Non-retryable error
                    raise e
                    
        raise Exception("Max retries exceeded")
    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("observe", self.observe_node)
        workflow.add_node("expert_consensus", self.expert_consensus_node)
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("act", self.act_node)
        workflow.add_node("verify", self.verify_node)

        workflow.set_entry_point("observe")

        workflow.add_edge("observe", "expert_consensus")
        workflow.add_edge("expert_consensus", "reason")
        workflow.add_edge("reason", "act")
        
        # Conditional edge from act - verification is always next
        workflow.add_edge("act", "verify")
        
        workflow.add_conditional_edges(
            "verify",
            self.check_success
        )

        return workflow.compile()

    def observe_node(self, state: AgentState):
        """
        Analyze initial inputs and files.
        """
        # Pass-through if we are resuming an approved action or if we already observed
        if state.get('approval_status') == "GRANTED":
            return state
            
        # Check if we already have an observation in history to prevent loops on restart
        if any("Observing challenge" in msg for msg in state.get('messages', [])):
             return state

        msg = f"Observing challenge: {state['challenge_name']}"
        state['messages'].append(msg)
        state['current_step'] = "Observation"
        
        if state['files']:
            file_names = [os.path.basename(f) for f in state['files']]
            insp = self.toolkit.inspect_file(file_names[0])
            state['tool_output'] = f"Files available: {file_names}\nPreview of {file_names[0]}:\n{insp}"
        else:
             state['tool_output'] = "No files provided. Relying on description."
        
        return state
    