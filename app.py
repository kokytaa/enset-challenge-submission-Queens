import streamlit as st
import os
import time
import shutil
from brain import PwnGPTBrain

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SANDBOX_PATH = os.path.join(BASE_DIR, "sandbox_workspace")
os.makedirs(SANDBOX_PATH, exist_ok=True)

FLAG_ACCESS_CODE = "1234"  # ← Changez ce code ici

# --- Theme Toggle ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

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
def load_css():
    theme = st.session_state.get("theme", "dark")
    css_file = "css/style.css" if theme == "dark" else "css/style.css"
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

    # 2. Clear Sandbox Files
    sandbox_path = SANDBOX_PATH
    if os.path.exists(sandbox_path):
        try:
            shutil.rmtree(sandbox_path)
            os.makedirs(sandbox_path)
        except Exception as e:
            st.error(f"Failed to clear sandbox: {e}")

    # 3. Clear session
    st.session_state.logs = []
    st.session_state.flag = None
    st.session_state.running = False
    st.session_state.current_graph_state = None
    st.session_state.waiting_for_approval = False
    st.session_state.flag_revealed = False
    st.session_state.flag_access_attempts = 0
    st.session_state.show_flag_input = False
    st.session_state.flag_status = "locked"

# --- Sidebar Inputs ---
with st.sidebar:
    st.image("PwnGPT.png", width=300)
    st.title("PwnGPT Config")

    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🧑‍🎓 Student (Solver)"

    st.radio("Mode de l'application", ["🧑‍🎓 Student (Solver)", "🧑‍🏫 Professor (Generator)"], key="app_mode")

    # Theme Toggle Button
    theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
    theme_label = "Light Mode" if st.session_state.theme == "dark" else "Dark Mode"

    if st.button(f"{theme_icon} {theme_label}", key="theme_toggle"):
        toggle_theme()
        st.rerun()

    st.divider()

    if st.session_state.app_mode == "🧑‍🎓 Student (Solver)":
        challenge_name = st.text_input("Challenge Name", "Web Intrusion 101")
        category = st.selectbox("Category", ["WEB", "PWN", "REV", "DFIR", "OSINT", "MISC", "CRYPTO"])
        flag_format = st.text_input("Flag Format (regex or prefix)", "CTF{")
        uploaded_files = st.file_uploader("Upload Challenge Files/Screenshots", accept_multiple_files=True)

        # Boutons côte à côte : INITIALIZE AGENT (gauche) + 🔒 FLAG (droite)
        if "show_flag_input" not in st.session_state:
            st.session_state.show_flag_input = False
        if "flag_status" not in st.session_state:
            st.session_state.flag_status = "locked"

        col_start, col_lock = st.columns([2, 1])
        with col_start:
            start_btn = st.button("🚀 INITIALIZE AGENT", type="primary", use_container_width=True)
        with col_lock:
            lock_icon = "🔓" if st.session_state.flag_status == "unlocked" else "🔒"
            status_text = st.session_state.flag_status.upper()
            if st.button(f"{lock_icon} {status_text}", key="open_flag_modal", use_container_width=True):
                st.session_state.show_flag_input = not st.session_state.show_flag_input
                st.rerun()

        # Display Flag Status and Unlocked Content
        st.markdown("---")
        if st.session_state.flag_status == "unlocked":
            # Flag is unlocked - show the status and flag
            st.success("🔓 **FLAG UNLOCKED**")
            if st.session_state.get("flag"):
                st.code(st.session_state.flag, language="text")
            else:
                st.info("Aucun flag trouvé pour l'instant.")
        elif st.session_state.show_flag_input:
            # Show password input form
            MAX_ATTEMPTS = 3
            attempts = st.session_state.get("flag_access_attempts", 0)
            remaining = MAX_ATTEMPTS - attempts

            if attempts >= MAX_ATTEMPTS:
                st.error("🔒 Accès bloqué. Trop de tentatives.")
            else:
                st.caption(f"🔐 Code requis — {remaining} essai(s) restant(s)")
                entered_code = st.text_input(
                    "Code d'accès",
                    type="password",
                    key="sidebar_flag_code_input",
                    label_visibility="collapsed",
                    placeholder="Entrez le code..."
                )
                if st.button("✅ Vérifier le code", key="sidebar_verify_btn", type="primary"):
                    if entered_code == FLAG_ACCESS_CODE:
                        st.session_state.flag_status = "unlocked"
                        st.session_state.flag_revealed = True
                        st.session_state.show_flag_input = False
                        st.rerun()
                    else:
                        st.session_state.flag_access_attempts = attempts + 1
                        left = MAX_ATTEMPTS - st.session_state.flag_access_attempts
                        if left > 0:
                            st.error(f"❌ Incorrect. {left} essai(s) restant(s).")
                        else:
                            st.error("🔒 Accès bloqué.")
                        st.rerun()

        st.divider()
        if st.button("🗑️ RESET ENVIRONMENT", type="secondary"):
            reset_env()
            st.rerun()

    else:
        st.info("Le mode Professeur est actif. Utilisez la fenêtre principale.")
        start_btn = False

