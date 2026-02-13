from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models import LockerEvent, Reservation, Compartment, Locker

class EventStore(ABC):
    @abstractmethod
    def load_all(self) -> List[LockerEvent]: ...
    @abstractmethod
    def load_by_locker(self, locker_id: str) -> List[LockerEvent]: ...
    @abstractmethod
    def append(self, event: LockerEvent) -> None: ...

class Projection(ABC):
    @abstractmethod
    def set_locker(self, locker: Locker) -> None: ...
    @abstractmethod
    def get_locker(self, locker_id: str) -> Optional[Locker]: ...