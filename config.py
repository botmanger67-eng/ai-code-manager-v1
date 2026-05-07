import os

class Settings:
    def __init__(self):
        # DeepSeek API
        self.DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
        # ▼▼▼ YAHAN MODEL BADLO ▼▼▼
        self.DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
        self.DEEPSEEK_TIMEOUT = 120

        # GitHub
        self.GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

        # Database (SQLite local file)
        self.DATABASE_URL = "sqlite+aiosqlite:///studio.db"

        # Server
        self.PORT = int(os.environ.get("PORT", "5000"))
        self.HOST = "0.0.0.0"

settings = Settings()

# Status check (optional)
if settings.DEEPSEEK_API_KEY and "your_key" not in settings.DEEPSEEK_API_KEY:
    print(f"🔑 DeepSeek API key loaded (model: {settings.DEEPSEEK_MODEL})")
else:
    print("⚠️  DeepSeek API key not found")

if settings.GITHUB_TOKEN and "your_token" not in settings.GITHUB_TOKEN:
    print("🐙 GitHub token loaded")
else:
    print("⚠️  GitHub token not found")

print(f"💾 Database: SQLite (studio.db)")
print(f"🌐 App will run on port {settings.PORT}")