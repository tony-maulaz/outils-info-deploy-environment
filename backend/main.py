import os
import sqlite3
import time

import jwt
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

APP_ENV = os.getenv("APP_ENV", "dev")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "")
SECRET_PATH = os.getenv("API_TOKEN_SECRET_PATH", "/run/secrets/api_token_secret")
DB_PASSWORD_SECRET_PATH = os.getenv("DB_PASSWORD_SECRET_PATH", "/run/secrets/db_password")

app = FastAPI(title="Env Demo", version="1.0")

# CORS: allow a comma-separated list of origins
origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _db_path_from_url(url: str) -> str:
    if url.startswith("sqlite:///"):
        return url.replace("sqlite://", "", 1)
    # Fallback: treat the value as a direct path
    return url


def _get_secret() -> str:
    try:
        with open(SECRET_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def _get_db_password() -> str:
    try:
        with open(DB_PASSWORD_SECRET_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def _get_conn() -> sqlite3.Connection:
    path = _db_path_from_url(DATABASE_URL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
    )
    return conn


@app.get("/api/health")
def health():
    # Simple DB check
    conn = _get_conn()
    conn.execute("SELECT 1")
    conn.close()
    return {"status": "ok", "env": APP_ENV, "db": "ok"}


@app.get("/api/items")
def list_items():
    conn = _get_conn()
    rows = conn.execute("SELECT id, name FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"]} for r in rows]


def _issue_jwt() -> str:
    secret = _get_secret()
    if not secret:
        raise HTTPException(status_code=500, detail="API_TOKEN_SECRET missing")
    now = int(time.time())
    payload = {
        "sub": "demo",
        "env": APP_ENV,
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _verify_jwt(authorization: str) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")

    secret = _get_secret()
    if not secret:
        raise HTTPException(status_code=500, detail="API_TOKEN_SECRET missing")

    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/api/items")
def add_item(payload: dict, authorization: str = Header(default="")):
    # Basic JWT check for writes
    _verify_jwt(authorization)

    name = (payload or {}).get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name required")

    conn = _get_conn()
    cur = conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()

    return {"id": item_id, "name": name}


@app.get("/api/config")
def config():
    # Not required but useful for demo
    db_password = _get_db_password()
    return {
        "env": APP_ENV,
        "log_level": LOG_LEVEL,
        "db_password_loaded": bool(db_password),
    }


@app.get("/api/token")
def get_token():
    # Demo endpoint: return a JWT so the frontend can store it
    return {"token": _issue_jwt()}
