import pytest

from reservation import BookingReference, Reservation, SeatId, Train, TrainId

from .helpers import FakeClient


def test_fake_client_comes_with_an_empty_train(
    fake_client: FakeClient, train_id: TrainId
) -> None:
    train = fake_client.get_train(train_id)
    for seat in train.seats():
        assert seat.is_free


def test_throws_when_trying_to_book_same_seat_with_different_booking_references(
    train_id: TrainId, train: Train, fake_client: FakeClient
) -> None:
    seat_ids = [SeatId.parse("1A"), SeatId.parse("2A")]
    train.book(seat_ids, BookingReference("1234"))

    fake_client.set_train(train)

    conflicting_seats = [SeatId.parse("2A"), SeatId.parse("3A")]
    conflicting_reservation = Reservation(
        train=train_id,
        seats=conflicting_seats,
        booking_reference=BookingReference("5678"),
    )

    with pytest.raises(Exception) as e:
        fake_client.make_reservation(conflicting_reservation)
    assert "already booked" in str(e.value)
