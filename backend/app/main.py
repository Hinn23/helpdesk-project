import asyncio
import logging
import os
import time
import random
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.api import users, tickets, comments, categories, auth, subscriptions, history, attachments_api, user_profiles, feed, admin_users, user_friends, messages
from app.api import auth as auth_router_mod
from app.api import events as events_router_mod
from app.models import User, Ticket, Comment, Category, Subscription, AuditLog, Attachment
from app.config import APP_NAME, APP_VERSION, APP_TAGLINE, ADMIN_EMAIL, BASE_DIR, DISABLE_RATE_LIMIT
from app.sse import events as sse_events
from app.ratelimit import RateLimitMiddleware

BANNER = rf"""

  _   _      _                   _
 | | | | ___| |_ ___ _ __   ___| |
 | |_| |/ _ \ __/ _ \ '_ \ / _ \ |
 |  _  |  __/ ||  __/ | | |  __/ |
 |_| |_|\___|\__\___|_| |_|\___|_|
  {APP_TAGLINE}

"""

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))
logger.addHandler(handler)
logging.getLogger("uvicorn").handlers.clear()
logging.getLogger("uvicorn").addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sse_events.set_loop(asyncio.get_event_loop())
    print(BANNER)
    logger.info(f"{APP_NAME} v{APP_VERSION} started")
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

if not DISABLE_RATE_LIMIT:
    app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUOTES = [
    "in prod it's a feature, in dev it's a bug",
    "backend работает — frontend отдыхает",
    "Лучший дедлайн — вчерашний",
    "DELETE FROM users WHERE role = 'guest' — шучу... или нет?",
    "Сделано с любовью в 3 часа ночи",
    "Прод — это когда dev уже забыл, что правил",
]


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)
    logger.info(f"{request.method:7s} {request.url.path:<40s} {response.status_code} [{duration}ms]")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Всё сломалось. Но мы уже чиним! (или нет)",
            "advice": "Попробуйте перезагрузить страницу или напишите админу",
            "admin_email": ADMIN_EMAIL,
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
        "tagline": APP_TAGLINE,
    }


@app.get("/api/stats")
def stats(request: Request):
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "motivation": random.choice(QUOTES),
    }


@app.get("/api/quote")
def quote():
    return {
        "quote": random.choice(QUOTES),
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(categories.router)
app.include_router(comments.router)
app.include_router(subscriptions.router)
app.include_router(subscriptions.user_router)
app.include_router(history.router)
app.include_router(attachments_api.router)
app.include_router(events_router_mod.router)
app.include_router(user_profiles.router)
app.include_router(feed.router)
app.include_router(admin_users.router)
app.include_router(user_friends.router)
app.include_router(messages.router)
