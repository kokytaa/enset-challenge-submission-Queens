# 🛡️ PwnGPT — Agentic AI for CTF Solving & Cybersecurity Training

**By**
Khallouf Kawtar & Fenjiro Wiam

---

## 🚀 Overview

**PwnGPT** is an advanced **Agentic AI system** designed to autonomously solve Capture The Flag (CTF) challenges while providing **step-by-step explanations** for learning.

It combines:

* 🤖 Large Language Models (Gemini)
* 🔁 Agentic reasoning (ReAct + LangGraph)
* 🧠 Multi-agent collaboration
* 🔐 Secure execution (Docker sandbox)

👉 Not just a solver — **an AI tutor for cybersecurity**
Aligned with: **Agentic AI for Education and Industry**

---

## 🧠 Key Features

### 🤖 Agentic AI (Core Innovation)

* ReAct Loop: **Observe → Expert Consensus → Reason → Act → Verify**
* Multi-agent system:

  * 🕵️ Forensics Investigator (files, steganography)
  * 🌐 Web Exploitation Specialist (web, injections)
  * ⚙️ Reverse Engineer (binaries, logic)
* Hierarchical decision-making (LLM = supervisor)

---

### ⚡ Autonomous CTF Solving

* Strategy generation using LLM
* Tool execution in sandbox
* Iterative reasoning until flag is found

---

### 📚 Learning Mode (Educational Impact)

* Step-by-step explanations
* Transparent reasoning
* Cybersecurity concepts:

  * SQL Injection (SQLi)
  * Buffer Overflow
  * Reverse Engineering
  * Forensics & Web Exploitation

👉 Turns CTF solving into a **learning experience**

---

### 🔎 RAG (Retrieval-Augmented Generation)

* Local knowledge base search
* Context-aware reasoning
* Reduced hallucinations

---

### 🔐 Security & Guardrails

* Command filtering (**Guardian system**)
* Docker sandbox (Kali Linux)
* Human-in-the-loop for risky actions
* Restricted access to sensitive paths

---

### 🌐 Interactive UI

* Built with **Streamlit**
* Real-time logs (reasoning + actions)
* User approval system
* Mobile-ready (future)

---

## 🏗️ Architecture

```
User
↓
Web Interface (Streamlit)
↓
Agentic System (LangGraph + ReAct)
↓
LLM (Gemini)
↓
Security Tools (Docker, Web, RAG)
↓
Result + Explanation
```

---

### 🔁 Orchestration Strategy

Hybrid architecture combining:

* ✅ Sequential (LangGraph workflow)
* ✅ Parallel (multi-agent experts)
* ✅ Hierarchical (LLM supervisor)
* ✅ Iterative (ReAct loop)

---

## ⚙️ Installation

### Prerequisites

* Python 3.10+
* Docker (installed & running)

---

### Setup

```bash
git clone https://github.com/kokytaa/PwnGPT.git
cd PwnGPT
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

### Option 1 — `.env` file

```env
GEMINI_API_KEY=your_api_key_here
```

### Option 2 — Streamlit secrets

```toml
GEMINI_API_KEY = "your_api_key_here"
```

---

## ▶️ Usage

Run the app:

```bash
streamlit run app.py
```

---

## 🧪 Workflow

1. Enter challenge name & description
2. Upload files (optional)
3. Agent analyzes the problem
4. Multi-agents propose strategies
5. LLM decides next action
6. Commands executed in Docker
7. Results verified automatically
8. Flag + explanation returned

---

## 🎯 Use Cases

### 🎓 Education

* Cybersecurity training
* CTF preparation
* Learning by reasoning

### 🏭 Industry

* SOC training simulations
* Pentesting assistance
* Vulnerability analysis

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **LLM:** Google Gemini
* **Agent Framework:** LangGraph
* **Sandbox:** Docker (Kali Linux)
* **RAG:** Local Knowledge Base

---

## 🔐 Security Design

* Command validation (SAFE / HIGH_RISK / BLOCKED)
* Sensitive paths protection
* Isolated execution (Docker)
* Human validation before critical actions

---

## 📊 Project Highlights

* ✅ Full Agentic Workflow (LangGraph)
* ✅ Multi-agent parallel reasoning
* ✅ Secure sandbox execution
* ✅ Explainable AI (Learning Mode)
* ✅ Human-in-the-loop control

---

## 🔮 Future Work

* 📱 Mobile interface
* 🧠 Advanced RAG (FAISS / vector DB)
* 🎯 Prompt optimization (A/B testing)
* 🔧 Fine-tuned cybersecurity models
* 🤝 Collaborative multi-user mode

---

## ⚠️ Disclaimer

This project is for educational and ethical cybersecurity purposes only.
Do not use it for unauthorized activities.

---

## 🏆 Hackathon Context

Developed during an Agentic AI Hackathon, evolving from an MVP to a fully autonomous intelligent system capable of reasoning, planning, and executing complex tasks.