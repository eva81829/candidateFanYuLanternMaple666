from domain.models import EventType, PayloadType, LockerEvent, Locker, Compartment, Reservation
from domain.repositories import EventStore, Projection


class InMemoryProjection(Projection):
    def __init__(self):
        self._lockers: dict[str, Locker] = {} # key = locker_id
        self._reservations: dict[str, Reservation] = {} # key = reservation_id

    def apply(self, event: LockerEvent) -> None:
        if event.type == EventType.COMPARTMENT_REGISTERED:
            self._register_compartment(event)

    def query_locker(self, locker_id: str) -> Locker | None:
        return self._lockers.get(locker_id)
    
    # def query_compartment(self, locker_id: str, compartment_id: str) -> Compartment | None:
    #     locker = self._lockers.get(locker_id)
    #     if not locker:
    #         return None
    #     return locker.get_compartment(compartment_id)

    # def query_reservation(self, reservation_id: str) -> Reservation | None:
    #     return self._reservations.get(reservation_id)

    def _register_compartment(self, event: LockerEvent) -> None:
        # if a locker cannot be found, it is treated as a new locker and added
        locker = self.query_locker(event.locker_id)
        if not locker:
            locker = Locker(event.locker_id)

        compartment_id = event.payload[PayloadType.COMPARTMENT_ID]
        locker.add_compartment(compartment_id)
        self._lockers[event.locker_id] = locker

    # def create_reservation():


    #         if event.type == EventType.RESERVATION_CREATED:
    #             resv_id = event.payload[PayloadType.RESERVATION_ID]
    #             status = event.payload[PayloadType.STATUS]
    #             self._reservations[resv_id] = Reservation(resv_id, status)


    # def deposite_parcel():
    # def picked_up_parcel():
    # def expire_reservation():      
    # def report_fault(): 
    # def clear_fault():


    # def rebuild(self, event_store: EventStore) -> None:
    #     for event in event_store.load_all():
    #         self.apply(event)
