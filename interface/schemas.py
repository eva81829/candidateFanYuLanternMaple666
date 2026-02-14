from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Any
from domain.models import EventType, ResvStatus

class Event(BaseModel):
    event_id: UUID
    occurred_at: datetime
    locker_id: str
    type: EventType
    payload: dict[str, Any]

class LockerSummary(BaseModel):
    locker_id: str
    compartments: int
    active_reservations: int
    degraded_compartments: int
    state_hash: str

# If the compartment has an active reservation, active_reservation = reservation_id
class CompartmentStatus(BaseModel):
    compartment_id: str
    degraded: bool
    active_reservation: str | None = None

class ReservationStatus(BaseModel):
    reservation_id: str
    status: ResvStatus