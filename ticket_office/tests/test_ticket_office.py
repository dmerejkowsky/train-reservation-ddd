from client import BookingReference, Reservation, Seat, SeatId, Train, TrainId
from ticket_office import TicketOffice

from .conftest import FakeClient, make_empty_train


def test_seat() -> None:
    seat_id = SeatId.parse("1A")
    seat = Seat.free_seat_with_id(seat_id)
    assert seat.id == seat_id


def test_seat_ids_are_value_objects() -> None:
    x = SeatId.parse("1A")
    y = SeatId.parse("1A")
    z = SeatId.parse("2A")

    assert x == y
    assert x != z
    assert x <= y < z


def test_retrieve_booking_reference_from_train(train: Train) -> None:
    seat_id = SeatId.parse("1A")
    booking_reference = BookingReference("123456")

    train.book(seat_id, booking_reference)

    assert train.booking_reference(seat_id) == booking_reference


def test_get_empty_train(
    fake_client: FakeClient, train_id: TrainId, train: Train
) -> None:
    train = fake_client.get_train(train_id)
    for seat in train.seats():
        assert seat.is_free


class Context:
    def __init__(self) -> None:
        self.fake_client = FakeClient()
        self.train_id = TrainId("express_2000")
        self.ticket_office = TicketOffice(client=self.fake_client)
        self.train = make_empty_train(self.train_id)
        self.fake_client.set_train(self.train)

    def book_seat(self, id: SeatId, booking_reference: BookingReference) -> None:
        self.train.book(id, booking_reference)


def test_reserve_seats_from_empty_train() -> None:
    context = Context()
    context.fake_client.set_booking_reference(BookingReference("1234"))
    reservation = context.ticket_office.reserve(context.train_id, 4)

    check_reservation(
        reservation,
        train_id=context.train_id,
        booking_reference=BookingReference("1234"),
        seat_count=4,
    )


def test_reserve_four_additional_seats() -> None:
    context = Context()
    old_booking_reference = BookingReference("old")
    for id in ["1A", "2A", "3A", "4A"]:
        context.book_seat(SeatId.parse(id), old_booking_reference)

    new_booking_reference = BookingReference("new")
    context.fake_client.set_booking_reference(new_booking_reference)
    reservation = context.ticket_office.reserve(context.train_id, 4)

    check_reservation(
        reservation,
        train_id=context.train_id,
        booking_reference=new_booking_reference,
        seat_count=4,
    )


def check_reservation(
    reservation: Reservation,
    *,
    train_id: TrainId,
    seat_count: int,
    booking_reference: BookingReference,
) -> None:
    assert reservation.booking_reference == booking_reference
    assert reservation.train == train_id
    seat_ids = reservation.seats
    assert len(seat_ids) == seat_count

    coaches = {s.coach_id for s in seat_ids}
    assert len(coaches) == 1, f"All seats should have the same coach {seat_ids}"
