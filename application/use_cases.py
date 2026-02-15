from domain.models import EventResult, LockerEvent, Locker, Compartment, Reservation
from domain.repositories import EventStore, Projection

class LockerService:
    def __init__(self, projection: Projection, event_store: EventStore):
        self.projection = projection
        self.event_store = event_store

    def handle(self, event: LockerEvent):
        result = self.projection.apply(event, self.event_store)
        if result != EventResult.SUCCESS:
            return result
        return self.event_store.append(event)

    def get_locker_state(self, locker_id: str) -> Locker:
        return self.projection.query_locker(locker_id)

    def get_compartment_state(self, locker_id: str, compartment_id: str) -> Compartment:
        return self.projection.query_compartment(locker_id, compartment_id)

    def get_reservation_state(self, reservation_id: str) -> Reservation:
        return self.projection.query_reservation(reservation_id)