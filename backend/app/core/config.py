"""Application configuration from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from backend/.env using absolute path
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_FILE)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-xxx")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
