import uuid
from domain.models import EventType, LockerEvent, Reservation, Compartment, Locker
from domain.repositories import EventStore, Projection

class LockerService:
    def __init__(self, projection: Projection, event_store: EventStore):
        self.projection = projection
        self.event_store = event_store

    def handle(self, event: LockerEvent):
        if event.type == EventType.COMPARTMENT_REGISTERED:
            self._register_compartment(event.locker_id)      

    def _new_id(self) -> str:
        return str(uuid.uuid4())
    
    def _register_locker(self, locker_id: str) -> Locker:
        locker = Locker(locker_id)
        self.projection.set_locker(locker)
        return locker

    def _register_compartment(self, locker_id: str) -> str:
        locker = self.projection.get_locker(locker_id)
        if not locker:
            locker = self._register_locker(locker_id)

        compartment_id = self._new_id()
        compartment = Compartment(compartment_id)
        locker.add_compartment(compartment)
        self.projection.set_locker(locker)
        self.event_store.append_event({"type": "CompartmentRegistered", "locker_id": locker.locker_id, "compartment_id": compartment_id})
        return compartment_id
    
    # def create_reservation():
    # def deposite_parcel():
    # def picked_up_parcel():
    # def expire_reservation():      
    # def report_fault(): 
    # def clear_fault():    
