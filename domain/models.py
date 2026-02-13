from typing import Dict, Literal
from enum import Enum

class EventType(str, Enum):
    COMPARTMENT_REGISTERED = "CompartmentRegistered"
    RESERVATION_CREATED = "ReservationCreated"
    PARCEL_DEPOSITED = "ParcelDeposited"
    PARCEL_PICKED_UP = "ParcelPickedUp"
    RESERVATION_EXPIRED = "ReservationExpired"
    FAULT_REPORTED = "FaultReported"
    FAULT_CLEARED = "FaultCleared"

class LockerEvent:
    def __init__(self, event_id: str, occurred_at: str, locker_id: str, type: EventType, payload: str):
        self.event_id = event_id
        self.occurred_at = occurred_at
        self.locker_id = locker_id
        self.type = type
        self.payload = payload

class ReservationStatus(str, Enum):
    CREATED = "CREATED"
    DEPOSITED = "DEPOSITED"
    PICKED_UP = "PICKED_UP"
    EXPIRED = "EXPIRED"

class Reservation:
    def __init__(self, reservation_id: str, status: ReservationStatus):
        self.reservation_id = reservation_id
        self.status = status

class Compartment:
    def __init__(self, compartment_id: str):
        self.compartment_id = compartment_id
        self.degraded: bool = False
        self.reservation: Reservation = None

class Locker:
    def __init__(self, locker_id: str):
        self.locker_id = locker_id
        self.compartments: Dict[str, Compartment] = {}
        self.num_compartment: int = 0
        self.num_reservation: int = 0
        self.num_degraded: int = 0
        self.state_hash: str = None

    def add_compartment(self, compartment: Compartment):
        if compartment.compartment_id in self.compartments:
            raise Exception("Compartment already exists")
        self.compartments[compartment.compartment_id] = compartment