# --- Main Layout ---
if st.session_state.app_mode == "🧑‍🏫 Professor (Generator)":
    st.markdown("# 🧠 CTF Challenge Generator")
    teacher_prompt = st.text_area("Que voulez-vous générer ?", height=150,
                                  placeholder="Ex: crée un challenge web niveau moyen sur SQL injection...")

    if st.button("🚀 GENERATE CHALLENGE", type="primary"):
        with st.spinner("Génération du challenge en cours (peut prendre une minute)..."):
            from generator_agent import CTFGeneratorAgent
            generator = CTFGeneratorAgent(workspace_dir=SANDBOX_PATH)
            result = generator.generate_challenge(teacher_prompt)

            if "error" in result:
                st.error(f"Erreur: {result['error']}")
            else:
                st.success("Challenge généré avec succès !")
                st.markdown(f"### {result.get('challenge_name', 'Challenge')}")
                st.markdown(f"**Catégorie:** {result.get('category', 'N/A')}")
                st.markdown("#### Description étudiante")
                st.info(result.get('description', ''))
                st.markdown("#### Flag")
                st.code(result.get('flag', ''), language="text")

                saved_files = result.get('saved_files', [])
                if saved_files:
                    st.markdown("#### Fichiers générés")
                    for fname in saved_files:
                        file_path = os.path.join(SANDBOX_PATH, fname)
                        with open(file_path, "rb") as f:
                            st.download_button(label=f"⬇️ Télécharger {fname}", data=f, file_name=fname, key=fname)
    st.stop()

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("# 🛡️ PwnGPT: Agentic CTF Solver")
    description = st.text_area("Challenge Description / Briefing", height=150,
                               placeholder="Paste the challenge text or clue here...")
    hints = st.text_area("Hints (Optional)", height=100, placeholder="Enter any provided hints here...")

# --- Session State Management ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "running" not in st.session_state:
    st.session_state.running = False
if "flag" not in st.session_state:
    st.session_state.flag = None
if "current_graph_state" not in st.session_state:
    st.session_state.current_graph_state = None
if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False
if "flag_access_attempts" not in st.session_state:
    st.session_state.flag_access_attempts = 0
if "flag_revealed" not in st.session_state:
    st.session_state.flag_revealed = False
if "show_flag_input" not in st.session_state:
    st.session_state.show_flag_input = False
if "flag_status" not in st.session_state:
    st.session_state.flag_status = "locked"

# --- Logic Flow ---
if start_btn:
    st.session_state.running = True
    st.session_state.logs = []
    st.session_state.flag = None
    st.session_state.waiting_for_approval = False
    st.session_state.current_graph_state = None
    st.session_state.flag_revealed = False
    st.session_state.flag_access_attempts = 0
    st.session_state.show_flag_input = False
    st.session_state.flag_status = "locked"

    with st.spinner("Initializing Toolkit (Pulling Docker Image if needed, this may take a minute)..."):
        file_paths = []
        upload_dir_path = SANDBOX_PATH
        if not os.path.exists(upload_dir_path):
            os.makedirs(upload_dir_path)

        if uploaded_files:
            file_paths, _ = save_uploaded_files(uploaded_files, target_dir=upload_dir_path)

        try:
            brain = PwnGPTBrain(upload_dir=upload_dir_path)
            initial_state = {
                "challenge_name": challenge_name,
                "challenge_description": description,
                "hints": hints,
                "files": file_paths,
                "messages": [],
                "current_step": "Start",
                "tool_output": "",
                "flag_found": None,
                "current_action": {},
                "approval_status": "NONE",
                "flag_format": flag_format
            }
            st.session_state.current_graph_state = initial_state
        except RuntimeError as e:
            st.error(f"Initialization Failed: {str(e)}")
            st.session_state.running = False

