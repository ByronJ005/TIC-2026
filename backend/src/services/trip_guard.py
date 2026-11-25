from typing import List, Protocol
from pydantic import BaseModel


class ActiveTripsReport(BaseModel):
    active_trips_count: int = 0
    active_reservations_count: int = 0
    affected_user_ids: List[int] = []

    @property
    def has_active_trips_or_reservations(self) -> bool:
        return self.active_trips_count > 0 or self.active_reservations_count > 0


class TripReservationGuard(Protocol):
    def check_active_trips_or_reservations(self, route_id: int) -> ActiveTripsReport: ...


class NoopTripReservationGuard:
    """
    Default guard implementation for Submódulo 05.
    Returns 0 active trips and reservations since trips/reservations
    modules are not yet implemented in this sprint.
    """

    def check_active_trips_or_reservations(self, route_id: int) -> ActiveTripsReport:
        return ActiveTripsReport(
            active_trips_count=0,
            active_reservations_count=0,
            affected_user_ids=[],
        )


def get_trip_guard() -> TripReservationGuard:
    return NoopTripReservationGuard()
