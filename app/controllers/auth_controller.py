import secrets
import sqlite3
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin

USER_COLUMNS = "user_id, username, name, email, phone, address, access_id"

# Shows an "Authorize" button in /docs where you paste your access_id.
api_key_header = APIKeyHeader(name="X-Access-Id", auto_error=False)


def register(db: sqlite3.Connection, data: UserCreate) -> dict:
    access_id = secrets.token_hex(16)  # 32 random hex chars, cannot be guessed
    try:
        cur = db.execute(
            "INSERT INTO users (username, password, name, email, phone, address, access_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data.username, data.password, data.name, data.email, data.phone, data.address, access_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken",
        )

    row = db.execute(
        f"SELECT {USER_COLUMNS} FROM users WHERE user_id = ?", (cur.lastrowid,)
    ).fetchone()
    return dict(row)


def login(db: sqlite3.Connection, data: UserLogin) -> dict:
    user = db.execute(
        f"SELECT {USER_COLUMNS} FROM users WHERE username = ? AND password = ?",
        (data.username, data.password),
    ).fetchone()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )
    return dict(user)


def get_current_user(
    access_id: Optional[str] = Depends(api_key_header),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Dependency: find the user who owns the X-Access-Id header, or return 401."""
    if not access_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Access-Id header")
    user = db.execute(
        "SELECT user_id, username FROM users WHERE access_id = ?", (access_id,)
    ).fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access id")
    return dict(user)
