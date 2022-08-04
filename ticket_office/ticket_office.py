import json
from typing import Any

from client import Client, Reservation, TrainId


class TicketOffice(object):
    def __init__(self, *, client: Client) -> None:
        self.client = client

    def reserve(self, train_id: TrainId, seat_count: int) -> Reservation:
        manifest = self.client.get_manifest(train_id)
        available_seats = (s for s in manifest.seats() if s.is_free)
        to_reserve = []
        for i in range(seat_count):
            to_reserve.append(next(available_seats))

        booking_reference = self.client.get_booking_reference()

        seat_ids = [s.id for s in to_reserve]
        reservation = Reservation(
            train=train_id, seats=seat_ids, booking_reference=booking_reference
        )

        self.client.make_reservation(reservation)

        return reservation
