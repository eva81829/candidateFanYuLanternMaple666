from domain.models import EventType, ResvStatus,PayloadType, LockerEvent, Locker, Compartment, Reservation
from domain.repositories import EventStore, Projection

class InMemoryProjection(Projection):
    def __init__(self):
        self._lockers: dict[str, Locker] = {} # key = locker_id
        self._reservations: dict[str, Reservation] = {} # key = reservation_id

    def apply(self, event: LockerEvent) -> None:
        if event.type == EventType.COMPARTMENT_REGISTERED:
            self._register_compartment(event)
        elif event.type == EventType.RESERVATION_CREATED:
            self._create_reservation(event)  
        elif event.type == EventType.RESERVATION_EXPIRED:
            self._expire_reservation(event)

    def query_locker(self, locker_id: str) -> Locker | None:
        return self._lockers.get(locker_id)
    
    def query_compartment(self, locker_id: str, compartment_id: str) -> Compartment | None:
        locker = self._lockers.get(locker_id)
        if not locker:
            return None
        return locker.get_compartment(compartment_id)

    def query_reservation(self, reservation_id: str) -> Reservation | None:
        return self._reservations.get(reservation_id)

    def _register_compartment(self, event: LockerEvent) -> None:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        if not comp_id:
            raise Exception("Compartment ID required")

        # if a locker cannot be found, it is treated as a new locker and added
        locker = self.query_locker(event.locker_id)
        if not locker:
            locker = Locker(event.locker_id)
            self._lockers[event.locker_id] = locker

        locker.add_compartment(comp_id)

    def _create_reservation(self, event: LockerEvent) -> None:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        if not comp_id:
            raise Exception("Compartment ID required")
        
        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        if not resv_id:
            raise Exception("Reservation ID required")

        locker = self.query_locker(event.locker_id)
        if not locker:
            raise Exception("Locker not found")

        if resv_id in self._reservations:
            raise Exception("Reservation ID duplicates")

        locker.add_reservation(comp_id, resv_id)
        self._reservations[resv_id] = locker.get_reservation(comp_id)

    # def deposite_parcel():
    # def picked_up_parcel():

    # set reservation to "EXPIRED"
    def _expire_reservation(self, event: LockerEvent) -> None:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        if not comp_id:
            raise Exception("Compartment ID required")
        
        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        if not resv_id:
            raise Exception("Reservation ID required")

        locker = self.query_locker(event.locker_id)
        if not locker:
            raise Exception("Locker not found")

        locker.update_reservation(comp_id, resv_id, ResvStatus.EXPIRED)

    # def report_fault():
    # def clear_fault():


    # def rebuild(self, event_store: EventStore) -> None:
    #     for event in event_store.load_all():
    #         self.apply(event)
