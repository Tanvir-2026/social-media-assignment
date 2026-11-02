"""Fill app.db with fake users and posts for manual testing.

Usage (from the project root):
    uv run python seed.py            # add data only if the database is empty
    uv run python seed.py --reset    # wipe all users and posts first
"""
import random
import secrets
import sys
from datetime import datetime, timedelta, timezone

from app.database import create_tables, get_connection

random.seed(42)  # same fake data every run

PASSWORD = "password123"

USERS = [
    ("alice", "Alice Johnson", "alice@example.com", "+8801700000001", "Dhaka"),
    ("bob", "Bob Smith", "bob@example.com", "+8801700000002", "Chittagong"),
    ("charlie", "Charlie Brown", "charlie@example.com", None, None),
    ("diana", "Diana Prince", "diana@example.com", "+8801700000004", "Sylhet"),
    ("evan", "Evan Wright", "evan@example.com", None, "Khulna"),
]

CATEGORIES = ["tech", "sports", "music", "travel", "food", "news"]

TITLES = {
    "tech": ["Why I switched to FastAPI", "SQLite is underrated", "Learning layered architecture", "Testing with pytest fixtures"],
    "sports": ["Weekend cricket recap", "Best football matches this season", "Starting a running habit"],
    "music": ["Albums on repeat this week", "Learning guitar at 30", "Lo-fi playlists for coding"],
    "travel": ["A weekend in Cox's Bazar", "Packing light for a week", "Hidden spots in Sylhet"],
    "food": ["Perfecting homemade biryani", "Street food tour", "Easy dinners under 20 minutes"],
    "news": ["Local tech meetup announced", "New library opens downtown", "City adds more bike lanes"],
}

BODY = (
    "This is a sample post created by seed.py so the API has something to list, "
    "filter and paginate. Edit or delete it freely."
)


def main() -> None:
    reset = "--reset" in sys.argv
    conn = get_connection()
    try:
        if reset:
            conn.execute("DROP TABLE IF EXISTS posts")
            conn.execute("DROP TABLE IF EXISTS users")
            conn.commit()
        create_tables(conn)

        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            print("Database already has users. Run with --reset to wipe and reseed.")
            return

        # Users
        creds = []
        user_ids = []
        for username, name, email, phone, address in USERS:
            access_id = secrets.token_hex(16)
            cur = conn.execute(
                "INSERT INTO users (username, password, name, email, phone, address, access_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, PASSWORD, name, email, phone, address, access_id),
            )
            user_ids.append(cur.lastrowid)
            creds.append((username, access_id))

        # Posts: spread over the last 30 days, oldest inserted first
        now = datetime.now(timezone.utc)
        post_count = 40
        for i in range(post_count):
            category = random.choice(CATEGORIES)
            title = f"{random.choice(TITLES[category])} #{i + 1}"
            created = now - timedelta(days=30) + timedelta(hours=18 * i + random.randint(0, 5))
            updated = created
            if random.random() < 0.25:  # some posts were edited later
                updated = created + timedelta(hours=random.randint(1, 48))
            conn.execute(
                "INSERT INTO posts (post_title, post_body, post_category, created_at, updated_at, user_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (title, BODY, category, created.isoformat(), updated.isoformat(), random.choice(user_ids)),
            )
            conn.execute(
            "UPDATE users SET post_count = "
            "(SELECT COUNT(*) FROM posts WHERE posts.user_id = users.user_id)"
        )
        conn.commit()

        print(f"Created {len(USERS)} users and {post_count} posts.\n")
        print(f"All passwords: {PASSWORD}\n")
        print(f"{'username':<10} access_id (send as X-Access-Id header)")
        for username, access_id in creds:
            print(f"{username:<10} {access_id}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()