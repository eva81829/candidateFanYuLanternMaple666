import pytest
from fastapi.testclient import TestClient
from interface.api import app
from pathlib import Path

event_file = Path("events.jsonl")
event_file.write_text("")

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

def test_api_flow(client: TestClient) -> None:
    event = {
        "event_id": "ABC",
        "occurred_at": "2026-02-12T10:00:00Z",
        "locker_id": "L1",
        "type": "CompartmentRegistered",
        "payload": {"some_key": "some_value"}
    }
    
    response = client.post("/events", json = event)
    assert response.status_code == 200