from pydantic import BaseModel
from typing import Literal
from domain.models import EventType

class Event(BaseModel):
        event_id: str
        occurred_at: str
        locker_id: str
        type: EventType
        payload: str