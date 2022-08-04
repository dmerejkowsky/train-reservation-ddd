from dataclasses import dataclass
from functools import total_ordering

from value_object import ValueObject


class BookingReference(ValueObject):
    pass


class SeatNumber(ValueObject):
    pass


class CoachId(ValueObject):
    pass


@total_ordering
@dataclass(frozen=True)
class SeatId:
    number: SeatNumber
    coach_id: CoachId

    @classmethod
    def parse(cls, value: str) -> "SeatId":
        assert len(value) == 2
        number = SeatNumber(int(value[0]))
        coach_id = CoachId(value[1])
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
        self.booking_reference = booking_reference

    @property
    def is_free(self) -> bool:
        return self.booking_reference is None


class TrainId(ValueObject):
    pass


class Train:
    def __init__(self, *, id: TrainId, seats: list[Seat]) -> None:
        self.id = id
        self._seats: dict[SeatId, Seat] = {}
        for seat in seats:
            self._seats[seat.id] = seat

    def booking_reference(self, seat_id: SeatId) -> BookingReference | None:
        seat = self._seats.get(seat_id)
        if not seat:
            return None
        return seat.booking_reference

    def is_free(self, seat_id: SeatId) -> bool:
        assert seat_id in self._seats
        return self._seats[seat_id].is_free

    def book(self, seat_id: SeatId, booking_reference: BookingReference) -> None:
        assert seat_id in self._seats
        self._seats[seat_id].book(booking_reference)

    def seats(self) -> list[Seat]:
        return list(self._seats.values())

    def __repr__(self) -> str:
        return f"{self.seats()}"


@dataclass(frozen=True)
class Reservation:
    train: TrainId
    seats: list[SeatId]
    booking_reference: BookingReference
