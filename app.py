import streamlit as st
import os

# --- Page Config ---
st.set_page_config(
    page_title="PwnGPT - CTF Solver",
    page_icon="🛡️",
    layout="wide"
)

# --- Helper ---
def save_uploaded_files(uploaded_files, target_dir="uploads"):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(target_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(file_path)
    return paths

# --- Session State ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "flag" not in st.session_state:
    st.session_state.flag = None

# --- Sidebar ---
with st.sidebar:
    st.title("🛡️ PwnGPT Config")
    st.divider()

    challenge_name = st.text_input("Challenge Name", "Web Intrusion 101")
    category = st.selectbox("Category", ["WEB", "PWN", "REV", "DFIR", "OSINT", "MISC", "CRYPTO"])
    flag_format = st.text_input("Flag Format", "CTF{")

    uploaded_files = st.file_uploader("Upload Challenge Files", accept_multiple_files=True)

    start_btn = st.button("🚀 Start Agent", type="primary")

    st.divider()
    if st.button("🗑️ Reset", type="secondary"):
        st.session_state.logs = []
        st.session_state.flag = None
        st.rerun()

# --- Main ---
st.markdown("# 🛡️ PwnGPT: Autonomous CTF Solver")

description = st.text_area("Challenge Description", height=150,
                            placeholder="Paste the challenge text here...")
hints = st.text_area("Hints (Optional)", height=80,
                     placeholder="Any provided hints...")

st.divider()

# --- Start Logic ---
if start_btn:
    st.session_state.logs = []
    st.session_state.flag = None

    # Save uploaded files
    file_paths = []
    if uploaded_files:
        file_paths = save_uploaded_files(uploaded_files)
        st.success(f"✅ {len(file_paths)} file(s) uploaded.")

    # Simulate agent call (brain.py not connected yet)
    st.session_state.logs.append(f"Challenge: {challenge_name}")
    st.session_state.logs.append(f"Category: {category}")
    st.session_state.logs.append(f"Description received. Waiting for agent...")

    st.info("🔄 Agent initialized. (Brain integration coming next commit.)")

# --- Console ---
st.markdown("### 🧠 Console")
if st.session_state.logs:
    for line in st.session_state.logs:
        st.text(line)
else:
    st.info("No logs yet. Start the agent to begin.")