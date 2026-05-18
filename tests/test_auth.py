def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_success(client, admin_user):
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client, admin_user):
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "mauvais"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/auth/login", json={"email": "inconnu@test.com", "password": "test"})
    assert res.status_code == 401


def test_login_inactive_user(client, inactive_user):
    res = client.post("/auth/login", json={"email": "inactive@test.com", "password": "pass123"})
    assert res.status_code == 403


def test_me_authenticated(client, admin_user, admin_token):
    res = client.get("/auth/me", headers=auth_header(admin_token))
    assert res.status_code == 200
    assert res.json()["email"] == "admin@test.com"
    assert res.json()["role"] == "admin"


def test_me_unauthenticated(client):
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_invalid_token(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer token.invalide"})
    assert res.status_code == 401
