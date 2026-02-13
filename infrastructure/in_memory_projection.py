from typing import Dict, Optional
from domain.models import Reservation, Compartment, Locker
from domain.repositories import Projection

class InMemoryProjection(Projection):
    def __init__(self):
        self._lockers: Dict[str, Locker] = {}

    def set_locker(self, locker: Locker) -> None:
        self._lockers[locker.locker_id] = locker

    def get_locker(self, locker_id: str) -> Optional[Locker]:
        return self._lockers.get(locker_id)
