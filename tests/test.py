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

    comp1_id = "C1"
    comp2_id = "C2"
    comp3_id = "C3"
    comp4_id = "C4"    

    resv1_id = "R1"
    resv2_id = "R2"
    resv3_id = "R3"
    resv4_id = "R4"    

    same_event_id = str(uuid.uuid4())
    reported_event_id = str(uuid.uuid4())

# 1. **OpenAPI contract tests**
#    - Use `openapi.yaml` as the source for validation.
#    - Requests violating the OpenAPI schema must return `422`.
    # COMPARTMENT_REGISTERED: locker1_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {} # without PayloadType.COMPARTMENT_ID: comp1_id
    }
    response = client.post("/events", json = event)
    assert response.status_code == 422

#    - Valid requests must conform exactly to the response schemas.
    # COMPARTMENT_REGISTERED: locker1_id, comp1_id
    event = {
        "event_id": same_event_id,
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 202

    # RESERVATION_CREATED: locker1_id, comp1_id, resv1_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.RESERVATION_CREATED,
        "payload": {PayloadType.COMPARTMENT_ID: comp1_id, PayloadType.RESERVATION_ID: resv1_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code  == 202
    
    # get_locker
    response = client.get(f"/lockers/{locker1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["compartments"] == 1

    # get_compartment
    response = client.get(f"/lockers/{locker1_id}/compartments/{comp1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["active_reservation"] == resv1_id

    # get_reservation
    response = client.get(f"/reservations/{resv1_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data[PayloadType.STATUS] == ResvStatus.CREATED

# 2. **Event idempotency**
#    - Re-sending the same `event_id` must not change state.
    # COMPARTMENT_REGISTERED: locker1_id, comp2_id
    event = {
        "event_id": same_event_id,
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp2_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["description"] == "Duplicate event (idempotent)"

# 3. **Invalid state transitions**
#    - Deposit before reservation
   # COMPARTMENT_REGISTERED: locker1_id, comp3_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp3_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 202
   # PARCEL_DEPOSITED: locker1_id, comp3_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.PARCEL_DEPOSITED,
        "payload": {PayloadType.COMPARTMENT_ID: comp3_id, PayloadType.RESERVATION_ID: resv3_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 409

#    - Pickup before deposit
    # RESERVATION_CREATED: locker1_id, comp3_id, resv3_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.RESERVATION_CREATED,
        "payload": {PayloadType.COMPARTMENT_ID: comp3_id, PayloadType.RESERVATION_ID: resv3_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code  == 202
   # PARCEL_PICKED_UP: locker1_id, comp3_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.PARCEL_PICKED_UP,
        "payload": {PayloadType.COMPARTMENT_ID: comp3_id, PayloadType.RESERVATION_ID: resv3_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 409

#    - Pickup after expiration
    # RESERVATION_EXPIRED: locker1_id, comp3_id, resv3_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.RESERVATION_EXPIRED,
        "payload": {PayloadType.COMPARTMENT_ID: comp3_id, PayloadType.RESERVATION_ID: resv3_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 202

    response = client.get(f"/reservations/{resv3_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data[PayloadType.STATUS] == ResvStatus.EXPIRED
   # PARCEL_PICKED_UP: locker1_id, comp3_id, resv3_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.PARCEL_PICKED_UP,
        "payload": {PayloadType.COMPARTMENT_ID: comp3_id, PayloadType.RESERVATION_ID: resv3_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 409

# 4. **Fault degradation and clearing**
#    - Severity threshold behavior
    # COMPARTMENT_REGISTERED: locker1_id, comp4_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.COMPARTMENT_REGISTERED,
        "payload": {PayloadType.COMPARTMENT_ID: comp4_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 202

   # FAULT_REPORTED: locker1_id, comp4_id
    event = {
        "event_id": reported_event_id,
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.FAULT_REPORTED,
        "payload": {PayloadType.COMPARTMENT_ID: comp4_id, PayloadType.SEVERITY: 3}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 202
    json_data = response.json()
    assert json_data["description"] == "Event accepted"

    # RESERVATION_CREATED: locker1_id, comp4_id, resv4_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.RESERVATION_CREATED,
        "payload": {PayloadType.COMPARTMENT_ID: comp4_id, PayloadType.RESERVATION_ID: resv4_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code  == 409

# #    - Invalid `FaultCleared` references
   # FAULT_CLEARED: locker1_id, comp4_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.FAULT_CLEARED,
        "payload": {PayloadType.COMPARTMENT_ID: comp4_id, PayloadType.REPORTED_EVENT_ID: str(uuid.uuid4())}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 422

   # FAULT_CLEARED: locker1_id, comp4_id
    event = {
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now().isoformat(),
        "locker_id": locker1_id,
        "type": EventType.FAULT_CLEARED,
        "payload": {PayloadType.COMPARTMENT_ID: comp4_id, PayloadType.REPORTED_EVENT_ID: reported_event_id}
    }
    response = client.post("/events", json = event)
    assert response.status_code == 202
