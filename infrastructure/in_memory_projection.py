from domain.models import EventResult, EventType, PayloadType, LockerEvent, Locker, Compartment, Reservation
from domain.repositories import EventStore, Projection

class InMemoryProjection(Projection):
    def __init__(self):
        self._lockers: dict[str, Locker] = {} # key = locker_id
        self._reservations: dict[str, Reservation] = {} # key = reservation_id

    def rebuild(self, event_store: EventStore) -> int:
        for event in event_store.load_all():
            self.apply(event)
        return EventResult.SUCCESS

    def apply(self, event: LockerEvent, event_store: EventStore) -> int:
        result = EventResult.SUCCESS
        if event.type == EventType.COMPARTMENT_REGISTERED:
            result =  self._register_compartment(event)
        elif event.type == EventType.RESERVATION_CREATED:
            result = self._create_reservation(event)
        elif event.type == EventType.PARCEL_DEPOSITED:
            result = self._deposite_parcel(event)
        elif event.type == EventType.PARCEL_PICKED_UP:
            result = self._picked_up_parcel(event)                     
        elif event.type == EventType.RESERVATION_EXPIRED:
            result = self._expire_reservation(event)
        elif event.type == EventType.FAULT_REPORTED:
            result = self._report_fault(event)
        elif event.type == EventType.FAULT_CLEARED:
            result = self._clear_fault(event, event_store)     
        return result

    def query_locker(self, locker_id: str) -> Locker | None:
        return self._lockers.get(locker_id)
    
    def query_compartment(self, locker_id: str, compartment_id: str) -> Compartment | None:
        locker = self._lockers.get(locker_id)
        if not locker:
            return None
        return locker.get_compartment(compartment_id)

    def query_reservation(self, reservation_id: str) -> Reservation | None:
        return self._reservations.get(reservation_id)

    def _register_compartment(self, event: LockerEvent) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR

        # if a locker cannot be found, it is treated as a new locker and added
        locker = self.query_locker(event.locker_id)
        if not locker:
            locker = Locker(event.locker_id)
            self._lockers[event.locker_id] = locker

        return locker.add_compartment(comp_id)

    def _create_reservation(self, event: LockerEvent) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR
        
        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        # Reservation ID required
        if not resv_id:
            return EventResult.VALIDATION_ERROR
        
        locker = self.query_locker(event.locker_id)
        # Locker not found
        if not locker:
            return EventResult.VALIDATION_ERROR

        # Reservation ID duplicates
        if resv_id in self._reservations:
            return EventResult.VALIDATION_ERROR

        result = locker.add_reservation(comp_id, resv_id)
        if result != EventResult.SUCCESS:
            return result

        self._reservations[resv_id] = locker.get_reservation(comp_id)
        return EventResult.SUCCESS

    def _deposite_parcel(self, event: LockerEvent) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR

        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        # Reservation ID required
        if not resv_id:
            return EventResult.VALIDATION_ERROR

        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        # Reservation ID required
        if not resv_id:
            return EventResult.VALIDATION_ERROR

        locker = self.query_locker(event.locker_id)
        # Locker not found
        if not locker:
            return EventResult.VALIDATION_ERROR

        return locker.deposite_parcel(comp_id, resv_id)  

    def _picked_up_parcel(self, event: LockerEvent) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR

        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        # Reservation ID required
        if not resv_id:
            return EventResult.VALIDATION_ERROR

        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        # Reservation ID required
        if not resv_id:
            return EventResult.VALIDATION_ERROR

        locker = self.query_locker(event.locker_id)
        # Locker not found
        if not locker:
            return EventResult.VALIDATION_ERROR

        return locker.pick_up_parcel(comp_id, resv_id)             

    # set reservation to "EXPIRED"
    def _expire_reservation(self, event: LockerEvent) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR
        
        resv_id = event.payload.get(PayloadType.RESERVATION_ID)
        # Reservation ID required
        if not resv_id:
            return EventResult.VALIDATION_ERROR

        locker = self.query_locker(event.locker_id)
        # Locker not found
        if not locker:
            return EventResult.VALIDATION_ERROR

        return locker.expire_reservation(comp_id, resv_id)

    def _report_fault(self, event: LockerEvent) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR

        severity = event.payload.get(PayloadType.SEVERITY)
        # Severity required
        if not severity:
            return EventResult.VALIDATION_ERROR

        locker = self.query_locker(event.locker_id)
        # Locker not found
        if not locker:
            return EventResult.VALIDATION_ERROR
        
        return locker.report_fault_compartment(comp_id, severity)

    def _clear_fault(self, event: LockerEvent, event_store: EventStore) -> int:
        comp_id = event.payload.get(PayloadType.COMPARTMENT_ID)
        # Compartment ID required
        if not comp_id:
            return EventResult.VALIDATION_ERROR

        reported_event_id = event.payload.get(PayloadType.REPORTED_EVENT_ID)
        # a `FaultCleared` event must reference a prior `FaultReported.event_id`
        if not reported_event_id:
            return EventResult.VALIDATION_ERROR

        locker = self.query_locker(event.locker_id)
        # Locker not found
        if not locker:
            return EventResult.VALIDATION_ERROR

        events = event_store.load_by_locker(event.locker_id) 
        is_reported = False
        is_cleared = False
        for e in events:
            # the referenced fault must belong to the same compartment
            if e.type == EventType.FAULT_REPORTED:
                if (e.payload.get(PayloadType.COMPARTMENT_ID) == comp_id
                    and e.event_id  == reported_event_id):
                    is_reported = True
            elif e.type == EventType.FAULT_CLEARED:
                if (e.payload.get(PayloadType.COMPARTMENT_ID) == comp_id
                    and e.payload.get(PayloadType.REPORTED_EVENT_ID) == reported_event_id):
                    is_cleared = True

        # # clearing a non-existing or already-cleared fault is invalid
        if (not is_reported or is_cleared):
            return EventResult.VALIDATION_ERROR

        return locker.clear_fault_compartment(comp_id)
