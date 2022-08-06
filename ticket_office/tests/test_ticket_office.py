import pytest

from reservation import BookingReference, Reservation, SeatId, Train, TrainId
from ticket_office import NotEnoughFreeSeats, TicketOffice

from .conftest import FakeClient, make_empty_train


class Context:
    def __init__(self, booked_seats: list[str]) -> None:
        self.fake_client = FakeClient()
        self.train_id = TrainId("express_2000")
        self.ticket_office = TicketOffice(client=self.fake_client)
        self.train = make_empty_train(self.train_id)
        ids = [SeatId.parse(s) for s in booked_seats]
        booking_reference = BookingReference("old")
        self.train.book(ids, booking_reference)
        self.fake_client.set_train(self.train)

    def reserve(self, seat_count: int) -> Reservation:
        self.fake_client.set_booking_reference(BookingReference("new"))
        reservation = self.ticket_office.reserve(self.train_id, seat_count)
        return reservation


def test_reserve_seats_from_empty_train() -> None:
    """
    Given an empty train where all seats are free
    When we book 4 seats
    Then the reservation is valid
    """
    context = Context(booked_seats=[])

    reservation = context.reserve(4)

    check_reservation(
        reservation,
        train=context.train,
        seat_count=4,
    )


def test_reserve_four_additional_seats() -> None:
    """
    Given a train with 8 seats remaining in coach A
    When we book 4 seats
    Then it makes a valid reservation
    """
    context = Context(booked_seats=["01A", "02A"])

    reservation = context.reserve(4)

    check_reservation(
        reservation,
        train=context.train,
        seat_count=4,
    )


def test_chose_correct_coach_when_the_first_one_is_almost_full() -> None:
    """
    Given:
        Coach A is at 80%
        Coach B is free
    When booking 4 seats
    Then we book 4 seats in coach B

    """
    context = Context(
        booked_seats=["01A", "02A", "03A", "04A", "05A", "06A", "07A", "08A"],
    )

    reservation = context.reserve(4)

    check_reservation(
        reservation,
        train=context.train,
        seat_count=4,
    )


def test_chose_next_coach_when_the_first_one_is_at_60_percent() -> None:
    """
    Given:
        Coach A is at 50%
        Coach B is at 40%
    When:
        Booking 3 seats
    Then:
        We book 3 seats in coach B because booking one seat in coach A
        would make the occupancy for A greater than 70%
    """
    # fmt: off
    booked_seats = [
        "01A", "02A", "03A", "04A", "05A",
        "01B", "02B", "03B", "04B",
    ]
    # fmt: on
    context = Context(booked_seats=booked_seats)

    reservation = context.reserve(3)

    check_reservation(
        reservation,
        train=context.train,
        seat_count=3,
    )


def test_raise_if_going_over_70_percent_for_the_whole_train() -> None:
    # Note: the algorithm we use guarantees that no coach every goes
    # above 70% - so this can happens only if there were bookings
    # not made by us ...
    """
    Given:
        Coach A is at 80%
        Coach B is at 70%
        Coach C is at 60%
        Coach D is at 70%
        Coach E is at 70%
    When:
        Booking 1 seat
    Then
       It fails with NotEnoughFreeSeats
    """
    # fmt: off
    booked_seats = [
        "01A", "02A", "03A", "04A", "05A", "06A", "07A", "08A",
        "01B", "02B", "03B", "04B", "05B", "06B", "07B",
        "01C", "02C", "03C", "04C", "05C", "06C", "07B",
        "01D", "02D", "03D", "04D", "05D", "06D", "07B",
        "01E", "02E", "03E", "04E", "05E", "06E", "07B",
    ]
    # fmt: on
    context = Context(booked_seats=booked_seats)

    with pytest.raises(NotEnoughFreeSeats):
        context.reserve(3)


def test_fail_when_no_coach_can_be_filled() -> None:
    """
    Given: all coaches are at 70%
    When:
        Booking 1 seat
    Then
       It fails with NotEnoughFreeSeats
    """
    # fmt: off
    booked_seats = [
        "01A", "02A", "03A", "04A", "05A", "06A", "07A",
        "01B", "02B", "03B", "04B", "05B", "06B", "07B",
        "01C", "02C", "03C", "04C", "05C", "06C", "07C",
        "01D", "02D", "03D", "04D", "05D", "06D", "07D",
        "01E", "02E", "03E", "04E", "05E", "06E", "07E",
    ]
    # fmt: on
    context = Context(booked_seats=booked_seats)

    with pytest.raises(NotEnoughFreeSeats):
        context.reserve(3)


def check_reservation(
    reservation: Reservation,
    *,
    train: Train,
    seat_count: int,
) -> None:
    train.book(reservation.seats, reservation.booking_reference)

    seat_ids = reservation.seats
    assert len(seat_ids) == seat_count

    # Check all seats in the reservation are in the same coach
    coaches = {s.coach_id for s in seat_ids}
    assert len(coaches) == 1, f"All seats should have the same coach {seat_ids}"

    # Check total occupancy is below 0.7
    for coach in train.coaches():
        occupancy = train.occupancy()
        assert occupancy <= 0.7, (
            f"Not enough room in coach {coach} : {train.seats_in_coach(coach)}.\n"
            f"Reservation was:\n{reservation}"
        )
