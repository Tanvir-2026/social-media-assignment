from tests.conftest import auth, make_post, make_user


def test_create_post_with_valid_access_id(client):
    user = make_user(client)
    res = client.post(
        "/posts",
        json={"post_title": "Hi", "post_body": "Body", "post_category": "news"},
        headers=auth(user),
    )
    assert res.status_code == 201
    assert res.json()["user_id"] == user["user_id"]
    assert client.get(f"/posts/{res.json()['post_id']}").status_code == 200


def test_create_post_without_access_id(client):
    res = client.post(
        "/posts",
        json={"post_title": "Hi", "post_body": "Body", "post_category": "news"},
    )
    assert res.status_code == 401


def test_create_post_with_fake_access_id(client):
    res = client.post(
        "/posts",
        json={"post_title": "Hi", "post_body": "Body", "post_category": "news"},
        headers={"X-Access-Id": "not-a-real-id"},
    )
    assert res.status_code == 401


def test_list_posts_newest_first(client):
    user = make_user(client)
    first = make_post(client, user, title="first")
    second = make_post(client, user, title="second")
    res = client.get("/posts")
    assert res.status_code == 200
    ids = [p["post_id"] for p in res.json()["items"]]
    assert ids == [second["post_id"], first["post_id"]]


def test_filter_by_category(client):
    user = make_user(client)
    make_post(client, user, category="news")
    make_post(client, user, category="sports")
    items = client.get("/posts", params={"category": "news"}).json()["items"]
    assert len(items) == 1
    assert all(p["post_category"] == "news" for p in items)


def test_pagination(client):
    user = make_user(client)
    for i in range(12):
        make_post(client, user, title=f"post {i}")
    body = client.get("/posts", params={"page": 2, "page_size": 5}).json()
    assert len(body["items"]) == 5
    assert body["total"] == 12
    assert body["total_pages"] == 3
    assert body["page"] == 2


def test_update_own_post(client):
    user = make_user(client)
    post = make_post(client, user)
    res = client.put(
        f"/posts/{post['post_id']}", json={"post_title": "Changed"}, headers=auth(user)
    )
    assert res.status_code == 200
    assert res.json()["post_title"] == "Changed"
    assert res.json()["post_body"] == post["post_body"]


def test_update_other_users_post(client):
    alice = make_user(client, "alice")
    bob = make_user(client, "bob")
    post = make_post(client, alice)
    res = client.put(
        f"/posts/{post['post_id']}", json={"post_title": "Hacked"}, headers=auth(bob)
    )
    assert res.status_code == 403


def test_update_without_access_id(client):
    user = make_user(client)
    post = make_post(client, user)
    res = client.put(f"/posts/{post['post_id']}", json={"post_title": "x"})
    assert res.status_code == 401


def test_delete_other_users_post(client):
    alice = make_user(client, "alice")
    bob = make_user(client, "bob")
    post = make_post(client, alice)
    assert client.delete(f"/posts/{post['post_id']}", headers=auth(bob)).status_code == 403


def test_delete_own_post_then_fetch(client):
    user = make_user(client)
    post = make_post(client, user)
    assert client.delete(f"/posts/{post['post_id']}", headers=auth(user)).status_code == 204
    assert client.get(f"/posts/{post['post_id']}").status_code == 404

def test_post_count_follows_create_and_delete(client):
    user = make_user(client)
    assert user["post_count"] == 0

    first = make_post(client, user)
    make_post(client, user)
    login = client.post("/auth/login", json={"username": "alice", "password": "secret"})
    assert login.json()["post_count"] == 2

    client.delete(f"/posts/{first['post_id']}", headers=auth(user))
    login = client.post("/auth/login", json={"username": "alice", "password": "secret"})
    assert login.json()["post_count"] == 1