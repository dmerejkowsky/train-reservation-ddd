from ticket_office.domain.reservation import (
    BookingReference,
    Reservation,
    SeatId,
    TrainId,
)
from ticket_office.infra.http_client import HttpClient


def test_can_get_empty_train(train_id: TrainId, http_client: HttpClient) -> None:
    train = http_client.get_train(train_id)

    actual_seats = train.seats()
    assert len(actual_seats) == 16
    for seat in actual_seats:
        assert seat.is_free


def test_can_book_some_seats(train_id: TrainId, http_client: HttpClient) -> None:
    seat_ids = [
        SeatId.parse("01A"),
        SeatId.parse("02A"),
    ]
    booking_reference = BookingReference("123456")
    reservation = Reservation(
        train=train_id, seats=seat_ids, booking_reference=booking_reference
    )

    http_client.make_reservation(reservation)

    train = http_client.get_train(train_id)

    for seat_id in seat_ids:
        assert not train.is_free(seat_id)


def test_can_get_booking_reference(http_client: HttpClient) -> None:
    booking_reference = http_client.get_booking_reference()
    assert booking_reference
