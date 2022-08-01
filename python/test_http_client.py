from client import BookingReference, Seat, SeatId, TrainId, Reservation
from http_client import HttpClient


def test_can_get_empty_manifest(train_id: TrainId, http_client: HttpClient) -> None:
    manifest = http_client.get_manifest(train_id)

    actual_seats = manifest.seats()
    assert len(actual_seats) == 16
    for seat in actual_seats:
        assert seat.is_free


def test_can_book_some_seats(train_id: TrainId, http_client: HttpClient) -> None:
    seat_ids = [
        SeatId.parse("1A"),
        SeatId.parse("2A"),
    ]
    booking_reference = BookingReference("123456")
    reservation = Reservation(
        train_id=train_id, seats=seat_ids, booking_reference=booking_reference
    )

    http_client.make_reservation(reservation)
