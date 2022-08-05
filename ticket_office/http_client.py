import json
from typing import Any

import httpx

from client import Client
from reservation import (
    BookingReference,
    CoachId,
    Reservation,
    Seat,
    SeatNumber,
    Train,
    TrainId,
)


class HttpClient(Client):
    def __init__(self) -> None:
        self._client = httpx.Client()

    def reset(self, train_id: TrainId) -> None:
        # Note: only for tests!
        response = self._client.post("http://localhost:8081/reset/" + str(train_id))
        response.raise_for_status()

    def get_train(self, train_id: TrainId) -> Train:
        response = self._client.get(
            "http://localhost:8081/data_for_train/" + str(train_id)
        )
        response.raise_for_status()

        return parse_train_data(train_id, response.json())

    def make_reservation(self, reservation: Reservation) -> None:
        train_id = reservation.train
        seat_ids = reservation.seats
        booking_reference = reservation.booking_reference

        # Note: this is *not* reservation.as_dict(), in particular,
        # payload["seats"] is a *string*
        payload: dict[str, str] = {
            "train_id": str(train_id),
            "seats": json.dumps([str(i) for i in seat_ids]),
            "booking_reference": str(booking_reference),
        }

        response = self._client.post("http://localhost:8081/reserve", data=payload)
        # Note: sadly, the train_data responds with 200 OK and with invalid json
        # in case of error
        if "already booked" in response.text:
            raise Exception("Already booked")

    def get_booking_reference(self) -> BookingReference:
        response = self._client.get("http://localhost:8082/booking_reference")
        response.raise_for_status()
        return BookingReference(response.text)


def parse_train_data(train_id: TrainId, train_data: Any) -> Train:
    seat_dicts = train_data["seats"].values()
    seats: list[Seat] = []
    for seat_dict in seat_dicts:
        coach_id = CoachId(seat_dict["coach"])
        number = SeatNumber(int(seat_dict["seat_number"]))
        booking_str = seat_dict["booking_reference"]
        if booking_str:
            booking_reference = BookingReference(booking_str)
        else:
            booking_reference = None
        seat = Seat(
            number=number, coach_id=coach_id, booking_reference=booking_reference
        )
        seats.append(seat)

    return Train(id=train_id, seats=seats)
