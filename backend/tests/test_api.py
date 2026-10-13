import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["service"] == "LifeOS AI"

def test_quick_parse_task():
    response = client.post(
        "/api/v1/tasks/quick-parse",
        json={"text": "Write thesis report tomorrow high priority"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert data["priority"] in ["HIGH", "URGENT", "MEDIUM", "LOW"]

def test_get_tasks():
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_sync_calendar():
    response = client.post("/api/v1/calendar/sync")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_notes_crud():
    # Create note
    create_resp = client.post(
        "/api/v1/notes/",
        json={"title": "Test Note Title", "content": "Test Note Content for LifeOS"}
    )
    assert create_resp.status_code == 200
    note_id = create_resp.json()["id"]
    
    # Summarize
    sum_resp = client.post(f"/api/v1/notes/{note_id}/summarize")
    assert sum_resp.status_code == 200
    assert sum_resp.json()["summary"] is not None
    
    # Delete note
    del_resp = client.delete(f"/api/v1/notes/{note_id}")
    assert del_resp.status_code == 200
