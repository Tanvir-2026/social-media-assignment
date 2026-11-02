VALID = {
    "username": "alice",
    "password": "secret",
    "name": "Alice",
    "email": "alice@example.com",
}


def test_register_valid(client):
    res = client.post("/auth/register", json=VALID)
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "alice"
    assert "user_id" in body
    assert "password" not in body


def test_register_duplicate_username(client):
    client.post("/auth/register", json=VALID)
    res = client.post("/auth/register", json={**VALID, "email": "other@example.com"})
    assert res.status_code == 409


def test_register_missing_field(client):
    data = {k: v for k, v in VALID.items() if k != "email"}
    res = client.post("/auth/register", json=data)
    assert res.status_code == 422


def test_login_correct(client):
    user = client.post("/auth/register", json=VALID).json()
    res = client.post("/auth/login", json={"username": "alice", "password": "secret"})
    assert res.status_code == 200
    assert res.json()["user_id"] == user["user_id"]


def test_login_wrong_password(client):
    client.post("/auth/register", json=VALID)
    res = client.post("/auth/login", json={"username": "alice", "password": "nope"})
    assert res.status_code == 401