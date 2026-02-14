import uuid
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from domain.models import EventType, ResvStatus, PayloadType
from interface.api import app
from pathlib import Path

# event_file = Path("events.jsonl")
# event_file.write_text("")

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

# def _new_id(self) -> str:
#     return str(uuid.uuid4())
    

def test_api_flow(client: TestClient) -> None:
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": "L1",
        "type": "CompartmentRegistered",
        "payload": {PayloadType.COMPARTMENT_ID: "C1"}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

    # locker_id = uuid.uuid4()
    # compartment_id = uuid.uuid4()

    # response = client.get(f"/lockers/{locker_id}")
    # assert response.status_code == 200

    # response = client.get(f"/lockers/{locker_id}/compartments/{compartment_id}")
    # assert response.status_code == 200

    # reservation_id = "R3"
    # response = client.get(f"/reservations/{reservation_id}")
    # assert response.status_code == 200
    # json_data = response.json()
    # assert json_data[PayloadType.STATUS] == ResvStatus.CREATED
