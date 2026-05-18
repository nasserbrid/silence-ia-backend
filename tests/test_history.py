import pytest

from app.models.session import Session
from tests.conftest import TestingSession

SESSION_PAYLOAD = {
    "type_discours": "pitch",
    "type_discours_label": "Pitch commercial",
    "duree_prevue_min": 5.0,
    "duree_effective_sec": 280,
    "transcription": "Bonjour je m'appelle Nicolas.",
    "analyse": "## Score global : 85%",
    "word_count": 6,
}


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_history_empty(client, regular_user, user_token):
    res = client.get("/api/history/", headers=auth_header(user_token))
    assert res.status_code == 200
    assert res.json() == []


def test_save_session(client, regular_user, user_token):
    res = client.post("/api/history/", json=SESSION_PAYLOAD, headers=auth_header(user_token))
    assert res.status_code == 201
    assert res.json()["type_discours"] == "pitch"
    assert res.json()["user_id"] == regular_user.id


def test_get_history_returns_own_sessions(client, regular_user, user_token):
    client.post("/api/history/", json=SESSION_PAYLOAD, headers=auth_header(user_token))
    res = client.get("/api/history/", headers=auth_header(user_token))
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_delete_own_session(client, regular_user, user_token):
    save = client.post("/api/history/", json=SESSION_PAYLOAD, headers=auth_header(user_token))
    session_id = save.json()["id"]
    res = client.delete(f"/api/history/{session_id}", headers=auth_header(user_token))
    assert res.status_code == 204


def test_delete_other_user_session_forbidden(client, regular_user, user_token, admin_user, admin_token):
    save = client.post("/api/history/", json=SESSION_PAYLOAD, headers=auth_header(admin_token))
    session_id = save.json()["id"]
    res = client.delete(f"/api/history/{session_id}", headers=auth_header(user_token))
    assert res.status_code == 403


def test_delete_nonexistent_session(client, regular_user, user_token):
    res = client.delete("/api/history/9999", headers=auth_header(user_token))
    assert res.status_code == 404


def test_history_unauthenticated(client):
    res = client.get("/api/history/")
    assert res.status_code == 401
