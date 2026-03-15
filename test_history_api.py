from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from backend.api import history
from backend.api.auth import get_current_user_id


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(history.router, prefix="/api")
    app.dependency_overrides[get_current_user_id] = lambda: "test-user-123"
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_diary_entries():
    return [
        {
            "entry_id": "entry-1",
            "text": "<p>First journal entry</p>",
            "timestamp": "2026-03-10T09:00:00",
            "user_id": "test-user-123",
        },
        {
            "entry_id": "entry-2",
            "text": "<p>Second <strong>journal</strong> entry</p>",
            "timestamp": "2026-03-11T09:00:00",
            "user_id": "test-user-123",
        },
        {
            "entry_id": "entry-3",
            "text": "<p>Third journal entry</p>",
            "timestamp": "2026-03-12T09:00:00",
            "user_id": "test-user-123",
        },
    ]


@pytest.fixture
def sample_mood_entries():
    return [
        {
            "mood_id": "mood-1",
            "mood": "calm",
            "intensity": 3,
            "note": "Pretty steady today",
            "date": "2026-03-10",
            "timestamp": "2026-03-10T08:00:00",
            "user_id": "test-user-123",
        },
        {
            "mood_id": "mood-2",
            "mood": "anxious",
            "intensity": 7,
            "note": "Busy afternoon",
            "date": "2026-03-11",
            "timestamp": "2026-03-11T08:00:00",
            "user_id": "test-user-123",
        },
        {
            "mood_id": "mood-3",
            "mood": "hopeful",
            "intensity": 6,
            "note": "Feeling better",
            "date": "2026-03-12",
            "timestamp": "2026-03-12T08:00:00",
            "user_id": "test-user-123",
        },
    ]


def test_list_diary_entries_returns_chronological_entries(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get("/api/history/diary")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["total"] == 3
    assert len(data["entries"]) == 3

    # HTML should be stripped in preview output
    assert data["entries"][0]["entry_id"] == "entry-1"
    assert data["entries"][0]["text"] == "First journal entry"
    assert data["entries"][1]["text"] == "Second journal entry"


def test_list_diary_entries_empty_returns_success_with_zero(client, monkeypatch):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: [])

    response = client.get("/api/history/diary")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["total"] == 0
    assert data["entries"] == []


def test_navigate_diary_without_current_id_returns_first_entry(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get("/api/history/diary/nav")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["entry"]["entry_id"] == "entry-1"
    assert data["entry"]["plain_text"] == "First journal entry"
    assert data["position"] == 0
    assert data["total"] == 3
    assert data["has_previous"] is False
    assert data["has_next"] is True
    assert data["previous_entry_id"] is None
    assert data["next_entry_id"] == "entry-2"


def test_navigate_diary_next_moves_forward(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get(
        "/api/history/diary/nav",
        params={"current_entry_id": "entry-1", "direction": "next"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["entry"]["entry_id"] == "entry-2"
    assert data["position"] == 1
    assert data["has_previous"] is True
    assert data["has_next"] is True
    assert data["previous_entry_id"] == "entry-1"
    assert data["next_entry_id"] == "entry-3"


def test_navigate_diary_previous_moves_back(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get(
        "/api/history/diary/nav",
        params={"current_entry_id": "entry-3", "direction": "previous"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["entry"]["entry_id"] == "entry-2"
    assert data["position"] == 1
    assert data["has_previous"] is True
    assert data["has_next"] is True


def test_navigate_diary_next_at_end_stays_at_last_entry(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get(
        "/api/history/diary/nav",
        params={"current_entry_id": "entry-3", "direction": "next"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["entry"]["entry_id"] == "entry-3"
    assert data["position"] == 2
    assert data["has_previous"] is True
    assert data["has_next"] is False
    assert data["next_entry_id"] is None


def test_navigate_diary_previous_at_start_stays_at_first_entry(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get(
        "/api/history/diary/nav",
        params={"current_entry_id": "entry-1", "direction": "previous"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["entry"]["entry_id"] == "entry-1"
    assert data["position"] == 0
    assert data["has_previous"] is False
    assert data["has_next"] is True


def test_navigate_diary_invalid_entry_id_returns_404(client, monkeypatch, sample_diary_entries):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    response = client.get(
        "/api/history/diary/nav",
        params={"current_entry_id": "does-not-exist", "direction": "current"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Diary entry not found"


def test_navigate_diary_empty_returns_404(client, monkeypatch):
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: [])

    response = client.get("/api/history/diary/nav")
    assert response.status_code == 404
    assert response.json()["detail"] == "No diary entries found"


def test_list_moods_returns_entries(client, monkeypatch, sample_mood_entries):
    monkeypatch.setattr(history, "_get_user_mood_history", lambda user_id: sample_mood_entries)

    response = client.get("/api/history/moods")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["total"] == 3
    assert len(data["moods"]) == 3
    assert data["moods"][0]["mood_id"] == "mood-1"
    assert data["moods"][1]["mood"] == "anxious"


def test_navigate_moods_without_current_id_returns_first(client, monkeypatch, sample_mood_entries):
    monkeypatch.setattr(history, "_get_user_mood_history", lambda user_id: sample_mood_entries)

    response = client.get("/api/history/moods/nav")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["mood"]["mood_id"] == "mood-1"
    assert data["position"] == 0
    assert data["total"] == 3
    assert data["has_previous"] is False
    assert data["has_next"] is True
    assert data["next_mood_id"] == "mood-2"


def test_navigate_moods_next_moves_forward(client, monkeypatch, sample_mood_entries):
    monkeypatch.setattr(history, "_get_user_mood_history", lambda user_id: sample_mood_entries)

    response = client.get(
        "/api/history/moods/nav",
        params={"current_mood_id": "mood-1", "direction": "next"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["mood"]["mood_id"] == "mood-2"
    assert data["position"] == 1
    assert data["has_previous"] is True
    assert data["has_next"] is True


def test_navigate_moods_previous_moves_back(client, monkeypatch, sample_mood_entries):
    monkeypatch.setattr(history, "_get_user_mood_history", lambda user_id: sample_mood_entries)

    response = client.get(
        "/api/history/moods/nav",
        params={"current_mood_id": "mood-3", "direction": "previous"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["mood"]["mood_id"] == "mood-2"
    assert data["position"] == 1


def test_navigate_moods_invalid_id_returns_404(client, monkeypatch, sample_mood_entries):
    monkeypatch.setattr(history, "_get_user_mood_history", lambda user_id: sample_mood_entries)

    response = client.get(
        "/api/history/moods/nav",
        params={"current_mood_id": "bad-id", "direction": "current"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Mood history item not found"


def test_navigate_moods_empty_returns_404(client, monkeypatch):
    monkeypatch.setattr(history, "_get_user_mood_history", lambda user_id: [])

    response = client.get("/api/history/moods/nav")
    assert response.status_code == 404
    assert response.json()["detail"] == "No mood history found"


def test_missing_auth_returns_401_when_override_removed(app, monkeypatch, sample_diary_entries):
    app.dependency_overrides = {}
    monkeypatch.setattr(history, "_get_user_diary_entries", lambda user_id: sample_diary_entries)

    client = TestClient(app)
    response = client.get("/api/history/diary")
    assert response.status_code == 401