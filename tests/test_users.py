def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_users_as_admin(client, admin_user, admin_token):
    res = client.get("/admin/users/", headers=auth_header(admin_token))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_users_as_client_forbidden(client, regular_user, user_token):
    res = client.get("/admin/users/", headers=auth_header(user_token))
    assert res.status_code == 403


def test_get_users_unauthenticated(client):
    res = client.get("/admin/users/")
    assert res.status_code == 401


def test_create_user(client, admin_user, admin_token):
    res = client.post(
        "/admin/users/",
        json={"email": "nouveau@test.com", "password": "pass123", "role": "client"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 201
    assert res.json()["email"] == "nouveau@test.com"
    assert res.json()["role"] == "client"


def test_create_duplicate_user(client, admin_user, admin_token):
    client.post(
        "/admin/users/",
        json={"email": "dup@test.com", "password": "pass123", "role": "client"},
        headers=auth_header(admin_token),
    )
    res = client.post(
        "/admin/users/",
        json={"email": "dup@test.com", "password": "autre", "role": "client"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 409


def test_update_user(client, admin_user, admin_token, regular_user):
    res = client.patch(
        f"/admin/users/{regular_user.id}",
        json={"is_active": False},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["is_active"] is False


def test_delete_user(client, admin_user, admin_token, regular_user):
    res = client.delete(
        f"/admin/users/{regular_user.id}",
        headers=auth_header(admin_token),
    )
    assert res.status_code == 204


def test_delete_nonexistent_user(client, admin_user, admin_token):
    res = client.delete("/admin/users/9999", headers=auth_header(admin_token))
    assert res.status_code == 404