def run_agent_step():
    """Runs the agent loop until it finishes or hits an approval request."""
    if not st.session_state.current_graph_state:
        return

    upload_dir_path = SANDBOX_PATH
    brain = PwnGPTBrain(upload_dir=upload_dir_path)
    app = brain.graph

    tab_console, tab_artifacts = st.tabs(["🧠 Thinking Console", "📂 Artifact Gallery"])

    with tab_console:
        console_placeholder = st.empty()

    with tab_artifacts:
        artifacts_placeholder = st.empty()

    def format_log(line: str) -> str:
        line_esc = line.replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith("Thought:"):
            return f'<div class="log-thought">{line_esc}</div>'
        elif line.startswith("Ran command:") or line.startswith("Scraped URL:"):
            return f'<div class="log-command">> {line_esc}</div>'
        elif line.startswith("Observing challenge:"):
            return f'<div class="log-obs">{line_esc}</div>'
        elif "Expert Panel" in line or "Expert Consensus" in line:
            return f'<div class="log-expert">{line_esc}</div>'
        elif "SUCCESS:" in line or "✅" in line:
            return f'<div class="log-success">{line_esc}</div>'
        elif "⛔" in line or "⚠️" in line or "Error" in line:
            return f'<div class="log-error">{line_esc}</div>'
        elif "✋" in line:
            return f'<div class="log-warning">{line_esc}</div>'
        else:
            return f'<div>{line_esc}</div>'

    def render_logs():
        formatted_lines = [format_log(log) for log in st.session_state.logs]
        console_html = "".join(formatted_lines)
        console_placeholder.markdown(f'<div class="console-box">{console_html}</div>', unsafe_allow_html=True)

    def render_artifacts():
        sandbox_path = SANDBOX_PATH
        if os.path.exists(sandbox_path):
            files = []
            for root, dirs, filenames in os.walk(sandbox_path):
                for f in filenames:
                    files.append(os.path.relpath(os.path.join(root, f), sandbox_path))
            if files:
                file_list = "\n".join([f"- {f}" for f in files])
                artifacts_placeholder.markdown(f"**Current Files:**\n{file_list}")
            else:
                artifacts_placeholder.info("No artifacts yet.")

    render_logs()
    render_artifacts()

    try:
        for event in app.stream(st.session_state.current_graph_state):
            for node, state in event.items():
                st.session_state.current_graph_state = state

                if state.get('messages'):
                    st.session_state.logs = state['messages']

                if state.get('flag_found'):
                    st.session_state.flag = state['flag_found']
                    st.session_state.running = False
                    render_logs()
                    render_artifacts()
                    st.rerun()
                    return

                if state.get('approval_status') == "REQUESTED":
                    st.session_state.waiting_for_approval = True
                    render_logs()
                    render_artifacts()
                    st.rerun()
                    return

                render_logs()
                render_artifacts()

                current_action = state.get('current_action', {}).get('action')
                if current_action == "finish":
                    st.session_state.running = False
                    return

                if "Reasoning Error" in str(state.get('messages', [])[-1]):
                    st.error("Agent encountered a critical error. Stopping.")
                    st.session_state.running = False
                    return

                time.sleep(0.1)

    except Exception as e:
        st.error(f"Agent Crashed: {str(e)}")
        st.session_state.running = False

# Auto-run if running and not waiting
if st.session_state.running and not st.session_state.waiting_for_approval:
    run_agent_step()

