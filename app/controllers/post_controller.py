import math
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.schemas.post import PostCreate, PostUpdate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_post_or_404(db: sqlite3.Connection, post_id: int) -> dict:
    post = db.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,)).fetchone()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return dict(post)


def create_post(db: sqlite3.Connection, data: PostCreate, user_id: int) -> dict:
    now = _now()
    cur = db.execute(
        "INSERT INTO posts (post_title, post_body, post_category, created_at, updated_at, user_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (data.post_title, data.post_body, data.post_category, now, now, user_id),
    )
    db.execute("UPDATE users SET post_count = post_count + 1 WHERE user_id = ?", (user_id,))
    db.commit()
    return _get_post_or_404(db, cur.lastrowid)


def get_post(db: sqlite3.Connection, post_id: int) -> dict:
    return _get_post_or_404(db, post_id)


def list_posts(
    db: sqlite3.Connection,
    category: Optional[str],
    user_id: Optional[int],
    search: Optional[str],
    page: int,
    page_size: int,
    sort: str,
) -> dict:
    where = []
    params = []
    if category is not None:
        where.append("post_category = ?")
        params.append(category)
    if user_id is not None:
        where.append("user_id = ?")
        params.append(user_id)
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        where.append("LOWER(post_title) LIKE ? ESCAPE '\\'")
        params.append(f"%{escaped.lower()}%")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    total = db.execute(f"SELECT COUNT(*) FROM posts {where_sql}", params).fetchone()[0]

    direction = "DESC" if sort == "newest" else "ASC"
    rows = db.execute(
        f"SELECT * FROM posts {where_sql} "
        f"ORDER BY created_at {direction}, post_id {direction} LIMIT ? OFFSET ?",
        params + [page_size, (page - 1) * page_size],
    ).fetchall()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }


def update_post(db: sqlite3.Connection, post_id: int, data: PostUpdate, user_id: int) -> dict:
    post = _get_post_or_404(db, post_id)
    if post["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the author")

    changes = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if changes:
        changes["updated_at"] = _now()
        set_sql = ", ".join(f"{col} = ?" for col in changes)  # column names come from the schema
        db.execute(
            f"UPDATE posts SET {set_sql} WHERE post_id = ?",
            list(changes.values()) + [post_id],
        )
        db.commit()
    return _get_post_or_404(db, post_id)


def delete_post(db: sqlite3.Connection, post_id: int, user_id: int) -> None:
    post = _get_post_or_404(db, post_id)
    if post["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the author")
    db.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
    db.execute("UPDATE users SET post_count = post_count - 1 WHERE user_id = ?", (user_id,))
    db.commit()
