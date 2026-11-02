import sqlite3

DATABASE_PATH = "app.db"


def get_connection(path: str = DATABASE_PATH) -> sqlite3.Connection:
    """Open a SQLite connection that returns rows as dict-like objects."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create all tables if they do not exist yet."""
    from .models.user import CREATE_USERS_TABLE
    from .models.post import CREATE_POSTS_TABLE, CREATE_POSTS_CATEGORY_INDEX

    conn.execute(CREATE_USERS_TABLE)
    conn.execute(CREATE_POSTS_TABLE)
    conn.execute(CREATE_POSTS_CATEGORY_INDEX)
    conn.commit()


def init_db() -> None:
    conn = get_connection()
    try:
        create_tables(conn)
    finally:
        conn.close()


def get_db():
    """FastAPI dependency: one connection per request."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()