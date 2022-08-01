from typing import Any

import httpx

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


class HttpClient(Client):
    def __init__(self) -> None:
        self._client = httpx.Client()

    def reset(self, train_id: TrainId) -> None:
        # Note: only for tests!
        response = self._client.post("http://localhost:8081/reset/" + str(train_id))
        response.raise_for_status()

    def get_manifest(self, train_id: TrainId) -> Manifest:
        response = self._client.get(
            "http://localhost:8081/data_for_train/" + str(train_id)
        )
        response.raise_for_status()

        return manifest_from_train_data(response.json())


def manifest_from_train_data(train_data: Any) -> Manifest:
    assert "seats" in train_data
    seat_dicts = train_data["seats"].values()
    seats: list[Seat] = []
    for seat_dict in seat_dicts:
        coach_id = CoachId(seat_dict["coach"])
        number = SeatNumber(int(seat_dict["seat_number"]))
        seat_id = SeatId(number=number, coach_id=coach_id)
        booking_str = seat_dict["booking_reference"]
        if booking_str:
            booking_reference = BookingReference(seat_dict["booking_reference"])
        else:
            booking_reference = None
        seat = Seat(
            number=number, coach_id=coach_id, booking_reference=booking_reference
        )
        seats.append(seat)

    return Manifest(seats=seats)
