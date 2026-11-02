import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.database import create_tables, get_db
from app.main import app


@pytest.fixture()
def client():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)

    def override_get_db():
        yield conn

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    conn.close()


def make_user(client, username="alice", email=None):
    res = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": "secret",
            "name": username.title(),
            "email": email or f"{username}@example.com",
        },
    )
    assert res.status_code == 201
    return res.json()


def auth(user):
    """Header that proves who the caller is."""
    return {"X-Access-Id": user["access_id"]}


def make_post(client, user, title="Hello", category="general", body="Body text"):
    res = client.post(
        "/posts",
        json={"post_title": title, "post_body": body, "post_category": category},
        headers=auth(user),
    )
    assert res.status_code == 201
    return res.json()
