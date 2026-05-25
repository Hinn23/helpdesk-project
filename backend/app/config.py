import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'helpdesk.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

APP_NAME = "Helpdesk Lite"
APP_VERSION = "0.3.0"
APP_TAGLINE = "Где баги становятся фичами"
ADMIN_EMAIL = "boss@helpdesk.local"

ALLOWED_EMAIL_DOMAINS = os.getenv("ALLOWED_EMAIL_DOMAINS", "gmail.com,mail.ru,yandex.ru")
if ALLOWED_EMAIL_DOMAINS:
    ALLOWED_EMAIL_DOMAINS = {d.strip() for d in ALLOWED_EMAIL_DOMAINS.split(",")}

DISABLE_RATE_LIMIT = os.getenv("DISABLE_RATE_LIMIT", "true").lower() in ("true", "1", "yes")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
