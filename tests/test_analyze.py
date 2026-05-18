from unittest.mock import MagicMock

import pytest

from app.main import app
from app.services.analyze import get_anthropic_client

ANALYZE_PAYLOAD = {
    "type_discours": "pitch",
    "type_discours_label": "Pitch commercial",
    "duree_min": "5",
    "transcript": "Bonjour, je m'appelle Nicolas.",
    "images": [],
    "audio_stats": {},
    "visual_stats": {},
}


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_anthropic():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="## Analyse simulée\nScore global : 85%")]
    )
    app.dependency_overrides[get_anthropic_client] = lambda: mock_client
    yield mock_client
    del app.dependency_overrides[get_anthropic_client]


def test_analyze_authenticated(client, regular_user, user_token):
    res = client.post(
        "/api/analyze",
        json=ANALYZE_PAYLOAD,
        headers=auth_header(user_token),
    )
    assert res.status_code == 200
    assert "analyse" in res.json()
    assert "Analyse simulée" in res.json()["analyse"]


def test_analyze_unauthenticated(client):
    res = client.post("/api/analyze", json=ANALYZE_PAYLOAD)
    assert res.status_code == 401


def test_analyze_calls_anthropic(client, regular_user, user_token, mock_anthropic):
    client.post(
        "/api/analyze",
        json=ANALYZE_PAYLOAD,
        headers=auth_header(user_token),
    )
    assert mock_anthropic.messages.create.called
    call_kwargs = mock_anthropic.messages.create.call_args.kwargs
    assert call_kwargs["model"] is not None
    assert call_kwargs["max_tokens"] == 5000
