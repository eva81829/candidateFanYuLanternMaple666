from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from domain.models import Reservation, Compartment, Locker

class EventStore(ABC):
    @abstractmethod
    def append_event(self, event: Dict[str, Any]) -> None: ...
    @abstractmethod
    def read_events(self): ...
    
class Projection(ABC):
    @abstractmethod
    def set_locker(self, locker: Locker) -> None: ...
    @abstractmethod
    def get_locker(self, locker_id: str) -> Optional[Locker]: ...