from fastapi import FastAPI, HTTPException
from domain.models import LockerEvent
from application.use_cases import LockerService
from infrastructure.in_memory_projection import InMemoryProjection
from infrastructure.in_memory_event_store import InMemoryEventStore
from interface.schemas import Event

# initialize
app = FastAPI()
projection = InMemoryProjection()
event_store = InMemoryEventStore()
service = LockerService(projection, event_store)

@app.post("/events")
def handle_event(event: Event):
    locker_event = LockerEvent(event.event_id, event.occurred_at, event.locker_id, event.type, event.payload)
    service.handle(locker_event)
