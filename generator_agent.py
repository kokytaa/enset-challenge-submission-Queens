import os
import json
import streamlit as st
import time
import random

try:
    import google.generativeai as genai
    API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
except:
    genai = None
    API_KEY = None


SYSTEM_PROMPT = """You are a CTF generator."""

class CTFGeneratorAgent:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)

        # SAFE MODEL INIT
        self.model = None
        if genai and API_KEY:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            except:
                self.model = None

    # -------------------------
    # 🔥 FALLBACK LOCAL DEMO
    # -------------------------
    def _fallback_challenge(self, prompt):
        return {
        "challenge_name": "Web Login Bypass Demo",
        "category": "WEB",
        "description": f"""
## Challenge

Une application de login PHP filtre mal les entrées utilisateur.

Objectif : contourner l'authentification et récupérer le flag.

Hint: pense aux conditions SQL / bypass logique.

Prompt original: {prompt}
        """,
        "flag": "CTF{sql_bypass_success}",

        "files": [
            {
                "filename": "index.php",
                "content": """<?php
// Simple vulnerable login demo (CTF)

$flag = "CTF{sql_bypass_success}";

$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

echo "<h2>Login Page</h2>";

if ($username == "admin" && $password == "admin123") {
    echo "Welcome admin!<br>";
    echo "FLAG: " . $flag;
} else {
    echo "<form method='POST'>
        Username: <input name='username'><br>
        Password: <input name='password' type='password'><br>
        <button type='submit'>Login</button>
    </form>";
}
?>
"""
            }
        ]
    }

    # -------------------------
    # SAFE GENERATION
    # -------------------------
    def _safe_generate(self, prompt):
        if not self.model:
            return None

        try:
            return self.model.generate_content(prompt)
        except Exception:
            return None

    # -------------------------
    # MAIN FUNCTION
    # -------------------------
    def generate_challenge(self, teacher_prompt: str):

        full_prompt = f"""
        {SYSTEM_PROMPT}

        Teacher Prompt:
        {teacher_prompt}

        Return ONLY JSON.
        """

        response = self._safe_generate(full_prompt)

        # -------------------------
        # CASE 1: GEMINI OK
        # -------------------------
        if response and hasattr(response, "text"):
            try:
                text = response.text.replace("```json", "").replace("```", "").strip()
                challenge_data = json.loads(text)
            except:
                challenge_data = self._fallback_challenge(teacher_prompt)

        # -------------------------
        # CASE 2: GEMINI FAIL → DEMO
        # -------------------------
        else:
            challenge_data = self._fallback_challenge(teacher_prompt)

        # -------------------------
        # SAVE FILES
        # -------------------------
        saved_files = []
        for f in challenge_data.get("files", []):
            filename = os.path.basename(f["filename"])
            path = os.path.join(self.workspace_dir, filename)

            with open(path, "w", encoding="utf-8") as out:
                out.write(f["content"])

            saved_files.append(filename)

        challenge_data["saved_files"] = saved_files

        return challenge_data