import os
from pathlib import Path
from dotenv import load_dotenv

_env_file = Path(__file__).parent.parent / ".env.bot.secret"
if _env_file.exists():
    load_dotenv(_env_file)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LMS_API_BASE_URL = os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
LMS_API_KEY = os.getenv("LMS_API_KEY", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "coder-model")
