# 🚀 AI Code Manager Studio Pro

**Chat with AI, generate full project code in real time, and push to GitHub — all in one place.**

A FastAPI application that uses **DeepSeek AI (V4 Flash)** to plan your project, generate each file live (with progress streaming), and push the generated code directly to a GitHub repository. A sidebar shows all your past projects.

---

## ✨ Features

- 🤖 **AI-Powered Planning** – Describe your project, AI creates a detailed file plan.
- ⚡ **Live Code Generation** – Watch each file being generated in real time (SSE streaming).
- 📂 **Sidebar History** – All past projects appear in the sidebar; click to review.
- ➕ **New Project Button** – Start a fresh project with one click.
- 🐙 **GitHub Push** – Enter a repo name and push all generated files instantly.
- 🔐 **Secure Keys** – API keys are stored in the `.env` file and never exposed to the browser.
- 💻 **Modern Web UI** – Dark theme, smooth animations, beginner‑friendly.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI + Uvicorn (Python 3.8+)
- **AI:** DeepSeek API (default: `deepseek-v4-flash`)
- **Database:** SQLite (file‑based, zero configuration)
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Integration:** GitHub API

---

## 📋 Prerequisites

- Python 3.8 or newer
- [DeepSeek API Key](https://platform.deepseek.com/) (free credits work)
- [GitHub Personal Access Token](https://github.com/settings/tokens) with `repo` scope (needed for push)

---

## 🚀 Quick Start

### 1. Clone or download the project
```bash
git clone <your-repo-url>
cd ai-code-manager

2. (Optional) Create a virtual environment
bash
python -m venv venv
# Windows activation:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Set your API keys
Create a .env file in the project folder and add:

text
DEEPSEEK_API_KEY=sk-YourDeepseekKeyHere
GITHUB_TOKEN=ghp_YourGithubTokenHere
⚠️ Never commit .env to GitHub (already in .gitignore).

5. Run the app
bash
python main.py
Open your browser and go to: http://localhost:5000

💡 How to Use
New Project – Click the + New Project button in the sidebar.

Describe Your Project – Write in detail what you want to build (e.g., "REST API for a todo app with authentication").

Analyze & Create Plan – AI will show you the file structure and plan.

Review Plan → Generate Code – Watch each file being generated live.

Push to GitHub – Enter a repository name and push all files.

Past projects are always accessible from the sidebar.

🧪 Changing the AI Model
The default model is deepseek-v4-flash.
To use a different model, add this line to your .env file:

text
DEEPSEEK_MODEL=deepseek-chat
(Replace with any valid DeepSeek model ID)

🌐 API Endpoints (for developers)
Method	Endpoint	Description
GET	/	Main UI (HTML page)
GET	/api/sessions	List all past sessions
GET	/api/session/{id}	Session details with plan and files
POST	/api/analyze	Analyze project description
POST	/api/generate-code	Generate code (streaming SSE)
POST	/api/push-to-github	Push generated code to GitHub
🐞 Troubleshooting
Problem	Solution
"DeepSeek API key not configured"	Make sure .env contains a valid DEEPSEEK_API_KEY.
"GitHub push failed"	Check that GITHUB_TOKEN is correct and has repo permission.
App not accessible on port	Verify firewall settings or change PORT in config.py.
Progress stream not showing	Clear browser cache or inspect the browser console.
📁 Project Structure
text
ai-code-manager/
├── main.py                # FastAPI application
├── config.py              # Settings (API keys, model, port)
├── database.py            # Database models (SQLite)
├── requirements.txt
├── .env                   # Your secret keys (keep private!)
├── .gitignore
├── README.md
├── handlers/
│   ├── __init__.py
│   ├── chat.py            # DeepSeek API interaction
│   └── github.py          # GitHub push logic
├── static/
│   ├── style.css          # Dark theme styles
│   └── app.js             # Frontend logic (SSE, sidebar)
└── templates/
    └── index.html         # Main page template
📝 License
MIT – Free to use, modify, and share.

Made for beginners – AI‑powered coding, simplified.