CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT NOT NULL UNIQUE,
    password  TEXT NOT NULL,          -- plain text for now (learning project only)
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    phone     TEXT,
    address   TEXT,
    access_id TEXT NOT NULL UNIQUE    -- secret random id, sent in X-Access-Id header
)
"""
