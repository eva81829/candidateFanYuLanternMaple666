from __future__ import annotations
from typing import Any
from enum import Enum

class EventType(str, Enum):
    COMPARTMENT_REGISTERED = "CompartmentRegistered"
    RESERVATION_CREATED = "ReservationCreated"
    PARCEL_DEPOSITED = "ParcelDeposited"
    PARCEL_PICKED_UP = "ParcelPickedUp"
    RESERVATION_EXPIRED = "ReservationExpired"
    FAULT_REPORTED = "FaultReported"
    FAULT_CLEARED = "FaultCleared"

class ResvStatus(str, Enum):
    CREATED = "CREATED"
    DEPOSITED = "DEPOSITED"
    PICKED_UP = "PICKED_UP"
    EXPIRED = "EXPIRED"

class PayloadType(str, Enum):
    COMPARTMENT_ID = "compartment_id"
    RESERVATION_ID = "reservation_id"
    STATUS = "status"

class LockerEvent:
    def __init__(self, event_id: str, occurred_at: str, locker_id: str, type: EventType, payload: dict[str, Any]):
        self.event_id = event_id
        self.occurred_at = occurred_at
        self.locker_id = locker_id
        self.type = type
        self.payload = payload


# class Service:
#     def __init__(self):
    
#     def get_locker(self, locker_id: str) -> Locker | None:
#         return self._lockers.get(locker_id)

#     def _add_locker(self, locker_id: str):
#         # if locker_id in self._lockers:
#         #     raise Exception("Locker already exists")
#         locker = Locker(locker_id)
#         self._lockers[locker_id] = locker



# Aggregate Root
class Locker:
    def __init__(self, locker_id: str):
        self.locker_id = locker_id
        self._compartments: dict[str, Compartment] = {}  # {"compartment_id", Compartment} 
        self.num_compartment: int = 0
        self.num_reservation: int = 0
        self.num_degraded: int = 0
        self.state_hash: str = None

    def get_compartment(self, compartment_id: str) -> Compartment | None:
        return self._compartments.get(compartment_id)

    def add_compartment(self, compartment_id: str) -> None:
        if compartment_id in self._compartments:
            raise Exception("Compartment already exists")

        compartment = Compartment(compartment_id)
        self._compartments[compartment_id] = compartment

    def get_reservation(self, compartment_id: str) -> Reservation | None:
        compartment_id
        if compartment_id not in self._compartments:
            raise Exception("Compartment not found")
        
        compartment = self._compartments[compartment_id]
        return compartment.reservation

    def add_reservation(self, compartment_id: str, reservation_id: str) -> None:
        # a reservation can only exist for an existing compartment
        if compartment_id not in self._compartments:
            raise Exception("Compartment not found")
        
        # a compartment can have at most one active reservation at a time
        compartment = self._compartments[compartment_id]
        if compartment.reservation:
            raise Exception("Reservation already exists")
        
        reservation = Reservation(reservation_id)
        compartment.reservation = reservation

    # def degrade_compartment(self, compartment_id: str) -> None:

        
    #     compartment = self._compartments[compartment_id]
    #     compartment.degraded = True
    #     compartment.reservation = None

    # def update_reservation(self, compartment_id: str, reservation_id: str, status: ResvStatus):
    #     # a reservation can only exist for an existing compartment
    #     if compartment_id not in self._compartments:
    #         raise Exception("Compartment not found")
        
    #     # reservation can only be updated for an existing reservation
    #     compartment = self._compartments[compartment_id]
    #     if not compartment.reservation:
    #         raise Exception("Reservation not found")

    #     if compartment.reservation.reservation_id != reservation_id:
    #         raise Exception("Reservation ID does not match")
    #     compartment.reservation.status = status

class Compartment:
    def __init__(self, compartment_id: str):
        self.compartment_id = compartment_id
        self.degraded: bool = False
        self.reservation: Reservation | None = None

class Reservation:
    def __init__(self, reservation_id: str):
        self.reservation_id = reservation_id
        self.status: ResvStatus = ResvStatus.CREATED
