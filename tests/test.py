import uuid
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from domain.models import EventType, ResvStatus, PayloadType
from interface.api import app
from pathlib import Path

event_file = Path("events.jsonl")
event_file.write_text("")

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

# def _new_id(self) -> str:
#     return str(uuid.uuid4())

def test_api_flow(client: TestClient) -> None:
    locker1_id = "L1"
    locker2_id = "L2"

    comp1_id = "C1"
    comp2_id = "C2"

    resv1_id = "R1"
    resv2_id = "R2" 

    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": "L1",
        "type": EventType.RESERVATION_CREATED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id, PayloadType.RESERVATION_ID: resv1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200   
    
    response = client.get(f"/lockers/{locker1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["compartments"] == 1

    response = client.get(f"/lockers/{locker1_id}/compartments/{comp1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["active_reservation"] == resv1_id

    response = client.get(f"/reservations/{resv1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data[PayloadType.STATUS] == ResvStatus.CREATED

    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": "L1",
        "type": EventType.RESERVATION_EXPIRED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id, PayloadType.RESERVATION_ID: resv1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

    response = client.get(f"/reservations/{resv1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data[PayloadType.STATUS] == ResvStatus.EXPIRED
