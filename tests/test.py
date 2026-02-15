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

def test_api_flow(client: TestClient) -> None:
    locker1_id = "L1"
    locker2_id = "L2"

    comp1_id = "C1"
    comp2_id = "C2"

    resv1_id = "R1"
    resv2_id = "R2" 

    # COMPARTMENT_REGISTERED: locker1_id, comp1_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

    # RESERVATION_CREATED: locker1_id, comp1_id, resv1_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
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

    # RESERVATION_EXPIRED: locker1_id, comp1_id, resv1_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.RESERVATION_EXPIRED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id, PayloadType.RESERVATION_ID: resv1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

    response = client.get(f"/reservations/{resv1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data[PayloadType.STATUS] == ResvStatus.EXPIRED

    # COMPARTMENT_REGISTERED: locker2_id, comp2_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker2_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp2_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200

   # FAULT_REPORTED: locker2_id, comp2_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker2_id,
        "type": EventType.FAULT_REPORTED,
        "payload": {PayloadType.COMPARTMENT_ID: comp2_id, PayloadType.SEVERITY: 3}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200