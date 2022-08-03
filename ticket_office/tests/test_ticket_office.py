import pytest

from client import (
    BookingReference,
    Client,
    CoachId,
    Manifest,
    Seat,
    SeatId,
    SeatNumber,
    TrainId,
)
from .conftest import FakeClient


def test_seat() -> None:
    seat_id = SeatId.parse("1A")
    seat = Seat.from_id(seat_id)
    assert seat.id == seat_id


def test_seat_ids_are_value_objects() -> None:
    x = SeatId.parse("1A")
    y = SeatId.parse("1A")
    z = SeatId.parse("2A")

    assert x == y
    assert x != z
    assert x <= y < z


def test_manifest_has_no_booking_reference_by_default() -> None:
    seats = [
        Seat.parse("1A"),
        Seat.parse("2A"),
    ]

    manifest = Manifest.with_free_seats(seats)

    seat_id = SeatId.parse("1A")
    assert manifest.booking_reference(seat_id) is None


def test_retrieve_booking_reference_from_manifest() -> None:
    seat_id = SeatId.parse("1A")
    seats = [Seat.from_id(seat_id)]
    manifest = Manifest.with_free_seats(seats)

    booking_reference = BookingReference("123456")

    manifest.book(seat_id, booking_reference)

    assert manifest.booking_reference(seat_id) == booking_reference


def test_get_empty_manifest(fake_client: FakeClient, train_id: TrainId) -> None:
    manifest = fake_client.get_manifest(train_id)

    assert manifest.seats() == []


def test_retrieved_set_manifest(fake_client: FakeClient, train_id: TrainId) -> None:
    seats = [
        Seat.parse("1A"),
        Seat.parse("2A"),
    ]

    manifest = Manifest.with_free_seats(seats)
    fake_client.set_manifest(manifest)

    response = fake_client.get_manifest(train_id)

    assert response == manifest
