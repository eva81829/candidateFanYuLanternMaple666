from fastapi import FastAPI, Response, status
from domain.models import EventResult, LockerEvent
from application.use_cases import LockerService
from infrastructure.in_memory_projection import InMemoryProjection
from infrastructure.file_event_store import FileEventStore
from interface.schemas import Event, LockerSummary, CompartmentStatus, ReservationStatus

# initialize
app = FastAPI()
projection = InMemoryProjection()
event_store = FileEventStore()
service = LockerService(projection, event_store)

@app.put("/rebuild")
def rebuild_events() -> None:
    service.rebuild_events()

@app.post("/events")
def handle_event(event: Event) -> Response:
    locker_event = LockerEvent(event.event_id, event.occurred_at, event.locker_id, event.type, event.payload)
    result = service.handle_event(locker_event)
    if result == EventResult.SUCCESS:
        content = '{"description": "Event accepted"}'
        status_code = status.HTTP_202_ACCEPTED
    elif result == EventResult.DUPLICATE:
        content = '{"description": "Duplicate event (idempotent)"}'
        status_code = status.HTTP_200_OK
    elif result == EventResult.DOMAIN_VIOLATION:
        content = '{"description": "Domain rule violation"}'
        status_code = status.HTTP_409_CONFLICT
    elif result == EventResult.VALIDATION_ERROR:
        content = '{"description": "Validation error"}'
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

    return Response(
        content = content,
        status_code = status_code,
        media_type = "application/json"
    )

@app.get("/lockers/{locker_id}")
def get_locker(locker_id: str) -> LockerSummary | None:
    locker = service.get_locker_state(locker_id)
    if locker is None:
        return None
    
    return LockerSummary(
            locker_id = locker.locker_id,
            compartments = locker.num_compartment,
            active_reservations = locker.num_reservation,
            degraded_compartments = locker.num_degraded,
            state_hash = locker.state_hash
        )

@app.get("/lockers/{locker_id}/compartments/{compartment_id}")
def get_compartment(locker_id: str, compartment_id: str) -> CompartmentStatus | None:
    compartment = service.get_compartment_state(locker_id, compartment_id)
    if compartment is None:
        return None
    
    return CompartmentStatus(
            compartment_id = compartment.compartment_id,
            degraded = compartment.degraded,
            active_reservation = compartment.reservation.reservation_id if compartment.reservation else None
        )

@app.get("/reservations/{reservation_id}")
def get_reservation(reservation_id: str) -> ReservationStatus | None:
    reservation = service.get_reservation_state(reservation_id)
    if reservation is None:
        return None
    
    return ReservationStatus(
            reservation_id = reservation.reservation_id,
            status = reservation.status
        )
