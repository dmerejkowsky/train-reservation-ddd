import pytest

from ticket_office.domain.reservation import (
    AlreadyBooked,
    BookingReference,
    CoachId,
    Seat,
    SeatId,
    SeatNumber,
    Train,
    TrainId,
)


def test_cannot_create_invalid_booking_references() -> None:
    with pytest.raises(ValueError):
        BookingReference("")


def test_cannot_create_empty_train_id() -> None:
    with pytest.raises(ValueError):
        TrainId("")


def test_cannot_create_blank_train_id() -> None:
    with pytest.raises(ValueError):
        TrainId("  \t")


def test_can_create_empty_seats() -> None:
    seat_id = SeatId.parse("01A")
    seat = Seat.free_seat_with_id(seat_id)
    assert seat.id == seat_id
    assert seat.is_free


def test_seat_ids_are_value_objects() -> None:
    x = SeatId.parse("01A")
    y = SeatId.parse("01A")
    z = SeatId.parse("02A")

    assert x == y
    assert x != z
    assert x <= y < z


def test_parse_seat_ids() -> None:
    x = SeatId.parse("01A")
    assert x.coach_id == CoachId("A")
    assert x.number == SeatNumber(1)


def test_seat_can_go_from_free_to_booked() -> None:
    number = SeatNumber(1)
    coach_id = CoachId("A")
    seat = Seat(number=number, coach_id=coach_id, booking_reference=None)

    booking_reference = BookingReference("123")
    seat.book(booking_reference)

    assert seat.booking_reference == booking_reference


def test_seat_can_be_booked_twice_with_the_same_reference() -> None:
    number = SeatNumber(1)
    coach_id = CoachId("A")
    booking_reference = BookingReference("123")
    seat = Seat(number=number, coach_id=coach_id, booking_reference=booking_reference)

    seat.book(booking_reference)

    assert seat.booking_reference == booking_reference


def test_seat_cannot_be_booked_with_conflicting_references() -> None:
    number = SeatNumber(1)
    coach_id = CoachId("A")
    first_booking_reference = BookingReference("123")
    second_booking_reference = BookingReference("456")
    seat = Seat(
        number=number, coach_id=coach_id, booking_reference=first_booking_reference
    )

    with pytest.raises(AlreadyBooked) as e:
        seat.book(second_booking_reference)
    print(e.value)


def test_can_book_some_seats(train: Train) -> None:
    seat_1 = SeatId.parse("01A")
    seat_2 = SeatId.parse("02A")
    booking_reference = BookingReference("123456")

    train.book([seat_1, seat_2], booking_reference)

    for seat in seat_1, seat_2:
        assert train.booking_reference(seat) == booking_reference


def test_compute_occupancy_by_coach(train: Train) -> None:
    coach_id = CoachId("A")
    booking_reference = BookingReference("1234")
    ids = [SeatId(number=SeatNumber(i), coach_id=coach_id) for i in range(1, 6)]
    train.book(ids, booking_reference)

    assert train.occupancy_for_coach_after_booking(coach_id, seat_count=1) == 0.6
