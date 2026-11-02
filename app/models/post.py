


# Table definition for posts. Each post belongs to exactly one user.

CREATE_POSTS_TABLE = """
CREATE TABLE IF NOT EXISTS posts (
    post_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    post_title    TEXT NOT NULL,
    post_body     TEXT NOT NULL,
    post_category TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    user_id       INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
"""

CREATE_POSTS_CATEGORY_INDEX = """
CREATE INDEX IF NOT EXISTS ix_posts_post_category ON posts (post_category)
"""