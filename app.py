import streamlit as st
import os
import time
import shutil
from brain import PwnGPTBrain
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SANDBOX_PATH = os.path.join(BASE_DIR, "sandbox_workspace")
os.makedirs(SANDBOX_PATH, exist_ok=True)
# --- Theme Toggle ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # Default theme

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# --- Page Config ---
st.set_page_config(
    page_title="PwnGPT - Autonomous CTF Solver",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Custom CSS ---
# --- Load Custom CSS ---
def load_css():
    theme = st.session_state.get("theme", "dark")
    css_file = "css/style_dark.css" if theme == "dark" else "css/style_light.css"
    
    try:
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file '{css_file}' not found. Using default styles.")
load_css()
# --- Helper Functions ---
def save_uploaded_files(uploaded_files, target_dir="uploads"):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(target_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(file_path)
    return paths, target_dir

def reset_env():
    """Clears the sandbox and session state, and KILLS the persistent Docker container."""
    # 1. Kill Container
    try:
        import subprocess
        subprocess.run(["docker", "rm", "-f", "pwngpt-session"], capture_output=True)
    except Exception as e:
        print(f"Failed to kill docker: {e}")