# --- Display Console & Artifacts ---
if not st.session_state.running or st.session_state.waiting_for_approval:

    tab_console, tab_artifacts = st.tabs(["🧠 Thinking Console", "📂 Artifact Gallery"])

    with tab_console:
        if st.session_state.logs:
            formatted_lines = []
            for line in st.session_state.logs:
                line_esc = line.replace("<", "&lt;").replace(">", "&gt;")
                if line.startswith("Thought:"):
                    formatted_lines.append(f'<div class="log-thought">{line_esc}</div>')
                elif line.startswith("Ran command:") or line.startswith("Scraped URL:"):
                    formatted_lines.append(f'<div class="log-command">> {line_esc}</div>')
                elif line.startswith("Observing challenge:"):
                    formatted_lines.append(f'<div class="log-obs">{line_esc}</div>')
                elif "SUCCESS:" in line or "✅" in line:
                    formatted_lines.append(f'<div class="log-success">{line_esc}</div>')
                elif "⛔" in line or "⚠️" in line or "Error" in line:
                    formatted_lines.append(f'<div class="log-error">{line_esc}</div>')
                elif "✋" in line:
                    formatted_lines.append(f'<div class="log-warning">{line_esc}</div>')
                else:
                    formatted_lines.append(f'<div>{line_esc}</div>')
            console_html = "".join(formatted_lines)
            st.markdown(f'<div class="console-box">{console_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Agent not started yet.")

    with tab_artifacts:
        st.markdown("### 📦 Sandbox Artifacts")
        sandbox_path = SANDBOX_PATH
        if os.path.exists(sandbox_path):
            files = []
            for root, dirs, filenames in os.walk(sandbox_path):
                for f in filenames:
                    files.append(os.path.relpath(os.path.join(root, f), sandbox_path))

            if files:
                for f in files:
                    col_file, col_dl = st.columns([4, 1])
                    with col_file:
                        st.code(f, language="text")
                    with col_dl:
                        file_full_path = os.path.join(sandbox_path, f)
                        try:
                            with open(file_full_path, "rb") as dl_file:
                                st.download_button(
                                    label="⬇️",
                                    data=dl_file,
                                    file_name=os.path.basename(f),
                                    key=f"dl_{f}"
                                )
                        except Exception as e:
                            st.error("Error reading file")
            else:
                st.info("No artifacts found in workspace.")
        else:
            st.warning("Sandbox workspace not initialized.")

# Approval UI Overlay
if st.session_state.waiting_for_approval:
    action = st.session_state.current_graph_state.get('current_action', {})
    st.warning(f"⚠️ **HIGH RISK ACTION DETECTED**")
    st.code(f"Action: {action.get('action')}\nCommand: {action.get('argument')}", language="bash")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ APPROVE ACTION", type="primary"):
            st.session_state.current_graph_state['approval_status'] = "GRANTED"
            st.session_state.waiting_for_approval = False
            st.rerun()

    with col_b:
        if st.button("🛑 DENY ACTION"):
            st.session_state.current_graph_state['approval_status'] = "DENIED"
            st.session_state.waiting_for_approval = False
            st.rerun()

# --- Success & Feedback Loop ---
if st.session_state.flag:
    st.markdown(f"""
    <div class="success-box">
        🚩 POTENTIAL FLAG DETECTED: {st.session_state.flag}
    </div>
    """, unsafe_allow_html=True)

    st.info("Please verify if this is the correct flag.")

    col_confirm, col_reject = st.columns(2)

    with col_confirm:
        if st.button("✅ Confirm & Generate Write-up", type="primary"):
            with st.spinner("Generating Write-up..."):
                upload_dir_path = SANDBOX_PATH
                brain = PwnGPTBrain(upload_dir=upload_dir_path)
                writeup = brain.generate_writeup(st.session_state.current_graph_state)
                st.markdown("## 📝 CTF Write-up")
                st.markdown(writeup)
                st.balloons()

    with col_reject:
        if st.button("❌ Incorrect - Keep Searching"):
            st.session_state.current_graph_state['messages'].append(
                f"User Feedback: The flag '{st.session_state.flag}' is INCORRECT. Disregard it and continue searching."
            )
            st.session_state.current_graph_state['flag_found'] = None
            st.session_state.flag = None
            st.session_state.flag_revealed = False
            st.session_state.flag_access_attempts = 0
            st.session_state.running = True
            st.rerun()