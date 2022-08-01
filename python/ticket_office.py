import httpx
import json

from client import Client, TrainId


class TicketOffice(object):
    def __init__(self, *, client: Client) -> None:
        self.client = client
        self.httpx_client = httpx.Client()

    def reserve(self, *args: str) -> str:
        # CherryPy stuff
        assert len(args) == 2
        train_id_str = args[0]
        seat_count_str = args[1]

        number_of_seats = int(seat_count_str)
        train_id = TrainId(train_id_str)

        manifest = self.client.get_manifest(train_id)
        available_seats = (s for s in manifest.seats() if s.is_free)
        to_reserve = []
        for i in range(number_of_seats):
            to_reserve.append(next(available_seats))
        booking_reference = self.httpx_client.get(
            "http://localhost:8082/booking_reference"
        ).text

        seat_ids = [s.id for s in to_reserve]
        reservation = {
            "train_id": train_id,
            "booking_reference": booking_reference,
            "seats": seat_ids,
        }

        reservation_payload = {
            "train_id": reservation["train_id"],
            "seats": json.dumps(reservation["seats"]),
            "booking_reference": reservation["booking_reference"],
        }

        response = self.httpx_client.post(
            "http://localhost:8081/reserve", data=reservation_payload
        ).json()
        assert response.get("seats")

        return json.dumps(reservation)


if __name__ == "__main__":
    """Deploy this class as a web service using CherryPy"""
    import cherrypy
    from http_client import HttpClient

    TicketOffice.reserve.exposed = True  # type: ignore[attr-defined]
    cherrypy.config.update({"server.socket_port": 8083})
    cherrypy.quickstart(TicketOffice(client=HttpClient()))
