from dataclasses import dataclass
import abc


class SeatNumber:
    def __init__(self, value: int):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"SeatNumber({self})"


class CoachId:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"CoachId({self})"


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

    def __str__(self) -> str:
        return f"{self.number}{self.coach_id}"

    def __repr__(self) -> str:
        return f"SeatId({self})"


class BookingReference:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"BookingReference({self})"


@dataclass
class Seat:
    number: SeatNumber
    coach_id: CoachId
    booking_reference: BookingReference | None = None

    @property
    def id(self) -> SeatId:
        return SeatId(number=self.number, coach_id=self.coach_id)

    @classmethod
    def from_id(cls, id: SeatId) -> "Seat":
        return cls(id.number, id.coach_id)

    @classmethod
    def parse(cls, value: str) -> "Seat":
        id = SeatId.parse(value)
        return cls.from_id(id)

    def book(self, booking_reference: BookingReference) -> None:
        self.booking_reference = booking_reference

    @property
    def is_free(self) -> bool:
        return self.booking_reference is None


class Manifest:
    def __init__(self, *, seats: list[Seat]) -> None:
        self._seats: dict[SeatId, Seat] = {}
        for seat in seats:
            self._seats[seat.id] = seat

    @classmethod
    def empty(cls) -> "Manifest":
        return cls(seats=[])

    @classmethod
    def with_free_seats(cls, seats: list[Seat]) -> "Manifest":
        return cls(seats=seats)

    def booking_reference(self, seat_id: SeatId) -> BookingReference | None:
        seat = self._seats.get(seat_id)
        if not seat:
            return None
        return seat.booking_reference

    def book(self, seat_id: SeatId, booking_reference: BookingReference) -> None:
        assert seat_id in self._seats
        self._seats[seat_id].book(booking_reference)

    def seats(self) -> list[Seat]:
        return list(self._seats.values())

    def __repr__(self) -> str:
        return f"{self.seats()}"


class TrainId:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Reservation:
    train_id: TrainId
    seats: list[SeatId]
    booking_reference: BookingReference


class Client(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_manifest(self, train_id: TrainId) -> Manifest:
        pass

    @abc.abstractmethod
    def make_reservation(self, reservation: Reservation) -> None:
        pass
