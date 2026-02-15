from __future__ import annotations
from typing import Any
from enum import Enum

class EventResult(Enum):
    SUCCESS = 1
    DUPLICATE = 2
    DOMAIN_VIOLATION = 3
    VALIDATION_ERROR = 4

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
    SEVERITY = "severity"

class LockerEvent:
    def __init__(self, event_id: str, occurred_at: str, locker_id: str, type: EventType, payload: dict[str, Any]):
        self.event_id = event_id
        self.occurred_at = occurred_at
        self.locker_id = locker_id
        self.type = type
        self.payload = payload

# Aggregate Root
class Locker:
    def __init__(self, locker_id: str):
        self.locker_id = locker_id
        self.num_compartment: int = 0
        self.num_reservation: int = 0
        self.num_degraded: int = 0
        self.state_hash: str = ""
        self._compartments: dict[str, Compartment] = {}  # {"compartment_id", Compartment} 

    def get_compartment(self, compartment_id: str) -> Compartment | None:
        return self._compartments.get(compartment_id)

    def add_compartment(self, compartment_id: str) -> int:
        # Compartment already exists
        if compartment_id in self._compartments:
            return EventResult.DOMAIN_VIOLATION

        compartment = Compartment(compartment_id)
        self._compartments[compartment_id] = compartment
        self.num_compartment += 1
        return EventResult.SUCCESS

    def report_fault_compartment(self, compartment_id: str, severity: int) -> int:
        # Compartment not found
        if compartment_id not in self._compartments:
            return EventResult.DOMAIN_VIOLATION
        
        # a compartment with fault of severity ≥ 3 are degraded
        if severity >= 3:
            compartment = self._compartments[compartment_id]
            compartment.degraded = True
        return EventResult.SUCCESS

    def get_reservation(self, compartment_id: str) -> Reservation | None:
        if compartment_id not in self._compartments:
            return None

        compartment = self._compartments[compartment_id]
        return compartment.reservation

    def add_reservation(self, compartment_id: str, reservation_id: str) -> int:
        # a reservation can only exist for an existing compartment
        if compartment_id not in self._compartments:
            return EventResult.DOMAIN_VIOLATION

        # a compartment can have at most one active reservation at a time
        compartment = self._compartments[compartment_id]
        if compartment.reservation:
            return EventResult.DOMAIN_VIOLATION

        # a degraded compartment cannot accept new reservations
        if compartment.degraded:
            return EventResult.DOMAIN_VIOLATION

        reservation = Reservation(reservation_id)
        compartment.reservation = reservation
        self.num_reservation += 1
        return EventResult.SUCCESS

    def update_reservation(self, compartment_id: str, reservation_id: str, status: ResvStatus) -> int:
        # a reservation can only exist for an existing compartment
        if compartment_id not in self._compartments:
            return EventResult.DOMAIN_VIOLATION

        # reservation can only be updated for an existing reservation
        compartment = self._compartments[compartment_id]
        if not compartment.reservation:
            return EventResult.DOMAIN_VIOLATION

        # Reservation ID does not match
        if compartment.reservation.reservation_id != reservation_id:
            return EventResult.DOMAIN_VIOLATION

        compartment.reservation.status = status
        return EventResult.SUCCESS

class Compartment:
    def __init__(self, compartment_id: str):
        self.compartment_id = compartment_id
        self.degraded: bool = False
        self.reservation: Reservation | None = None

class Reservation:
    def __init__(self, reservation_id: str):
        self.reservation_id = reservation_id
        self.status: ResvStatus = ResvStatus.CREATED
