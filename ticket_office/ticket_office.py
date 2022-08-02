import httpx
import json

from client import Client, TrainId, Reservation


class TicketOffice(object):
    def __init__(self, *, client: Client) -> None:
        self.client = client

    def reserve(self, train_id: str, seat_count: str) -> str:
        train_id_ = TrainId(train_id)
        number_of_seats = int(seat_count)

        manifest = self.client.get_manifest(train_id_)
        available_seats = (s for s in manifest.seats() if s.is_free)
        to_reserve = []
        for i in range(number_of_seats):
            to_reserve.append(next(available_seats))

        booking_reference = self.client.get_booking_reference()

        seat_ids = [s.id for s in to_reserve]
        reservation = Reservation(
            train=train_id_, seats=seat_ids, booking_reference=booking_reference
        )

        self.client.make_reservation(reservation)

        return serialize_reservation(reservation)


def serialize_reservation(reservation: Reservation) -> str:
    train_id = reservation.train
    seat_ids = reservation.seats
    booking_reference = reservation.booking_reference

    payload = {
        "train_id": str(train_id),
        "seats": [str(s) for s in seat_ids],
        "booking_reference": str(booking_reference),
    }

    return json.dumps(payload)


if __name__ == "__main__":
    """Deploy this class as a web service using CherryPy"""
    import cherrypy
    from http_client import HttpClient

    TicketOffice.reserve.exposed = True  # type: ignore[attr-defined]
    cherrypy.config.update({"server.socket_port": 8083})
    cherrypy.quickstart(TicketOffice(client=HttpClient()))
