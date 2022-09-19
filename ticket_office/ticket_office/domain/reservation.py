from dataclasses import dataclass
from functools import total_ordering

from ticket_office.domain.value_object import ValueObject


class BookingReference(ValueObject[str]):
    def validate(self, value: str) -> None:
        if not value:
            raise ValueError("BookingReference cannot be empty")


class SeatNumber(ValueObject[int]):
    def validate(self, value: int) -> None:
        if value <= 0 or value > 100:
            raise ValueError("Seat number must be between 1 and 99")


class CoachId(ValueObject[str]):
    def validate(self, value: str) -> None:
        if value not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            raise ValueError("Coach ID should be one uppercase letter")


@total_ordering
@dataclass(frozen=True)
class SeatId:
    number: SeatNumber
    coach_id: CoachId

    @classmethod
    def parse(cls, value: str) -> "SeatId":
        if len(value) != 3:
            raise ValueError(f"{value} should have length 2")
        number = SeatNumber(int(value[0:2]))
        coach_id = CoachId(value[2])
        return cls(number, coach_id)

    def __lt__(self, other: "SeatId") -> bool:
        return str(self) < str(other)

    def __str__(self) -> str:
        return f"{self.number}{self.coach_id}"

    def __repr__(self) -> str:
        return f"SeatId({self})"


@dataclass
class Seat:
    number: SeatNumber
    coach_id: CoachId
    booking_reference: BookingReference | None = None

    def __str__(self) -> str:
        return f"Seat(id={self.id}, booking_reference={self.booking_reference})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def id(self) -> SeatId:
        return SeatId(number=self.number, coach_id=self.coach_id)

    @classmethod
    def free_seat_with_id(cls, id: SeatId) -> "Seat":
        return cls(id.number, id.coach_id)

    @classmethod
    def parse(cls, value: str) -> "Seat":
        id = SeatId.parse(value)
        return cls.free_seat_with_id(id)

    def book(self, booking_reference: BookingReference) -> None:
        if self.booking_reference is None:
            self.booking_reference = booking_reference
        if self.booking_reference == booking_reference:
            return
        raise AlreadyBooked(self.id, self.booking_reference, booking_reference)

    @property
    def is_free(self) -> bool:
        return self.booking_reference is None


class TrainId(ValueObject[str]):
    def validate(self, value: str) -> None:
        if not value or value.isspace():
            raise ValueError("train id should not be blank")


class Train:
    """
    For the purpose of reservation, a train is a fixed collection of seats.
    Invariants:
        * no two seats have the same id
        * self._caches contains the list of all the coach ids
    """

    def __init__(self, *, id: TrainId, seats: list[Seat]) -> None:
        self.id = id
        self._seats: dict[SeatId, Seat] = {}
        self._coaches: set[CoachId] = set()
        for seat in seats:
            coach_id = seat.coach_id
            self._seats[seat.id] = seat
            self._coaches.add(coach_id)

    def booking_reference(self, seat_id: SeatId) -> BookingReference | None:
        seat = self._seats.get(seat_id)
        if not seat:
            return None
        return seat.booking_reference

    def _get_seat(self, id: SeatId) -> Seat:
        res = self._seats.get(id)
        if not res:
            raise SeatNotFound(id, train_id=self.id)
        return res

    def is_free(self, seat_id: SeatId) -> bool:
        seat = self._get_seat(seat_id)
        return seat.is_free

    def book(self, seats: list[SeatId], booking_reference: BookingReference) -> None:
        for seat_id in seats:
            seat = self._get_seat(seat_id)
            seat.book(booking_reference)

    def seats(self) -> list[Seat]:
        return list(self._seats.values())

    def seats_in_coach(self, coach_id: CoachId) -> list[Seat]:
        return [s for s in self._seats.values() if s.coach_id == coach_id]

    def coaches(self) -> list[CoachId]:
        return sorted(self._coaches)

    def occupied_seats_in_coach(self, coach_id: CoachId) -> list[Seat]:
        seats_in_coach = self.seats_in_coach(coach_id)
        return [s for s in seats_in_coach if not s.is_free]

    def occupancy_for_coach(self, coach_id: CoachId) -> float:
        seats_in_coach = self.seats_in_coach(coach_id)
        occupied_seats_in_coach = self.occupied_seats_in_coach(coach_id)
        return (len(occupied_seats_in_coach)) / len(seats_in_coach)

    def occupancy_for_coach_after_booking(
        self, coach_id: CoachId, seat_count: int
    ) -> float:
        seats_in_coach = self.seats_in_coach(coach_id)
        occupied_seats_in_coach = self.occupied_seats_in_coach(coach_id)
        return (len(occupied_seats_in_coach) + seat_count) / len(seats_in_coach)

    def occupancy_after_booking(self, seat_count: int) -> float:
        occupied_seats = [s for s in self._seats.values() if not s.is_free]
        return (len(occupied_seats) + seat_count) / len(self._seats)

    def occupancy(self) -> float:
        occupied_seats = [s for s in self._seats.values() if not s.is_free]
        return len(occupied_seats) / len(self._seats)

    def __repr__(self) -> str:
        return f"{self.seats()}"


@dataclass(frozen=True)
class Reservation:
    train: TrainId
    seats: list[SeatId]
    booking_reference: BookingReference

    def __str__(self) -> str:
        return f"Reservation(reference={self.booking_reference}, train={self.train}, seats={[str(i) for i in self.seats]})"


class SeatNotFound(Exception):
    def __init__(self, id: SeatId, train_id: TrainId):
        self.id = id
        self.train_id = train_id

    def __str__(self) -> str:
        return "No seat with id {self.id} in {self.train_id}"


class AlreadyBooked(Exception):
    def __init__(
        self,
        id: SeatId,
        current_booking_reference: BookingReference,
        invalid_booking_reference: BookingReference,
    ):
        self.id = id
        self.current_booking_reference = current_booking_reference
        self.invalid_booking_reference = invalid_booking_reference

    def __str__(self) -> str:
        res = f"Trying to book seat '{self.id}' with '{self.invalid_booking_reference}'"
        res += f" but it's already booked with '{self.current_booking_reference}'"
        return res
