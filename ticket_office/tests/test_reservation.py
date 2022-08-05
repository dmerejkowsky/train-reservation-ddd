from reservation import BookingReference, CoachId, Seat, SeatId, SeatNumber, Train


def test_can_create_empty_seats() -> None:
    seat_id = SeatId.parse("1A")
    seat = Seat.free_seat_with_id(seat_id)
    assert seat.id == seat_id
    assert seat.is_free


def test_seat_ids_are_value_objects() -> None:
    x = SeatId.parse("1A")
    y = SeatId.parse("1A")
    z = SeatId.parse("2A")

    assert x == y
    assert x != z
    assert x <= y < z


def test_parse_seat_ids() -> None:
    x = SeatId.parse("0A")
    assert x.coach_id == CoachId("A")
    assert x.number == SeatNumber(0)


def test_can_book_some_seats(train: Train) -> None:
    seat_1 = SeatId.parse("1A")
    seat_2 = SeatId.parse("2A")
    booking_reference = BookingReference("123456")

    train.book([seat_1, seat_2], booking_reference)

    for seat in seat_1, seat_2:
        assert train.booking_reference(seat) == booking_reference


def test_compute_occupancy_by_coach(train: Train) -> None:
    coach_id = CoachId("A")
    booking_reference = BookingReference("1234")
    ids = [SeatId(number=SeatNumber(i), coach_id=coach_id) for i in range(0, 5)]
    train.book(ids, booking_reference)

    assert train.occupancy_for_coach_after_booking(coach_id, seat_count=1) == 0.6
