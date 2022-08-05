from reservation import BookingReference, Reservation, SeatId, Train, TrainId
from ticket_office import TicketOffice

from .conftest import FakeClient, make_empty_train


class Context:
    def __init__(self) -> None:
        self.fake_client = FakeClient()
        self.train_id = TrainId("express_2000")
        self.ticket_office = TicketOffice(client=self.fake_client)
        self.train = make_empty_train(self.train_id)
        self.fake_client.set_train(self.train)

    def book_seats(self, seats: list[str], booking_reference: BookingReference) -> None:
        ids = [SeatId.parse(s) for s in seats]
        self.train.book(ids, booking_reference)


def test_reserve_seats_from_empty_train() -> None:
    """
    Given an empty train where all seats are free
    When we book 4 seats
    Then the reservation is valid
    """
    context = Context()
    context.fake_client.set_booking_reference(BookingReference("1234"))
    reservation = context.ticket_office.reserve(context.train_id, 4)

    check_reservation(
        reservation,
        train=context.train,
        booking_reference=BookingReference("1234"),
        seat_count=4,
    )


def test_reserve_four_additional_seats() -> None:
    """
    Given a train with 8 seats remaining in coach A
    When we book 4 seats
    Then it makes a valid reservation
    """
    context = Context()
    old_booking_reference = BookingReference("old")
    context.book_seats(["1A", "2A"], old_booking_reference)

    new_booking_reference = BookingReference("new")
    context.fake_client.set_booking_reference(new_booking_reference)
    reservation = context.ticket_office.reserve(context.train_id, 4)

    check_reservation(
        reservation,
        train=context.train,
        booking_reference=new_booking_reference,
        seat_count=4,
    )


def test_chose_correct_coach_when_the_first_one_is_almost_full() -> None:
    """
    Given:
        Coach B is free
        Coach A is at 80%
    When booking 4 seats
    Then we book 4 seats in coach B

    """
    context = Context()
    old_booking_reference = BookingReference("old")
    context.book_seats(
        ["0A", "1A", "2A", "3A", "4A", "5A", "6A"],
        old_booking_reference,
    )

    new_booking_reference = BookingReference("new")
    context.fake_client.set_booking_reference(new_booking_reference)
    reservation = context.ticket_office.reserve(context.train_id, 4)

    check_reservation(
        reservation,
        train=context.train,
        booking_reference=new_booking_reference,
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
    context = Context()
    old_booking_reference = BookingReference("old")
    context.book_seats(
        ["0A", "1A", "2A", "3A", "4A"],
        old_booking_reference,
    )

    new_booking_reference = BookingReference("new")
    context.fake_client.set_booking_reference(new_booking_reference)
    reservation = context.ticket_office.reserve(context.train_id, 3)

    check_reservation(
        reservation,
        train=context.train,
        booking_reference=new_booking_reference,
        seat_count=3,
    )


def check_reservation(
    reservation: Reservation,
    *,
    train: Train,
    seat_count: int,
    booking_reference: BookingReference,
) -> None:
    assert reservation.booking_reference == booking_reference
    assert reservation.train == train.id
    seat_ids = reservation.seats
    assert len(seat_ids) == seat_count

    # Simulate a booking
    train.book(reservation.seats, booking_reference)

    # Check all seats in the reservation are in the same coach
    coaches = {s.coach_id for s in seat_ids}
    assert len(coaches) == 1, f"All seats should have the same coach {seat_ids}"

    for coach in train.coaches():
        occupancy = train.occupancy_for_coach(coach)
        assert occupancy <= 0.7, (
            f"Not enough room in coach {coach} : {train.seats_in_coach(coach)}.\n"
            f"Reservation was:\n{reservation}"
        )
