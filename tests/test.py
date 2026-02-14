import uuid
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from interface.api import app
from interface.schemas import Event
from pathlib import Path

event_file = Path("events.jsonl")
event_file.write_text("")

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

def test_api_flow(client: TestClient) -> None:
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": "L1",
        "type": "CompartmentRegistered",
        "payload": {"some_key": "some_value"}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

    locker_id = uuid.uuid4()
    compartment_id = uuid.uuid4()
    reservation_id = uuid.uuid4()

    response = client.get(f"/lockers/{locker_id}")
    assert response.status_code == 200

    response = client.get(f"/lockers/{locker_id}/compartments/{compartment_id}")
    assert response.status_code == 200

    response = client.get(f"/reservations/{reservation_id}")
    assert response.status_code == 200
